import json
import math
import re
from collections import Counter


def _tokenize(text: str) -> list[str]:
    if not text:
        return []
    normalized = re.sub(r"[^0-9a-zA-Z\u00C0-\u017F]+", " ", text.lower())
    return [token for token in normalized.split() if len(token) > 1]


def build_job_model(jobs: list[dict], smoothing: float = 1.0) -> dict:
    """Xây dựng mô hình Naïve Bayes dựa trên các job hiện có."""
    if not jobs:
        return {
            "classes": [],
            "priors": {},
            "feature_counts": {},
            "totals": {},
            "vocab": set(),
            "titles": {},
            "smoothing": smoothing,
        }

    priors = {}
    feature_counts = {}
    totals = {}
    vocab = set()
    titles = {}
    total_jobs = len(jobs)

    for job in jobs:
        job_id = job.get("id")
        titles[job_id] = job.get("title", "Không rõ")

        required_skills = job.get("required_skills") or "[]"
        if isinstance(required_skills, str):
            try:
                required_skills = json.loads(required_skills)
            except Exception:
                required_skills = []

        job_text = " ".join(
            [
                str(job.get("title", "")),
                str(job.get("description", "")),
                " ".join(required_skills or []),
            ]
        )
        tokens = _tokenize(job_text)
        feature_counts[job_id] = Counter(tokens)
        totals[job_id] = sum(feature_counts[job_id].values())
        vocab.update(feature_counts[job_id].keys())
        priors[job_id] = 1.0 / total_jobs

    return {
        "classes": [job.get("id") for job in jobs],
        "priors": priors,
        "feature_counts": feature_counts,
        "totals": totals,
        "vocab": vocab,
        "titles": titles,
        "smoothing": smoothing,
    }


def _score_job(model: dict, cv_text: str, cv_skills: list[str], job_id) -> float:
    tokens = _tokenize(" ".join([cv_text or "", " ".join(cv_skills or [])]))
    if not tokens:
        return float("-inf")

    prior = model["priors"].get(job_id, 1e-9)
    score = math.log(prior)
    vocab_size = max(1, len(model["vocab"]))
    feature_counts = model["feature_counts"].get(job_id, Counter())
    total = model["totals"].get(job_id, 0) + model["smoothing"] * vocab_size

    for token in tokens:
        count = feature_counts.get(token, 0) + model["smoothing"]
        score += math.log(count / total)

    return score


def predict_job_for_cv(cv_skills: list[str], cv_text: str, model: dict) -> str:
    """Dự đoán Job phù hợp nhất cho một CV bằng mô hình Naïve Bayes."""
    if not model or not model.get("classes"):
        return "Không có job để dự đoán"

    best_job = max(model["classes"], key=lambda job_id: _score_job(model, cv_text, cv_skills, job_id))
    return model["titles"].get(best_job, "Không xác định")
