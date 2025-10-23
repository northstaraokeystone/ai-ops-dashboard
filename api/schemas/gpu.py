from pydantic import BaseModel


class GPUExperiment(BaseModel):
    model_type: str
    batch_size: int
    epochs: int
    gpu_time_ms: float


class GPUAnalysisRequest(BaseModel):
    experiments: list[GPUExperiment]


class GPUAnalysisResponse(BaseModel):
    potential_savings_pct: float | None
    recommendations: list[str]
    total_experiments: int
    avg_gpu_time: float
    batch_size_impact: dict[int, float]
    epochs_impact: dict[int, float]
    model_type_impact: dict[str, float]
