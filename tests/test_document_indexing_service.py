
from unittest.mock import Mock

from app.models.document import (
    DocumentPage,
    ExtractedDocument,
)
from app.services.chunking_service import DocumentChunk
from app.services.document_indexing_service import (
    DocumentIndexingService,
)


def test_index_document():
    pdf_service = Mock()
    chunking_service = Mock()
    embedding_service = Mock()
    vector_store = Mock()

    extracted_document = ExtractedDocument(
        document_id="doc-123",
        total_pages=1,
        pages=[
            DocumentPage(
                page_number=1,
                text="Texto sobre arquitetura.",
            )
        ],
    )

    chunks = [
        DocumentChunk(
            document_id="doc-123",
            chunk_index=0,
            page_start=1,
            page_end=1,
            text="Texto sobre arquitetura.",
        )
    ]

    pdf_service.extract_text.return_value = extracted_document
    chunking_service.split.return_value = chunks
    embedding_service.embed_documents.return_value = [
        [0.1, 0.2, 0.3]
    ]

    service = DocumentIndexingService(
        pdf_service=pdf_service,
        chunking_service=chunking_service,
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    result = service.index_document(
        document_id="doc-123",
        content=b"fake-pdf-content",
    )

    assert result == 1

    pdf_service.extract_text.assert_called_once_with(
        content=b"fake-pdf-content",
        document_id="doc-123",
    )

    chunking_service.split.assert_called_once_with(
        extracted_document
    )

    embedding_service.embed_documents.assert_called_once_with(
        ["Texto sobre arquitetura."]
    )

    vector_store.upsert_chunks.assert_called_once_with(
        ids=["doc-123:chunk-0"],
        texts=["Texto sobre arquitetura."],
        embeddings=[[0.1, 0.2, 0.3]],
        metadatas=[
            {
                "document_id": "doc-123",
                "chunk_index": 0,
                "page_start": 1,
                "page_end": 1,
            }
        ],
    )


def test_index_document_without_chunks():
    pdf_service = Mock()
    chunking_service = Mock()
    embedding_service = Mock()
    vector_store = Mock()

    chunking_service.split.return_value = []

    service = DocumentIndexingService(
        pdf_service=pdf_service,
        chunking_service=chunking_service,
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    result = service.index_document(
        document_id="doc-empty",
        content=b"fake-pdf-content",
    )

    assert result == 0
    embedding_service.embed_documents.assert_not_called()
    vector_store.upsert_chunks.assert_not_called()
