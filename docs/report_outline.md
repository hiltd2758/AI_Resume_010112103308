# Dàn ý báo cáo và slide dự án CV–JD Matcher

## 1. Trang bìa
- Mục tiêu: Giới thiệu tên đề tài, nhóm thực hiện và bối cảnh bài toán.
- Nội dung cần viết: Tên dự án, tên nhóm, lớp/môn, thời gian thực hiện.
- Ảnh / bảng / screenshot nên chèn: Logo hoặc ảnh minh họa CV và JD.
- Thành viên chịu trách nhiệm cung cấp: Cả nhóm.
- Số slide gợi ý: 1.

## 2. Giới thiệu đề tài
- Mục tiêu: Trình bày bài toán ghép CV với JD và lý do cần hệ thống hỗ trợ tự động.
- Nội dung cần viết: Vấn đề thực tế, khó khăn khi so sánh thủ công, ý nghĩa của hệ thống.
- Ảnh / bảng / screenshot nên chèn: Sơ đồ nhỏ mô tả luồng CV -> xử lý -> kết quả.
- Thành viên chịu trách nhiệm cung cấp: Cả nhóm.
- Số slide gợi ý: 1.

## 3. Mục tiêu và phạm vi
- Mục tiêu: Xác định mục tiêu chức năng và giới hạn của hệ thống.
- Nội dung cần viết: Mục tiêu chính, phạm vi dữ liệu đầu vào, phạm vi tính năng, những phần không làm.
- Ảnh / bảng / screenshot nên chèn: Bảng mục tiêu và phạm vi.
- Thành viên chịu trách nhiệm cung cấp: Cả nhóm.
- Số slide gợi ý: 1.

## 4. Kiến trúc tổng quan hệ thống
- Mục tiêu: Cho thấy toàn bộ kiến trúc và cách các module phối hợp.
- Nội dung cần viết: Luồng dữ liệu từ upload CV đến kết quả cuối cùng, các module chính, vai trò từng thành viên.
- Ảnh / bảng / screenshot nên chèn: Sơ đồ kiến trúc tổng quan.
- Thành viên chịu trách nhiệm cung cấp: Cả nhóm, phối hợp tổng hợp bởi người thuyết trình.
- Số slide gợi ý: 1-2.

## 5. Thu thập và xử lý dữ liệu CV/JD
- Mục tiêu: Mô tả cách đọc, tách và chuẩn hóa dữ liệu đầu vào.
- Nội dung cần viết: Nguồn CV/JD, cách trích xuất văn bản, làm sạch dữ liệu, tách kỹ năng và thông tin liên quan.
- Ảnh / bảng / screenshot nên chèn: Ví dụ CV/JD đầu vào, bảng dữ liệu mẫu.
- Thành viên chịu trách nhiệm cung cấp: Cả nhóm.
- Số slide gợi ý: 1.

## 6. Module Naïve Bayes — Dũng
- Mục tiêu: Giới thiệu module phân loại/matching dựa trên Naïve Bayes.
- Nội dung cần viết: Ý tưởng mô hình, feature đầu vào, cách huấn luyện và dự đoán, kết quả chính.
- Ảnh / bảng / screenshot nên chèn: Biểu đồ kết quả, ví dụ prediction, bảng chỉ số đánh giá.
- Thành viên chịu trách nhiệm cung cấp: Dũng.
- Số slide gợi ý: 1-2.

## 7. Module RAG — Hi
- Mục tiêu: Trình bày cách truy hồi thông tin và sinh câu trả lời/đề xuất có ngữ cảnh.
- Nội dung cần viết: Vector hóa, lưu trữ vector, truy hồi Top-K, cách tạo phản hồi từ ngữ cảnh.
- Ảnh / bảng / screenshot nên chèn: Sơ đồ RAG, ví dụ retrieval, ví dụ output.
- Thành viên chịu trách nhiệm cung cấp: Hi.
- Số slide gợi ý: 1-2.

## 8. Module Skill-gap — Hai
- Mục tiêu: Trình bày logic so sánh JD và CV, xác định khoảng cách kỹ năng và gợi ý cải thiện.
- Nội dung cần viết: Flow chuẩn hóa dữ liệu, matched/missing/extra skills, skill_gap_score, recommendations, quy ước khi JD rỗng.
- Ảnh / bảng / screenshot nên chèn: Sơ đồ flow Skill-gap, ví dụ input/output, bảng gợi ý kỹ năng.
- Thành viên chịu trách nhiệm cung cấp: Hai.
- Số slide gợi ý: 1-2.

## 9. Giao diện hệ thống — Thương
- Mục tiêu: Giới thiệu cách người dùng tương tác với hệ thống.
- Nội dung cần viết: Các trang chính, luồng thao tác, cách hiển thị kết quả và thông tin kỹ năng.
- Ảnh / bảng / screenshot nên chèn: Screenshot trang upload, trang kết quả, phần hiển thị skill-gap nếu có.
- Thành viên chịu trách nhiệm cung cấp: Thương.
- Số slide gợi ý: 1-2.

## 10. Kết quả demo toàn hệ thống
- Mục tiêu: Cho thấy hệ thống hoạt động end-to-end.
- Nội dung cần viết: Kịch bản demo, dữ liệu mẫu, kết quả từ các module, điểm nổi bật.
- Ảnh / bảng / screenshot nên chèn: Ảnh chụp màn hình demo, bảng kết quả tổng hợp.
- Thành viên chịu trách nhiệm cung cấp: Cả nhóm.
- Số slide gợi ý: 1.

## 11. Đánh giá
- Mục tiêu: Đánh giá chất lượng hệ thống và mức độ đáp ứng yêu cầu.
- Nội dung cần viết: Độ chính xác tương đối, tính hữu ích, độ ổn định, kết quả kiểm thử.
- Ảnh / bảng / screenshot nên chèn: Bảng test, bảng so sánh hoặc bảng tổng hợp kết quả.
- Thành viên chịu trách nhiệm cung cấp: Cả nhóm, tổng hợp bởi người báo cáo.
- Số slide gợi ý: 1.

## 12. Hạn chế
- Mục tiêu: Nêu rõ những giới hạn hiện tại của hệ thống.
- Nội dung cần viết: Giới hạn về dữ liệu, độ linh hoạt của rule-based logic, độ bao phủ kỹ năng, giới hạn UI hoặc triển khai.
- Ảnh / bảng / screenshot nên chèn: Không bắt buộc, có thể dùng bảng ngắn.
- Thành viên chịu trách nhiệm cung cấp: Cả nhóm.
- Số slide gợi ý: 1.

## 13. Hướng phát triển
- Mục tiêu: Định hướng mở rộng sau khi hoàn thành phiên bản hiện tại.
- Nội dung cần viết: Cải thiện extraction, mở rộng mapping kỹ năng, tối ưu UI, thêm đánh giá chi tiết, mở rộng dữ liệu.
- Ảnh / bảng / screenshot nên chèn: Danh sách bullet hoặc sơ đồ roadmap.
- Thành viên chịu trách nhiệm cung cấp: Cả nhóm.
- Số slide gợi ý: 1.

## 14. Phân công thành viên
- Mục tiêu: Làm rõ vai trò và phần việc của từng người trong nhóm.
- Nội dung cần viết: Tên thành viên, nhiệm vụ, phần đã hoàn thành.
- Ảnh / bảng / screenshot nên chèn: Bảng phân công công việc.
- Thành viên chịu trách nhiệm cung cấp: Cả nhóm.
- Số slide gợi ý: 1.

## 15. Kết luận
- Mục tiêu: Tổng kết giá trị của dự án và thông điệp cuối cùng.
- Nội dung cần viết: Những gì hệ thống đã giải quyết, bài học chính, kết quả tổng quan.
- Ảnh / bảng / screenshot nên chèn: Không bắt buộc.
- Thành viên chịu trách nhiệm cung cấp: Cả nhóm.
- Số slide gợi ý: 1.

---

## Checklist tài liệu cần nhóm cung cấp để hoàn thiện báo cáo và slide

### Dũng cần gửi
- Dataset CV có nhãn.
- Cách tạo feature vector.
- Kết quả train/predict Naïve Bayes.
- Chỉ số đánh giá hoặc demo.

### Hi cần gửi
- Cấu hình vector DB.
- Embedding model.
- Ví dụ retrieval Top-K.
- Ví dụ hỏi đáp RAG.
- Screenshot/output RAG.

### Hai cần gửi
- Flow Skill-gap.
- File module.
- Test.
- Demo input/output.
- Recommendation mapping.

### Thương cần gửi
- Mockup/UI.
- Screenshot trang kết quả.
- Cách hiển thị skill-gap.
- Screenshot phần kỹ năng thiếu.

### Cả nhóm cần chuẩn bị
- CV mẫu.
- JD mẫu.
- Sơ đồ kiến trúc.
- Screenshot demo hệ thống cuối.
- Danh sách công nghệ.
- Phân công thành viên.

---

## Module Skill-Gap - Thành viên Hai

### Bài toán

Xác định mức độ kỹ năng trong CV đáp ứng kỹ năng yêu cầu trong JD, tách biệt với điểm LLM/Groq và đủ dễ giải thích khi vấn đáp.

### Thiết kế

- Chuẩn hóa kỹ năng về canonical form.
- Loại duplicate nhưng giữ thứ tự xuất hiện hợp lý.
- So sánh deterministic bằng tập kỹ năng đã canonicalize.
- Tính coverage theo số kỹ năng JD duy nhất.
- Sinh recommendation rule-based cho từng kỹ năng thiếu.

### Cài đặt

- Module chính: `scoring/skill_gap.py`.
- Parser dùng chung normalization: `parsing/skill_extractor.py`.
- Rule-based scorer dùng chung normalization khi tính skill score.
- Không phụ thuộc Streamlit, Groq, RAG hoặc network.

### Kịch bản demo

1. CV Python/Backend match 100% với Job Python.
2. CV Front End dùng `HTML5`, `CSS3`, `WordPress` match với Job `HTML`, `CSS`, `WordPress`.
3. CV Python so với Job Front End trả missing skill rõ ràng, không gây hiểu nhầm là lỗi parser.

### Kết quả test

Test tự động bằng `python -m unittest scoring.test_skill_gap -v`, bao gồm exact match, alias, duplicate, partial match, input rỗng, text enrichment và recommendation.

### Giới hạn

Module hiện dựa trên keyword/alias, chưa thay thế semantic skill matching. Các skill gần nghĩa như `PostgreSQL` và `SQL` chỉ match nếu được định nghĩa alias hoặc taxonomy rõ ràng.

### Định hướng phát triển

- Bổ sung taxonomy skill.
- Thêm trọng số theo vai trò tuyển dụng.
- Kết hợp semantic matching như lớp gợi ý, nhưng giữ deterministic coverage làm baseline.
