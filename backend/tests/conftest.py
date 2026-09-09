"""Shared pytest fixtures for Denwa backend test suite."""
import base64
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from nacl.encoding import Base64Encoder
from nacl.signing import SigningKey

# Generate one real Ed25519 keypair for the whole test session. Tests sign
# payloads with TEST_SIGNING_KEY; the app verifies them against the
# corresponding public key, injected below as TELNYX_PUBLIC_KEY.
TEST_SIGNING_KEY = SigningKey.generate()
_TEST_PUBLIC_KEY_B64 = TEST_SIGNING_KEY.verify_key.encode(encoder=Base64Encoder).decode("utf-8")

# Setup test environment variables
os.environ["TELNYX_PUBLIC_KEY"] = _TEST_PUBLIC_KEY_B64
os.environ["WEBHOOK_SKIP_SIGNATURE_CHECK"] = "false"
os.environ["WEBHOOK_TIMESTAMP_TOLERANCE_SECONDS"] = "300"
os.environ["CALLE_API_KEY"] = "test_calle_api_key"
os.environ["CALLE_BASE_URL"] = "https://mock-calle.test"
os.environ["CALLE_DEFAULT_FALLBACK_REGION"] = "US"

from app.db.models import Base, Company
from app.db.database import get_db
from app.main import app

from sqlalchemy.pool import StaticPool

TEST_DB_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def db_session(monkeypatch):
    """Create a fresh SQLite in-memory database for each test with StaticPool."""
    engine = create_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Monkeypatch app.db.database.SessionLocal and engine so job_queue and workers use test db
    monkeypatch.setattr("app.db.database.engine", engine)
    monkeypatch.setattr("app.db.database.SessionLocal", TestingSessionLocal)
    monkeypatch.setattr("app.queue.job_queue.SessionLocal", TestingSessionLocal)
    monkeypatch.setattr("app.worker.callback_worker.SessionLocal", TestingSessionLocal)
    
    session = TestingSessionLocal()
    yield session
    
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """FastAPI TestClient with overridden get_db dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()



@pytest.fixture
def sample_company(db_session):
    """Create and return a sample test company."""
    company = Company(name="Acme Corp", phone_number="+16502530000")
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    return company