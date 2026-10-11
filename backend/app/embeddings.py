from langchain_core.embeddings import Embeddings
from langchain_huggingface import HuggingFaceEmbeddings


class E5Embeddings(Embeddings):

    def __init__(self, model_name: str):
        self._impl = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._impl.embed_documents([f"passage: {t}" for t in texts])

    def embed_query(self, text: str) -> list[float]:
        return self._impl.embed_query(f"query: {text}")
