from sqlalchemy.orm import Session
from typing import Tuple
from api.services.cryptography_service import CryptographyService
from api.models import InteractionLog as InteractionModel
from api.schemas.interaction import InteractionCreate


def create_interaction(
    db: Session, interaction: InteractionCreate
) -> Tuple[InteractionModel, bool]:
    """
    Creates a new interaction or returns an existing one (idempotency).
    Returns a tuple of (interaction_model, created_boolean).
    """
    interaction_data = interaction.model_dump()
    canonical_hash = CryptographyService.generate_hash(interaction_data)

    db_interaction = (
        db.query(InteractionModel)
        .filter(InteractionModel.canonical_hash == canonical_hash)
        .first()
    )
    if db_interaction:
        return db_interaction, False  # Found existing, so created=False

    new_interaction = InteractionModel(
        **interaction_data, canonical_hash=canonical_hash
    )
    db.add(new_interaction)
    db.commit()
    db.refresh(new_interaction)

    return new_interaction, True  # Created new, so created=True
