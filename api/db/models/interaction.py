import uuid
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from api.db.base_class import Base


class Interaction(Base):
    __tablename__ = "events"

    # Core Fields
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    canonical_hash = Column(String, unique=True, nullable=False, index=True)

    # Foreign Keys & Metadata
    # We will uncomment these as we build the other tables
    # event_type_id = Column(Integer, ForeignKey("event_types.id"), nullable=False)
    # principal_id = Column(UUID(as_uuid=True), ForeignKey("principals.id"), nullable=False)

    # Fields from the Pydantic Schema
    action_type = Column(Integer, nullable=False)
    agent_id = Column(UUID(as_uuid=True), nullable=False)
    causality_id = Column(UUID(as_uuid=True), nullable=False)
    environment_hash = Column(String, nullable=False)
    session_id = Column(String, nullable=False)
    details = Column(JSON, nullable=False)

    # Fields for The Veil & Auditing
    status = Column(
        Enum("active", "amended", "retracted", name="event_status"),
        default="active",
        nullable=False,
    )
    amends_event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=True)
