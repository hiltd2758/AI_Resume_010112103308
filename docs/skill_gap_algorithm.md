# Thiết kế logic so sánh JD và CV

## Mục tiêu
Tài liệu này mô tả logic phân tích skill-gap giữa danh sách kỹ năng trong CV và danh sách kỹ năng yêu cầu trong JD. Kết quả dùng để xác định kỹ năng phù hợp, kỹ năng còn thiếu, kỹ năng bổ sung và mức độ phù hợp tổng thể.

## Phạm vi
- So sánh theo tập hợp kỹ năng, không dùng LLM.
- Chuẩn hóa chữ hoa/chữ thường và khoảng trắng.
- Xử lý trùng lặp dữ liệu đầu vào.
- Trả về kết quả dạng dictionary để module khác có thể dùng trực tiếp.
- Bổ sung recommendation rule-based từ `SKILL_RECOMMENDATIONS` trong config.

## Input
- `cv_skills: list[str]`
- `job_skills: list[str]`

Ví dụ:
- CV: `['Python', 'SQL', 'Pandas', 'Git']`
- JD: `['Python', 'SQL', 'Docker', 'FastAPI', 'React']`

## Output chuẩn
```python
{
    "matched_skills": [...],
    "missing_skills": [...],
    "extra_skills": [...],
    "skill_gap_score": 0.0,
    "recommendations": [...]
}
```

Các key tương thích bổ sung có thể giữ lại:
- `additional_skills`
- `gap_percentage`
- `matched_percentage`
- `coverage_percentage`
- `*_display`

## Luồng xử lý
1. Nhận `cv_skills` và `job_skills`.
2. Bỏ giá trị `None` và phần tử không phải chuỗi.
3. Chuẩn hóa bằng `strip()` và `lower()`.
4. Loại trùng lặp bằng tập hợp.
5. So sánh CV với JD để lấy:
   - `matched_skills`
   - `missing_skills`
   - `extra_skills`
6. Tính `skill_gap_score` theo phần trăm kỹ năng JD được match.
7. Sinh `recommendations` từ các kỹ năng thiếu.
8. Trả về dictionary kết quả.

## Quy ước khi JD rỗng
Nếu `job_skills` rỗng hoặc sau chuẩn hóa không còn kỹ năng:
- `missing_skills = []`
- `recommendations = []`
- `skill_gap_score = 100.0`
- `matched_percentage = 100.0` nếu key này được giữ lại
- `coverage_percentage = 100.0` nếu key này được giữ lại

Lý do: không có yêu cầu thì không còn khoảng cách kỹ năng cần lấp.

## Công thức
- `matched_count = số kỹ năng giao nhau`
- `gap_count = số kỹ năng thiếu`
- `job_skills_total = số kỹ năng JD sau chuẩn hóa`
- `gap_percentage = gap_count / job_skills_total * 100`
- `matched_percentage = matched_count / job_skills_total * 100`
- `coverage_percentage = 100 - gap_percentage`
- `skill_gap_score = matched_count / job_skills_total * 100`

## Recommendation rule-based
Với mỗi kỹ năng thiếu:
- Nếu có mapping trong `SKILL_RECOMMENDATIONS`, dùng nội dung gợi ý tương ứng.
- Nếu không có mapping, dùng fallback:
  - `Bổ sung kiến thức và một project minh chứng cho kỹ năng: {skill}.`

## Ví dụ kết quả
```python
{
    "matched_skills": ["python", "sql"],
    "missing_skills": ["docker", "fastapi", "react"],
    "extra_skills": ["git", "pandas"],
    "skill_gap_score": 40.0,
    "recommendations": [
        "Học Docker: containerize ứng dụng, docker-compose và các thực hành tốt nhất.",
        "Xây API với FastAPI, viết unit test và triển khai bằng Docker.",
        "Học React hooks, quản lý state bằng Redux hoặc Context API và làm SPA."
    ]
}
```

## Ghi chú triển khai
- Module phải chạy độc lập.
- Không phụ thuộc UI.
- Không gọi API ngoài.
- Ưu tiên dùng dữ liệu đầu vào đã có sẵn từ pipeline xử lý CV/JD.
