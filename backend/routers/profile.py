from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from models.database import SessionLocal, ProfileCheck
from services.risk_score import compute_final_risk_score

router = APIRouter()

class ProfileRequest(BaseModel):
    profile_url: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/check-profile")
def check_profile(data: ProfileRequest, db: Session = Depends(get_db)):
    dummy_features = {
        "profile_pic": 1,
        "nums_length_username": 0.1,
        "fullname_words": 2,
        "nums_length_fullname": 0,
        "name_equals_username": 0,
        "description_length": 45,
        "external_url": 0,
        "private": 0,
        "posts": 20,
        "followers": 500,
        "follows": 300
    }

    result = compute_final_risk_score(dummy_features)

    new_check = ProfileCheck(
        profile_url=data.profile_url,
        risk_score=result["risk_score"],
        status=result["risk_level"]
    )
    db.add(new_check)
    db.commit()
    db.refresh(new_check)

    return {
        "id": new_check.id,
        "profile_url": new_check.profile_url,
        "risk_score": new_check.risk_score,
        "status": new_check.status,
        "checked_at": new_check.checked_at
    }