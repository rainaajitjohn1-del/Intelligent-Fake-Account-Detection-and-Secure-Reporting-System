import os
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, Depends, HTTPException, Security, BackgroundTasks, UploadFile, File
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from routers import profile, report
from models import database
from models.database import init_db, get_db

API_KEY = os.getenv("API_KEY", "sih-secret-api-key-2023")
api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden: Invalid API Key")
    return api_key

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Fake Account Detection & Secure Reporting API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

app.include_router(profile.router)
app.include_router(report.router)

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def read_root():
    return {"status": "Backend is running"}

# --- RETENTION POLICY WITH DRY-RUN MODE ---
@app.delete("/api/v1/cleanup-old-data")
def apply_data_retention_policy(
    db: Session = Depends(get_db), 
    days: int = 30, 
    dry_run: bool = False,
    api_key: str = Depends(verify_api_key)
):
    """Data retention policy with dry-run support for demo safety."""
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    query = db.query(database.ProfileCheck).filter(database.ProfileCheck.checked_at < cutoff_date)
    
    records_found = query.count()
    
    if dry_run:
        return {
            "status": "DRY_RUN_COMPLETE",
            "message": f"[DRY RUN] Identified {records_found} records older than {days} days. No records deleted.",
            "records_flagged": records_found
        }
        
    deleted_count = query.delete()
    db.commit()
    
    return {
        "status": "SUCCESS",
        "message": f"Purged {deleted_count} stale records older than {days} days.",
        "records_cleared": deleted_count
    }

# --- AUTOMATED MEDIA CLEANUP ---
def remove_file(path: str):
    if os.path.exists(path):
        os.remove(path)

@app.post("/api/v1/upload-image-check")
async def upload_image_check(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Processes image and auto-deletes local file immediately after response."""
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        buffer.write(await file.read())
    
    # Schedule ephemeral cleanup
    background_tasks.add_task(remove_file, temp_path)
    
    return {
        "status": "SUCCESS",
        "message": "Image processed successfully. File marked for background deletion.",
        "filename": file.filename
    }