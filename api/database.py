from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.core.config import settings

# Create the SQLAlchemy engine as the single source of truth for database connections.
# Why: Centralizes configuration for maintainability (SRP: one file for DB setup), using
# settings.DATABASE_URL for env-agnostic flexibility (dev/prod switching via env vars).
# pool_pre_ping=True enables connection validation on checkout, detecting stale connections
# in long-running processes like FastAPI, aligning with Pragmatic Programmer resilience
# and Fowler patterns for robust data access layers.
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

# Create a configured sessionmaker for generating database sessions.
# Why: Provides a factory for scoped sessions in FastAPI dependencies (e.g., via Depends),
# with autocommit=False and autoflush=False to ensure explicit transaction control,
# preventing unintended commits/flushes and supporting TDD/Beck XP practices for reliable
# testing and data integrity in AI trust ledgers (e.g., atomic agent log inserts).
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
