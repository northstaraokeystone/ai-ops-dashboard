# In api/routers/interaction.py
from fastapi import APIRouter, status
from api.schemas.interaction import InteractionCreate, InteractionRead
from api.services.interaction import create_interaction

router = APIRouter(
    prefix="/api/interaction",
    tags=["Interaction"],
)


@router.post("/", response_model=InteractionRead, status_code=status.HTTP_201_CREATED)
def handle_create_interaction(interaction: InteractionCreate):
    interaction_dict = interaction.model_dump()
    new_interaction = create_interaction(interaction_data=interaction_dict)
    return new_interaction
