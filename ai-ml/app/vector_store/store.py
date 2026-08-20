"""In-memory cosine-similarity vector store. Swap for Chroma/FAISS if time allows (see requirements.txt).

TODO(ai/ml):
- store(company_id, chunk, vector) -> keep per-company, so retrieval never crosses companies.
- top_k(company_id, query_vector, k) -> list of chunks ranked by cosine similarity.
- numpy cosine similarity is enough: dot(a, b) / (norm(a) * norm(b)).
"""
import numpy as np

_store: dict[int, list[tuple[str, list[float]]]] = {}  # company_id -> [(chunk_text, vector)]


def add(company_id: int, chunk_text: str, vector: list[float]) -> None:
    """TODO(ai/ml): append to _store[company_id]."""
    raise NotImplementedError


def top_k(company_id: int, query_vector: list[float], k: int = 5) -> list[str]:
    """TODO(ai/ml): cosine similarity over _store[company_id], return top-k chunk texts."""
    raise NotImplementedError
