# api/schemas/interaction.py

from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel


class InteractionCreate(BaseModel):
    """
    Pydantic model for creating a new interaction log entry.

    This model validates the input data from the API request.
    """

    agent_id: UUID
    environment_hash: str
    causality_id: Optional[UUID] = None
    action_type: int
    payload: Dict[str, Any]


class InteractionResponse(BaseModel):
    """
    Pydantic model for the response after processing an interaction log.

    This model defines the structure of the API response.
    """

    id: UUID
    status: str
