from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import chat, documents, registry
from app.config import settings
from app.embeddings import E5Embeddings
from app.vectorstore import (
    ensure_collection,
    get_vector_store,
    get_weaviate_client,
    wait_for_weaviate,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Path(settings.docs_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.registry_db_path).parent.mkdir(parents=True, exist_ok=True)
    registry.init_db(settings.registry_db_path)

    client = get_weaviate_client()
    wait_for_weaviate(client)
    ensure_collection(client)

    embeddings = E5Embeddings(settings.embedding_model)

    app.state.weaviate_client = client
    app.state.embeddings = embeddings
    app.state.vector_store = get_vector_store(client, embeddings)

    yield

    client.close()


app = FastAPI(title="RAG API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router)
app.include_router(chat.router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
