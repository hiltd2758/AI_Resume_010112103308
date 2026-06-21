"""Trang tạo Job Description (Role: Dũng)."""
import streamlit as st
from core.storage import add_job, list_jobs, delete_job
from rag.indexer import index_job, delete_job_index

st.title("💼 Tạo Job")

with st.form("create_job_form"):
    title = st.text_input("Tên vị trí")
    description = st.text_area("Mô tả công việc")
    required_skills = st.text_input("Kỹ năng yêu cầu (cách nhau bởi dấu phẩy)", placeholder="Python, SQL, React")
    required_experience_years = st.number_input("Số năm kinh nghiệm yêu cầu", min_value=0, max_value=20, value=1)
    submitted = st.form_submit_button("Tạo Job")

if submitted:
    if not title:
        st.error("Nhập tên vị trí.")
    else:
        skills_list = [s.strip() for s in required_skills.split(",") if s.strip()]
        job_id = add_job(title, description, skills_list, required_experience_years)
        try:
            index_job(job_id, title, description)
        except Exception as e:
            st.warning(f"Chưa tạo được embedding cho Job (sẽ không dùng được RAG search): {e}")
        st.success(f"Đã tạo Job #{job_id}: {title}")

st.divider()
st.subheader("Danh sách Job")
jobs = list_jobs()
if jobs:
    for j in jobs:
        col1, col2, col3, col4, col5 = st.columns([1, 3, 4, 2, 2])
        col1.write(f"#{j['id']}")
        col2.write(j["title"])
        col3.write(j["required_skills"])
        col4.write(f"{j['required_experience_years']} năm")
        if col5.button("🗑️ Xoá", key=f"del_job_{j['id']}"):
            delete_job(j["id"])
            try:
                delete_job_index(j["id"])
            except Exception as e:
                st.warning(f"Đã xoá Job nhưng chưa xoá được embedding trong RAG: {e}")
            st.rerun()
else:
    st.caption("Chưa có Job nào.")