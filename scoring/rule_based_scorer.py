

def score_skills(cv_skills: list[str], job_skills: list[str]) -> float:
    if not job_skills:
        return 50.0
    matched = len(set(cv_skills) & set(job_skills))
    return (matched / len(job_skills)) * 50


def score_experience(cv_years: int, required_years: int) -> float:
    if cv_years >= required_years:
        return 50.0
    if required_years == 0:
        return 50.0
    return max(0.0, (cv_years / required_years) * 50)


def calculate_rule_based_score(cv_skills, job_skills, cv_years, required_years) -> float:
    return round(score_skills(cv_skills, job_skills) + score_experience(cv_years, required_years), 2)
