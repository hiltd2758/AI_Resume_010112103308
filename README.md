# CV-JD Matcher (Streamlit)

App Streamlit chấm % match giữa CV và Job Description, kết hợp Rule-based (skill/kinh nghiệm) + AI (Groq - Llama 3.3) để đánh giá sâu và đưa khuyến nghị phỏng vấn.

## Cấu trúc
```
app.py                 -> Trang Home
pages/
  1_Upload_CV.py        -> Upload CV, xem CV đã parse
  2_Tao_Job.py           -> Tạo/xem Job Description
  3_Ket_qua_ung_vien.py  -> Bảng % match + chi tiết recommend
core/
  config.py              -> Cấu hình, danh sách skill keywords
  storage.py              -> Lưu trữ Job/CV/MatchResult (SQLite)
parsing/                  -> Đọc CV (PDF/Word), trích skill, kinh nghiệm
scoring/                  -> Rule-based scorer + gọi Groq (Llama 3.3) recommend
data/                      -> CV/Job mẫu để test
```

## Chạy thử

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env   # điền GROQ_API_KEY
streamlit run app.py
```

**Mac/Linux:**
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # điền GROQ_API_KEY
streamlit run app.py
```

## Luồng xử lý
1. Upload CV (trang Upload_CV) -> parsing đọc text -> trích skill (rule-based) + số năm KN (regex)
2. Tạo Job (trang Tao_Job) -> lưu skill yêu cầu + kinh nghiệm yêu cầu
3. Trang Kết_qua_ung_vien -> chạy `rule_based_scorer` (skill 50% + kinh nghiệm 50%) -> gọi `llm_recommender` (Groq) tinh điểm + nhận xét + câu hỏi PV -> hiển thị bảng, sort theo % match

Phân công chi tiết theo tuần: `docs/jira_tasks_by_week.csv`
