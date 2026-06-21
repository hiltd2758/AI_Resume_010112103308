"""Trang Upload CV (Role: Dũng, gọi service từ Hải)."""
import streamlit as st
from parsing.pdf_extractor import extract_text
from parsing.skill_extractor import extract_skills
from parsing.experience_extractor import extract_experience_years
from core.storage import add_cv, list_cvs

st.title("📤 Upload CV")

with st.form("upload_cv_form"):
    candidate_name = st.text_input("Tên ứng viên")
    uploaded_file = st.file_uploader("Chọn file CV (.pdf hoặc .docx)", type=["pdf", "docx"])
    submitted = st.form_submit_button("Upload & Phân tích")

if submitted:
    if not candidate_name or not uploaded_file:
        st.error("Nhập tên ứng viên và chọn file CV.")
    else:
        with st.spinner("Đang đọc & phân tích CV..."):
            text = extract_text(uploaded_file)
            skills = extract_skills(text)
            years = extract_experience_years(text)
            cv_id = add_cv(candidate_name, text, skills, years)
        st.success(f"Đã thêm CV #{cv_id} cho {candidate_name}")
        st.write("**Kỹ năng phát hiện:**", ", ".join(skills) if skills else "Không phát hiện")
        st.write("**Số năm kinh nghiệm phát hiện:**", years)

st.divider()
st.subheader("Danh sách CV đã upload")
cvs = list_cvs()
if cvs:
    st.dataframe(
        [{"ID": c["id"], "Tên": c["candidate_name"], "Skills": c["skills"], "KN (năm)": c["experience_years"]} for c in cvs],
        use_container_width=True,
    )
else:
    st.caption("Chưa có CV nào.")
