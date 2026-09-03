"""Caller phone number -> CALL-E-supported region code.

Confirmed supported list: US, SG, MY, IN, AE, AU, CA, GB, VN, DE, JP, FR, MX, BR, ID, PH, KE,NG.
"""

import phonenumbers
from phonenumbers import NumberParseException, region_code_for_number

from app.config import CALLE_DEFAULT_FALLBACK_REGION

SUPPORTED_REGIONS = {
    "US", "SG", "MY", "IN", "AE", "AU", "CA", "GB", "VN", "DE", "JP", "FR",
    "MX", "BR", "ID", "PH", "KE", "NG",
}


def resolve_region(caller_number: str) -> str:
    """Resolve a caller phone number in E.164 format to a CALL-E supported region code.

    Falls back to CALLE_DEFAULT_FALLBACK_REGION (e.g. 'US') if invalid or unsupported.
    """
    if not caller_number:
        return CALLE_DEFAULT_FALLBACK_REGION

    try:
        parsed = phonenumbers.parse(caller_number, None)
        if not phonenumbers.is_valid_number(parsed):
            return CALLE_DEFAULT_FALLBACK_REGION
        region = region_code_for_number(parsed)
        if region in SUPPORTED_REGIONS:
            return region
    except NumberParseException:
        pass
    except Exception:
        pass

    return CALLE_DEFAULT_FALLBACK_REGION
