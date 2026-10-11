import asyncio
import os
import uuid

from fastapi import APIRouter, File, HTTPException, Request, UploadFile

from app import registry
from app.config import settings
from app.ingestion import executor, process_pdf_job
from app.jobs import job_store
from app.security import has_pdf_extension, make_safe_filename, sniff_is_pdf
from app.vectorstore import delete_by_doc_id

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.post("")
async def upload_documents(
    request: Request, files: list[UploadFile] = File(...)
) -> dict:
    vector_store = request.app.state.vector_store
    job_ids: list[str] = []

    for f in files:
        if not f.filename or not has_pdf_extension(f.filename):
            raise HTTPException(400, f"Sadece PDF dosyaları kabul edilir: {f.filename}")

        head = await f.read(8)
        if not sniff_is_pdf(head):
            raise HTTPException(400, f"Geçersiz PDF içeriği: {f.filename}")
        await f.seek(0)

        doc_id, stored_name = make_safe_filename(f.filename)
        dest_path = os.path.join(settings.docs_dir, stored_name)
        with open(dest_path, "wb") as out:
            while chunk := await f.read(1024 * 1024):
                out.write(chunk)

        job_id = str(uuid.uuid4())
        job_store.create(job_id, f.filename)
        loop = asyncio.get_running_loop()
        loop.run_in_executor(
            executor,
            process_pdf_job,
            job_id,
            dest_path,
            doc_id,
            f.filename,
            vector_store,
        )
        job_ids.append(job_id)

    return {"job_ids": job_ids}


@router.get("/jobs")
async def list_jobs() -> list[dict]:
    return job_store.list_all()


@router.get("/jobs/{job_id}")
async def get_job_status(job_id: str) -> dict:
    job = job_store.get(job_id)
    if job is None:
        raise HTTPException(404, "job bulunamadı")
    return job


@router.get("")
async def list_documents() -> list[dict]:
    return registry.list_documents(settings.registry_db_path)


@router.delete("/{doc_id}")
async def delete_document(doc_id: str, request: Request) -> dict:
    row = registry.delete_document(settings.registry_db_path, doc_id)
    if not row:
        raise HTTPException(404, "doküman bulunamadı")

    client = request.app.state.weaviate_client
    delete_by_doc_id(client, doc_id)

    stored_path = os.path.join(settings.docs_dir, row["stored_filename"])
    if os.path.exists(stored_path):
        os.remove(stored_path)

    return {"status": "deleted"}
