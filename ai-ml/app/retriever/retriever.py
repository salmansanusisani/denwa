"""Given a likely topic (the customer's exact question isn't known before the call),
return the most relevant chunks for that company.

The real question is unknown pre-call, so retrieve_company_context() also supports a
SET of likely topics (e.g. the top FAQ categories) and returns the union of matches —
cheaper than guessing one wrong topic and pre-seeding nothing useful.
"""
from __future__ import annotations

from app.embeddings.embedder import embed
from app.vector_store import store


def retrieve_for_topic(company_id: int, topic: str, k: int = 5) -> list[str]:
    """Embed a single topic and return the top-k relevant chunks for the company."""
    if not topic.strip():
        return []
    vector = embed(topic)
    return store.top_k(company_id, vector, k=k)


def retrieve_company_context(company_id: int, topics: list[str], k_per_topic: int = 3) -> list[str]:
    """Union of top-k chunks across several likely topics, deduped, order stable."""
    seen: set[str] = set()
    chunks: list[str] = []
    for topic in topics:
        for chunk in retrieve_for_topic(company_id, topic, k=k_per_topic):
            if chunk not in seen:
                seen.add(chunk)
                chunks.append(chunk)
    return chunks