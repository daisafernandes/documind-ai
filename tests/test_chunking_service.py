
from app.models.document import (
    DocumentPage,
    ExtractedDocument,
)
from app.services.chunking_service import ChunkingService


def test_split_document_into_chunks():
    document = ExtractedDocument(
        document_id="doc-123",
        total_pages=1,
        pages=[
            DocumentPage(
                page_number=1,
                text="A" * 1200,
            )
        ],
    )

    service = ChunkingService(
        chunk_size=500,
        chunk_overlap=100,
    )

    chunks = service.split(document)

    assert len(chunks) == 3
    assert chunks[0].chunk_index == 0
    assert chunks[1].chunk_index == 1
    assert chunks[2].chunk_index == 2
    assert all(c.page_start == 1 for c in chunks)
    assert all(c.page_end == 1 for c in chunks)
    assert all(len(c.text) <= 500 for c in chunks)


def test_empty_page_produces_no_chunks():
    document = ExtractedDocument(
        document_id="doc-456",
        total_pages=1,
        pages=[
            DocumentPage(page_number=1, text="")
        ],
    )

    service = ChunkingService()

    assert service.split(document) == []


def test_invalid_overlap():
    try:
        ChunkingService(
            chunk_size=500,
            chunk_overlap=500,
        )
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_chunk_can_span_multiple_pages():
    document = ExtractedDocument(
        document_id="doc-123",
        total_pages=2,
        pages=[
            DocumentPage(
                page_number=1,
                text="A" * 300,
            ),
            DocumentPage(
                page_number=2,
                text="B" * 300,
            ),
        ],
    )

    service = ChunkingService(
        chunk_size=500,
        chunk_overlap=100,
    )

    chunks = service.split(document)

    assert len(chunks) == 2

    assert chunks[0].page_start == 1
    assert chunks[0].page_end == 2

    assert chunks[1].page_start == 2
    assert chunks[1].page_end == 2

    assert "A" in chunks[0].text
    assert "B" in chunks[0].text

