from services.ml_inference import predict_risk

def compute_final_risk_score(profile_features: dict) -> dict:
    ml_score = predict_risk(profile_features)

    risk_level = "low"
    if ml_score > 0.7:
        risk_level = "high"
    elif ml_score > 0.4:
        risk_level = "medium"

    return {
        "risk_score": ml_score,
        "risk_level": risk_level
    }