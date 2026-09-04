"""Document upload — proxies to the AI/ML ingestion pipeline and persists documents."""
import json
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
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

    # Attempt to chunk document for AI/ML retrieval
    chunks_created = 0
    try:
        # Simple sliding/paragraph chunking fallback if ai-ml module is not loaded
        raw_paragraphs = [p.strip() for p in raw_text.split("\n\n") if p.strip()]
        if not raw_paragraphs and raw_text.strip():
            raw_paragraphs = [raw_text.strip()]

        for p in raw_paragraphs:
            chunk = Chunk(
                document_id=doc.id,
                text=p,
                embedding_vector=json.dumps([]),
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
    return [
        {
            "id": d.id,
            "company_id": d.company_id,
            "filename": d.filename,
            "uploaded_at": d.uploaded_at.isoformat() if d.uploaded_at else None,
        }
        for d in docs
    ]

