import re
from core.config import get_scan_skill_keywords

# Skill ngắn/dễ nhầm: yêu cầu phải là từ độc lập (surrounded by spaces/punctuation/boundary)
# thay vì chỉ dùng \b
_AMBIGUOUS_SKILLS = {"c", "r", "go", "c#", "c++", "dart", "rust", "perl"}

def _build_pattern(skill_lower: str) -> str | None:
    if not skill_lower:  # bỏ qua skill rỗng
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
    scan_list = get_scan_skill_keywords(extra_skills)
    text_lower = text.lower()
    found = []

    for skill in scan_list:
        pattern = _build_pattern(skill.lower())
        if pattern and re.search(pattern, text_lower):  # skip nếu pattern là None
            found.append(skill)

    return found
def _build_pattern(skill_lower: str) -> str:
    """
    Tạo regex pattern phù hợp cho từng loại skill:
    - Skill thông thường: \b...\b (word boundary)
    - Skill ngắn/dễ nhầm (C, R, Go...): (?<![\\w])...(?![\\w]) để đảm bảo
      không khớp khi nằm trong từ khác (vd "Go" không khớp trong "Google", "Golang")
    - Skill kết thúc bằng ký tự đặc biệt (C++, C#, .NET): \b ở đầu +
      lookahead (?![\\w]) ở cuối
    """
    escaped = re.escape(skill_lower)

    if skill_lower in _AMBIGUOUS_SKILLS:
        # Phải là từ hoàn toàn độc lập: không có \w liền trước hoặc sau
        return rf"(?<!\w){escaped}(?!\w)"

    # Kiểm tra ký tự cuối có phải \w không (chữ/số)
    last_char_is_word = bool(re.match(r"\w", skill_lower[-1]))

    if last_char_is_word:
        return rf"\b{escaped}\b"
    else:
        # Kết thúc bằng ký tự đặc biệt (++, #, .): \b đầu + lookahead cuối
        return rf"\b{escaped}(?!\w)"


def extract_skills(text: str, extra_skills: list[str] | None = None) -> list[str]:
    """
    Trích xuất danh sách skill xuất hiện trong text CV.

    Args:
        text: nội dung CV đã extract
        extra_skills: skill lấy từ JD hiện có (để không bị giới hạn whitelist cứng).
                      Nếu None, chỉ quét theo SKILL_KEYWORDS mặc định.

    Returns:
        list[str]: các skill tìm thấy, giữ casing gốc từ keyword list.
    """
    scan_list = get_scan_skill_keywords(extra_skills)
    text_lower = text.lower()
    found = []

    for skill in scan_list:
        pattern = _build_pattern(skill.lower())
        if re.search(pattern, text_lower):
            found.append(skill)

    return found