"""Thin orchestration layer for AI/ML — the public surface Backend can call later.

  ingest_document(company_id, document_id, raw_text)  # upload path
  ingest_documents(company_id, documents)             # batch upload path
  build(company_id, likely_topic)                     # === task_builder.build_task

Keeps imports short at call sites and gives us one place to evolve (e.g. move the
store to Chroma/FAISS, add per-document routes) without touching Backend's contract.
"""
from __future__ import annotations

from app.embeddings.embedder import embed_batch
from app.ingestion.chunker import Chunk, chunk_text
from app.task_builder import builder
from app.vector_store import store


def ingest_document(company_id: int, document_id: int, raw_text: str) -> int:
    """Chunk, embed and store a single document. Returns the number of chunks stored."""
    chunks = chunk_text(raw_text, document_id)
    if not chunks:
        return 0
    vectors = embed_batch([c.text for c in chunks])
    for chunk, vector in zip(chunks, vectors):
        store.add(company_id, chunk.text, vector)
    return len(chunks)


def ingest_documents(company_id: int, documents: list[tuple[int, str]]) -> int:
    """Ingest several (document_id, raw_text) pairs for one company in batch."""
    total = 0
    for document_id, raw_text in documents:
        total += ingest_document(company_id, document_id, raw_text)
    return total


def build(company_id: int, likely_topic: str) -> dict:
    """Backend-facing alias of the task-builder contract."""
    return builder.build_task(company_id, likely_topic)


__all__ = ["Chunk", "chunk_text", "ingest_document", "ingest_documents", "build", "builder", "store"]