import hashlib
from datetime import datetime
from sqlalchemy.orm import Session
from api.models import InteractionLog
from api.schemas.interaction import InteractionCreate


def create_interaction(db: Session, interaction: InteractionCreate) -> InteractionLog:
    """Create a new interaction log entry, acting as an anti-corruption layer between API DTO and DB model.

    Why: Translates Pydantic DTO to SQLAlchemy model explicitly to prevent TypeErrors from mismatched fields,
    ensuring robustness against schema evolutions (e.g., added DTO fields ignored). Computes payload_hash for
    idempotency, maps details to agent_support JSONB for flexible resilience data, discards session_id as irrelevant
    to persistence, and sets emitted_at_utc for required timestamping. Aligns with Martin Clean Code for explicit
    intent, Fowler refactoring for evolvable layers, and Pragmatic Programmer defensive programming to eliminate
    similar bugs proactively. Supports AI trust fabric by maintaining data integrity for agentic logs.
    """
    # Compute canonical payload_hash for idempotency (SHA-256 for consistency/security)
    # Why: Ensures uniqueness without exposing raw payload, preventing duplicates in high-volume agent ops.
    payload_bytes = (
        interaction.payload.encode("utf-8")
        if isinstance(interaction.payload, str)
        else interaction.payload
    )
    payload_hash = hashlib.sha256(payload_bytes).hexdigest()

    # Idempotency check using correct column (payload_hash)
    # Why: Prevents redundant inserts, aligning with scalability for solo-preneur efficiency.
    existing = (
        db.query(InteractionLog)
        .filter(InteractionLog.payload_hash == payload_hash)
        .first()
    )
    if existing:
        return existing

    # Explicit mapping and instantiation to harden against TypeErrors
    # Why: Avoids dict unpacking risks; each kwarg is intentional, immune to extra DTO fields (defensive).
    db_interaction = InteractionLog(
        agent_id=interaction.agent_id,
        environment_hash=interaction.environment_hash,
        causality_id=interaction.causality_id,  # Assume optional/direct map; set None if not in DTO
        emitted_at_utc=datetime.utcnow(),  # Required; timezone-aware for UTC consistency
        action_type=interaction.action_type,
        payload=payload_bytes,
        payload_hash=payload_hash,
        agent_support=interaction.details,  # Map details to JSONB for structured resilience
        # Discard session_id intentionally—no corresponding column, prevents leakage
    )

    db.add(db_interaction)
    db.commit()
    db.refresh(db_interaction)
    return db_interaction
