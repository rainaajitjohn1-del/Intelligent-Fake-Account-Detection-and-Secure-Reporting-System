from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

class ReportCreate(BaseModel):
    platform: str
    raw_username: str
    reason: str
    overall_risk_score: float
    risk_breakdown: Optional[Dict[str, float]] = None
    rhythm_score: Optional[float] = None
    cluster_flag: Optional[bool] = False

class ReportResponse(BaseModel):
    id: int
    status: str
    hashed_username: str
    created_at: datetime

    class Config:
        from_attributes = True