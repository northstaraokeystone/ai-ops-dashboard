# api/routers/interaction.py

from fastapi import APIRouter, Response

from api.schemas.interaction import InteractionCreate, InteractionResponse
from api.services.interaction import create_interaction

router = APIRouter(prefix="/interactions", tags=["interactions"])


@router.post("/", response_model=InteractionResponse)
def post_interaction(
    interaction: InteractionCreate, response: Response
) -> InteractionResponse:
    """
    Endpoint to create a new interaction log or return existing if duplicate.

    Args:
        interaction: Validated input data.
        response: FastAPI Response object to set status code dynamically.

    Returns:
        InteractionResponse with the ID and status.
    """
    result = create_interaction(interaction)
    if result.status == "DUPLICATE":
        response.status_code = 200
    else:
        response.status_code = 201
    return result
