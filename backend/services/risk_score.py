from services.ml_inference import predict_risk

def compute_final_risk_score(profile_features: dict, rhythm_score: float = 0.0) -> dict:
    ml_score = predict_risk(profile_features)

    # Noisy-OR: either a strong ML signal or a strong rhythm signal drives risk up
    final_score = round(1 - (1 - ml_score) * (1 - rhythm_score), 2)

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