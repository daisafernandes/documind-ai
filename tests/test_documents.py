
from io import BytesIO
import pymupdf

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def create_test_pdf() -> BytesIO:
    document = pymupdf.open()
    page = document.new_page()

    page.insert_text(
        (72, 72),
        "DocuMind AI - Test Document",
    )

    content = document.tobytes()
    document.close()

    return BytesIO(content)

def test_upload_valid_pdf():
    response = client.post(
        "/documents",
        files={
            "file": (
                "test.pdf",
                create_test_pdf(),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 202

    data = response.json()

    assert "document_id" in data
    assert data["filename"] == "test.pdf"
    assert data["status"] == "pending"


def test_upload_invalid_file_type():
    response = client.post(
        "/documents",
        files={
            "file": (
                "test.txt",
                BytesIO(b"Hello world"),
                "text/plain",
            )
        },
    )

    assert response.status_code == 415


def test_upload_exceeds_size_limit():
    large_file = BytesIO(b"x" * (10 * 1024 * 1024 + 1))

    response = client.post(
        "/documents",
        files={
            "file": (
                "large.pdf",
                large_file,
                "application/pdf",
            )
        },
    )

    assert response.status_code == 413

def test_upload_corrupted_pdf():
    response = client.post(
        "/documents",
        files={
            "file": (
                "corrupted.pdf",
                BytesIO(b"Not a real PDF"),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 422
