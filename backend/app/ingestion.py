import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app import registry
from app.config import settings
from app.jobs import job_store

logger = logging.getLogger(__name__)

executor = ThreadPoolExecutor(max_workers=1)


def _clean_metadata(chunk: Document, doc_id: str, original_filename: str) -> Document:
    page_number = chunk.metadata.get("page_number") or 1
    return Document(
        page_content=chunk.page_content,
        metadata={
            "source": original_filename,
            "page_number": int(page_number),
            "doc_id": doc_id,
        },
    )


def process_pdf_job(
    job_id: str,
    file_path: str,
    doc_id: str,
    original_filename: str,
    vector_store,
) -> None:
    try:
        job_store.update(
            job_id, status="processing", stage="metin çıkarılıyor", progress_percent=10
        )
        loader = UnstructuredFileLoader(file_path, mode="paged", strategy="fast")
        documents = loader.load()
        page_count = len(documents)

        job_store.update(job_id, stage="parçalanıyor", progress_percent=30)
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size, chunk_overlap=settings.chunk_overlap
        )
        chunks = splitter.split_documents(documents)
        chunks = [_clean_metadata(c, doc_id, original_filename) for c in chunks]

        total = len(chunks)
        if total == 0:
            raise ValueError(
                "Bu PDF'ten metin çıkarılamadı (taranmış/görsel bir doküman olabilir)."
            )

        batch_size = 16
        for i in range(0, total, batch_size):
            batch = chunks[i : i + batch_size]
            vector_store.add_documents(batch)
            done = min(i + batch_size, total)
            job_store.update(
                job_id,
                stage=f"embedding {done}/{total}",
                progress_percent=30 + int(60 * done / max(total, 1)),
            )

        registry.insert_document(
            settings.registry_db_path,
            doc_id,
            original_filename,
            f"{doc_id}.pdf",
            page_count,
            total,
            datetime.now(timezone.utc).isoformat(),
        )
        job_store.update(
            job_id, stage="tamamlandı", status="done", progress_percent=100
        )
    except Exception as e:  # noqa: BLE001
        logger.exception("PDF isleme hatasi: %s", original_filename)
        job_store.update(job_id, stage="hata", status="error", error=str(e))
