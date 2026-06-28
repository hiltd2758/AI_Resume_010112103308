"""Gọi Groq API để tinh chỉnh điểm + nhận xét + gợi ý câu hỏi PV (Role: Bá)."""
import json
import re
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

# Vấn đề 2 (fix): regex strip code fence đúng cách, thay cho .strip("```json")
_CODE_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE)


def build_prompt(job_description, cv_skills, cv_years, cv_text, rule_score) -> str:
    skills_text = (
        ", ".join(cv_skills) if isinstance(cv_skills, (list, tuple)) else str(cv_skills)
    )
    return PROMPT_TEMPLATE.format(
        job_description=job_description,
        cv_skills=skills_text,
        cv_years=cv_years,
        cv_text=cv_text[:1500],  # tránh prompt quá dài, tốn token
        rule_score=rule_score,
    )


def _strip_code_fence(text: str) -> str:
    """Xoá markdown code fence (```json ... ```) đúng cách theo prefix/suffix,
    KHÔNG dùng .strip(chars) vì nó xoá theo từng ký tự đơn lẻ -> dễ cắt nhầm JSON thật."""
    return _CODE_FENCE_RE.sub("", text.strip()).strip()


def _clamp_score(value):
    """Vấn đề 3 (fix): clamp final_score về [0, 100]. Trả None nếu không parse được số."""
    if value is None:
        return None
    try:
        score = float(value)
    except (TypeError, ValueError):
        return None
    return max(0, min(100, score))


def _extract_json_text(text: str) -> str:
    """Tách JSON object từ output LLM, loại bỏ code fence và dòng thừa."""
    if not text:
        return text
    text = _CODE_FENCE_RE.sub("", text.strip()).strip()
    try:
        json.loads(text)
        return text
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return text[start : end + 1]
        return text


def _normalize_llm_result(result: dict, rule_score: float) -> dict:
    """Chuẩn hoá output đầu ra LLM, fallback về rule_score khi cần."""
    if result is None:
        result = {}

    final_score = _clamp_score(result.get("final_score"))
    if final_score is None:
        final_score = rule_score
        if not result.get("recommendation"):
            result["recommendation"] = "Sử dụng điểm rule-based do LLM chưa trả về score hợp lệ."
    result["final_score"] = final_score

    interview_questions = result.get("interview_questions")
    if interview_questions is None:
        result["interview_questions"] = []
    elif isinstance(interview_questions, str):
        result["interview_questions"] = [interview_questions]
    elif isinstance(interview_questions, list):
        result["interview_questions"] = [str(q) for q in interview_questions if q is not None]
    else:
        result["interview_questions"] = [str(interview_questions)]

    for key in ["pros", "cons", "recommendation"]:
        value = result.get(key)
        result[key] = "" if value is None else str(value)

    return result


def call_llm(prompt: str) -> dict:
    if not GROQ_API_KEY:
        return {
            "final_score": None,
            "pros": "",
            "cons": "",
            "recommendation": "Chưa cấu hình GROQ_API_KEY trong .env",
            "interview_questions": [],
        }

    from groq import Groq
    client = Groq(api_key=GROQ_API_KEY)

    max_retries = 2
    last_error = None

    for attempt in range(max_retries + 1):
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.3,
            )
            text = completion.choices[0].message.content.strip()
            text = _extract_json_text(text)

            try:
                result = json.loads(text)
            except json.JSONDecodeError as parse_err:
                # Vấn đề 4 (fix): retry cả lỗi parse JSON, không chỉ rate-limit
                last_error = parse_err
                if attempt < max_retries:
                    time.sleep(2)
                    continue
                return {
                    "final_score": None,
                    "pros": "",
                    "cons": "",
                    "recommendation": f"Không gọi được Groq API (JSONDecodeError sau {max_retries + 1} lần thử), dùng tạm điểm rule-based.",
                    "interview_questions": [],
                }

            # Vấn đề 3 (fix): clamp final_score về [0, 100] trước khi trả về
            result["final_score"] = _clamp_score(result.get("final_score"))
            return result

        except Exception as e:
            is_rate_limit = "429" in str(e) or "rate_limit" in str(e).lower()
            last_error = e
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

    # Không nên tới đây, nhưng đảm bảo luôn có return
    return {
        "final_score": None,
        "pros": "",
        "cons": "",
        "recommendation": f"Không gọi được Groq API ({type(last_error).__name__ if last_error else 'Unknown'}), dùng tạm điểm rule-based.",
        "interview_questions": [],
    }


def get_llm_recommendation(job_description, cv_skills, cv_years, cv_text, rule_score) -> dict:
    prompt = build_prompt(job_description, cv_skills, cv_years, cv_text, rule_score)
    result = call_llm(prompt)
    return _normalize_llm_result(result, rule_score)


# ============================================================================
# RAG: Chức năng hỏi đáp CV/JD (Tích hợp retrieval Top-K vào luồng LLM)
# ============================================================================

RAG_PROMPT_TEMPLATE = """Bạn là trợ lý tuyển dụng AI. Dưới đây là các đoạn dữ liệu liên quan nhất
truy xuất được từ hệ thống (RAG) để hỗ trợ trả lời câu hỏi của Hiring Manager.

--- Ngữ cảnh liên quan (Top-{top_k}, độ liên quan giảm dần) ---
{context}
--- Hết ngữ cảnh ---

Câu hỏi: {question}

Hãy trả lời ngắn gọn, dựa trên ngữ cảnh trên. Nếu ngữ cảnh không đủ thông tin
để trả lời, hãy nói rõ là không đủ thông tin, không tự suy diễn thêm.
"""

# Vấn đề 5 (fix): giới hạn tổng độ dài context, tương tự cv_text[:1500] ở build_prompt
MAX_RAG_CONTEXT_CHARS = 3000


def build_rag_context(results: list) -> str:
    """Định dạng kết quả retrieval (Top-K) thành đoạn text để đưa vào prompt.
    Giới hạn tổng độ dài context để tránh vượt token limit khi top_k lớn."""
    if not results:
        return "(Không tìm được dữ liệu liên quan)"

    parts = []
    total_len = 0
    for i, r in enumerate(results, start=1):
        snippet = (r.get("text") or "")[:600]
        score = r.get("score", 0)
        part = f"[{i}] {r.get('name', 'Không rõ')} (score={score:.3f})\n{snippet}"

        if total_len + len(part) > MAX_RAG_CONTEXT_CHARS:
            remaining = MAX_RAG_CONTEXT_CHARS - total_len
            if remaining > 0:
                parts.append(part[:remaining] + "...(đã cắt do vượt giới hạn context)")
            break

        parts.append(part)
        total_len += len(part)

    return "\n\n".join(parts)


def _call_llm_text(prompt: str) -> str:
    """Gọi Groq trả về plain text (khác call_llm() vì câu hỏi không cần ép JSON format)."""
    if not GROQ_API_KEY:
        return "Chưa cấu hình GROQ_API_KEY trong .env"

    from groq import Groq
    client = Groq(api_key=GROQ_API_KEY)
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Không gọi được Groq API: {type(e).__name__}: {e}"


def answer_question_about_job(question: str, job_text: str, top_k: int = 3) -> dict:
    """
    Trả lời câu hỏi liên quan tới 1 Job, dùng RAG:
    retrieval Top-K CV liên quan nhất tới job_text -> đưa vào prompt -> hỏi LLM.
    """
    from rag.indexer import search_cvs_for_job

    retrieval_error = None
    try:
        retrieved = search_cvs_for_job(job_text, top_k=top_k)
    except Exception as e:
        retrieved = []
        retrieval_error = f"{type(e).__name__}: {e}"

    context = build_rag_context(retrieved)
    prompt = RAG_PROMPT_TEMPLATE.format(top_k=top_k, context=context, question=question)
    answer = _call_llm_text(prompt)

    return {"answer": answer, "retrieved": retrieved, "retrieval_error": retrieval_error}


def answer_question_about_cv(question: str, cv_text: str, top_k: int = 3) -> dict:
    """
    Trả lời câu hỏi liên quan tới 1 CV, dùng RAG:
    retrieval Top-K Job liên quan nhất tới cv_text -> đưa vào prompt -> hỏi LLM.
    """
    from rag.indexer import search_jobs_for_cv

    retrieval_error = None
    try:
        retrieved = search_jobs_for_cv(cv_text, top_k=top_k)
    except Exception as e:
        retrieved = []
        retrieval_error = f"{type(e).__name__}: {e}"

    context = build_rag_context(retrieved)
    prompt = RAG_PROMPT_TEMPLATE.format(top_k=top_k, context=context, question=question)
    answer = _call_llm_text(prompt)

    return {"answer": answer, "retrieved": retrieved, "retrieval_error": retrieval_error}