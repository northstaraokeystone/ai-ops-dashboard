import gzip
import hashlib
import json
from datetime import datetime, timezone
from typing import Dict, Any

from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker  # <--- 1. IMPORT THE CORRECT TOOL

from api.core.config import settings
from api.schemas.interaction import InteractionCreate, InteractionResponse

# Global engine and session maker
engine = create_engine(settings.DATABASE_URL)
# 2. USE THE TOOL CORRECTLY WITH THE ENGINE
Session = sessionmaker(bind=engine)


def create_interaction(interaction: InteractionCreate) -> InteractionResponse:
    """
    Creates a new interaction log entry or returns the existing one if a duplicate is detected.

    This function implements idempotency by checking for existing records with the same
    payload_hash before inserting. To prevent race conditions, it uses a PostgreSQL
    advisory lock based on the payload_hash.

    Args:
        interaction: The validated input data for the interaction.

    Returns:
        InteractionResponse: Contains the ID of the logged interaction and the status
        ("LOGGED" for new, "DUPLICATE" for existing).

    Note:
        The advisory lock ensures serialized access for operations with the same payload_hash,
        preventing duplicate inserts under concurrency without relying solely on the unique constraint.
    """
    # Create canonical JSON serialization for hashing and storage
    canonical_json = json.dumps(
        interaction.payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    payload_bytes = canonical_json.encode("utf-8")

    # Compress the payload for storage
    compressed_payload = gzip.compress(payload_bytes)

    # Compute SHA-256 hash of the uncompressed canonical payload
    payload_hash = hashlib.sha256(payload_bytes).hexdigest()

    # Compute a 64-bit lock ID from the payload_hash (for advisory lock)
    lock_id_bytes = hashlib.sha256(payload_hash.encode("utf-8")).digest()[:8]
    lock_id = int.from_bytes(lock_id_bytes, byteorder="big", signed=True)

    # Current UTC timestamp
    emitted_at_utc = datetime.now(timezone.utc)

    # Prepare insert parameters
    params: Dict[str, Any] = {
        "agent_id": interaction.agent_id,
        "environment_hash": interaction.environment_hash,
        "causality_id": interaction.causality_id,
        "emitted_at_utc": emitted_at_utc,
        "action_type": interaction.action_type,
        "payload": compressed_payload,
        "payload_hash": payload_hash,
    }

    with Session() as session:
        try:
            with session.begin():
                # Acquire advisory lock to serialize operations on this hash
                session.execute(
                    text("SELECT pg_advisory_xact_lock(:lock_id)"), {"lock_id": lock_id}
                )

                # Check for existing record with the same payload_hash
                existing_result = session.execute(
                    text(
                        """
                        SELECT id FROM interaction_log WHERE payload_hash = :payload_hash LIMIT 1
                        """
                    ),
                    {"payload_hash": payload_hash},
                )
                existing_id = existing_result.scalar()

                if existing_id is not None:
                    return InteractionResponse(id=existing_id, status="DUPLICATE")

                # Insert new record if no duplicate found
                insert_result = session.execute(
                    text(
                        """
                        INSERT INTO interaction_log (
                            agent_id, environment_hash, causality_id, emitted_at_utc,
                            action_type, payload, payload_hash
                        )
                        VALUES (
                            :agent_id, :environment_hash, :causality_id, :emitted_at_utc,
                            :action_type, :payload, :payload_hash
                        )
                        RETURNING id
                        """
                    ),
                    params,
                )
                new_id = insert_result.scalar()

                return InteractionResponse(id=new_id, status="LOGGED")

        except IntegrityError:
            # Fallback in case of unexpected integrity error (e.g., race outside lock)
            with session.begin():
                fallback_result = session.execute(
                    text(
                        """
                        SELECT id FROM interaction_log WHERE payload_hash = :payload_hash LIMIT 1
                        """
                    ),
                    {"payload_hash": payload_hash},
                )
                fallback_id = fallback_result.scalar()
                if fallback_id is not None:
                    return InteractionResponse(id=fallback_id, status="DUPLICATE")
                else:
                    raise  # Rethrow if no record found (unexpected)
