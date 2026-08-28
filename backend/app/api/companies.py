"""Company CRUD - create company (onboarding form lands here)."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Company
from app.utils.phone import normalize_phone_number

router = APIRouter(prefix="/companies", tags=["companies"])


class CompanyCreate(BaseModel):
    name: str
    phone_number: str


class CompanyOut(BaseModel):
    id: int
    name: str
    phone_number: str

    class Config:
        from_attributes = True


@router.post("/", response_model=CompanyOut, status_code=201)
def create_company(payload: CompanyCreate, db: Session = Depends(get_db)):
    normalized = normalize_phone_number(payload.phone_number)
    if normalized is None:
        raise HTTPException(
            status_code=422,
            detail="Invalid phone_number format. Please include the country code (e.g. +962791234567).",
        )

    existing = db.query(Company).filter(Company.phone_number == normalized).first()
    if existing is not None:
        raise HTTPException(status_code=409, detail="A company with this phone_number already exists.")

    company = Company(name=payload.name, phone_number=normalized)
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@router.get("/{company_id}", response_model=CompanyOut)
def get_company(company_id: int, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found.")
    return company


def get_company_by_business_number(db: Session, business_number: str) -> Company | None:
    """Core routing lookup used by the telephony webhook: given the number the
    customer called, find which Company it belongs to. Returns None if unknown
    (caller must decide how to handle the webhook should reject unknown numbers).
    """
    normalized = normalize_phone_number(business_number)
    if normalized is None:
        return None
    return db.query(Company).filter(Company.phone_number == normalized).first()