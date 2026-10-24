
from pydantic import BaseModel


class DocumentPage(BaseModel):
    page_number: int
    text: str


class ExtractedDocument(BaseModel):
    document_id: str
    total_pages: int
    pages: list[DocumentPage]
