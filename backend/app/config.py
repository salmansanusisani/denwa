"""Env var loading for the backend service."""
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./denwa.db")
CALLE_API_KEY = os.getenv("CALLE_API_KEY", "")
CALLE_BASE_URL = os.getenv("CALLE_BASE_URL", "")
CALLE_DEFAULT_FALLBACK_REGION = os.getenv("CALLE_DEFAULT_FALLBACK_REGION", "US")

# Telephony provider (Telnyx) - the account's PUBLIC key (Mission Control
# Portal -> Account Settings -> Keys & Credentials -> Public Key), used to
# verify the Ed25519 signature on incoming webhooks.
TELNYX_PUBLIC_KEY = os.getenv("TELNYX_PUBLIC_KEY", "")

# Max age (seconds) a webhook's `telnyx-timestamp` may have before we reject
# it as a possible replay attack. Telnyx recommends enforcing a window.
WEBHOOK_TIMESTAMP_TOLERANCE_SECONDS = int(os.getenv("WEBHOOK_TIMESTAMP_TOLERANCE_SECONDS", "300"))

# When True, skips signature verification. Only for local dev testing with
# fake/self-signed payloads before a real Twilio account exists.
# TODO(backend): this MUST be false (or unset) before any real demo/deploy.
WEBHOOK_SKIP_SIGNATURE_CHECK = os.getenv("WEBHOOK_SKIP_SIGNATURE_CHECK", "false").lower() == "true"
