from scoring.skill_gap import extract_skills_from_text


def extract_skills(text: str) -> list[str]:
    # Dùng chung bộ chuẩn hóa của Skill-Gap để tránh parser và scoring lệch nhau.
    return extract_skills_from_text(text)
