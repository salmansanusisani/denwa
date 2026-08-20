"""Caller phone number -> CALL-E-supported region code.

Confirmed supported list (docs/ARCHITECTURE.md): US, SG, MY, IN, AE, AU, CA, GB, VN, DE, JP, FR,
MX, BR, ID, PH, KE. NG is NOT on the list — fall back to CALLE_DEFAULT_FALLBACK_REGION.
"""
import phonenumbers
from phonenumbers import region_code_for_number

from app.config import CALLE_DEFAULT_FALLBACK_REGION

SUPPORTED_REGIONS = {
    "US", "SG", "MY", "IN", "AE", "AU", "CA", "GB", "VN", "DE", "JP", "FR", "MX", "BR", "ID", "PH", "KE",
}


def resolve_region(caller_number: str) -> str:
    """TODO(backend):
    1. Parse caller_number with phonenumbers.parse().
    2. Get the region code with region_code_for_number().
    3. If it's in SUPPORTED_REGIONS, return it; otherwise return CALLE_DEFAULT_FALLBACK_REGION.
    Handle parse errors (phonenumbers.NumberParseException) -> fallback region too.
    """
    raise NotImplementedError
