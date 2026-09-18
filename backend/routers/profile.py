from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from models.database import get_db, hash_data, ProfileCheck
from services.risk_score import compute_final_risk_score
from services.rhythm_analysis import compute_rhythm_score
from services.cluster_detection import check_cluster_similarity

router = APIRouter()

class ProfileRequest(BaseModel):
    profile_url: str
    post_timestamps: list[float] = []  # optional: hours between posts, for demo purposes

def parse_platform_and_username(profile_url: str):
    platform = "unknown"
    for name in ["twitter.com", "x.com", "instagram.com", "facebook.com", "linkedin.com"]:
        if name in profile_url:
            platform = name.split(".")[0]
            break
    username = profile_url.rstrip("/").split("/")[-1]
    return platform, username

@router.post("/check-profile")
def check_profile(data: ProfileRequest, db: Session = Depends(get_db)):
    platform, username = parse_platform_and_username(data.profile_url)

    dummy_features = {
        "profile_pic": 1, "nums_length_username": 0.1, "fullname_words": 2,
        "nums_length_fullname": 0, "name_equals_username": 0, "description_length": 45,
        "external_url": 0, "private": 0, "posts": 20, "followers": 500, "follows": 300
    }

    rhythm_score = compute_rhythm_score(data.post_timestamps)
    result = compute_final_risk_score(dummy_features, rhythm_score)

    is_clustered = check_cluster_similarity(db, {"ml_score": result["ml_score"]})

    hashed_user = hash_data(username)

    new_check = ProfileCheck(
        platform=platform,
        hashed_username=hashed_user,
        overall_risk_score=result["risk_score"],
        risk_breakdown={"ml_score": result["ml_score"], "rhythm_score": result["rhythm_score"]},
        rhythm_score=result["rhythm_score"],
        cluster_flag=is_clustered
    )
    db.add(new_check)
    db.commit()
    db.refresh(new_check)

    return {
        "id": new_check.id,
        "platform": new_check.platform,
        "risk_score": new_check.overall_risk_score,
        "rhythm_score": new_check.rhythm_score,
        "cluster_flag": new_check.cluster_flag,
        "status": result["risk_level"],
        "checked_at": new_check.checked_at
    }