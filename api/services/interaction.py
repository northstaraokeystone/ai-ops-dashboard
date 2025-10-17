from sqlalchemy.orm import Session
from api.services.cryptography_service import CryptographyService
from api.db.models.interaction import (
    Interaction as InteractionModel,
)  # We will create this model next
from api.schemas.interaction import InteractionCreate


def create_interaction(db: Session, interaction: InteractionCreate) -> InteractionModel:
    """
    Creates a new interaction event, generates its hash, and saves it to the database.
    """
    # 1. Convert the Pydantic model to a dictionary for hashing
    interaction_data = interaction.model_dump()

    # 2. Generate the deterministic hash
    canonical_hash = CryptographyService.generate_hash(interaction_data)

    # 3. Check for existing hash for idempotency
    db_interaction = (
        db.query(InteractionModel)
        .filter(InteractionModel.canonical_hash == canonical_hash)
        .first()
    )
    if db_interaction:
        # If it exists, return the existing record
        return db_interaction

    # 4. Create a new SQLAlchemy model instance and save it
    new_interaction = InteractionModel(
        **interaction_data, canonical_hash=canonical_hash
    )
    db.add(new_interaction)
    db.commit()
    db.refresh(new_interaction)

    return new_interaction
