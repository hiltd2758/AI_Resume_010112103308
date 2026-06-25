# Skill-Gap Integration Contract

## Hàm cần import

```python
from scoring.skill_gap import analyze_skill_gap
```

## Input cần lấy từ CV/Job

- `cv_skills`: danh sách kỹ năng đã parse từ CV, ví dụ `["HTML5", "CSS3", "WordPress"]`.
- `job_skills`: danh sách kỹ năng yêu cầu của Job, ví dụ `["HTML", "CSS", "WordPress"]`.
- `cv_text` tùy chọn: raw text của CV. Nên truyền khi dữ liệu CV cũ trong database có trường `skills` rỗng hoặc thiếu.
- `job_text` tùy chọn: raw text của JD. Có thể truyền khi muốn enrich từ mô tả Job.

## Ví dụ gọi hàm

```python
result = analyze_skill_gap(
    cv_skills=cv_skills,
    job_skills=job_skills,
    cv_text=cv_raw_text,
    job_text=job_description,
)
```

## Field UI nên hiển thị

- Skill coverage: `result["coverage_score"]` hoặc `result["skill_gap_score"]`.
- Kỹ năng phù hợp: `result["matched_skills"]`.
- Kỹ năng còn thiếu: `result["missing_skills"]`.
- Kỹ năng bổ sung: `result["extra_skills"]`.
- Recommendations: `result["recommendations"]`.

## Cảnh báo tích hợp

- Không dùng LLM score để thay thế `coverage_score`.
- `skill_gap_score` được giữ để tương thích ngược và vẫn có nghĩa là coverage phần trăm.
- `missing_percent` mới là phần trăm khoảng trống kỹ năng.
- Khi CV cũ có `skills` trống, truyền thêm `cv_text` nếu có để module tự enrich bằng keyword/alias an toàn.

## Output tối thiểu

```python
{
    "matched_skills": ["HTML", "CSS"],
    "missing_skills": ["WordPress"],
    "extra_skills": ["Python"],
    "matched_count": 2,
    "job_skills_total": 3,
    "skill_gap_score": 66.67,
    "coverage_score": 66.67,
    "missing_percent": 33.33,
    "recommendations": [
        {
            "skill": "WordPress",
            "priority": "high",
            "recommendation": "...",
            "suggested_evidence": "..."
        }
    ],
    "status": "ok"
}
```
