from pydantic import BaseModel, Field

class IntegrityRequest(BaseModel):
    records: list[dict] = Field(..., min_length=1)
    target_col: str | None = None

class IntegrityResponse(BaseModel):
    integrity_score: float
    alert_level: str
    recommendations: list[str]
    missing_score: float
    schema_score: float
    duplicate_score: float
    imbalance_score: float | None
    missing_by_col: dict[str, float]