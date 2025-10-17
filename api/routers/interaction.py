from fastapi import APIRouter, HTTPException

# ... other imports

from api.services.interaction import create_interaction

router = APIRouter()


@router.post("/interaction/")
def handle_create_interaction(
    interaction_data: dict,
):  # Use a Pydantic model here later
    try:
        result = create_interaction(interaction_data)
        return result
    except Exception:
        # In a real app, log the error `e`
        raise HTTPException(status_code=500, detail="An internal error occurred.")
