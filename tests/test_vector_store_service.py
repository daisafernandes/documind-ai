
import pytest

from app.services.vector_store_service import VectorStoreService


@pytest.fixture
def vector_store(tmp_path):
    return VectorStoreService(
        persist_directory=str(tmp_path / "chroma"),
        collection_name="test_documents",
    )


def test_upsert_chunks(vector_store):
    vector_store.upsert_chunks(
        ids=["chunk-1", "chunk-2"],
        texts=[
            "Text about application performance",
            "Text about database security",
        ],
        embeddings=[
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
        ],
        metadatas=[
            {"document_id": "doc-1", "page": 1},
            {"document_id": "doc-1", "page": 2},
        ],
    )

    assert vector_store.count() == 2


def test_upsert_is_idempotent(vector_store):
    data = {
        "ids": ["chunk-1"],
        "texts": ["Text about performance"],
        "embeddings": [[1.0, 0.0, 0.0]],
        "metadatas": [
            {"document_id": "doc-1", "page": 1}
        ],
    }

    vector_store.upsert_chunks(**data)
    vector_store.upsert_chunks(**data)

    assert vector_store.count() == 1


def test_search_returns_closest_chunk(vector_store):
    vector_store.upsert_chunks(
        ids=["chunk-1", "chunk-2"],
        texts=[
            "Text about performance",
            "Text about security",
        ],
        embeddings=[
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
        ],
        metadatas=[
            {"document_id": "doc-1", "page": 1},
            {"document_id": "doc-1", "page": 2},
        ],
    )

    results = vector_store.search(
        query_embedding=[0.9, 0.1, 0.0],
        top_k=1,
    )

    assert results["ids"][0][0] == "chunk-1"
    assert results["documents"][0][0] == (
        "Text about performance"
    )
    assert results["metadatas"][0][0]["page"] == 1


def test_data_persists_between_instances(tmp_path):
    directory = str(tmp_path / "persistent_chroma")

    first_store = VectorStoreService(
        persist_directory=directory,
        collection_name="test_documents",
    )

    first_store.upsert_chunks(
        ids=["chunk-1"],
        texts=["Persistent document"],
        embeddings=[[1.0, 0.0, 0.0]],
        metadatas=[{"document_id": "doc-1", "page": 1}],
    )

    second_store = VectorStoreService(
        persist_directory=directory,
        collection_name="test_documents",
    )

    assert second_store.count() == 1
