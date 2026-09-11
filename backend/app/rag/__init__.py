"""Vendored RAG pipeline for the Denwa backend.

Chunk -> embed -> store -> retrieve -> build CALL-E task. A self-contained copy
of `ai-ml/` kept inside the backend package (as ``app.rag``) so the worker and
document-upload route can use it without tripping over the `ai-ml/app` package
name collision that makes cross-module dynamic imports unstable.

The vector store is process-local and in-memory, but it is rehydrated from the
database at startup (see ``app.rag.ingest.rehydrate_index``), so knowledge
uploaded in a previous run stays retrievable.
"""