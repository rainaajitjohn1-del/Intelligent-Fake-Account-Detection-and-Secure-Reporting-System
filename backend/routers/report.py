import hashlib
from fastapi import APIRouter, Depends, HTTPException, Security, status, Request
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from models.database import get_db, hash_data, ProfileCheck, Report
import schemas

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

API_KEY = "sih-secret-api-key-2023"
api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid or missing API Key")
    return api_key

@router.post("/api/v1/report", response_model=schemas.ReportResponse)
@limiter.limit("10/minute")
def create_report(request: Request, payload: schemas.ReportCreate, db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)):
    hashed_user = hash_data(payload.raw_username)

    profile_check = ProfileCheck(
        platform=payload.platform,
        hashed_username=hashed_user,
        overall_risk_score=payload.overall_risk_score,
        risk_breakdown=payload.risk_breakdown
    )
    db.add(profile_check)
    db.commit()
    db.refresh(profile_check)

    report = Report(profile_check_id=profile_check.id, reason=payload.reason, status="PENDING")
    db.add(report)
    db.commit()
    db.refresh(report)

    return schemas.ReportResponse(id=report.id, status=report.status, hashed_username=hashed_user, created_at=report.created_at)

@router.get("/api/v1/reports")
@limiter.limit("20/minute")
def list_reports(request: Request, db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)):
    return db.query(Report).all()