# Kiến trúc & Phân vai trò (Streamlit)

## Roles
| Người | Phụ trách |
|---|---|
| Hil (Lead) | Storage layer (SQLite), CRUD Job/CV, ghép luồng match |
| Hải | Đọc CV (PDF/Word), rule-based skill extractor, regex kinh nghiệm |
| Bá | Thuật toán % match, tích hợp Gemini API, prompt + recommend |
| Dũng | Streamlit pages: Upload CV, Tạo Job, Kết quả ứng viên |
| Thương | Data mẫu, test thủ công, hỗ trợ debug, báo cáo |

## Luồng xử lý
1. Tạo Job (trang 2) -> lưu skill/kinh nghiệm yêu cầu
2. Upload CV (trang 1) -> parsing (text, skill, kinh nghiệm) -> lưu DB
3. Trang Kết quả ứng viên (trang 3): rule-based scorer -> gọi Gemini -> lưu MatchResult -> hiển thị bảng + chi tiết

Chi tiết task theo tuần: `jira_tasks_by_week.csv` / `.xlsx`
