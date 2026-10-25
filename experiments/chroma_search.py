
import chromadb
from sentence_transformers import SentenceTransformer


MODEL_NAME = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)


def main():
    model = SentenceTransformer(MODEL_NAME)

    client = chromadb.PersistentClient(
        path="./storage/chroma"
    )

    collection = client.get_or_create_collection(
        name="documind_experiment",
        metadata={"hnsw:space": "cosine"},
    )

    documents = [
        "Reduzimos a latência utilizando Redis e otimizando queries.",
        "O restaurante oferece pratos vegetarianos.",
        "A autenticação multifator ajuda a proteger dados sensíveis.",
    ]

    embeddings = model.encode(documents).tolist()

    collection.upsert(
        ids=["chunk-1", "chunk-2", "chunk-3"],
        documents=documents,
        embeddings=embeddings,
        metadatas=[
            {"page": 1},
            {"page": 2},
            {"page": 3},
        ],
    )

    print(f"Total de registros no ChromaDB: {collection.count()}")

    question = "Como melhorar a velocidade da aplicação?"

    question_embedding = model.encode(
        question
    ).tolist()

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=2,
        include=["documents", "metadatas", "distances"],
    )

    print(f"Pergunta: {question}")
    print("\nResultados:")

    for document, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        print(f"\nTexto: {document}")
        print(f"Página: {metadata['page']}")
        print(f"Distância: {distance:.4f}")


if __name__ == "__main__":
    main()
