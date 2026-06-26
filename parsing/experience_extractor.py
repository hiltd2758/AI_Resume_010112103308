import re

# Pattern yêu cầu "kinh nghiệm/experience" phải xuất hiện gần số năm
# (trong vòng ~60 ký tự trước hoặc sau) — không còn optional nữa.
# Hai pattern: tiếng Anh và tiếng Việt, cả 2 đều bắt buộc từ khoá liên quan.
_PATTERNS = [
    # "X years of experience" / "X+ years experience" / "X years' experience"
    r"(\d+)\s*\+?\s*years?'?\s*(?:of\s+)?experience",
    # "kinh nghiệm X năm" hoặc "X năm kinh nghiệm" (thứ tự linh hoạt)
    r"kinh\s+nghi[eệ]m\s+(\d+)\s*\+?\s*n[aă]m",
    r"(\d+)\s*\+?\s*n[aă]m\s+kinh\s+nghi[eệ]m",
]

# Số năm kinh nghiệm hợp lý tối đa — giá trị lớn hơn thường là
# nhầm (năm tháng, mã số, v.v.) nên bị loại bỏ.
_MAX_REASONABLE_YEARS = 40


def extract_experience_years(text: str) -> tuple[int, list[str]]:
    """
    Trích xuất số năm kinh nghiệm từ văn bản CV.

    Returns:
        (years, matched_snippets):
            - years: số năm lớn nhất tìm được trong khoảng [0, 40], 0 nếu không tìm thấy
            - matched_snippets: danh sách câu/đoạn gốc khớp được (để caller log/hiển thị
              cho người dùng kiểm tra lại nếu cần)
    """
    years_found = []
    snippets = []

    for pattern in _PATTERNS:
        for m in re.finditer(pattern, text, flags=re.IGNORECASE):
            value = int(m.group(1))
            if value > _MAX_REASONABLE_YEARS:
                continue  # bỏ qua giá trị vô lý (năm tháng, mã số...)

            years_found.append(value)

            # Lấy đoạn ngữ cảnh xung quanh match để caller có thể log/hiển thị
            start = max(0, m.start() - 30)
            end = min(len(text), m.end() + 30)
            snippet = text[start:end].replace("\n", " ").strip()
            snippets.append(f"…{snippet}…")

    years = max(years_found) if years_found else 0
    return years, snippets