
from pydantic import BaseModel

from app.models.document import ExtractedDocument


class DocumentChunk(BaseModel):
    document_id: str
    chunk_index: int
    page_start: int
    page_end: int
    text: str


class ChunkingService:
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 100,
    ):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")

        if not 0 <= chunk_overlap < chunk_size:
            raise ValueError("Invalid chunk overlap")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split(
        self,
        document: ExtractedDocument,
    ) -> list[DocumentChunk]:

        text_parts = []
        page_ranges = []
        position = 0

        for page in document.pages:
            page_text = page.text.strip()

            if not page_text:
                continue

            if text_parts:
                text_parts.append("\n")
                position += 1

            start = position
            text_parts.append(page_text)
            position += len(page_text)

            page_ranges.append(
                (start, position, page.page_number)
            )

        full_text = "".join(text_parts)

        if not full_text:
            return []

        chunks = []
        start = 0
        chunk_index = 0

        while start < len(full_text):
            end = min(
                start + self.chunk_size,
                len(full_text),
            )

            chunk_text = full_text[start:end]

            overlapping_pages = [
                page_number
                for page_start, page_end, page_number
                in page_ranges
                if page_start < end and page_end > start
            ]

            if overlapping_pages:
                chunks.append(
                    DocumentChunk(
                        document_id=document.document_id,
                        chunk_index=chunk_index,
                        page_start=min(overlapping_pages),
                        page_end=max(overlapping_pages),
                        text=chunk_text,
                    )
                )

                chunk_index += 1

            if end == len(full_text):
                break

            start = end - self.chunk_overlap

        return chunks
