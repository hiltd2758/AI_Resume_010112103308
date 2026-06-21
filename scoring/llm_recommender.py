"""Gọi Groq API để tinh chỉnh điểm + nhận xét + gợi ý câu hỏi PV (Role: Bá)."""
import json
import time
from core.config import GROQ_API_KEY

PROMPT_TEMPLATE = """Bạn là một chuyên gia Tuyển dụng AI. Tôi có một Job Description như sau: {job_description}

Ứng viên có thông tin trích xuất:
- Kỹ năng: {cv_skills}
- Kinh nghiệm: {cv_years} năm
- Toàn bộ text CV: {cv_text}

Hãy thực hiện:
1. Đánh giá lại % match (tối ưu dựa trên ngữ cảnh, điểm rule-based ban đầu: {rule_score}).
2. Nhận xét ngắn gọn (Ưu điểm, Nhược điểm).
3. Khuyến nghị có nên phỏng vấn không, và câu hỏi kỹ thuật nên hỏi.

Trả về JSON đúng format, không thêm chữ nào khác:
{{"final_score": 0, "pros": "", "cons": "", "recommendation": "", "interview_questions": []}}
"""


def build_prompt(job_description, cv_skills, cv_years, cv_text, rule_score) -> str:
    return PROMPT_TEMPLATE.format(
        job_description=job_description,
        cv_skills=cv_skills,
        cv_years=cv_years,
        cv_text=cv_text[:1500],  # tránh prompt quá dài, tốn token
        rule_score=rule_score,
    )


def call_llm(prompt: str) -> dict:
    if not GROQ_API_KEY:
        return {
            "final_score": 0,
            "pros": "",
            "cons": "",
            "recommendation": "Chưa cấu hình GROQ_API_KEY trong .env",
            "interview_questions": [],
        }

    from groq import Groq
    client = Groq(api_key=GROQ_API_KEY)

    max_retries = 2
    for attempt in range(max_retries + 1):
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.3,
            )
            text = completion.choices[0].message.content.strip()
            text = text.strip("```json").strip("```")
            return json.loads(text)
        except Exception as e:
            is_rate_limit = "429" in str(e) or "rate_limit" in str(e).lower()
            if is_rate_limit and attempt < max_retries:
                time.sleep(10)
                continue
            return {
                "final_score": None,
                "pros": "",
                "cons": "",
                "recommendation": f"Không gọi được Groq API ({type(e).__name__}), dùng tạm điểm rule-based.",
                "interview_questions": [],
            }


def get_llm_recommendation(job_description, cv_skills, cv_years, cv_text, rule_score) -> dict:
    prompt = build_prompt(job_description, cv_skills, cv_years, cv_text, rule_score)
    return call_llm(prompt)
