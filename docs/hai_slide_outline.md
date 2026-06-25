# Slide Outline - Skill-Gap

## Slide 1: Bài toán Skill-Gap trong hệ thống CV-JD Matching

- Mục tiêu: biết ứng viên đang đáp ứng và thiếu kỹ năng nào so với JD.
- Yêu cầu: deterministic, dễ giải thích, không phụ thuộc LLM.

## Slide 2: Input/Output của module

- Input: `cv_skills`, `job_skills`, tùy chọn `cv_text`, `job_text`.
- Output: matched skills, missing skills, extra skills, coverage score, recommendations.

## Slide 3: Flow xử lý

- Nhận kỹ năng từ CV/JD.
- Normalize và canonicalize.
- Loại duplicate.
- So sánh canonical skill.
- Trả kết quả sẵn sàng cho UI.

## Slide 4: Chuẩn hóa và alias skill

- `HTML5` -> `HTML`.
- `CSS3` -> `CSS`.
- `Word Press` -> `WordPress`.
- `NodeJS` -> `Node.js`.
- Regex boundary giúp tránh match nhầm `Java` với `JavaScript`.

## Slide 5: Công thức tính coverage

```text
coverage_score = matched_required_skills / total_required_skills * 100
missing_percent = 100 - coverage_score
```

- Duplicate trong JD không tính nhiều lần.
- Extra skill không làm giảm điểm.

## Slide 6: Recommendation cho skill thiếu

- Mỗi missing skill có đúng một recommendation.
- Recommendation gồm skill, priority, nội dung học và bằng chứng nên có.
- Không gọi LLM/Groq.

## Slide 7: Demo/test cases

- Python Backend match 100%.
- HTML5/CSS3/WordPress match Front End 100%.
- Python Backend so với Front End trả missing rõ ràng.
- Unit test kiểm tra alias, duplicate, input rỗng và text enrichment.

## Slide 8: Hạn chế và hướng phát triển

- Hạn chế: keyword/alias-based, chưa hiểu semantic sâu.
- Hướng phát triển: taxonomy skill, weighting theo JD, semantic matching có kiểm soát.
