import re
import instaloader

L = instaloader.Instaloader()

def extract_username_features(username: str) -> dict:
    """Real signals computed directly from the username string — always reliable."""
    digits = sum(c.isdigit() for c in username)
    length = len(username) if username else 1
    return {
        "nums_length_username": round(digits / length, 2) if length else 0,
    }

def extract_live_instagram_features(username: str) -> dict:
    """
    Attempts a real fetch of public Instagram profile data.
    Returns None if it fails (rate-limited, private, login-walled, etc.)
    so the caller can fall back gracefully.
    """
    try:
        profile = instaloader.Profile.from_username(L.context, username)
        return {
            "profile_pic": 1 if profile.profile_pic_url else 0,
            "fullname_words": len(profile.full_name.split()) if profile.full_name else 0,
            "nums_length_fullname": 0,  # could refine further
            "name_equals_username": 1 if profile.full_name.lower() == username.lower() else 0,
            "description_length": len(profile.biography) if profile.biography else 0,
            "external_url": 1 if profile.external_url else 0,
            "private": 1 if profile.is_private else 0,
            "posts": profile.mediacount,
            "followers": profile.followers,
            "follows": profile.followees,
        }
    except Exception as e:
        print(f"Live fetch failed for {username}: {e}")
        return None

def get_profile_features(username: str, platform: str) -> tuple[dict, bool]:
    """
    Returns (features, is_real_data).
    Tries live fetch first (Instagram only). Falls back to reasonable
    defaults combined with real username-derived signals if fetch fails
    or platform isn't supported.
    """
    username_features = extract_username_features(username)

    if platform == "instagram":
        live_features = extract_live_instagram_features(username)
        if live_features:
            live_features.update(username_features)
            return live_features, True

    # Fallback — still uses REAL username-derived data, only the
    # network-dependent fields are estimated
    fallback = {
        "profile_pic": 1,
        "fullname_words": 2,
        "nums_length_fullname": 0,
        "name_equals_username": 0,
        "description_length": 45,
        "external_url": 0,
        "private": 0,
        "posts": 20,
        "followers": 500,
        "follows": 300,
    }
    fallback.update(username_features)
    return fallback, False