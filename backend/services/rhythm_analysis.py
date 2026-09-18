import statistics

def compute_rhythm_score(post_timestamps: list) -> float:
    """
    post_timestamps: list of numbers representing hours between each post
    (in a real system, these would be derived from actual post history).
    Returns a score 0-1 where higher = more bot-like (unnaturally consistent timing).
    """
    if len(post_timestamps) < 2:
        return 0.0

    variance = statistics.pvariance(post_timestamps)
    mean_interval = statistics.mean(post_timestamps)

    if mean_interval == 0:
        return 1.0

    # low variance relative to mean = suspiciously consistent = bot-like
    consistency_ratio = variance / (mean_interval ** 2)

    # invert and normalize: low consistency_ratio -> high rhythm risk
    rhythm_risk = max(0.0, min(1.0, 1 - consistency_ratio))
    return round(rhythm_risk, 2)