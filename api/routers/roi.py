from fastapi import APIRouter, HTTPException
from api.schemas.roi import ROISimulationRequest, ROISimulationResponse
from api.services.roi_service import simulate_roi

router = APIRouter(prefix="/api/roi", tags=["ROI Simulation"])

@router.post("/simulate", response_model=ROISimulationResponse)
async def simulate(request: ROISimulationRequest):
    try:
        # Pass the request body as a dictionary
        result = simulate_roi(request.model_dump())
        return ROISimulationResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
