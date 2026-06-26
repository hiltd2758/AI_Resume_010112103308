import pdfplumber
from docx import Document

# Ngưỡng tối thiểu để coi là extract được nội dung có nghĩa
_MIN_TEXT_LENGTH = 50


def extract_text_from_pdf(file_obj) -> str:
    text = ""
    with pdfplumber.open(file_obj) as pdf:
        for page in pdf.pages:
            text += (page.extract_text() or "") + "\n"
    return text


def extract_text_from_docx(file_obj) -> str:
    doc = Document(file_obj)
    return "\n".join(p.text for p in doc.paragraphs)


def extract_text(uploaded_file) -> tuple[str, str | None]:
    """
    Trích xuất text từ file PDF hoặc DOCX.

    Returns:
        (text, warning):
            - text: nội dung trích xuất (có thể rỗng nếu lỗi/scan ảnh)
            - warning: chuỗi cảnh báo nếu có vấn đề, None nếu ổn
    """
    name = uploaded_file.name.lower()

    try:
        if name.endswith(".pdf"):
            text = extract_text_from_pdf(uploaded_file)
        elif name.endswith(".docx"):
            text = extract_text_from_docx(uploaded_file)
        else:
            raise ValueError("Định dạng file không hỗ trợ, chỉ nhận .pdf hoặc .docx")
    except ValueError:
        raise
    except Exception as e:
        # File corrupt hoặc lỗi đọc — trả về text rỗng kèm cảnh báo
        # thay vì crash toàn trang Streamlit
        return "", f"Không thể đọc file '{uploaded_file.name}': {e}"

    # Cảnh báo nếu text quá ngắn — thường do PDF scan ảnh không có text layer
    if len(text.strip()) < _MIN_TEXT_LENGTH:
        warning = (
            f"Nội dung trích xuất từ '{uploaded_file.name}' quá ngắn "
            f"({len(text.strip())} ký tự). "
            "Có thể CV là file scan ảnh — hệ thống sẽ không đọc được skill/kinh nghiệm chính xác."
        )
        return text, warning

    return text, None