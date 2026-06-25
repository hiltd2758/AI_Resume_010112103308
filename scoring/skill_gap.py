"""Deterministic Skill-Gap analysis for CV-JD matching.

This module compares candidate skills with job-required skills without using
Streamlit, Groq, embeddings, or any external service.

`skill_gap_score` is kept for backward compatibility. It means the same thing
as `coverage_score`: matched required skills / total required skills * 100.
`missing_percent` is the actual percentage of missing required skills.
"""

from __future__ import annotations

import re
from collections.abc import Iterable

from core.config import SKILL_KEYWORDS, SKILL_RECOMMENDATIONS


SKILL_ALIASES = {
    "Python": ["Python"],
    "Java": ["Java"],
    "JavaScript": ["JavaScript"],
    "React": ["React"],
    "Node.js": ["Node.js", "NodeJS", "Node JS"],
    "SQL": ["SQL"],
    "FastAPI": ["FastAPI", "Fast API"],
    "Spring Boot": ["Spring Boot", "SpringBoot"],
    "Docker": ["Docker"],
    "Git": ["Git"],
    "TensorFlow": ["TensorFlow", "Tensor Flow"],
    "Pandas": ["Pandas"],
    "HTML": ["HTML", "HTML5"],
    "CSS": ["CSS", "CSS3"],
    "WordPress": ["WordPress", "Word Press"],
    "PHP": ["PHP"],
    "PHP-Fusion": ["PHP-Fusion", "PHP Fusion"],
    "Concrete5": ["Concrete5", "Concrete 5"],
    "AWS": ["AWS"],
    "Linux": ["Linux"],
    "NumPy": ["NumPy", "Numpy"],
    "scikit-learn": ["scikit-learn", "Scikit Learn", "sklearn"],
    "Machine Learning": ["Machine Learning"],
    "PyTorch": ["PyTorch", "Pytorch"],
    "Flask": ["Flask"],
}


def _comparison_key(value: str) -> str:
    """Chuẩn hóa key nội bộ để so sánh alias ổn định."""
    value = re.sub(r"[\s._-]+", "", value.strip().casefold())
    return value


def _clean_skill(value: str) -> str:
    """Làm sạch một skill đơn lẻ trước khi canonicalize."""
    value = re.sub(r"\s+", " ", value.strip())
    return value.strip(" ,;|/")


ALIAS_TO_CANONICAL = {}
for canonical_skill, aliases in SKILL_ALIASES.items():
    ALIAS_TO_CANONICAL[_comparison_key(canonical_skill)] = canonical_skill
    for alias in aliases:
        ALIAS_TO_CANONICAL[_comparison_key(alias)] = canonical_skill


def canonicalize_skill(skill: object) -> str | None:
    """Return canonical display name for one skill, or None when invalid.

    Comment tiếng Việt: hàm này không dùng substring, chỉ chuẩn hóa một giá trị
    skill đã được tách sẵn để tránh nhầm `Java` với `JavaScript`.
    """
    if not isinstance(skill, str):
        return None

    cleaned_skill = _clean_skill(skill)
    if not cleaned_skill:
        return None

    return ALIAS_TO_CANONICAL.get(_comparison_key(cleaned_skill), cleaned_skill)


def normalize_skills(skills: object) -> list[str]:
    """Normalize, canonicalize, and deduplicate skills while preserving order."""
    if skills is None:
        return []

    if isinstance(skills, str):
        raw_skills = re.split(r"[,;|\n]+", skills)
    elif isinstance(skills, Iterable):
        raw_skills = list(skills)
    else:
        raw_skills = []

    normalized_skills = []
    seen_keys = set()
    for raw_skill in raw_skills:
        canonical_skill = canonicalize_skill(raw_skill)
        if canonical_skill is None:
            continue

        skill_key = _comparison_key(canonical_skill)
        if skill_key in seen_keys:
            continue

        seen_keys.add(skill_key)
        normalized_skills.append(canonical_skill)

    return normalized_skills


def _alias_pattern(alias: str) -> str:
    """Tạo regex boundary để alias không match nhầm bên trong từ khác."""
    escaped_chars = []
    for char in alias:
        if char.isspace():
            escaped_chars.append(r"[\s._-]+")
        elif char in {".", "-", "_"}:
            escaped_chars.append(r"[\s._-]*")
        else:
            escaped_chars.append(re.escape(char))

    return r"(?<![A-Za-z0-9])" + "".join(escaped_chars) + r"(?![A-Za-z0-9])"


TEXT_SKILL_PATTERNS = []
for canonical_skill in SKILL_KEYWORDS:
    canonical_name = canonicalize_skill(canonical_skill)
    if canonical_name is None:
        continue
    aliases = SKILL_ALIASES.get(canonical_name, [canonical_name])
    for alias in aliases:
        TEXT_SKILL_PATTERNS.append((canonical_name, re.compile(_alias_pattern(alias), re.IGNORECASE)))


def extract_skills_from_text(text: str | None) -> list[str]:
    """Extract known skills from raw text with safe boundaries and aliases."""
    if not isinstance(text, str) or not text.strip():
        return []

    found_skills = []
    seen_keys = set()
    for canonical_skill, pattern in TEXT_SKILL_PATTERNS:
        skill_key = _comparison_key(canonical_skill)
        if skill_key in seen_keys:
            continue
        if pattern.search(text):
            seen_keys.add(skill_key)
            found_skills.append(canonical_skill)

    return found_skills


def _recommendation_key(skill: str) -> str:
    """Đưa canonical skill về key tương thích với SKILL_RECOMMENDATIONS."""
    return _comparison_key(skill)


def build_recommendations(missing_skills: object, display_map: dict | None = None) -> list[dict]:
    """Build structured recommendations for missing skills only."""
    display_map = display_map or {}
    recommendations = []
    seen_keys = set()

    for skill in normalize_skills(missing_skills):
        skill_key = _comparison_key(skill)
        if skill_key in seen_keys:
            continue
        seen_keys.add(skill_key)

        display_skill = display_map.get(skill, skill)
        recommendation_text = SKILL_RECOMMENDATIONS.get(
            _recommendation_key(skill),
            f"Bổ sung kiến thức nền tảng về {display_skill}, làm một bài thực hành nhỏ và đưa bằng chứng vào portfolio.",
        )
        recommendations.append(
            {
                "skill": display_skill,
                "priority": "high",
                "recommendation": recommendation_text,
                "suggested_evidence": f"GitHub repository, project demo hoặc ghi chú học tập có sử dụng {display_skill}.",
            }
        )

    return recommendations


def _skill_key_map(skills: list[str]) -> dict[str, str]:
    return {_comparison_key(skill): skill for skill in skills}


def analyze_skill_gap(cv_skills, job_skills, cv_text=None, job_text=None):
    """Analyze skill coverage between CV skills and job-required skills.

    Args:
        cv_skills (list[str] | str | None): Skills extracted from CV.
        job_skills (list[str] | str | None): Skills required by the job.
        cv_text (str | None): Optional raw CV text used to enrich missing parsed skills.
        job_text (str | None): Optional raw JD text used to enrich missing parsed skills.

    Returns:
        dict: UI-ready result. Important fields:
            - `skill_gap_score`: backward-compatible coverage percentage.
            - `coverage_score`: clearer alias of the same coverage value.
            - `missing_percent`: 100 - coverage_score.

    Comment tiếng Việt: khi JD không có skill yêu cầu, coverage được quy ước là
    100% vì không có kỹ năng bắt buộc nào bị thiếu.
    """
    cv_skills_normalized = normalize_skills(cv_skills)
    job_skills_normalized = normalize_skills(job_skills)

    if cv_text:
        cv_skills_normalized = normalize_skills(cv_skills_normalized + extract_skills_from_text(cv_text))
    if job_text:
        job_skills_normalized = normalize_skills(job_skills_normalized + extract_skills_from_text(job_text))

    cv_skill_map = _skill_key_map(cv_skills_normalized)
    job_skill_map = _skill_key_map(job_skills_normalized)

    cv_keys = set(cv_skill_map)
    job_keys = set(job_skill_map)

    matched_keys = [key for key in job_skill_map if key in cv_keys]
    missing_keys = [key for key in job_skill_map if key not in cv_keys]
    extra_keys = [key for key in cv_skill_map if key not in job_keys]

    matched_skills = [job_skill_map[key] for key in matched_keys]
    missing_skills = [job_skill_map[key] for key in missing_keys]
    extra_skills = [cv_skill_map[key] for key in extra_keys]

    matched_count = len(matched_skills)
    gap_count = len(missing_skills)
    job_skills_total = len(job_skills_normalized)

    if job_skills_total == 0:
        coverage_score = 100.0
        status = "no_job_skills"
        note = "Job không có kỹ năng yêu cầu; quy ước coverage là 100% vì không có skill nào bị thiếu."
    else:
        coverage_score = round((matched_count / job_skills_total) * 100, 2)
        status = "ok"
        note = ""

    missing_percent = round(100.0 - coverage_score, 2)

    result = {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "extra_skills": extra_skills,
        "additional_skills": extra_skills,
        "matched_skills_display": matched_skills,
        "missing_skills_display": missing_skills,
        "additional_skills_display": extra_skills,
        "extra_skills_display": extra_skills,
        "matched_count": matched_count,
        "gap_count": gap_count,
        "job_skills_total": job_skills_total,
        "skill_gap_score": coverage_score,
        "coverage_score": coverage_score,
        "coverage_percentage": coverage_score,
        "matched_percentage": coverage_score,
        "missing_percent": missing_percent,
        "gap_percentage": missing_percent,
        "recommendations": build_recommendations(missing_skills),
        "cv_skills_normalized": cv_skills_normalized,
        "job_skills_normalized": job_skills_normalized,
        "status": status,
        "note": note,
    }

    return result


if __name__ == "__main__":
    demo_result = analyze_skill_gap(["HTML5", "CSS3", "wordpress"], ["HTML", "CSS", "WordPress"])
    print(demo_result)
