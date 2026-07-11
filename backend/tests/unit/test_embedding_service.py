import pytest

from app.core.config import Settings
from app.core.exceptions import EmbeddingError
from app.services.embedding_service import embed_text, embed_texts


@pytest.fixture
def settings() -> Settings:
    return Settings()


def test_embed_text_returns_configured_dimension(settings: Settings) -> None:
    embedding = embed_text("Experienced Python engineer.", settings)

    assert len(embedding) == settings.embedding_dimension
    assert all(isinstance(value, float) for value in embedding)


def test_embed_texts_batch_preserves_order(settings: Settings) -> None:
    embeddings = embed_texts(["Python", "PostgreSQL"], settings)

    assert len(embeddings) == 2
    assert embeddings[0] != embeddings[1]


def test_embed_texts_empty_list_returns_empty(settings: Settings) -> None:
    assert embed_texts([], settings) == []


def test_embed_text_raises_on_dimension_mismatch(settings: Settings) -> None:
    bad_settings = Settings(embedding_dimension=999)

    with pytest.raises(EmbeddingError):
        embed_text("anything", bad_settings)


def _l2_distance(a: list[float], b: list[float]) -> float:
    return sum((x - y) ** 2 for x, y in zip(a, b, strict=True)) ** 0.5


def test_similar_texts_are_closer_than_dissimilar_texts(settings: Settings) -> None:
    python_experience = embed_text("Experienced Python backend engineer.", settings)
    python_job = embed_text("Looking for a Python backend developer.", settings)
    unrelated = embed_text("Watercolor painting techniques for beginners.", settings)

    similar_distance = _l2_distance(python_experience, python_job)
    dissimilar_distance = _l2_distance(python_experience, unrelated)

    assert similar_distance < dissimilar_distance
