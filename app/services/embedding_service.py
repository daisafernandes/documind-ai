
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    MODEL_NAME = (
        "sentence-transformers/"
        "paraphrase-multilingual-MiniLM-L12-v2"
    )

    def __init__(self):
        self.model = SentenceTransformer(self.MODEL_NAME)

    def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        if not texts:
            return []

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=False,
        )

        return embeddings.tolist()

    def embed_query(
        self,
        query: str,
    ) -> list[float]:
        embedding = self.model.encode(
            query,
            convert_to_numpy=True,
            show_progress_bar=False,
        )

        return embedding.tolist()
