from pydantic import BaseModel, Field

class ROIPeriodMetrics(BaseModel):
    period: int
    cum_roi: float
    net_roi: float

class ROISimulationRequest(BaseModel):
    periods: int = 12
    retraining_cost_usd: int = 6000

class ROISimulationResponse(BaseModel):
    timeline: list[ROIPeriodMetrics]
    total_roi: float
    breach_period: int | None
    summary: dict