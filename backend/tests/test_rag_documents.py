"""Tests for the RAG pipeline wiring: document upload -> chunk -> embed -> retrieve."""
import io
import json

from app.db.models import CallJob, CallResult, Chunk, Document
from app.rag import store
from app.integrations.ai_ml import get_verified_context_and_task


FAQ_TEXT = """\
Frequently Asked Questions:

Q: What are your store hours?
A: We are open Monday to Friday from 9am to 5pm.

Q: How much is shipping?
A: Free standard shipping on all US orders over $50. Otherwise it's a flat fee.
"""


def test_document_upload_embeds_and_persists(client, sample_company, db_session):
    files = {"file": ("faq.txt", io.BytesIO(FAQ_TEXT.encode("utf-8")), "text/plain")}
    resp = client.post(
        "/documents/upload",
        data={"company_id": sample_company.id},
        files=files,
    )
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["chunks_count"] >= 1

    doc = db_session.query(Document).filter(Document.id == payload["id"]).first()
    assert doc is not None

    chunks = db_session.query(Chunk).filter(Chunk.document_id == doc.id).all()
    assert len(chunks) == payload["chunks_count"]
    for chunk in chunks:
        vector = json.loads(chunk.embedding_vector)
        assert isinstance(vector, list) and len(vector) > 0

    # The in-memory store should now be searchable for this company.
    assert store.size(sample_company.id) == len(chunks)


def test_retrieval_surfaces_uploaded_knowledge(client, sample_company, db_session):
    files = {"file": ("faq.txt", io.BytesIO(FAQ_TEXT.encode("utf-8")), "text/plain")}
    assert client.post(
        "/documents/upload", data={"company_id": sample_company.id}, files=files
    ).status_code == 200

    built = get_verified_context_and_task(
        company_id=sample_company.id,
        caller_number="+16502531111",
        likely_topic="your store opening hours",
    )
    assert "9am" in built["task"]
    assert "result_schema" in built


def test_documents_list_includes_chunk_stats(client, sample_company, db_session):
    files = {"file": ("faq.txt", io.BytesIO(FAQ_TEXT.encode("utf-8")), "text/plain")}
    assert client.post(
        "/documents/upload", data={"company_id": sample_company.id}, files=files
    ).status_code == 200

    resp = client.get(f"/documents/?company_id={sample_company.id}")
    assert resp.status_code == 200
    listed = resp.json()
    assert len(listed) == 1
    assert listed[0]["chunks_count"] >= 1
    assert listed[0]["status"] == "Active"