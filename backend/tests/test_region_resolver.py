"""Tests for phone number to CALL-E region resolution and fallback."""
from app.region.resolver import resolve_region


def test_resolve_supported_regions():
    # US number
    assert resolve_region("+16502530000") == "US"
    # Singapore number
    assert resolve_region("+6561234567") == "SG"
    # Great Britain / UK
    assert resolve_region("+442071838750") == "GB"
    # Germany
    assert resolve_region("+4930123456") == "DE"
    # Japan
    assert resolve_region("+81312345678") == "JP"
    # Nigeria
    assert resolve_region("+2348012345678") == "NG"


def test_resolve_unsupported_region_falls_back():
    # Jordan number -> falls back to US
    assert resolve_region("+962791234567") == "US"
    # Egypt number -> falls back to US
    assert resolve_region("+201012345678") == "US"


def test_resolve_invalid_numbers():
    assert resolve_region("") == "US"
    assert resolve_region("invalid-phone") == "US"
    assert resolve_region(None) == "US"