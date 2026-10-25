
from app.services.pdf_service import PDFService
from app.services.paragraph_chunking_service import (
    ParagraphChunkingService,
)
from app.services.embedding_service import EmbeddingService
from app.services.vector_store_service import VectorStoreService


class DocumentIndexingService:
    def __init__(
        self,
        pdf_service: PDFService,
        chunking_service: ParagraphChunkingService,
        embedding_service: EmbeddingService,
        vector_store: VectorStoreService,
    ):
        self.pdf_service = pdf_service
        self.chunking_service = chunking_service
        self.embedding_service = embedding_service
        self.vector_store = vector_store

    def index_document(
        self,
        document_id: str,
        content: bytes,
    ) -> int:
        extracted_document = self.pdf_service.extract_text(
            content=content,
            document_id=document_id,
        )

        chunks = self.chunking_service.split(
            extracted_document
        )

        if not chunks:
            return 0

        texts = [chunk.text for chunk in chunks]

        embeddings = self.embedding_service.embed_documents(
            texts
        )

        ids = [
            f"{document_id}:chunk-{chunk.chunk_index}"
            for chunk in chunks
        ]

        metadatas = [
            {
                "document_id": document_id,
                "chunk_index": chunk.chunk_index,
                "page_start": chunk.page_start,
                "page_end": chunk.page_end,
            }
            for chunk in chunks
        ]

        self.vector_store.upsert_chunks(
            ids=ids,
            texts=texts,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        return len(chunks)
