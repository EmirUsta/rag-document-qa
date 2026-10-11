import json

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.models import ChatRequest
from app.rag import clear_history, get_history, stream_answer

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("")
async def chat(payload: ChatRequest, request: Request) -> StreamingResponse:
    client = request.app.state.weaviate_client
    embeddings = request.app.state.embeddings

    async def gen():
        async for event in stream_answer(
            client, embeddings, payload.session_id, payload.message
        ):
            yield json.dumps(event, ensure_ascii=False) + "\n"

    return StreamingResponse(gen(), media_type="application/x-ndjson")


@router.get("/history")
async def history(session_id: str) -> list[dict]:
    h = get_history(session_id)
    return [{"role": m.type, "content": m.content} for m in h.messages]


@router.delete("/history")
async def reset_history(session_id: str) -> dict:
    clear_history(session_id)
    return {"status": "cleared"}
