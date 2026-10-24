from fastapi import FastAPI

from app.api.documents import router as documents_router

app = FastAPI(
    title="DocuMind AI",
    description="DocuMind AI powered by RAG.",
    version="0.1.0",
)

app.include_router(documents_router)

@app.get("/health", tags=["Health"])
def health_check():
    return {
            "status": "ok",
            "server": "documind-ai"
        }