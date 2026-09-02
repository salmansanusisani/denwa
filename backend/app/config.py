"""Env var loading for the backend service."""
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./denwa.db")
CALLE_API_KEY = os.getenv("CALLE_API_KEY", "")
CALLE_BASE_URL = os.getenv("CALLE_BASE_URL", "")
CALLE_DEFAULT_FALLBACK_REGION = os.getenv("CALLE_DEFAULT_FALLBACK_REGION", "US")

# Telephony provider (Twilio) - used to verify the authenticity of incoming
# missed-call webhooks. Must be kept secret; never log or expose this value.
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")

# When True, skips signature verification. Only for local dev testing with
# fake/self-signed payloads before a real Twilio account exists.
# TODO(backend): this MUST be false (or unset) before any real demo/deploy.
WEBHOOK_SKIP_SIGNATURE_CHECK = os.getenv("WEBHOOK_SKIP_SIGNATURE_CHECK", "false").lower() == "true"
