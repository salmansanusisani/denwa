# AI / ML

Owns: document ingestion, embeddings, retrieval, answer + task generation.

## Tasks

- [ ] Document ingestion pipeline — chunk an uploaded file/text into retrieval-sized pieces.
- [ ] Embedding + vector store — embed each chunk, store it (in-memory cosine similarity is fine).
- [ ] Retriever — given a likely topic, return the most relevant chunks for that company.
- [ ] Answer/task-builder LLM step — retrieved chunks → (a) condensed answer content, (b) a CALL-E task string
      + resultSchema.
- [ ] Prompt safety pass — task must instruct the CALL-E agent to only answer from provided content and offer
      a human follow-up when it can't, so it doesn't invent answers.

## Definition of Done

- [ ] Sample company's FAQ/policy doc chunks and embeds with no manual cleanup.
- [ ] Retrieval returns genuinely relevant chunks for 5 realistic test questions per demo company.
- [ ] Generated task string is valid, concise, within CALL-E's task field length limit.
- [ ] Generated resultSchema is valid JSON Schema and matches backend/frontend expectations.
- [ ] Tested against a real CALL-E call — agent uses the provided content, doesn't hallucinate.

## Layout

```
app/
├── ingestion/       # chunker.py — file/text -> chunks
├── embeddings/       # embedder.py — chunks -> vectors
├── vector_store/      # store.py — in-memory cosine similarity (swap for Chroma/FAISS if time allows)
├── retriever/         # retriever.py — topic -> top-k relevant chunks
└── task_builder/       # builder.py — chunks -> (task string, resultSchema)
```

## Contract with Backend

`task_builder.build_task(company_id, likely_topic)` should return:

```python
{
    "task": "<string, pre-seeded instruction for CALL-E>",
    "result_schema": { ... valid JSON Schema, matches CallResult fields ... }
}
```
This is what `backend/app/worker/callback_worker.py` calls before hitting CALL-E — keep the return shape
stable, or ping backend before changing it (see docs/ROLES_AND_DOD.md, "Suggesting an upgrade").
