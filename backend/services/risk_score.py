from services.ml_inference import predict_risk

def compute_final_risk_score(profile_features: dict, rhythm_score: float = 0.0) -> dict:
    ml_score = predict_risk(profile_features)

    # combine ML score and rhythm score (weighted)
    final_score = round(min((ml_score * 0.7) + (rhythm_score * 0.3), 1.0), 2)

    risk_level = "low"
    if final_score > 0.7:
        risk_level = "high"
    elif final_score > 0.4:
        risk_level = "medium"

    return {
        "risk_score": final_score,
        "ml_score": ml_score,
        "rhythm_score": rhythm_score,
        "risk_level": risk_level
    }