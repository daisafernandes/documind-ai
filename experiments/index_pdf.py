
from pathlib import Path

from app.services.pdf_service import PDFService
from app.services.paragraph_chunking_service import (
    ParagraphChunkingService,
)
from app.services.embedding_service import EmbeddingService
from app.services.vector_store_service import VectorStoreService
from app.services.document_indexing_service import (
    DocumentIndexingService,
)


QUESTION = (
    "Why does the Transformer use self-attention "
    "instead of recurrence?"
)


def run_experiment(
    pdf_content: bytes,
    embedding_service: EmbeddingService,
    overlap: int,
    collection_name: str,
):
    vector_store = VectorStoreService(
        persist_directory="./storage/chroma",
        collection_name=collection_name,
    )

    indexing_service = DocumentIndexingService(
        pdf_service=PDFService(),
        chunking_service=ParagraphChunkingService(
            chunk_size=500,
            chunk_overlap=overlap,
        ),
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    total_chunks = indexing_service.index_document(
        document_id="attention-paper",
        content=pdf_content,
    )

    query_embedding = embedding_service.embed_query(QUESTION)

    results = vector_store.search(
        query_embedding=query_embedding,
        top_k=3,
    )

    print(f"\nCollection: {collection_name}")
    print(f"Overlap: {overlap}")
    print(f"Chunks indexed: {total_chunks}")
    print(f"Records stored: {vector_store.count()}")

    for position, (text, metadata, distance) in enumerate(
        zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ),
        start=1,
    ):
        print(f"\nResult {position}")
        print(f"Pages: {metadata['page_start']}-{metadata['page_end']}")
        print(f"Distance: {distance:.4f}")
        print(f"Text: {text[:500]}")


def main():
    pdf_path = Path("storage/uploads/test-document.pdf")
    pdf_content = pdf_path.read_bytes()

    embedding_service = EmbeddingService()

    run_experiment(
        pdf_content=pdf_content,
        embedding_service=embedding_service,
        overlap=0,
        collection_name="documind_baseline",
    )

    run_experiment(
        pdf_content=pdf_content,
        embedding_service=embedding_service,
        overlap=100,
        collection_name="documind_overlap",
    )


if __name__ == "__main__":
    main()
