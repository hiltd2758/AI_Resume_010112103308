
import json
import time
import streamlit as st
from core.storage import list_jobs, list_cvs, save_match_result, list_results_by_job, get_match_result
from scoring.rule_based_scorer import calculate_rule_based_score
from scoring.llm_recommender import get_llm_recommendation, answer_question_about_job
from scoring.skill_gap import missing_skills, skill_gap_score

DELAY_BETWEEN_CALLS = 4  # giây, tránh dội request gây 429

st.title("📊 Kết quả ứng viên")
st.write("Trang này hiển thị kết quả match CV với Job và chi tiết recommendation.")

jobs = list_jobs()
if not jobs:
    st.warning("Chưa có Job nào, vào trang Tạo Job trước.")
    st.stop()

job_options = {f"#{j['id']} - {j['title']}": j for j in jobs}
selected_label = st.selectbox("Chọn Job", list(job_options.keys()))
job = job_options[selected_label]
job_skills = json.loads(job["required_skills"])

cvs = list_cvs()
job_summary_col1, job_summary_col2 = st.columns([2, 1])
with job_summary_col1:
    st.subheader("Job hiện tại")
    st.write(f"**{job['title']}**")
    st.write("**Yêu cầu kinh nghiệm:**", f"{job['required_experience_years']} năm")
    st.write("**Kỹ năng yêu cầu:**", ", ".join(job_skills) if job_skills else "Không có")
with job_summary_col2:
    st.subheader("Tổng quan dữ liệu")
    st.metric("Số CV đã upload", len(cvs))
    st.metric("Số kết quả hiện có", len(list_results_by_job(job["id"])))

st.caption("Skill gap hiển thị mức độ đáp ứng kỹ năng JD của từng CV.")

# ============================================================================
# RAG: Hỏi đáp về Job này (retrieval Top-K CV liên quan + LLM trả lời)
# ============================================================================
st.divider()
with st.expander("🔎 Hỏi đáp về Job này (RAG)", expanded=False):
    st.caption(
        "Đặt câu hỏi tự do, hệ thống sẽ tự tìm Top-K CV liên quan nhất tới Job này "
        "(qua semantic search) rồi đưa cho LLM trả lời dựa trên ngữ cảnh đó."
    )
    rag_question = st.text_input(
        "Câu hỏi của bạn",
        placeholder="Ví dụ: Có CV nào có kinh nghiệm Docker không?",
        key="rag_question_job",
    )
    rag_top_k = st.slider("Số CV liên quan lấy làm ngữ cảnh (Top-K)", 1, 10, 3, key="rag_top_k_job")

    if st.button("Hỏi", key="rag_ask_job"):
        if not rag_question.strip():
            st.warning("Nhập câu hỏi trước khi bấm Hỏi.")
        else:
            with st.spinner("Đang tìm dữ liệu liên quan và hỏi LLM..."):
                job_text = f"{job['title']}\n{job['description'] or ''}"
                rag_result = answer_question_about_job(rag_question, job_text, top_k=rag_top_k)

            if rag_result["retrieval_error"]:
                st.warning(
                    f"Không truy xuất được dữ liệu RAG ({rag_result['retrieval_error']}). "
                    "Có thể model embedding chưa tải được hoặc chưa có CV nào được index."
                )

            st.write("**Trả lời:**")
            st.write(rag_result["answer"])

            if rag_result["retrieved"]:
                st.write("**Nguồn tham khảo (Top-K CV liên quan):**")
                for i, r in enumerate(rag_result["retrieved"], start=1):
                    st.caption(f"[{i}] {r.get('name', 'Không rõ')} — score={r.get('score', 0):.3f}")

if not cvs:
    st.info("Chưa có CV nào. Vui lòng vào trang Upload CV để thêm ứng viên.")
    st.stop()

force_rerun = st.checkbox("Chạy lại từ đầu (kể cả CV đã có kết quả)", value=False)
run_button = st.button("🔄 Chạy match cho tất cả CV")

if run_button:
    to_run = cvs if force_rerun else [
        cv for cv in cvs if get_match_result(cv["id"], job["id"]) is None
    ]
    skipped = len(cvs) - len(to_run)
    if not to_run:
        st.info("Không có CV mới cần chạy. Tick ô 'Chạy lại từ đầu' nếu muốn tính lại cho tất cả CV.")
    else:
        if skipped > 0 and not force_rerun:
            st.caption(f"Bỏ qua {skipped} CV đã có kết quả để tránh gọi API trùng. Tick ô trên nếu muốn chạy lại hết.")

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
                time.sleep(DELAY_BETWEEN_CALLS)
        st.success("Đã chạy match xong!")

st.divider()
results = list_results_by_job(job["id"])
if results:
    st.subheader("Kết quả match")
    st.dataframe(
        [
            {
                "Ứng viên": r["candidate_name"],
                "% Match": r["final_score"],
                "Rule-based": r["rule_based_score"],
                "Skill gap (%)": skill_gap_score(json.loads(r["skills"]), job_skills),
            }
            for r in results
        ],
        use_container_width=True,
    )

    for r in results:
        cv_skills = json.loads(r["skills"])
        missing = missing_skills(cv_skills, job_skills)
        gap_score = skill_gap_score(cv_skills, job_skills)
        with st.expander(f"{r['candidate_name']} — {r['final_score']}% (Rule: {r['rule_based_score']}%)"):
            st.write("**Ưu điểm:**")
            st.write(r["pros"] or "Không có")
            st.write("**Nhược điểm:**")
            st.write(r["cons"] or "Không có")
            st.write("**Khuyến nghị:**")
            st.write(r["recommendation"] or "Không có")

            col1, col2 = st.columns([2, 3])
            with col1:
                st.write("**Kỹ năng CV đã phát hiện:**")
                st.write(", ".join(cv_skills) if cv_skills else "Không có")
            with col2:
                st.write("**Skill gap:**")
                st.metric("Độ phủ kỹ năng", f"{gap_score}%")

            st.write("**Kỹ năng thiếu so với Job:**")
            if missing:
                st.write(", ".join(missing))
            else:
                st.write("Không có")

            questions = json.loads(r["interview_questions"]) if r["interview_questions"] else []
            if questions:
                st.write("**Câu hỏi phỏng vấn gợi ý:**")
                for q in questions:
                    st.write(f"- {q}")
            else:
                st.write("Không có câu hỏi gợi ý.")
else:
    st.info("Chưa có kết quả cho Job này. Bấm 'Chạy match cho tất cả CV' để tạo kết quả.")