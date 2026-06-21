from core.config import SKILL_KEYWORDS


def extract_skills(text: str) -> list[str]:
    text_lower = text.lower()
    return [s for s in SKILL_KEYWORDS if s.lower() in text_lower]
