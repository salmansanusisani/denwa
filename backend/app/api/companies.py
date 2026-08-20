"""Company CRUD — create company (onboarding form lands here)."""
from fastapi import APIRouter

router = APIRouter(prefix="/companies", tags=["companies"])


@router.post("/")
def create_company():
    """TODO(backend): accept {name, phone_number}, persist, return the new Company."""
    raise NotImplementedError


@router.get("/{company_id}")
def get_company(company_id: int):
    """TODO(backend): fetch a company by id."""
    raise NotImplementedError
