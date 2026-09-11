"""Document upload — chunks and embeds via the RAG pipeline, persists documents."""
import json
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Chunk, Company, Document

logger = logging.getLogger("denwa.documents")

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload")
async def upload_document(
    company_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload a knowledge base document for a company, save raw text and generate chunks."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail=f"Company with id {company_id} not found")

    try:
        content_bytes = await file.read()
        raw_text = content_bytes.decode("utf-8", errors="replace")
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not read uploaded file as text: {exc}",
        )

    doc = Document(
        company_id=company.id,
        filename=file.filename or "unknown_file.txt",
        raw_text=raw_text,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # Chunk + embed the document and store real vectors so the index is durable.
    chunks_created = 0
    try:
        from app.rag.ingest import ingest_for_company

        for text, vector in ingest_for_company(company.id, raw_text):
            chunk = Chunk(
                document_id=doc.id,
                text=text,
                embedding_vector=json.dumps(vector),
            )
            db.add(chunk)
            chunks_created += 1
        db.commit()
    except Exception as exc:
        logger.warning("Could not auto-chunk document id=%s: %s", doc.id, exc)

    logger.info(
        "Uploaded document id=%s for company_id=%s (%s bytes, %s chunks)",
        doc.id,
        company.id,
        len(raw_text),
        chunks_created,
    )

    return {
        "id": doc.id,
        "company_id": doc.company_id,
        "filename": doc.filename,
        "uploaded_at": doc.uploaded_at.isoformat() if doc.uploaded_at else None,
        "chunks_count": chunks_created,
    }


@router.get("/")
def list_documents(
    company_id: int = Query(..., description="The ID of the company"),
    db: Session = Depends(get_db),
):
    """List all knowledge base documents for a company."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail=f"Company with id {company_id} not found")

    docs = db.query(Document).filter(Document.company_id == company_id).all()
    counts = {
        row[0]: row[1]
        for row in db.query(Chunk.document_id, func.count(Chunk.id))
        .filter(Chunk.document_id.in_([d.id for d in docs]))
        .group_by(Chunk.document_id)
        .all()
    } if docs else {}

    return [
        {
            "id": d.id,
            "company_id": d.company_id,
            "filename": d.filename,
            "uploaded_at": d.uploaded_at.isoformat() if d.uploaded_at else None,
            "chunks_count": counts.get(d.id, 0),
            "status": "Active" if counts.get(d.id, 0) else "Processing",
        }
        for d in docs
    ]

