"""Given a likely topic (the customer's exact question isn't known before the call), return the
most relevant chunks for that company.

TODO(ai/ml):
1. embed the topic string with app.embeddings.embedder.embed.
2. app.vector_store.store.top_k(company_id, topic_vector, k).
3. Since the real question is unknown pre-call, consider retrieving for a small SET of likely
   topics (e.g. top FAQ categories) rather than one, and letting the task-builder condense across
   all of them — cheaper than guessing wrong and having nothing relevant pre-seeded.
"""


def retrieve_for_topic(company_id: int, topic: str, k: int = 5) -> list[str]:
    """TODO(ai/ml): implement retrieval."""
    raise NotImplementedError
