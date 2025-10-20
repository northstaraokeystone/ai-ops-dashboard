import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

from api.core.config import settings
from api.main import app
from api.models import Base  # Import the Base

# Override the DATABASE_URL for a fast, in-memory SQLite test database
TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
settings.DATABASE_URL = TEST_SQLALCHEMY_DATABASE_URL

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})

# --- THE FIX IS HERE ---
# Create all tables defined in our models in the test database.
Base.metadata.create_all(bind=engine)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a new database session for a test, and rollback after."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="module")
def client():
    """Create a TestClient for making API requests."""
    # This line below ensures that our Base.metadata.create_all() is run
    # before any tests use the client.
    yield TestClient(app)
    # Clean up the test database file after all tests in the module are done.
    import os

    if os.path.exists("./test.db"):
        os.remove("./test.db")


@pytest.fixture(scope="module")
def valid_payload() -> dict:
    """Provides a standard, valid payload for interaction tests."""
    return {
        "action_type": 1,
        "agent_id": "e8c80c0e-05a9-4ffe-9731-9389a7c7317a",
        "causality_id": "c4dfaf30-1472-4bc2-aae9-919983955bac",
        "environment_hash": "test_environment_hash_final",
        "payload": "This is a test payload.",  # <--- THE FIX
        "session_id": "s-12345-final",
        "details": {"message": "Final test successful."},
    }
