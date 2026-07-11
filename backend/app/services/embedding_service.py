import asyncio

from sentence_transformers import SentenceTransformer

from app.core.config import Settings
from app.core.exceptions import EmbeddingError

_models: dict[tuple[str, str], SentenceTransformer] = {}


def _get_model(model_name: str, device: str) -> SentenceTransformer:
    key = (model_name, device)
    if key not in _models:
        _models[key] = SentenceTransformer(model_name, device=device)
    return _models[key]


def embed_texts(texts: list[str], settings: Settings) -> list[list[float]]:
    """Embed a batch of texts using the configured sentence-transformers model.

    Returns one L2-normalized embedding vector per input text, in the same order.
    Raises EmbeddingError if the model's output dimension does not match the
    configured `embedding_dimension` (e.g. after a misconfigured model change).
    """
    if not texts:
        return []

    model = _get_model(settings.embedding_model, settings.embedding_device)
    vectors = model.encode(texts, normalize_embeddings=True, convert_to_numpy=True)
    embeddings = [vector.tolist() for vector in vectors]

    for embedding in embeddings:
        if len(embedding) != settings.embedding_dimension:
            raise EmbeddingError(
                f"Embedding model '{settings.embedding_model}' produced a "
                f"{len(embedding)}-dimensional vector; expected "
                f"{settings.embedding_dimension} (EMBEDDING_DIMENSION)."
            )

    return embeddings


def embed_text(text: str, settings: Settings) -> list[float]:
    return embed_texts([text], settings)[0]


async def embed_texts_async(texts: list[str], settings: Settings) -> list[list[float]]:
    """Async wrapper running the CPU-bound encode call off the event loop thread."""
    return await asyncio.to_thread(embed_texts, texts, settings)


async def embed_text_async(text: str, settings: Settings) -> list[float]:
    return (await embed_texts_async([text], settings))[0]
