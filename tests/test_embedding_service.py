
from unittest.mock import MagicMock, patch

import numpy as np

from app.services.embedding_service import EmbeddingService


@patch("app.services.embedding_service.SentenceTransformer")
def test_embed_documents(mock_transformer):
    mock_model = MagicMock()
    mock_model.encode.return_value = np.array([
        [0.1, 0.2, 0.3],
        [0.4, 0.5, 0.6],
    ])
    mock_transformer.return_value = mock_model

    service = EmbeddingService()

    result = service.embed_documents([
        "Primeiro chunk",
        "Segundo chunk",
    ])

    assert len(result) == 2
    assert len(result[0]) == 3

    mock_model.encode.assert_called_once_with(
        ["Primeiro chunk", "Segundo chunk"],
        convert_to_numpy=True,
        show_progress_bar=False,
    )


@patch("app.services.embedding_service.SentenceTransformer")
def test_embed_query(mock_transformer):
    mock_model = MagicMock()
    mock_model.encode.return_value = np.array(
        [0.1, 0.2, 0.3]
    )
    mock_transformer.return_value = mock_model

    service = EmbeddingService()

    result = service.embed_query(
        "Como melhorar a performance?"
    )

    assert len(result) == 3
    assert isinstance(result, list)


@patch("app.services.embedding_service.SentenceTransformer")
def test_embed_documents_empty_list(mock_transformer):
    service = EmbeddingService()

    result = service.embed_documents([])

    assert result == []
    mock_transformer.return_value.encode.assert_not_called()
