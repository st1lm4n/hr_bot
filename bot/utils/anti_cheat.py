import re

GENERIC_PATTERNS = [
    "как языковая модель",
    "в заключение",
    "подводя итог",
    "безусловно",
]


def detect_ai_like_text(text: str) -> bool:
    lower = text.lower()
    for pattern in GENERIC_PATTERNS:
        if pattern in lower:
            return True
    return False


def is_low_effort(text: str) -> bool:
    return len(text.split()) < 20
