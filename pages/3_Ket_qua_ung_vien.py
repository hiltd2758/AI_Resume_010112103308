import json
import time
import streamlit as st
from core.storage import list_jobs, list_cvs, save_match_result, list_results_by_job, get_match_result
from scoring.rule_based_scorer import calculate_rule_based_score
from scoring.llm_recommender import get_llm_recommendation

DELAY_BETWEEN_CALLS = 4  # giây, tránh dội request gây 429

st.title("📊 Kết quả ứng viên")

jobs = list_jobs()
if not jobs:
    st.warning("Chưa có Job nào, vào trang Tạo Job trước.")
    st.stop()

job_options = {f"#{j['id']} - {j['title']}": j for j in jobs}
selected_label = st.selectbox("Chọn Job", list(job_options.keys()))
job = job_options[selected_label]
job_skills = json.loads(job["required_skills"])

force_rerun = st.checkbox("Chạy lại từ đầu (kể cả CV đã có kết quả)", value=False)

if st.button("🔄 Chạy match cho tất cả CV"):
    cvs = list_cvs()
    to_run = cvs if force_rerun else [
        cv for cv in cvs if get_match_result(cv["id"], job["id"]) is None
    ]
    skipped = len(cvs) - len(to_run)
    if skipped:
        st.caption(f"Bỏ qua {skipped} CV đã có kết quả (tránh gọi API trùng). Tick ô trên nếu muốn chạy lại hết.")

    progress = st.progress(0, text="Đang tính điểm...")
    for i, cv in enumerate(to_run):
        cv_skills = json.loads(cv["skills"])
        rule_score = calculate_rule_based_score(
            cv_skills, job_skills, cv["experience_years"], job["required_experience_years"]
        )
        result = get_llm_recommendation(
            job["description"], cv_skills, cv["experience_years"], cv["raw_text"], rule_score
        )
        save_match_result(
            cv["id"], job["id"], rule_score,
            result.get("final_score") or rule_score, result.get("pros", ""),
            result.get("cons", ""), result.get("recommendation", ""),
            result.get("interview_questions", []),
        )
        progress.progress((i + 1) / max(len(to_run), 1), text=f"Đã xong {i+1}/{len(to_run)}")
        if i < len(to_run) - 1:
            time.sleep(DELAY_BETWEEN_CALLS)  # giãn cách request để tránh 429
    st.success("Đã chạy match xong!")

st.divider()
results = list_results_by_job(job["id"])
if results:
    st.dataframe(
        [{"Ứng viên": r["candidate_name"], "% Match": r["final_score"], "Rule-based": r["rule_based_score"]} for r in results],
        use_container_width=True,
    )
    for r in results:
        with st.expander(f"{r['candidate_name']} - {r['final_score']}%"):
            st.write("**Ưu điểm:**", r["pros"])
            st.write("**Nhược điểm:**", r["cons"])
            st.write("**Khuyến nghị:**", r["recommendation"])
            questions = json.loads(r["interview_questions"]) if r["interview_questions"] else []
            if questions:
                st.write("**Câu hỏi phỏng vấn gợi ý:**")
                for q in questions:
                    st.write("-", q)
else:
    st.caption("Chưa có kết quả, bấm 'Chạy match' ở trên.")
