# In api/schemas/interaction.py
import uuid
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime


class InteractionCreate(BaseModel):
    action_type: int
    agent_id: uuid.UUID
    causality_id: uuid.UUID
    environment_hash: str
    session_id: str
    payload: Any
    details: Dict[str, Any]


class InteractionRead(BaseModel):
    id: uuid.UUID
    canonical_hash: str
    timestamp: datetime

    class Config:
        from_attributes = True
