"""Trang tạo Job Description (Role: Dũng)."""
import streamlit as st
from core.storage import add_job, list_jobs

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
        st.success(f"Đã tạo Job #{job_id}: {title}")

st.divider()
st.subheader("Danh sách Job")
jobs = list_jobs()
if jobs:
    st.dataframe(
        [{"ID": j["id"], "Vị trí": j["title"], "Skill yêu cầu": j["required_skills"], "KN yêu cầu": j["required_experience_years"]} for j in jobs],
        use_container_width=True,
    )
else:
    st.caption("Chưa có Job nào.")
