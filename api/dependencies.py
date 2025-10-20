from typing import Generator
from sqlalchemy.orm import Session
from api.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Provide a database session for dependency injection in FastAPI routes.

    Why: Acts as a single source of truth for session management, ensuring per-request
    scoping to prevent state leakage across requests (SRP: one dep for DB access).
    Uses try-finally for robust cleanup, aligning with Pragmatic Programmer principles
    for resource acquisition and Beck XP for reliable, testable dependencies. This supports
    scalable, concurrent ops in AI trust fabric apps by avoiding shared sessions and
    enabling explicit commits, reducing errors in agentic data workflows (e.g., logging
    health metrics atomically).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
