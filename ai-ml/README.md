# AI / ML

Owns: document ingestion, embeddings, retrieval, answer + task generation.

## Run / test

```bash
pip install -r requirements.txt
cp .env.example .env        # add GROQ_API_KEY (free: console.groq.com)
python -m demo              # full pipeline: chunk -> embed -> retrieve -> CALL-E task + resultSchema
```

Providers (both free):
- **Embeddings:** fastembed `BAAI/bge-small-en-v1.5` — local ONNX, 384-dim, no key, one-time download
  to `~/.cache/fastembed`. Groq has no free embeddings API.
- **LLM (task condensing):** Groq `openai/gpt-oss-120b` via `GROQ_API_KEY`. Falls back to a template
  if no key / offline.

## Tasks

- [x] Document ingestion pipeline — chunk an uploaded file/text into retrieval-sized pieces.
- [x] Embedding + vector store — embed each chunk, store it (in-memory cosine similarity is fine).
- [x] Retriever — given a likely topic, return the most relevant chunks for that company.
- [x] Answer/task-builder LLM step — retrieved chunks → (a) condensed answer content, (b) a CALL-E task string
      + resultSchema.
- [x] Prompt safety pass — task must instruct the CALL-E agent to only answer from provided content and offer
      a human follow-up when it can't, so it doesn't invent answers.

## Definition of Done

- [x] Sample company's FAQ/policy doc chunks and embeds with no manual cleanup (`python -m demo`).
- [x] Retrieval returns genuinely relevant chunks for 5 realistic test questions per demo company
      (verified: 5/5 top hits, 384-dim embeddings).
- [x] Generated task string is valid, concise, within CALL-E's task field length limit.
- [x] Generated resultSchema is valid JSON Schema and matches backend/frontend expectations.
- [ ] Tested against a real CALL-E call — agent uses the provided content, doesn't hallucinate.

## Layout

```
app/
├── ingestion/       # chunker.py — file/text -> chunks
├── embeddings/       # embedder.py — chunks -> vectors (fastembed, local)
├── vector_store/      # store.py — in-memory cosine similarity (swap for Chroma/FAISS if time allows)
├── retriever/         # retriever.py — topic -> top-k relevant chunks
├── task_builder/       # builder.py — chunks -> (task string, resultSchema)
└── pipeline.py        # orchestration: ingest / ingest_documents / build
```

## Contract with Backend

`pipeline.build(company_id, likely_topic)` (alias of `task_builder.build_task`) returns:

```python
{
    "task": "<string, pre-seeded instruction for CALL-E>",
    "result_schema": { ... valid JSON Schema, matches CallResult fields ... }
}
```
This is what `backend/app/worker/callback_worker.py` calls before hitting CALL-E — keep the return shape
stable, or ping backend before changing it (see docs/ROLES_AND_DOD.md, "Suggesting an upgrade").
