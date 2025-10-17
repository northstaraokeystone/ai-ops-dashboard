import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.core.config_test import settings as test_settings

# You'll need to define your Base import here, assuming it's correctly exposed
# from api.db.base import Base

# CRITICAL FIX: Determine host based on environment
# In GitHub Actions (CI), the database service is named 'test_db'.
# Locally, it's 'localhost'.
if os.getenv("CI"):
    # Use the Docker service name for CI
    DB_HOST = "test_db"
else:
    # Use localhost for local development
    DB_HOST = "localhost"

# Construct the Test Database URL using the determined host
TEST_DATABASE_URL = test_settings.test_database_url.replace("localhost", DB_HOST)


@pytest.fixture(scope="session")
def db_engine():
    """Fixture to create the database engine."""
    engine = create_engine(TEST_DATABASE_URL)
    # NOTE: You'll likely need to create tables here using Base.metadata.create_all(engine)
    # This requires Base to be correctly imported.
    # Base.metadata.create_all(engine)
    yield engine
    # Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Fixture to provide a database session for each test."""
    connection = db_engine.connect()
    # Begin a transaction to rollback changes after the test runs
    transaction = connection.begin()
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=connection
    )
    session = TestingSessionLocal()

    yield session

    # Rollback the transaction to clean the database state
    session.close()
    transaction.rollback()
    connection.close()


# Note: Additional fixtures (like API client) are typically added here.
