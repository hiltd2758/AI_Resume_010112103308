from typing import List


def missing_skills(cv_skills: List[str], job_skills: List[str]) -> List[str]:
    """Trả về danh sách kỹ năng yêu cầu mà CV chưa có."""
    cv_set = {s.strip().lower() for s in cv_skills if s}
    missing = [skill for skill in job_skills if skill.strip().lower() not in cv_set]
    return missing


def skill_gap_score(cv_skills: List[str], job_skills: List[str]) -> float:
    """Tính % kỹ năng đã đáp ứng so với yêu cầu, dùng cho hiển thị."""
    if not job_skills:
        return 100.0
    matched = len(job_skills) - len(missing_skills(cv_skills, job_skills))
    return round((matched / len(job_skills)) * 100, 2)
