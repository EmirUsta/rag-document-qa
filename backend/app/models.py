from pydantic import BaseModel


class ChatRequest(BaseModel):
    session_id: str
    message: str


class SourceItem(BaseModel):
    file_name: str | None
    page_number: int | None


class DocumentInfo(BaseModel):
    doc_id: str
    original_filename: str
    page_count: int
    chunk_count: int
    uploaded_at: str


class JobStatus(BaseModel):
    status: str
    stage: str
    progress_percent: int
    error: str | None = None


class UploadResponse(BaseModel):
    job_ids: list[str]


class HistoryMessage(BaseModel):
    role: str
    content: str
