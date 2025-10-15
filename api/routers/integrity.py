from fastapi import APIRouter, HTTPException
from api.schemas.integrity import IntegrityRequest, IntegrityResponse
from api.services.integrity_service import validate_data_integrity

router = APIRouter(prefix="/api/integrity", tags=["Data Integrity"])

@router.post("/validate", response_model=IntegrityResponse)
async def validate(request: IntegrityRequest):
    try:
        result = validate_data_integrity(request.records, request.target_col)
        return IntegrityResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
