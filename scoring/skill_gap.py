

from typing import List

from core.config import SKILL_RECOMMENDATIONS


def build_recommendations(missing_skills, display_map=None):
    """Build recommendation strings for missing skills.

    Args:
        missing_skills (list[str]): Missing skills, typically normalized keys.
        display_map (dict | None): Optional mapping normalized -> display text.

    Returns:
        list[str]: list of recommendation strings in the same order
    """
    if display_map is None:
        display_map = {}

    recs = []
    for s in missing_skills:
        display = display_map.get(s, s)
        if s in SKILL_RECOMMENDATIONS:
            recs.append(SKILL_RECOMMENDATIONS[s])
        else:
            recs.append(f"Bổ sung kiến thức và một project minh chứng cho kỹ năng: {display}.")
    return recs


def analyze_skill_gap(cv_skills, job_skills):
    """
    Analyze skill gap between CV and job requirements.

    Compares two lists of skills (CV vs. Job) and identifies:
    - Matched skills: Present in both
    - Missing skills: Required by job but NOT in CV
    - Additional skills: In CV but NOT required by job

    Returns:
        dict: matched_skills, missing_skills, additional_skills, gap_count,
        matched_count, job_skills_total, gap_percentage, matched_percentage,
        coverage_percentage, skill_gap_score, recommendations (và các bản
        *_display giữ nguyên chữ hoa/thường gốc).
    """

    if cv_skills is None:
        cv_skills = []
    if job_skills is None:
        job_skills = []

    cv_skills = [s for s in cv_skills if s is not None and isinstance(s, str)]
    job_skills = [s for s in job_skills if s is not None and isinstance(s, str)]

    cv_display = {}
    for s in cv_skills:
        key = s.lower().strip()
        if key not in cv_display:
            cv_display[key] = s.strip()

    job_display = {}
    for s in job_skills:
        key = s.lower().strip()
        if key not in job_display:
            job_display[key] = s.strip()

    cv_normalized = set(cv_display.keys())
    job_normalized = set(job_display.keys())

    matched_norm = sorted(list(cv_normalized & job_normalized))
    missing_norm = sorted(list(job_normalized - cv_normalized))
    additional_norm = sorted(list(cv_normalized - job_normalized))

    matched_skills = matched_norm
    missing_skills_ = missing_norm
    additional_skills = additional_norm

    def map_display(norm_list, preferred_map, fallback_map):
        display_list = []
        for k in norm_list:
            if k in preferred_map:
                display_list.append(preferred_map[k])
            elif k in fallback_map:
                display_list.append(fallback_map[k])
            else:
                display_list.append(k)
        return display_list

    matched_skills_display = map_display(matched_norm, job_display, cv_display)
    missing_skills_display = map_display(missing_norm, job_display, cv_display)
    additional_skills_display = map_display(additional_norm, cv_display, job_display)

    gap_count = len(missing_norm)
    matched_count = len(matched_norm)
    job_skills_total = len(job_normalized)

    if job_skills_total == 0:
        gap_percentage = 0.0
        matched_percentage = 100.0
        coverage_percentage = 100.0
        skill_gap_score_ = 100.0
        recommendations = []
    else:
        gap_percentage = (gap_count / job_skills_total) * 100
        matched_percentage = (matched_count / job_skills_total) * 100
        coverage_percentage = 100 - gap_percentage
        skill_gap_score_ = round((matched_count / job_skills_total) * 100, 2)
        recommendations = build_recommendations(missing_norm, job_display)

    return {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills_,
        "additional_skills": additional_skills,
        "extra_skills": additional_skills,
        "matched_skills_display": matched_skills_display,
        "missing_skills_display": missing_skills_display,
        "additional_skills_display": additional_skills_display,
        "gap_count": gap_count,
        "matched_count": matched_count,
        "job_skills_total": job_skills_total,
        "gap_percentage": round(gap_percentage, 2),
        "matched_percentage": round(matched_percentage, 2),
        "coverage_percentage": round(coverage_percentage, 2),
        "skill_gap_score": skill_gap_score_,
        "recommendations": recommendations,
    }


# --- Wrapper tương thích với phiên bản đơn giản (nhánh feature/skill-gap-result-ui) ---

def missing_skills(cv_skills: List[str], job_skills: List[str]) -> List[str]:
    """Trả về danh sách kỹ năng yêu cầu mà CV chưa có (display casing)."""
    result = analyze_skill_gap(cv_skills, job_skills)
    return result["missing_skills_display"]


def skill_gap_score(cv_skills: List[str], job_skills: List[str]) -> float:
    """Tính % kỹ năng đã đáp ứng so với yêu cầu."""
    result = analyze_skill_gap(cv_skills, job_skills)
    return result["skill_gap_score"]


if __name__ == "__main__":
    result1 = analyze_skill_gap(
        cv_skills=["Python", "SQL", "Git", "Docker"],
        job_skills=["Python", "SQL", "AWS", "Kubernetes"]
    )
    print("Matched:", result1["matched_skills_display"])
    print("Missing:", result1["missing_skills_display"])
    print("Gap %:", result1["gap_percentage"])
    print("Skill gap score:", result1["skill_gap_score"])