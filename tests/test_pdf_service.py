
import pymupdf

from app.services.pdf_service import PDFService


def test_extract_text_from_pdf():
    document = pymupdf.open()
    page = document.new_page()

    page.insert_text(
        (72, 72),
        "Retrieval Augmented Generation",
    )

    content = document.tobytes()
    document.close()

    result = PDFService.extract_text(
        content=content,
        document_id="test-document",
    )

    assert result.document_id == "test-document"
    assert result.total_pages == 1
    assert len(result.pages) == 1
    assert result.pages[0].page_number == 1
    assert "Retrieval Augmented Generation" in (
        result.pages[0].text
    )
