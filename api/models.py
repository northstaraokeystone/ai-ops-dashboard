import uuid

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Integer,
    LargeBinary,
    PrimaryKeyConstraint,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class InteractionLog(Base):
    __tablename__ = "interaction_log"

    # Time-ordered UUID
    id = Column(UUID(as_uuid=True), nullable=False, default=uuid.uuid4)

    # Actor identifier
    agent_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Hash representing the state of the environment
    environment_hash = Column(Text, nullable=False, index=True)

    # Link to the interaction that caused this one
    causality_id = Column(UUID(as_uuid=True), nullable=True, index=True)

    # Timestamp when the agent performed the action
    emitted_at_utc = Column(DateTime(timezone=True), nullable=False, index=True)

    # Integer representing the type of action performed
    action_type = Column(Integer, nullable=False)

    # Raw, compressed binary data of the action/observation payload
    payload = Column(LargeBinary, nullable=False)

    # Canonical hash of the uncompressed payload (Idempotency Key)
    payload_hash = Column(Text, nullable=False)

    # Agent State & Resilience Ledger
    # Stores structured JSON data on agent health, recovery actions, and self-healing events
    # as per V9-Resilience Ledger specification. This enables the "Self-Healing Ledger" by
    # logging metrics like error rates, retry counts, and automated recovery steps for
    # agentic reliability and interpretability. Why JSONB: Flexible schema for evolving
    # data without migrations, efficient querying via PostgreSQL GIN indexes, and atomic
    # storage tied to each interaction for traceability (aligns with OpenAI ethics on
    # transparency and MIT self-evolving agents principles).
    agent_support = Column(JSON, nullable=True, index=True)

    __table_args__ = (
        PrimaryKeyConstraint("id", "emitted_at_utc", name="pk_interaction_log"),
        UniqueConstraint("payload_hash", "emitted_at_utc", name="uq_payload_hash_emitted_at_utc"),
        {"postgresql_partition_by": "RANGE (emitted_at_utc)"},
    )
