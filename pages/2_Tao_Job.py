import json
import streamlit as st
from core.config import SKILL_KEYWORDS
from core.storage import add_job, list_jobs, delete_job
from rag.indexer import index_job, delete_job_index


def _skill_badges(skills: list[str], color: str) -> str:
    badges = [
        f'<span style="background:{color};color:#fff;padding:2px 8px;'
        f'border-radius:12px;margin:2px;font-size:0.78em;display:inline-block">{s}</span>'
        for s in skills
    ]
    return " ".join(badges)


st.title("💼 Tạo Job")

with st.form("create_job_form"):
    title = st.text_input("Tên vị trí")
    description = st.text_area("Mô tả công việc")

    # UX: multiselect từ SKILL_KEYWORDS thay text_input tự do
    # -> tránh nhập sai chính tả, đồng bộ casing với extractor
    selected_skills = st.multiselect(
        "Kỹ năng yêu cầu",
        options=SKILL_KEYWORDS,
        placeholder="Chọn kỹ năng từ danh sách...",
    )
    # UX: vẫn cho nhập thêm skill ngoài whitelist (tự do)
    extra_skills_raw = st.text_input(
        "Kỹ năng khác (ngoài danh sách, cách nhau bởi dấu phẩy)",
        placeholder="Kubernetes, Golang, ...",
    )
    required_experience_years = st.number_input(
        "Số năm kinh nghiệm yêu cầu", min_value=0, max_value=20, value=1
    )
    submitted = st.form_submit_button("Tạo Job")

if submitted:
    if not title:
        st.error("Nhập tên vị trí.")
    else:
        # Gộp skill từ multiselect + skill tự do nhập thêm
        # Chuẩn hoá lowercase+strip skill tự do để đồng bộ với extractor
        extra_skills = [s.strip() for s in extra_skills_raw.split(",") if s.strip()]
        skills_list = selected_skills + extra_skills

        if not skills_list:
            st.warning("Chưa chọn kỹ năng nào — kết quả match skill sẽ không chính xác.")

        job_id = add_job(title, description, skills_list, required_experience_years)
        try:
            index_job(job_id, title, description)
        except Exception as e:
            st.warning(f"Chưa tạo được embedding cho Job (sẽ không dùng được RAG search): {e}")

        st.success(f"✅ Đã tạo Job #{job_id}: **{title}**")
        if skills_list:
            st.markdown(_skill_badges(skills_list, "#1565c0"), unsafe_allow_html=True)

# ── Danh sách Job ─────────────────────────────────────────────────────────────
st.divider()
st.subheader("Danh sách Job")
jobs = list_jobs()
if not jobs:
    st.caption("Chưa có Job nào.")
else:
    # UX: search/filter theo tên vị trí
    search = st.text_input("🔍 Tìm theo tên vị trí", placeholder="Nhập tên để lọc...")
    filtered = [j for j in jobs if search.lower() in j["title"].lower()] if search else jobs
    st.caption(f"Hiển thị {len(filtered)}/{len(jobs)} job")

    for j in filtered:
        col1, col2, col3, col4, col5 = st.columns([1, 3, 4, 2, 2])
        col1.write(f"#{j['id']}")
        col2.write(j["title"])

        # UX: skill badge thay JSON string thô
        with col3:
            try:
                skill_list = json.loads(j["required_skills"] or "[]")
                if skill_list:
                    st.markdown(_skill_badges(skill_list, "#6a1b9a"), unsafe_allow_html=True)
                else:
                    st.caption("Không có skill")
            except Exception:
                st.write(j["required_skills"])

        col4.write(f"{j['required_experience_years']} năm")
        if col5.button("🗑️ Xoá", key=f"del_job_{j['id']}"):
            delete_job(j["id"])
            try:
                delete_job_index(j["id"])
            except Exception as e:
                st.warning(f"Đã xoá Job nhưng chưa xoá được embedding trong RAG: {e}")
            st.rerun()