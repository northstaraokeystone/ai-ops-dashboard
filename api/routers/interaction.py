from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from api.dependencies import get_db
from api.models import InteractionLog
from api.schemas.interaction import InteractionCreate, InteractionRead

# Import the service function with a different name to avoid recursion
from api.services.interaction import create_interaction as create_interaction_service

router = APIRouter(prefix="/api/interaction", tags=["Interaction"])


@router.post("/", response_model=InteractionRead)
def handle_create_interaction(interaction: InteractionCreate, response: Response, db: Session = Depends(get_db)):
    """
    Handles the API request to create a new interaction.
    It calls the service layer to perform the business logic.
    """
    # Call the renamed service function
    new_interaction, created = create_interaction_service(db=db, interaction=interaction)

    # Set the status code dynamically
    if created:
        response.status_code = status.HTTP_201_CREATED
    else:
        response.status_code = status.HTTP_200_OK

    return new_interaction


@router.get("/", response_model=list[InteractionRead])
def handle_list_interactions(db: Session = Depends(get_db)):
    """
    Handles the API request to fetch all interaction log entries.
    """
    # The missing logic: query the database and return all records.
    return db.query(InteractionLog).all()
