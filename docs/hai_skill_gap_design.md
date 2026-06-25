# Thiết kế module Skill-Gap - Thành viên Hai

## Mục tiêu

Module Skill-Gap so sánh kỹ năng ứng viên trong CV với kỹ năng yêu cầu trong JD bằng logic deterministic, dễ kiểm thử và không phụ thuộc Streamlit, Groq/LLM hoặc RAG.

## Vấn đề thực tế

- `Python` và `python` từng có thể bị coi khác nhau.
- `HTML5`, `CSS3`, `Word Press` cần được hiểu lần lượt là `HTML`, `CSS`, `WordPress`.
- Dữ liệu CV cũ trong database có thể thiếu skill do parser trước đây dùng keyword hẹp.
- Skill-Gap phải tách biệt với điểm LLM, không để AI sửa kết quả so sánh kỹ năng.

## Input/Output

Input chính:

```python
analyze_skill_gap(cv_skills, job_skills, cv_text=None, job_text=None)
```

Output chính:

- `matched_skills`: kỹ năng yêu cầu có trong CV.
- `missing_skills`: kỹ năng JD yêu cầu nhưng CV thiếu.
- `extra_skills`: kỹ năng CV có thêm ngoài JD.
- `coverage_score`: phần trăm kỹ năng yêu cầu được đáp ứng.
- `skill_gap_score`: alias tương thích ngược của `coverage_score`.
- `missing_percent`: phần trăm kỹ năng yêu cầu còn thiếu.
- `recommendations`: gợi ý có cấu trúc cho từng kỹ năng còn thiếu.

## Flow xử lý

```text
CV skills / CV text
        |
Normalize + canonicalize + remove duplicate
        |
Job skills / Job text
        |
Normalize + canonicalize + remove duplicate
        |
Compare by canonical key
        |
Matched / Missing / Extra skills
        |
Coverage %, Missing %, Recommendations
        |
Dictionary output for UI/tests
```

## Normalization và alias

Module loại khoảng trắng thừa, không phân biệt hoa/thường và gom các biến thể phổ biến về canonical skill:

- `Python`, `python`, `PYTHON` -> `Python`
- `HTML`, `HTML5` -> `HTML`
- `CSS`, `CSS3` -> `CSS`
- `WordPress`, `Word Press` -> `WordPress`
- `Node.js`, `NodeJS`, `Node JS` -> `Node.js`
- `FastAPI`, `Fast API` -> `FastAPI`
- `Spring Boot`, `SpringBoot` -> `Spring Boot`
- `scikit-learn`, `Scikit Learn`, `sklearn` -> `scikit-learn`

Parser text dùng regex boundary để tránh nhận nhầm `Java` trong `JavaScript`.

## Công thức

```text
coverage_score = matched_required_skills / total_required_skills * 100
missing_percent = 100 - coverage_score
```

`total_required_skills` là số kỹ năng yêu cầu duy nhất của Job sau normalize. Duplicate không được tính nhiều lần. `extra_skills` không làm giảm điểm.

## Ý nghĩa field điểm

- `skill_gap_score`: giữ tên cũ để UI/test cũ không hỏng, nhưng ý nghĩa là coverage.
- `coverage_score`: tên rõ nghĩa hơn cho coverage.
- `missing_percent`: phần trăm khoảng trống kỹ năng.

## Recommendation

Mỗi kỹ năng thiếu sinh đúng một recommendation dạng:

```python
{
    "skill": "Docker",
    "priority": "high",
    "recommendation": "...",
    "suggested_evidence": "..."
}
```

Recommendation lấy từ `SKILL_RECOMMENDATIONS`; nếu chưa có mapping thì dùng fallback tiếng Việt rõ ràng.

## Edge case

- `cv_skills=None`: không crash, coi như CV chưa có kỹ năng.
- `job_skills=[]`: coverage quy ước là `100.0`, status là `no_job_skills`.
- Duplicate trong CV/JD: loại bỏ nhưng giữ thứ tự xuất hiện hợp lý.
- Skill không có alias: vẫn so sánh không phân biệt hoa/thường.

## Hạn chế

Module hiện là keyword/alias-based, chưa hiểu semantic sâu. Ví dụ `PostgreSQL` không tự động bằng `SQL` nếu chưa khai báo alias.

## Hướng phát triển

- Thêm taxonomy skill theo nhóm công nghệ.
- Thêm weighting theo mức độ quan trọng của từng skill.
- Kết hợp embedding/semantic matching nhưng vẫn giữ deterministic score làm baseline.
