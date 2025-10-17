from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.orm import Session
from api.db.session import get_db
from api.schemas.interaction import InteractionCreate, InteractionRead
from api.services.interaction import create_interaction

router = APIRouter(prefix="/api/interaction", tags=["Interaction"])


# Remove the hardcoded status_code from the decorator
@router.post(
    "/", response_model=InteractionRead, summary="Create a new Interaction Event"
)
def handle_create_interaction(
    interaction: InteractionCreate, response: Response, db: Session = Depends(get_db)
):

    new_interaction, created = create_interaction(db=db, interaction=interaction)

    # Set the status code dynamically based on whether the resource was created
    if created:
        response.status_code = status.HTTP_201_CREATED
    else:
        response.status_code = status.HTTP_200_OK

    return new_interaction
