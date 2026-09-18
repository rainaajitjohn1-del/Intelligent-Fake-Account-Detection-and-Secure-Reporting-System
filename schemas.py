from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

class ReportCreate(BaseModel):
    platform: str
    raw_username: str  # Frontend/ML passes raw name; backend hashes it automatically
    reason: str
    overall_risk_score: float
    risk_breakdown: Optional[Dict[str, float]] = None

class ReportResponse(BaseModel):
    id: int
    status: str
    hashed_username: str
    created_at: datetime

    class Config:
        from_attributes = True