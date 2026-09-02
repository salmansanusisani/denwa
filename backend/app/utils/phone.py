"""Phone number normalization utilities."""
import phonenumbers
from phonenumbers import NumberParseException


def normalize_phone_number(raw_number: str, default_region: str | None = None) -> str | None:
    """Normalize a phone number to E.164 format (e.g. +962791234567).

    Returns None if the number can't be parsed/is invalid, so callers must
    handle that explicitly rather than silently storing a bad number.
    """
    try:
        parsed = phonenumbers.parse(raw_number, default_region)
    except NumberParseException:
        return None

    if not phonenumbers.is_valid_number(parsed):
        return None

    return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)