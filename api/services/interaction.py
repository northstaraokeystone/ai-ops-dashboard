from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.core.config import settings

# --- LAZY INITIALIZATION PATTERN ---
# We define the engine and SessionLocal as None at the module level.
engine = None
SessionLocal = None


def get_db_session():
    """
    Creates and returns a new database session.
    The engine is initialized here, only on the first call.
    """
    global engine, SessionLocal

    # Initialize the engine only if it hasn't been already.
    if engine is None:
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        # In a full setup, you would create tables here if they don't exist:
        # Base.metadata.create_all(bind=engine)

    # Return a new session from the session factory.
    return SessionLocal()


# --- Your existing create_interaction function ---
# It now needs to get a session to work with.
def create_interaction(interaction_data: dict):
    """
    This is your business logic function.
    It should now get a database session and use it.
    """
    db_session = get_db_session()
    try:
        # Example: Create a new object and add it to the database
        # new_interaction = YourDBModel(**interaction_data)
        # db_session.add(new_interaction)
        # db_session.commit()
        # db_session.refresh(new_interaction)
        # return new_interaction

        # For now, just return a success message
        return {"status": "success", "info": "Database session created."}
    finally:
        db_session.close()
