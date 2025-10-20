from datetime import datetime
from typing import Any, Optional, Dict
from uuid import UUID

from pydantic import BaseModel, ConfigDict


# This schema defines the data we ACCEPT from the API client.
class InteractionCreate(BaseModel):
    action_type: int
    agent_id: UUID
    environment_hash: str
    payload: Any
    details: Optional[Dict[str, Any]] = None
    causality_id: Optional[UUID] = None
    session_id: Optional[str] = None  # Optional, as it's discarded by the service


# This schema defines the data we RETURN to the API client.
# It should perfectly mirror the fields available on the InteractionLog DB model.
class InteractionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    # Fields that directly map to the InteractionLog model
    id: UUID
    payload_hash: str
    emitted_at_utc: datetime
    agent_id: UUID
    action_type: int
    causality_id: Optional[UUID]
    environment_hash: str
    agent_support: Optional[Dict[str, Any]]

    # NOTE: 'session_id' and 'details' are not here because they don't exist
    # on the final DB object under those names. 'details' is returned as 'agent_support'.
