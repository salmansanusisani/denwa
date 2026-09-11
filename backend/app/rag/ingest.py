"""Bridges uploaded documents and the database into the in-memory vector store.

- ``ingest_for_company`` chunks + embeds raw text, adds it to the store and
  returns ``(text, vector)`` pairs so the API layer can persist the embedding
  in the ``chunks`` table (making the index durable across restarts).
- ``rehydrate_index`` rebuilds the in-memory store from persisted chunk rows at
  startup, so knowledge from a previous run is still retrievable.
"""
from __future__ import annotations

import json
import logging

from sqlalchemy.orm import Session

from app.db.models import Chunk, Document
from app.rag.chunker import chunk_text
from app.rag.embedder import embed, embed_batch
from app.rag import store

logger = logging.getLogger("denwa.rag")


def embed_chunks(raw_text: str) -> list[tuple[str, list[float]]]:
    """Chunk + embed raw text; returns [(text, l2-normalised vector), ...]."""
    texts = chunk_text(raw_text)
    if not texts:
        return []
    vectors = embed_batch(texts)
    return [(text, vector) for text, vector in zip(texts, vectors)]


def ingest_for_company(company_id: int, raw_text: str) -> list[tuple[str, list[float]]]:
    """Chunk, embed and index raw text for a company. Returns (text, vector) pairs."""
    pairs = embed_chunks(raw_text)
    for text, vector in pairs:
        store.add(company_id, text, vector)
    return pairs


def rehydrate_index(db: Session) -> int:
    """Rebuild the in-memory store from persisted chunk rows. Returns count."""
    rows = (
        db.query(Document.company_id, Chunk.text, Chunk.embedding_vector)
        .join(Chunk, Chunk.document_id == Document.id)
        .all()
    )
    store.clear()
    count = 0
    for company_id, text, vector_json in rows:
        vector: list[float] | None = None
        if vector_json:
            try:
                parsed = json.loads(vector_json)
                if isinstance(parsed, list) and parsed:
                    vector = parsed
            except ValueError:
                vector = None
        if not vector:
            vector = embed(text)
        store.add(company_id, text, vector)
        count += 1
    if count:
        logger.info("Rehydrated RAG index with %s chunks from the database.", count)
    return count