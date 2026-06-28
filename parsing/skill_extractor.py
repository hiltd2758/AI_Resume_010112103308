import re
from core.config import get_scan_skill_keywords

# Skill mà \b không đủ: cần lookahead/lookbehind chặt hơn
# "java" cần thêm vì "javascript" chứa "java" + ký tự \w liền sau
# -> \bjava\b vẫn KHÔNG match trong "javascript" về lý thuyết
# nhưng thêm vào _AMBIGUOUS_SKILLS để chắc chắn
_AMBIGUOUS_SKILLS = {"c", "r", "go", "c#", "c++", "dart", "rust", "perl", "java"}


def _build_pattern(skill_lower: str) -> str | None:
    skill_lower = skill_lower.strip()
    if not skill_lower:
        return None

    escaped = re.escape(skill_lower)

    if skill_lower in _AMBIGUOUS_SKILLS:
        return rf"(?<!\w){escaped}(?!\w)"

    last_char_is_word = bool(re.match(r"\w", skill_lower[-1]))

    if last_char_is_word:
        return rf"\b{escaped}\b"
    else:
        return rf"\b{escaped}(?!\w)"


def extract_skills(text: str, extra_skills: list[str] | None = None) -> list[str]:
    """
    Trích xuất danh sách skill xuất hiện trong text CV.

    Args:
        text: nội dung CV đã extract
        extra_skills: skill lấy từ JD hiện có để không bị giới hạn whitelist cứng.

    Returns:
        list[str]: các skill tìm thấy, giữ casing gốc từ keyword list.
    """
    scan_list = get_scan_skill_keywords(extra_skills)
    text_lower = text.lower()
    found = []

    for skill in scan_list:
        pattern = _build_pattern(skill.lower())
        if pattern and re.search(pattern, text_lower):
            found.append(skill)

    return found