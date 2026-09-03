"""Shared pytest fixtures for Denwa backend test suite."""
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Setup test environment variables
os.environ["TWILIO_AUTH_TOKEN"] = "test_twilio_secret_token"
os.environ["WEBHOOK_SKIP_SIGNATURE_CHECK"] = "false"
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
