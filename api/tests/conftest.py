import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.main import app
from api.dependencies import get_db
from api.models import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables once for the whole test session
Base.metadata.create_all(bind=engine)


@pytest.fixture()
def client() -> TestClient:
    # This fixture now controls the transaction for a single test function
    connection = engine.connect()
    transaction = connection.begin()
    db = TestingSessionLocal(bind=connection)

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

    # Clean up by rolling back the transaction
    db.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="module")
def valid_payload() -> dict:
    # ... (this part is correct)
    return {
        "action_type": 1,
        "agent_id": "e8c80c0e-05a9-4ffe-9731-9389a7c7317a",
        "causality_id": "c4dfaf30-1472-4bc2-aae9-919983955bac",
        "environment_hash": "test_environment_hash_final",
        "payload": "This is a test payload.",
        "session_id": "s-12345-final",
        "details": {"message": "Final test successful."},
    }
