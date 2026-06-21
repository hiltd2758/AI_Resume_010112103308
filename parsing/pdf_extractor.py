import pdfplumber
from docx import Document


def extract_text_from_pdf(file_obj) -> str:
    text = ""
    with pdfplumber.open(file_obj) as pdf:
        for page in pdf.pages:
            text += (page.extract_text() or "") + "\n"
    return text


def extract_text_from_docx(file_obj) -> str:
    doc = Document(file_obj)
    return "\n".join(p.text for p in doc.paragraphs)


def extract_text(uploaded_file) -> str:
    """uploaded_file: đối tượng từ st.file_uploader (Streamlit)."""
    name = uploaded_file.name.lower()
    if name.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)
    elif name.endswith(".docx"):
        return extract_text_from_docx(uploaded_file)
    raise ValueError("Định dạng file không hỗ trợ, chỉ nhận .pdf hoặc .docx")
