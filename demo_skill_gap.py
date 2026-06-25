import sys

from scoring.skill_gap import analyze_skill_gap


if hasattr(sys.stdout, "reconfigure"):
    # Bảo đảm demo tiếng Việt in được trên Windows console dùng code page cũ.
    sys.stdout.reconfigure(encoding="utf-8")


def print_case(title, cv_skills, job_skills, cv_text=None):
    result = analyze_skill_gap(cv_skills=cv_skills, job_skills=job_skills, cv_text=cv_text)

    print(f"\n=== {title} ===")
    print(f"CV skills: {cv_skills}")
    print(f"Job skills: {job_skills}")
    print(f"Kỹ năng phù hợp: {', '.join(result['matched_skills']) or 'Không có'}")
    print(f"Kỹ năng còn thiếu: {', '.join(result['missing_skills']) or 'Không có'}")
    print(f"Kỹ năng bổ sung: {', '.join(result['extra_skills']) or 'Không có'}")
    print(f"Skill coverage: {result['coverage_score']}%")
    print(f"Missing percent: {result['missing_percent']}%")

    if result["recommendations"]:
        print("Gợi ý cải thiện:")
        for index, item in enumerate(result["recommendations"], start=1):
            print(f"{index}. [{item['skill']}] {item['recommendation']}")
            print(f"   Bằng chứng nên có: {item['suggested_evidence']}")
    else:
        print("Gợi ý cải thiện: Không có kỹ năng bắt buộc nào bị thiếu.")


if __name__ == "__main__":
    print("PHÂN TÍCH SKILL-GAP DETERMINISTIC")
    print("Skill-Gap tách biệt với điểm LLM/Groq và chỉ dựa trên kỹ năng đã chuẩn hóa.")

    print_case(
        "Case 1 - CV Python/Backend match 100% với Job Python",
        ["Python", "SQL", "Docker", "Git", "Pandas"],
        ["python", "sql", "docker", "git", "pandas"],
    )

    print_case(
        "Case 2 - HTML5/CSS3/WordPress vẫn match Front End 100%",
        ["HTML5", "CSS3", "WordPress"],
        ["HTML", "CSS", "WordPress"],
    )

    print_case(
        "Case 3 - CV Python không phù hợp hoàn toàn với Job Front End là do mismatch dữ liệu",
        ["Python", "SQL", "Docker", "Git", "Pandas"],
        ["HTML", "CSS", "WordPress"],
    )
