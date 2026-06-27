import json
import streamlit as st
from parsing.pdf_extractor import extract_text
from parsing.skill_extractor import extract_skills
from parsing.experience_extractor import extract_experience_years
from core.storage import add_cv, list_cvs, delete_cv, list_jobs
from rag.indexer import index_cv, delete_cv_index


def _skill_badges(skills: list[str], color: str) -> str:
    badges = [
        f'<span style="background:{color};color:#fff;padding:2px 8px;'
        f'border-radius:12px;margin:2px;font-size:0.78em;display:inline-block">{s}</span>'
        for s in skills
    ]
    return " ".join(badges)


st.title("📤 Upload CV")

with st.form("upload_cv_form"):
    candidate_name = st.text_input("Tên ứng viên")
    uploaded_file = st.file_uploader("Chọn file CV (.pdf hoặc .docx)", type=["pdf", "docx"])
    submitted = st.form_submit_button("Upload & Phân tích")

if submitted:
    if not candidate_name or not uploaded_file:
        st.error("Nhập tên ứng viên và chọn file CV.")
    else:
        # UX: progress bar từng bước thay vì spinner chung
        progress = st.progress(0, text="Đang đọc file CV...")
        text, warning = extract_text(uploaded_file)
        if warning:
            st.warning(warning)
        if not text.strip():
            st.error("Không đọc được nội dung CV. Vui lòng kiểm tra lại file.")
            st.stop()

        progress.progress(30, text="Đang trích xuất kỹ năng...")
        all_job_skills = []
        try:
            for job in list_jobs():
                raw = job.get("required_skills") or "[]"
                skills_list = json.loads(raw) if isinstance(raw, str) else (raw or [])
                all_job_skills.extend(skills_list)
        except Exception:
            pass
        skills = extract_skills(text, extra_skills=all_job_skills)

        progress.progress(60, text="Đang phân tích kinh nghiệm...")
        years, snippets = extract_experience_years(text)

        progress.progress(80, text="Đang lưu & tạo embedding...")
        existing_names = [c["candidate_name"] for c in list_cvs()]
        if candidate_name in existing_names:
            st.warning(f"Đã có ứng viên tên '{candidate_name}'. Sẽ tạo bản mới (không ghi đè).")

        cv_id = add_cv(candidate_name, text, skills, years)
        try:
            index_cv(cv_id, candidate_name, text)
        except Exception as e:
            st.warning(f"Chưa tạo được embedding cho CV (sẽ không dùng được RAG search): {e}")

        progress.progress(100, text="Hoàn tất!")

        st.success(f"✅ Đã thêm CV #{cv_id} cho **{candidate_name}**")

        col1, col2 = st.columns(2)
        with col1:
            st.write("**Kỹ năng phát hiện:**")
            if skills:
                st.markdown(_skill_badges(skills, "#2e7d32"), unsafe_allow_html=True)
            else:
                st.caption("Không phát hiện kỹ năng nào.")
        with col2:
            st.metric("Số năm kinh nghiệm", years)

        if snippets:
            with st.expander("📌 Đoạn text dùng để tính kinh nghiệm (kiểm tra lại nếu cần)"):
                for s in snippets:
                    st.caption(s)

# ── Danh sách CV ─────────────────────────────────────────────────────────────
st.divider()
st.subheader("Danh sách CV đã upload")
cvs = list_cvs()
if not cvs:
    st.caption("Chưa có CV nào.")
else:
    # UX: search/filter theo tên
    search = st.text_input("🔍 Tìm theo tên ứng viên", placeholder="Nhập tên để lọc...")
    filtered = [c for c in cvs if search.lower() in c["candidate_name"].lower()] if search else cvs
    st.caption(f"Hiển thị {len(filtered)}/{len(cvs)} ứng viên")

    for c in filtered:
        col1, col2, col3, col4, col5 = st.columns([1, 3, 4, 2, 2])
        col1.write(f"#{c['id']}")
        col2.write(c["candidate_name"])

        # UX: hiển thị skill dạng badge thay vì JSON string thô
        with col3:
            try:
                skill_list = json.loads(c["skills"] or "[]")
                if skill_list:
                    st.markdown(_skill_badges(skill_list, "#1565c0"), unsafe_allow_html=True)
                else:
                    st.caption("Không có skill")
            except Exception:
                st.write(c["skills"])

        col4.write(f"{c['experience_years']} năm")
        if col5.button("🗑️ Xoá", key=f"del_cv_{c['id']}"):
            delete_cv(c["id"])
            try:
                delete_cv_index(c["id"])
            except Exception as e:
                st.warning(f"Đã xoá CV nhưng chưa xoá được embedding trong RAG: {e}")
            st.rerun()