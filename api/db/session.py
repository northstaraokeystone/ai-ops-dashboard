# In api/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.core.config import settings

# Create the engine once, using the URL from our central settings
engine = create_engine(settings.DATABASE_URL)

# Create the Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# This is the dependency that our routers will use
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
