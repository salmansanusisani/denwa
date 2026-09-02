"""In-memory cosine-similarity vector store.

Per-company so retrieval never crosses companies. Swap for Chroma/FAISS if there's
time over the weekend (see requirements.txt) — the public API can stay identical.

Vectors are treated as L2-normalised (see embedder), so cosine similarity is just
the dot product.
"""
from __future__ import annotations

import numpy as np

_store: dict[int, list[tuple[str, list[float]]]] = {}  # company_id -> [(chunk_text, vector)]


def add(company_id: int, chunk_text: str, vector: list[float]) -> None:
    """Store one chunk's vector for a company (appends; keeps insertion order)."""
    _store.setdefault(company_id, []).append((chunk_text, list(vector)))


def top_k(company_id: int, query_vector: list[float], k: int = 5) -> list[str]:
    """Return the top-k most similar chunk texts for a company by cosine similarity."""
    items = _store.get(company_id)
    if not items:
        return []
    q = np.asarray(query_vector, dtype=np.float32)
    scored = [(float(np.dot(q, np.asarray(v, dtype=np.float32))), t) for t, v in items]
    scored.sort(key=lambda s: s[0], reverse=True)
    return [text for _score, text in scored[:k]]


def clear() -> None:
    """Reset all data (mostly useful in tests / demo scripts)."""
    _store.clear()