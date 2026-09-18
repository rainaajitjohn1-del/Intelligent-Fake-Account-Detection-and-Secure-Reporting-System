from sqlalchemy.orm import Session
from models.database import ProfileCheck

def check_cluster_similarity(db: Session, current_features: dict, threshold: int = 3) -> bool:
    """
    Compares current profile's features against recently checked profiles.
    If 'threshold' or more recent profiles have near-identical feature values,
    flag this as part of a coordinated cluster.
    """
    recent_checks = db.query(ProfileCheck).order_by(ProfileCheck.checked_at.desc()).limit(20).all()

    similar_count = 0
    for check in recent_checks:
        breakdown = check.risk_breakdown or {}
        stored_score = breakdown.get("ml_score")
        if stored_score is None:
            continue
        # simple similarity: near-identical risk scores suggest same template/bot script
        if abs(stored_score - current_features.get("ml_score", 0)) < 0.03:
            similar_count += 1

    return similar_count >= threshold