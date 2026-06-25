# Thiết kế logic so sánh JD và CV

## Mục tiêu

Logic Skill-Gap so sánh danh sách kỹ năng trong CV với danh sách kỹ năng yêu cầu trong JD bằng phương pháp deterministic. Kết quả dùng để xác định kỹ năng phù hợp, kỹ năng còn thiếu, kỹ năng bổ sung và phần trăm coverage.

## Phạm vi

- So sánh theo kỹ năng canonical, không dùng LLM.
- Chuẩn hóa chữ hoa/thường, khoảng trắng và alias phổ biến.
- Xử lý trùng lặp dữ liệu đầu vào.
- Có thể enrich từ raw `cv_text` hoặc `job_text` khi danh sách skill đã lưu bị thiếu.
- Trả dictionary để UI hoặc module khác dùng trực tiếp.

## Input

```python
analyze_skill_gap(
    cv_skills,
    job_skills,
    cv_text=None,
    job_text=None,
)
```

## Output chuẩn

```python
{
    "matched_skills": ["Python", "SQL"],
    "missing_skills": ["Docker"],
    "extra_skills": ["Pandas"],
    "matched_count": 2,
    "job_skills_total": 3,
    "skill_gap_score": 66.67,
    "coverage_score": 66.67,
    "missing_percent": 33.33,
    "recommendations": [
        {
            "skill": "Docker",
            "priority": "high",
            "recommendation": "...",
            "suggested_evidence": "..."
        }
    ],
    "status": "ok"
}
```

`skill_gap_score` được giữ để tương thích ngược, nhưng ý nghĩa là phần trăm kỹ năng JD được CV đáp ứng. `missing_percent` mới là phần trăm khoảng trống kỹ năng.

## Luồng xử lý

1. Nhận `cv_skills`, `job_skills`, tùy chọn `cv_text`, `job_text`.
2. Bỏ giá trị `None`, phần tử không phải chuỗi và chuỗi rỗng.
3. Chuẩn hóa alias về canonical skill.
4. Loại duplicate nhưng giữ thứ tự xuất hiện.
5. So sánh theo canonical key.
6. Tính `coverage_score` và `missing_percent`.
7. Sinh recommendation cho từng skill thiếu.
8. Trả dictionary kết quả.

## Quy ước khi JD rỗng

Nếu JD không có kỹ năng yêu cầu sau chuẩn hóa:

- `missing_skills = []`
- `recommendations = []`
- `coverage_score = 100.0`
- `skill_gap_score = 100.0`
- `missing_percent = 0.0`
- `status = "no_job_skills"`

Lý do: không có yêu cầu kỹ năng nào thì không có kỹ năng bắt buộc bị thiếu.

## Công thức

```text
coverage_score = matched_required_skills / total_required_skills * 100
missing_percent = 100 - coverage_score
```

`total_required_skills` là số kỹ năng JD duy nhất sau normalize. Duplicate trong JD không làm tăng mẫu số. Extra skill của CV không làm giảm điểm.

## Recommendation rule-based

Với mỗi kỹ năng thiếu:

- Nếu có mapping trong `SKILL_RECOMMENDATIONS`, dùng nội dung tương ứng.
- Nếu không có mapping, dùng fallback tiếng Việt.
- Không sinh recommendation cho skill đã matched.
- Không gọi API ngoài.

## Ghi chú triển khai

- Module chính ở `scoring/skill_gap.py`.
- `parsing/skill_extractor.py` dùng lại regex boundary và alias của module Skill-Gap.
- `scoring/rule_based_scorer.py` dùng chung normalization khi tính điểm kỹ năng.
