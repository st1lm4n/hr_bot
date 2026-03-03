DEPTH_WEIGHT = 0.5
CRITICAL_WEIGHT = 0.3
CREATIVITY_WEIGHT = 0.2


def calculate_total(scores: dict) -> int:
    weighted = (
        scores["depth_score"] * DEPTH_WEIGHT
        + scores["critical_score"] * CRITICAL_WEIGHT
        + scores["creativity_score"] * CREATIVITY_WEIGHT
    )
    return round(weighted * 3)  # переводим обратно к шкале ~15
