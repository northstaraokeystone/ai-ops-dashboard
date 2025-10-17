import uuid
from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from api.db.base_class import Base


class Interaction(Base):
    __tablename__ = "events"  # Corresponds to our 'events' table

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # This assumes we will add tenant_id later
    # tenant_id = Column(UUID(as_uuid=True), index=True)
    # event_type_id = Column(Integer, ForeignKey("event_types.id"), nullable=False)
    # principal_id = Column(UUID(as_uuid=True), ForeignKey("principals.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    data = Column(JSON, nullable=False)
    canonical_hash = Column(String, unique=True, nullable=False, index=True)
    # ... other columns from your schema.sql
