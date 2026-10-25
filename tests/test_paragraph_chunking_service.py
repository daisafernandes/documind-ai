
from app.models.document import (
    DocumentPage,
    ExtractedDocument,
)
from app.services.paragraph_chunking_service import (
    ParagraphChunkingService,
)


def create_document(
    text: str,
    document_id: str = "doc-123",
) -> ExtractedDocument:
    return ExtractedDocument(
        document_id=document_id,
        total_pages=1,
        pages=[
            DocumentPage(
                page_number=1,
                text=text,
            )
        ],
    )


def test_paragraph_chunking_preserves_content():
    document = create_document(
        "First paragraph about RAG.\n\n"
        + ("X" * 150)
        + "\n\n"
        + "Last paragraph about embeddings."
    )

    service = ParagraphChunkingService(
        chunk_size=100
    )

    chunks = service.split(document)

    combined_text = "\n\n".join(
        chunk.text for chunk in chunks
    )

    assert combined_text.count(
        "First paragraph about RAG."
    ) == 1

    assert combined_text.count(
        "Last paragraph about embeddings."
    ) == 1

    long_paragraph_chunks = [
        chunk
        for chunk in chunks
        if chunk.text and set(chunk.text) == {"X"}
    ]

    assert len(long_paragraph_chunks) == 2

    assert [
        len(chunk.text)
        for chunk in long_paragraph_chunks
    ] == [100, 50]

    assert all(
        len(chunk.text) <= 100
        for chunk in chunks
    )


def test_small_paragraphs_are_grouped():
    document = create_document(
        "First paragraph.\n\n"
        "Second paragraph."
    )

    service = ParagraphChunkingService(
        chunk_size=100
    )

    chunks = service.split(document)

    assert len(chunks) == 1
    assert "First paragraph." in chunks[0].text
    assert "Second paragraph." in chunks[0].text


def test_empty_document():
    document = create_document("")

    service = ParagraphChunkingService()

    chunks = service.split(document)

    assert chunks == []


def test_chunk_indexes_are_sequential():
    document = create_document(
        "A" * 250
    )

    service = ParagraphChunkingService(
        chunk_size=100
    )

    chunks = service.split(document)

    assert [
        chunk.chunk_index
        for chunk in chunks
    ] == [0, 1, 2]


def test_chunks_preserve_page_metadata():
    document = ExtractedDocument(
        document_id="doc-456",
        total_pages=2,
        pages=[
            DocumentPage(
                page_number=1,
                text="First page paragraph.",
            ),
            DocumentPage(
                page_number=2,
                text="Second page paragraph.",
            ),
        ],
    )

    service = ParagraphChunkingService(
        chunk_size=100
    )

    chunks = service.split(document)

    assert len(chunks) == 1
    assert chunks[0].page_start == 1
    assert chunks[0].page_end == 2


def test_invalid_chunk_size():
    try:
        ParagraphChunkingService(chunk_size=0)
        assert False, "Expected ValueError"
    except ValueError:
        pass
