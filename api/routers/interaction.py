from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from api.db.session import get_db
from api.schemas.interaction import InteractionCreate, InteractionRead
from api.services.interaction import create_interaction

router = APIRouter(prefix="/api/interaction", tags=["Interaction"])


@router.post("/", response_model=InteractionRead, status_code=status.HTTP_201_CREATED)
def handle_create_interaction(
    interaction: InteractionCreate, db: Session = Depends(get_db)
):
    # The 'create_interaction' service now expects the db session
    return create_interaction(db=db, interaction=interaction)
