
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


def main():
    pdf_path = Path("storage/uploads/test-document.pdf")

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF not found: {pdf_path}"
        )

    document_id = "test-document"

    pdf_content = pdf_path.read_bytes()

    pdf_service = PDFService()
    chunking_service = ParagraphChunkingService(
        chunk_size=500
    )
    embedding_service = EmbeddingService()
    vector_store = VectorStoreService(
        persist_directory="./storage/chroma",
        collection_name="documind_documents",
    )

    indexing_service = DocumentIndexingService(
        pdf_service=pdf_service,
        chunking_service=chunking_service,
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    total_chunks = indexing_service.index_document(
        document_id=document_id,
        content=pdf_content,
    )

    print(f"Document ID: {document_id}")
    print(f"Chunks indexed: {total_chunks}")
    print(f"Total records in ChromaDB: {vector_store.count()}")

    question = "Why does the Transformer use self-attention instead of recurrence?"

    query_embedding = embedding_service.embed_query(
        question
    )

    results = vector_store.search(
        query_embedding=query_embedding,
        top_k=3,
    )

    print(f"\nQuestion: {question}")
    print("\nRetrieved chunks:")

    for text, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        print("\n--------------------------")
        print(f"Pages: {metadata['page_start']}-{metadata['page_end']}")
        print(f"Distance: {distance:.4f}")
        print(f"Text: {text}")


if __name__ == "__main__":
    main()
