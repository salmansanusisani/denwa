"""Env var loading for the backend service."""
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./denwa.db")
CALLE_API_KEY = os.getenv("CALLE_API_KEY", "")
CALLE_BASE_URL = os.getenv("CALLE_BASE_URL", "")
CALLE_DEFAULT_FALLBACK_REGION = os.getenv("CALLE_DEFAULT_FALLBACK_REGION", "US")
