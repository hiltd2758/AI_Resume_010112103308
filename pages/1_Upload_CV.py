import streamlit as st
from parsing.pdf_extractor import extract_text
from parsing.skill_extractor import extract_skills
from parsing.experience_extractor import extract_experience_years
from core.storage import add_cv, list_cvs, delete_cv
from rag.indexer import index_cv, delete_cv_index

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
            try:
                index_cv(cv_id, candidate_name, text)
            except Exception as e:
                st.warning(f"Chưa tạo được embedding cho CV (sẽ không dùng được RAG search): {e}")
        st.success(f"Đã thêm CV #{cv_id} cho {candidate_name}")
        st.write("**Kỹ năng phát hiện:**", ", ".join(skills) if skills else "Không phát hiện")
        st.write("**Số năm kinh nghiệm phát hiện:**", years)

st.divider()
st.subheader("Danh sách CV đã upload")
cvs = list_cvs()
if cvs:
    for c in cvs:
        col1, col2, col3, col4, col5 = st.columns([1, 3, 4, 2, 2])
        col1.write(f"#{c['id']}")
        col2.write(c["candidate_name"])
        col3.write(c["skills"])
        col4.write(f"{c['experience_years']} năm")
        if col5.button("🗑️ Xoá", key=f"del_cv_{c['id']}"):
            delete_cv(c["id"])
            try:
                delete_cv_index(c["id"])
            except Exception as e:
                st.warning(f"Đã xoá CV nhưng chưa xoá được embedding trong RAG: {e}")
            st.rerun()
else:
    st.caption("Chưa có CV nào.")