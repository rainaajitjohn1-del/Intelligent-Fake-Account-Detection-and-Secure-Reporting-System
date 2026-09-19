from sqlalchemy.orm import Session
from models.database import ProfileCheck

def check_cluster_similarity(db: Session, current_features: dict, threshold: int = 2):
    recent_checks = db.query(ProfileCheck).order_by(ProfileCheck.checked_at.desc()).limit(20).all()

    matched_ids = []
    matched_details = []

    for check in recent_checks:
        breakdown = check.risk_breakdown or {}
        stored_ml = breakdown.get("ml_score")
        stored_rhythm = breakdown.get("rhythm_score")
        if stored_ml is None or stored_rhythm is None:
            continue

        ml_close = abs(stored_ml - current_features.get("ml_score", 0)) < 0.03
        rhythm_close = abs(stored_rhythm - current_features.get("rhythm_score", 0)) < 0.1

        if ml_close and rhythm_close:
            matched_ids.append(check.id)
            matched_details.append({
                "id": check.id,
                "hashed_username": check.hashed_username,
                "ml_score": stored_ml,
                "rhythm_score": stored_rhythm
            })

    is_clustered = len(matched_ids) >= threshold
    return is_clustered, matched_ids, matched_details