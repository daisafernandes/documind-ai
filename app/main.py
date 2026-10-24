from fastapi import FastAPI

app = FastAPI(
    title="DocuMind AI",
    description="DocuMind AI powered by RAG.",
    version="0.1.0",
)

@app.get("/health", tags=["Health"])
def health_check():
    return {
            "status": "ok",
            "server": "documind-ai"
        }