import hashlib
import json
import time
import streamlit as st
from core.storage import list_jobs, list_cvs, save_match_result, list_results_by_job, get_match_result
from scoring.naive_bayes import build_job_model, predict_job_for_cv
from scoring.rule_based_scorer import calculate_rule_based_score
from scoring.llm_recommender import (
    get_llm_recommendation,
    answer_question_about_job,
    answer_question_about_cv,
)
from scoring.skill_gap import missing_skills, skill_gap_score

DELAY_BETWEEN_CALLS = 4

st.title("📊 Kết quả ứng viên")

jobs = list_jobs()
if not jobs:
    st.warning("Chưa có Job nào, vào trang Tạo Job trước.")
    st.stop()

job_options = {f"#{j['id']} - {j['title']}": j for j in jobs}
selected_label = st.selectbox("Chọn Job", list(job_options.keys()))
job = job_options[selected_label]
job_skills = json.loads(job["required_skills"] or "[]")


def _job_requirements_hash(job: dict) -> str:
    raw = json.dumps(
        {
            "required_skills": sorted(s.strip().lower() for s in job_skills),
            "required_experience_years": job["required_experience_years"],
        },
        sort_keys=True,
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _skill_badges(skills: list[str], highlight: set[str], color_hit: str, color_miss: str) -> str:
    """Render danh sách skill thành HTML badge xanh (có) / đỏ (thiếu)."""
    badges = []
    for s in skills:
        color = color_hit if s.strip().lower() in highlight else color_miss
        badges.append(
            f'<span style="background:{color};color:#fff;padding:2px 8px;'
            f'border-radius:12px;margin:2px;font-size:0.78em;display:inline-block">{s}</span>'
        )
    return " ".join(badges)


current_job_hash = _job_requirements_hash(job)

cvs = list_cvs()
job_model = build_job_model(list_jobs())
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

# ── RAG hỏi đáp ──────────────────────────────────────────────────────────────
st.divider()
with st.expander("🔎 Hỏi đáp về Job này (RAG)", expanded=False):
    st.caption(
        "Đặt câu hỏi tự do, hệ thống sẽ tự tìm Top-K CV liên quan nhất tới Job này "
        "rồi đưa cho LLM trả lời dựa trên ngữ cảnh đó."
    )
    rag_question = st.text_input(
        "Câu hỏi của bạn",
        placeholder="Ví dụ: Có CV nào có kinh nghiệm Docker không?",
        key="rag_question_job",
    )
    rag_top_k = st.slider("Top-K CV làm ngữ cảnh", 1, 10, 3, key="rag_top_k_job")

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
                    "Có thể chưa có CV nào được index."
                )
            st.write("**Trả lời:**")
            st.write(rag_result["answer"])
            if rag_result["retrieved"]:
                st.write("**Nguồn tham khảo:**")
                for i, r in enumerate(rag_result["retrieved"], start=1):
                    st.caption(f"[{i}] {r.get('name', 'Không rõ')} — score={r.get('score', 0):.3f}")


if not cvs:
    st.info("Chưa có CV nào. Vui lòng vào trang Upload CV để thêm ứng viên.")
    st.stop()

# ── Stale detection ───────────────────────────────────────────────────────────
results_by_cv = {r["cv_id"]: r for r in list_results_by_job(job["id"])}
stale_cv_ids = {
    cv_id
    for cv_id, r in results_by_cv.items()
    if r.get("job_requirements_hash") and r["job_requirements_hash"] != current_job_hash
}

if stale_cv_ids:
    st.warning(
        f"⚠️ Job đã được sửa sau khi {len(stale_cv_ids)} kết quả được tính. "
        "Các kết quả này đang hiển thị số liệu CŨ — chạy lại để cập nhật."
    )
    rerun_stale_only = st.button("🔁 Chỉ chạy lại CV bị ảnh hưởng bởi thay đổi JD")
else:
    rerun_stale_only = False

force_rerun = st.checkbox("Chạy lại từ đầu (kể cả CV đã có kết quả)", value=False)
run_button = st.button("🔄 Chạy match cho tất cả CV")


def _run_match(cv_list: list):
    """Chạy rule-based + LLM cho danh sách CV, lưu kết quả, hiện progress."""
    progress = st.progress(0, text="Chuẩn bị...")
    for i, cv in enumerate(cv_list):
        progress.progress(
            i / max(len(cv_list), 1),
            text=f"Đang xử lý {cv['candidate_name']} ({i+1}/{len(cv_list)})...",
        )
        cv_skills = json.loads(cv["skills"] or "[]")
        rule_score = calculate_rule_based_score(
            cv_skills, job_skills, cv["experience_years"], job["required_experience_years"]
        )
        result = get_llm_recommendation(
            job["description"], cv_skills, cv["experience_years"], cv["raw_text"], rule_score
        )
        job_prediction = predict_job_for_cv(cv_skills, cv["raw_text"], job_model)
        final_score = result["final_score"] if result.get("final_score") is not None else rule_score
        save_match_result(
            cv["id"], job["id"], rule_score,
            final_score, result.get("pros", ""),
            result.get("cons", ""), result.get("recommendation", ""),
            result.get("interview_questions", []),
            job_prediction=job_prediction,
            job_requirements_hash=current_job_hash,
        )
        if i < len(cv_list) - 1:
            time.sleep(DELAY_BETWEEN_CALLS)
    progress.progress(1.0, text="Hoàn tất!")


if run_button or rerun_stale_only:
    if rerun_stale_only:
        to_run = [cv for cv in cvs if cv["id"] in stale_cv_ids]
    else:
        to_run = cvs if force_rerun else [
            cv for cv in cvs if get_match_result(cv["id"], job["id"]) is None
        ]
    skipped = len(cvs) - len(to_run)
    if not to_run:
        st.info("Không có CV mới cần chạy. Tick 'Chạy lại từ đầu' nếu muốn tính lại.")
    else:
        if skipped > 0 and not force_rerun and not rerun_stale_only:
            st.caption(f"Bỏ qua {skipped} CV đã có kết quả.")
        _run_match(to_run)
        st.success("Đã chạy match xong!")
        st.rerun()

# ── Kết quả ──────────────────────────────────────────────────────────────────
st.divider()
results = list_results_by_job(job["id"])

if not results:
    st.info("Chưa có kết quả. Bấm 'Chạy match cho tất cả CV' để tạo kết quả.")
    st.stop()

st.subheader("Kết quả match")

# UX: sort kết quả
sort_by = st.selectbox(
    "Sắp xếp theo",
    ["% Match (cao → thấp)", "% Match (thấp → cao)", "Rule-based score", "Skill gap (%)"],
    index=0,
)
job_skills_lower = {s.strip().lower() for s in job_skills}

gap_scores_by_cv = {}
for r in results:
    cv_skills_r = json.loads(r["skills"] or "[]")
    gap_scores_by_cv[r["cv_id"]] = (cv_skills_r, skill_gap_score(cv_skills_r, job_skills))

if sort_by == "% Match (cao → thấp)":
    results = sorted(results, key=lambda r: r["final_score"] or 0, reverse=True)
elif sort_by == "% Match (thấp → cao)":
    results = sorted(results, key=lambda r: r["final_score"] or 0)
elif sort_by == "Rule-based score":
    results = sorted(results, key=lambda r: r["rule_based_score"] or 0, reverse=True)
elif sort_by == "Skill gap (%)":
    results = sorted(results, key=lambda r: gap_scores_by_cv[r["cv_id"]][1], reverse=True)

st.dataframe(
    [
        {
            "Ứng viên": r["candidate_name"],
            "% Match": r["final_score"],
            "Rule-based": r["rule_based_score"],
            "Skill gap (%)": gap_scores_by_cv[r["cv_id"]][1],
            "⚠️ JD đã đổi": "Có" if r["cv_id"] in stale_cv_ids else "",
        }
        for r in results
    ],
    use_container_width=True,
)

for r in results:
    cv_skills, gap_score = gap_scores_by_cv[r["cv_id"]]
    missing = missing_skills(cv_skills, job_skills)
    stale_note = " ⚠️ (kết quả cũ)" if r["cv_id"] in stale_cv_ids else ""

    with st.expander(
        f"{r['candidate_name']} — {r['final_score']}% (Rule: {r['rule_based_score']}%){stale_note}"
    ):
        if r["cv_id"] in stale_cv_ids:
            st.warning("Job đã được sửa — số liệu dưới đây có thể không còn đúng.")

        # UX: nút chạy lại per-ứng viên
        if st.button("🔁 Chạy lại cho ứng viên này", key=f"rerun_{r['cv_id']}"):
            cv_data = next((c for c in cvs if c["id"] == r["cv_id"]), None)
            if cv_data:
                with st.spinner(f"Đang chạy lại cho {r['candidate_name']}..."):
                    _run_match([cv_data])
                st.rerun()

        st.write("**Ưu điểm:**")
        st.write(r["pros"] or "Không có")
        st.write("**Nhược điểm:**")
        st.write(r["cons"] or "Không có")
        st.write("**Khuyến nghị:**")
        st.write(r["recommendation"] or "Không có")
        st.write("**Dự đoán Job phù hợp:**")
        st.write(r.get("job_prediction", "Không có"))

        col1, col2 = st.columns([2, 3])
        with col1:
            # UX: skill badge màu xanh (có trong JD) / xám (không yêu cầu)
            st.write("**Kỹ năng CV đã phát hiện:**")
            cv_skills_lower = {s.strip().lower() for s in cv_skills}
            matched_lower = cv_skills_lower & job_skills_lower
            st.markdown(
                _skill_badges(cv_skills, matched_lower, "#2e7d32", "#757575"),
                unsafe_allow_html=True,
            )
        with col2:
            st.write("**Skill gap:**")
            st.metric("Độ phủ kỹ năng", f"{gap_score}%")
            # UX: skill thiếu dạng badge đỏ
            st.write("**Kỹ năng thiếu so với Job:**")
            if missing:
                st.markdown(
                    _skill_badges(missing, set(), "#c62828", "#c62828"),
                    unsafe_allow_html=True,
                )
            else:
                st.success("Đáp ứng đủ kỹ năng yêu cầu ✓")

        questions = json.loads(r["interview_questions"]) if r["interview_questions"] else []
        if questions:
            st.write("**Câu hỏi phỏng vấn gợi ý:**")
            for q in questions:
                st.write(f"- {q}")
        else:
            st.caption("Không có câu hỏi gợi ý.")

        st.divider()
        st.subheader("🔎 Hỏi đáp về CV này")
        rag_question_cv = st.text_input(
            "Câu hỏi về CV",
            placeholder="Ví dụ: Ứng viên này phù hợp cho vị trí nào?",
            key=f"rag_question_cv_{r['cv_id']}",
        )
        rag_top_k_cv = st.slider(
            "Top-K Job làm ngữ cảnh", 1, 10, 3, key=f"rag_top_k_cv_{r['cv_id']}"
        )
        if st.button("Hỏi CV", key=f"rag_ask_cv_{r['cv_id']}"):
            if not rag_question_cv.strip():
                st.warning("Nhập câu hỏi trước khi bấm Hỏi.")
            else:
                with st.spinner("Đang tìm Job liên quan và hỏi LLM..."):
                    cv_text = r.get("raw_text", "")
                    cv_result = answer_question_about_cv(rag_question_cv, cv_text, top_k=rag_top_k_cv)
                if cv_result["retrieval_error"]:
                    st.warning(
                        f"Không truy xuất được dữ liệu RAG ({cv_result['retrieval_error']}). "
                        "Có thể chưa có Job nào được index."
                    )
                st.write("**Trả lời:**")
                st.write(cv_result["answer"])
                if cv_result["retrieved"]:
                    st.write("**Nguồn tham khảo:**")
                    for i, source in enumerate(cv_result["retrieved"], start=1):
                        st.caption(
                            f"[{i}] {source.get('name', 'Không rõ')} — score={source.get('score', 0):.3f}"
                        )