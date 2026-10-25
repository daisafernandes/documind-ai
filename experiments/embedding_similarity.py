
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim


def main():
    model = SentenceTransformer(
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    sentences = [
        "Como melhorar a velocidade da aplicação?",
        "Reduzimos a latência utilizando Redis e otimizando queries.",
        "O restaurante oferece pratos vegetarianos.",
        "How can we improve application performance?",
    ]

    embeddings = model.encode(
        sentences,
        convert_to_tensor=True,
    )

    print(f"Total de embeddings: {len(embeddings)}")
    print(f"Dimensões por embedding: {embeddings.shape[1]}")

    similarity_matrix = cos_sim(
        embeddings,
        embeddings,
    )

    print("\nMatriz de similaridade:")
    print(similarity_matrix)

    print("\nComparações:")

    print(
        "Pergunta x Performance:",
        similarity_matrix[0][1].item(),
    )

    print(
        "Pergunta x Restaurante:",
        similarity_matrix[0][2].item(),
    )


if __name__ == "__main__":
    main()
