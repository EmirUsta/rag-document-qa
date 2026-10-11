from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    groq_api_key: str
    groq_model: str = "llama-3.1-8b-instant"
    embedding_model: str = "intfloat/multilingual-e5-small"

    weaviate_host: str = "weaviate"
    weaviate_http_port: int = 8080
    weaviate_grpc_port: int = 50051
    weaviate_collection: str = "Document"

    docs_dir: str = "/app/data/docs"
    registry_db_path: str = "/app/data/registry.db"

    chunk_size: int = 2000
    chunk_overlap: int = 300
    top_k: int = 4
    grounding_distance_threshold: float = 0.55

    cors_origins: list[str] = ["http://localhost:5173"]


settings = Settings()
