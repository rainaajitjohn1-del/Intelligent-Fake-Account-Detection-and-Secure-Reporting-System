import joblib
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "ml_models", "fake_profile_model.pkl")

model = None

def load_model():
    global model
    if model is None and os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
    return model

def predict_risk(profile_features: dict) -> float:
    """
    profile_features must contain these keys:
    profile_pic, nums_length_username, fullname_words, nums_length_fullname,
    name_equals_username, description_length, external_url, private,
    posts, followers, follows
    """
    m = load_model()
    if m is None:
        return 0.42  # fallback if model file is missing

    feature_order = [
        "profile_pic", "nums_length_username", "fullname_words",
        "nums_length_fullname", "name_equals_username", "description_length",
        "external_url", "private", "posts", "followers", "follows"
    ]

    feature_values = [[profile_features.get(k, 0) for k in feature_order]]

    probability_fake = m.predict_proba(feature_values)[0][1]
    return round(float(probability_fake), 2)