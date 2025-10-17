import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

from api.core.config import settings
from api.main import app

# You'll need to add this import for your database models
# from api.db.base import Base

# Override the DATABASE_URL for a fast, in-memory SQLite test database
TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
settings.DATABASE_URL = TEST_SQLALCHEMY_DATABASE_URL

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
# This line below creates the tables in the test database.
# We will need to create and import 'Base' from your SQLAlchemy models.
# Base.metadata.create_all(bind=engine)

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
    with TestClient(app) as c:
        yield c


# ... (keep the existing fixtures at the top)


@pytest.fixture(scope="module")
def valid_payload() -> dict:
    """Provides a standard, valid payload for interaction tests."""
    return {
        "action_type": 1,
        "agent_id": "e8c80c0e-05a9-4ffe-9731-9389a7c7317a",
        "causality_id": "c4dfaf30-1472-4bc2-aae9-919983955bac",
        "environment_hash": "test_environment_hash_final",
        "session_id": "s-12345-final",
        "details": {"message": "Final test successful."},
    }
