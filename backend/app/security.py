import uuid

_PDF_MAGIC = b"%PDF-"


def make_safe_filename(original_name: str) -> tuple[str, str]:
    doc_id = uuid.uuid4().hex
    return doc_id, f"{doc_id}.pdf"


def has_pdf_extension(filename: str) -> bool:
    return filename.lower().endswith(".pdf")


def sniff_is_pdf(head_bytes: bytes) -> bool:
    return head_bytes.startswith(_PDF_MAGIC)
