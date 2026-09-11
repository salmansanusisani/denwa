"""Env var loading for the backend service."""
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./denwa.db")
CALLE_API_KEY = os.getenv("CALLE_API_KEY", "")
CALLE_BASE_URL = os.getenv("CALLE_BASE_URL", "")
CALLE_DEFAULT_FALLBACK_REGION = os.getenv("CALLE_DEFAULT_FALLBACK_REGION", "US")

# The business's real phone number (E.164). Reference only — company records
# themselves are created through the UI/API onboarding so that inbound webhooks
# can map missed calls to a registered company.
BUSINESS_PHONE_NUMBER = os.getenv("BUSINESS_PHONE_NUMBER", "")

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

# When True (default), the background callback worker loop starts with the app.
# Set to false in test environments so jobs are not processed mid-assertion.
WORKER_ENABLED = os.getenv("WORKER_ENABLED", "true").lower() == "true"
