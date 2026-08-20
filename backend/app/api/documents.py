"""Document upload — proxies to the AI/ML ingestion pipeline."""
from fastapi import APIRouter, UploadFile

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload")
async def upload_document(company_id: int, file: UploadFile):
    """TODO(backend):
    1. Save raw_text against the Document table.
    2. Call ai_ml.ingestion.chunker + embeddings to produce Chunks (in-process import, or
       an internal call if AI/ML ends up as its own service).
    3. Return success/failure so the frontend can show a state.
    """
    raise NotImplementedError
