from scoring.skill_gap import normalize_skills


def score_skills(cv_skills: list[str], job_skills: list[str]) -> float:
    if not job_skills:
        return 50.0

    # Vấn đề 1+2 (fix): chuẩn hoá (lowercase + strip) trước khi so khớp,
    # dùng chung hàm normalize_skills với skill_gap.py để 2 module không
    # cho ra kết quả mâu thuẫn nhau cho cùng 1 ứng viên.
    cv_normalized = normalize_skills(cv_skills)
    job_normalized = normalize_skills(job_skills)

    if not job_normalized:
        return 50.0

    matched = len(cv_normalized & job_normalized)
    # Vấn đề 2 (fix): denominator dùng set đã dedupe (len(job_normalized)),
    # không dùng len(job_skills) gốc -> Job nhập skill trùng lặp (vd "Python, SQL, Python")
    # sẽ không còn làm giảm điểm match một cách không công bằng.
    return (matched / len(job_normalized)) * 50


def score_experience(cv_years, required_years) -> float:
    # Vấn đề 3 (fix): validate/ép kiểu về int >= 0 trước khi so sánh,
    # tránh None >= 0 raise TypeError hoặc giá trị âm gây điểm vô nghĩa.
    cv_years = _to_non_negative_int(cv_years)
    required_years = _to_non_negative_int(required_years)

    if cv_years >= required_years:
        return 50.0
    if required_years == 0:
        return 50.0
    return max(0.0, (cv_years / required_years) * 50)


def _to_non_negative_int(value) -> int:
    """Ép kiểu về int >= 0. None hoặc giá trị âm/không hợp lệ -> 0."""
    try:
        n = int(value)
    except (TypeError, ValueError):
        return 0
    return max(0, n)


def calculate_rule_based_score(cv_skills, job_skills, cv_years, required_years) -> float:
    return round(score_skills(cv_skills, job_skills) + score_experience(cv_years, required_years), 2)