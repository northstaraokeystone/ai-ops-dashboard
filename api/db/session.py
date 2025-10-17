# In api/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.core.config import settings

# --- LAZY INITIALIZATION PATTERN ---
# Define as None at the module level.
engine = None
SessionLocal = None


def get_db():
    """
    This is a FastAPI dependency that provides a database session.
    It handles the creation of the engine and session factory on the first call.
    """
    global engine, SessionLocal

    # Initialize only once, on the first request that needs a DB.
    if engine is None:
        engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        # This is where you would create tables, for a real test setup
        # from api.db.base_class import Base
        # Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
