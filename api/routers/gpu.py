from fastapi import APIRouter, HTTPException
from schemas.gpu import GPUAnalysisRequest, GPUAnalysisResponse
from services.gpu_service import analyze_gpu_efficiency

router = APIRouter(prefix="/api/gpu", tags=["GPU Efficiency"])

@router.post("/analyze", response_model=GPUAnalysisResponse)
async def analyze(request: GPUAnalysisRequest):
    try:
        experiments = [exp.model_dump() for exp in request.experiments]
        result = analyze_gpu_efficiency(experiments)
        return GPUAnalysisResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
