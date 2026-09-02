"""Caller phone number -> CALL-E-supported region code.

Confirmed supported list (as of latest CALL-E dashboard check): US, SG, MY, IN, AE, AU, CA, GB,
VN, DE, JP, FR, MX, BR, ID, PH, KE, NL, PL, BD, NG, OM, TH.
"""
import phonenumbers
from phonenumbers import NumberParseException, region_code_for_number

from app.config import CALLE_DEFAULT_FALLBACK_REGION

SUPPORTED_REGIONS = {
    "US", "SG", "MY", "IN", "AE", "AU", "CA", "GB", "VN", "DE", "JP", "FR",
    "MX", "BR", "ID", "PH", "KE", "NL", "PL", "BD", "NG", "OM", "TH",
}


def resolve_region(caller_number: str) -> str:
    try:
        parsed = phonenumbers.parse(caller_number, None)
    except NumberParseException:
        return CALLE_DEFAULT_FALLBACK_REGION

    region = region_code_for_number(parsed)
    if region in SUPPORTED_REGIONS:
        return region
    return CALLE_DEFAULT_FALLBACK_REGION