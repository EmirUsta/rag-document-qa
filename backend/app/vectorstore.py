import time

import weaviate
from langchain_core.documents import Document
from langchain_weaviate.vectorstores import WeaviateVectorStore
from weaviate.classes.config import Configure, DataType, Property, VectorDistances
from weaviate.classes.query import Filter, MetadataQuery

from app.config import settings


def get_weaviate_client() -> weaviate.WeaviateClient:
    return weaviate.connect_to_custom(
        http_host=settings.weaviate_host,
        http_port=settings.weaviate_http_port,
        http_secure=False,
        grpc_host=settings.weaviate_host,
        grpc_port=settings.weaviate_grpc_port,
        grpc_secure=False,
    )


def wait_for_weaviate(client: weaviate.WeaviateClient, timeout: float = 60.0) -> None:
    start = time.time()
    last_err: Exception | None = None
    while time.time() - start < timeout:
        try:
            if client.is_ready():
                return
        except Exception as e:  # noqa: BLE001
            last_err = e
        time.sleep(2)
    raise RuntimeError(f"Weaviate {timeout}s icinde hazir olmadi: {last_err}")


def ensure_collection(client: weaviate.WeaviateClient) -> None:
    if client.collections.exists(settings.weaviate_collection):
        return
    client.collections.create(
        name=settings.weaviate_collection,
        vectorizer_config=Configure.Vectorizer.none(),
        vector_index_config=Configure.VectorIndex.hnsw(
            distance_metric=VectorDistances.COSINE
        ),
        properties=[
            Property(name="text", data_type=DataType.TEXT),
            Property(name="source", data_type=DataType.TEXT),
            Property(name="page_number", data_type=DataType.INT),
            Property(name="doc_id", data_type=DataType.TEXT),
        ],
    )


def get_vector_store(client: weaviate.WeaviateClient, embeddings) -> WeaviateVectorStore:
    return WeaviateVectorStore(
        client=client,
        index_name=settings.weaviate_collection,
        text_key="text",
        embedding=embeddings,
    )


def retrieve_with_scores(
    client: weaviate.WeaviateClient, embeddings, query: str, k: int
) -> list[tuple[Document, float]]:
    collection = client.collections.get(settings.weaviate_collection)
    vector = embeddings.embed_query(query)
    response = collection.query.near_vector(
        near_vector=vector,
        limit=k,
        return_metadata=MetadataQuery(distance=True),
        return_properties=["text", "source", "page_number", "doc_id"],
    )
    out: list[tuple[Document, float]] = []
    for obj in response.objects:
        doc = Document(
            page_content=obj.properties.get("text", ""),
            metadata={
                "source": obj.properties.get("source"),
                "page_number": obj.properties.get("page_number"),
                "doc_id": obj.properties.get("doc_id"),
            },
        )
        out.append((doc, obj.metadata.distance))
    return out


def delete_by_doc_id(client: weaviate.WeaviateClient, doc_id: str) -> None:
    collection = client.collections.get(settings.weaviate_collection)
    collection.data.delete_many(where=Filter.by_property("doc_id").equal(doc_id))
