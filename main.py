import os
import shutil
from datetime import datetime, timedelta, timezone

from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    Security,
    status,
    Request,
    UploadFile,
    File,
    BackgroundTasks,
)
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from database import engine, Base, get_db
import models, schemas
from models import hash_data

# Automatically create database tables on startup
Base.metadata.create_all(bind=engine)

# 1. Initialize Rate Limiter (Max 10 requests/minute per client IP)
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="SIH1364 - Secure Reporting API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 2. Security Setup (API Key Authentication)
API_KEY = os.getenv("X_API_KEY", "sih-secret-api-key-2023")
api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API Key"
        )
    return api_key

# 3. Privacy Utility: Cleanup Raw Image Files
def remove_file(path: str):
    """Data Minimization: Deletes temporary raw images immediately after processing."""
    if os.path.exists(path):
        os.remove(path)

# --- ROUTES ---

@app.get("/")
def root():
    return {"status": "Backend running successfully"}

@app.post("/api/v1/report", response_model=schemas.ReportResponse)
@limiter.limit("10/minute")  # Rate Limiting: Prevents route spamming
def create_report(
    request: Request,
    payload: schemas.ReportCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Hashes username via SHA-256 and persists profile check + report to PostgreSQL."""
    hashed_user = hash_data(payload.raw_username)

    # Save profile check entry
    profile_check = models.ProfileCheck(
        platform=payload.platform,
        hashed_username=hashed_user,
        overall_risk_score=payload.overall_risk_score,
        risk_breakdown=payload.risk_breakdown
    )
    db.add(profile_check)
    db.commit()
    db.refresh(profile_check)

    # Save moderation report entry
    report = models.Report(
        profile_check_id=profile_check.id,
        reason=payload.reason,
        status="PENDING"
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return schemas.ReportResponse(
        id=report.id,
        status=report.status,
        hashed_username=hashed_user,
        created_at=report.created_at
    )

@app.get("/api/v1/reports")
@limiter.limit("20/minute")
def list_reports(
    request: Request,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Fetch all reported instances for the admin/moderation dashboard."""
    return db.query(models.Report).all()

@app.post("/api/v1/upload-image-check")
async def process_image_check(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """Receives profile image, writes to temporary storage, and schedules immediate background deletion."""
    temp_path = f"temp_{file.filename}"
    
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Queue auto-deletion background task
    background_tasks.add_task(remove_file, temp_path)
    
    return {
        "status": "Image processed successfully",
        "detail": "Raw uploaded media queued for immediate deletion under privacy policies."
    }

@app.delete("/api/v1/cleanup-old-data")
def apply_data_retention_policy(
    db: Session = Depends(get_db), 
    days: int = 30, 
    api_key: str = Depends(verify_api_key)
):
    """Retention Policy: Deletes profile check entries older than specified days."""
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    deleted_count = db.query(models.ProfileCheck).filter(
        models.ProfileCheck.checked_at < cutoff_date
    ).delete()
    db.commit()
    
    return {
        "message": f"Data retention policy executed successfully.",
        "records_cleared": deleted_count,
        "cutoff_days": days
    }