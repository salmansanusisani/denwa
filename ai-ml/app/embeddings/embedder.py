"""Embeds chunk text into vectors.

TODO(ai/ml): pick an embedding provider (OpenAI/Anthropic embeddings API, or a local
sentence-transformers model if you want to avoid a second API key). Keep the vector dimension
consistent across the whole run — the in-memory store assumes fixed-size vectors.
"""


def embed(text: str) -> list[float]:
    """TODO(ai/ml): call the embedding model, return the vector."""
    raise NotImplementedError


def embed_batch(texts: list[str]) -> list[list[float]]:
    """TODO(ai/ml): batch version — cheaper than calling embed() in a loop if the provider supports it."""
    raise NotImplementedError
