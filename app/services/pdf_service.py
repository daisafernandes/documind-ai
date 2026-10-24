
import pymupdf

from app.models.document import (
    DocumentPage,
    ExtractedDocument,
)


class InvalidPDFError(Exception):
    pass


class PDFService:

    @staticmethod
    def extract_text(
        content: bytes,
        document_id: str,
    ) -> ExtractedDocument:
        pages = []

        with pymupdf.open(
            stream=content,
            filetype="pdf",
        ) as document:
            for page_index, page in enumerate(document):
                text = page.get_text("text", sort=True)

                pages.append(
                    DocumentPage(
                        page_number=page_index + 1,
                        text=text.strip(),
                    )
                )

            return ExtractedDocument(
                document_id=document_id,
                total_pages=document.page_count,
                pages=pages,
            )
    
    @staticmethod
    def validate(content: bytes) -> None:
        try:
            with pymupdf.open(
                stream=content,
                filetype="pdf",
            ) as document:

                if not document.is_pdf:
                    raise InvalidPDFError(
                        "The uploaded file is not a PDF"
                    )

                if document.needs_pass:
                    raise InvalidPDFError(
                        "Password-protected PDFs are not supported"
                    )

                if document.page_count == 0:
                    raise InvalidPDFError(
                        "PDF must contain at least one page"
                    )

        except InvalidPDFError:
            raise

        except Exception as exc:
            raise InvalidPDFError(
                "Invalid or corrupted PDF"
            ) from exc
