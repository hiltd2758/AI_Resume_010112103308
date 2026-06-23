from scoring.skill_gap import analyze_skill_gap


if __name__ == "__main__":
    cv_skills = ["Python", "SQL", "Pandas", "Git"]
    job_skills = ["Python", "SQL", "Docker", "FastAPI", "React"]

    result = analyze_skill_gap(cv_skills=cv_skills, job_skills=job_skills)

    matched = result.get("matched_skills_display", result.get("matched_skills", []))
    missing = result.get("missing_skills_display", result.get("missing_skills", []))
    extra = result.get("additional_skills_display", result.get("extra_skills", []))

    print("=== PHÂN TÍCH SKILL-GAP ===")
    print(f"Kỹ năng phù hợp: {', '.join(matched) if matched else 'Không có'}")
    print(f"Kỹ năng còn thiếu: {', '.join(missing) if missing else 'Không có'}")
    print(f"Kỹ năng bổ sung: {', '.join(extra) if extra else 'Không có'}")
    print(f"Độ phủ kỹ năng: {result['skill_gap_score']}%")

    print("\n=== GỢI Ý CẢI THIỆN ===")
    if result["recommendations"]:
        for index, recommendation in enumerate(result["recommendations"], start=1):
            print(f"{index}. {recommendation}")
    else:
        print("1. Không có gợi ý vì JD không có kỹ năng yêu cầu.")
