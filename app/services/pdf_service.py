
import pymupdf


class InvalidPDFError(Exception):
    pass


class PDFService:
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
