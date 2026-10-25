
import re

from app.models.document import (
    DocumentPage,
    ExtractedDocument,
)
from app.services.chunking_service import (
    ChunkingService,
    DocumentChunk,
)


class ParagraphChunkingService:
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 0,
    ):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")

        if not 0 <= chunk_overlap < chunk_size:
            raise ValueError(
                "chunk_overlap must be between 0 and chunk_size"
            )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split(
        self,
        document: ExtractedDocument,
    ) -> list[DocumentChunk]:
        chunks = []
        current_text = ""
        current_start_page = None
        current_end_page = None

        def flush():
            nonlocal current_text
            nonlocal current_start_page
            nonlocal current_end_page

            if not current_text:
                return

            chunks.append(
                DocumentChunk(
                    document_id=document.document_id,
                    chunk_index=len(chunks),
                    page_start=current_start_page,
                    page_end=current_end_page,
                    text=current_text.strip(),
                )
            )

            current_text = ""
            current_start_page = None
            current_end_page = None

        for page in document.pages:
            paragraphs = re.split(
                r"\n\s*\n",
                page.text.strip(),
            )

            for paragraph in paragraphs:
                paragraph = paragraph.strip()

                if not paragraph:
                    continue

                # Handle paragraphs larger than chunk_size
                if len(paragraph) > self.chunk_size:
                    flush()

                    temp_document = ExtractedDocument(
                        document_id=document.document_id,
                        total_pages=1,
                        pages=[
                            DocumentPage(
                                page_number=page.page_number,
                                text=paragraph,
                            )
                        ],
                    )

                    fallback = ChunkingService(
                        chunk_size=self.chunk_size,
                        chunk_overlap=self.chunk_overlap,
                    )

                    for chunk in fallback.split(temp_document):
                        chunks.append(
                            DocumentChunk(
                                document_id=document.document_id,
                                chunk_index=len(chunks),
                                page_start=chunk.page_start,
                                page_end=chunk.page_end,
                                text=chunk.text,
                            )
                        )

                    continue

                separator = "\n\n" if current_text else ""
                candidate = current_text + separator + paragraph

                if len(candidate) > self.chunk_size:
                    flush()

                    current_text = paragraph
                    current_start_page = page.page_number
                    current_end_page = page.page_number

                else:
                    current_text = candidate

                    if current_start_page is None:
                        current_start_page = page.page_number

                    current_end_page = page.page_number

        flush()

        return chunks
