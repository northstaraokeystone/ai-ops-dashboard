import hashlib
from datetime import datetime

from sqlalchemy.orm import Session

from api.models import InteractionLog
from api.schemas.interaction import InteractionCreate


def create_interaction(db: Session, interaction: InteractionCreate) -> tuple[InteractionLog, bool]:
    payload_bytes = interaction.payload.encode("utf-8")
    payload_hash = hashlib.sha256(payload_bytes).hexdigest()

    # Idempotency check
    existing = db.query(InteractionLog).filter(InteractionLog.payload_hash == payload_hash).first()
    if existing:
        return existing, False

    # Create new interaction
    db_interaction = InteractionLog(
        payload_hash=payload_hash,
        emitted_at_utc=datetime.utcnow(),
        agent_id=interaction.agent_id,
        action_type=interaction.action_type,
        agent_support=interaction.details,  # Map incoming details to agent_support
        causality_id=interaction.causality_id,  # Handle optional (defaults to None)
        environment_hash=interaction.environment_hash,
        payload=payload_bytes,  # Pass the encoded bytes to constructor
    )
    db.add(db_interaction)
    db.commit()
    db.refresh(db_interaction)
    return db_interaction, True
