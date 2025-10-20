from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class InteractionCreate(BaseModel):
    """Schema for creating a new interaction log entry via API input.

    Why: Validates incoming DTO fields for service layer mapping, ensuring type safety
    and preventing invalid data (e.g., non-UUID agent_id). Preserved unchanged per requirements,
    aligning with SRP for input validation and Fowler DTO patterns for API-DB separation.
    """

    agent_id: UUID
    action_type: int
    payload: str | bytes  # Flexible for raw/compressed data
    environment_hash: str
    session_id: str  # Discarded in service; API-only for context
    details: dict  # Mapped to agent_support JSONB in DB


class InteractionRead(BaseModel):
    """Schema for reading/serializing interaction log entries from DB.

    Why: Aligns exactly with InteractionLog model attributes to prevent validation errors,
    using Pydantic V2 ConfigDict for modern ORM mode (from_attributes=True) enabling
    direct instantiation from SQLAlchemy objects. Renamed fields (payload_hash, emitted_at_utc)
    fix mismatches; added agent_id/action_type for completeness, supporting comprehensive
    API responses without partial data bias in AI/ML analytics (e.g., full context for
    interpretability via SHAP on action_type). Enhances trust fabric by ensuring schema-DB fidelity.
    """

    payload_hash: str
    emitted_at_utc: datetime
    agent_id: UUID
    action_type: int

    model_config = ConfigDict(from_attributes=True)
