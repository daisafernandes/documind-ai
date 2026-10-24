
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.pdf_service import PDFService, InvalidPDFError


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)

UPLOAD_DIR = Path("storage/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post("", status_code=202)
async def upload_document(file: UploadFile = File(...)):
    # 1. Validate content type
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=415,
            detail="Only PDF files are supported",
        )

    # 2. Generate unique document ID
    document_id = str(uuid4())
    destination = UPLOAD_DIR / f"{document_id}.pdf"

    size = 0

    try:
        # 3. Save file in chunks
        with destination.open("wb") as output:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)

                if size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail="File exceeds the 10 MB limit",
                    )

                output.write(chunk)

        # 4. Validate PDF integrity
        try:
            PDFService.validate(destination.read_bytes())
        except InvalidPDFError as exc:
            raise HTTPException(
                status_code=422,
                detail=str(exc),
            ) from exc

        # 5. Return accepted document
        return {
            "document_id": document_id,
            "filename": file.filename,
            "status": "pending",
        }

    except Exception:
        # Remove partially uploaded or invalid files
        destination.unlink(missing_ok=True)
        raise

    finally:
        await file.close()
