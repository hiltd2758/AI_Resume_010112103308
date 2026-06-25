import os

try:
    from dotenv import load_dotenv
except Exception:
    # dotenv là tùy chọn để project vẫn chạy được trong môi trường test tối giản.
    def load_dotenv():
        return None


load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
DB_PATH = "cv_matching.db"

# Cấu hình RAG thuộc nhóm RAG, giữ nguyên hành vi hiện tại.
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "paraphrase-multilingual-MiniLM-L12-v2")
VECTOR_STORE_DIR = os.getenv("VECTOR_STORE_DIR", "vector_store")

# Danh sách kỹ năng dùng chung cho trích xuất và phân tích Skill-Gap.
SKILL_KEYWORDS = [
    "Python", "Java", "JavaScript", "React", "Node.js", "SQL",
    "FastAPI", "Spring Boot", "Docker", "Git", "TensorFlow", "Pandas",
    "HTML", "CSS", "WordPress", "PHP", "PHP-Fusion", "Concrete5",
    "AWS", "Linux", "NumPy", "scikit-learn", "Machine Learning",
    "PyTorch", "Flask",
]

# Key dùng dạng lowercase/canonical key để module Skill-Gap tra cứu ổn định.
SKILL_RECOMMENDATIONS = {
    "python": "Nâng cao Python bằng một project xử lý dữ liệu hoặc API nhỏ với test rõ ràng.",
    "java": "Ôn Java core và xây dựng một service backend nhỏ để chứng minh khả năng lập trình hướng đối tượng.",
    "javascript": "Làm một project frontend dùng JavaScript ES6+, thao tác DOM/API và xử lý bất đồng bộ.",
    "react": "Học React hooks, quản lý state và triển khai một SPA nhỏ vào portfolio.",
    "nodejs": "Thực hành Node.js với Express hoặc NestJS, hiểu async I/O và viết kiểm thử cơ bản.",
    "sql": "Thực hành SQL với join, indexing và một hệ quản trị dữ liệu như PostgreSQL hoặc MySQL.",
    "fastapi": "Xây API với FastAPI, viết unit test và triển khai bằng Docker.",
    "springboot": "Tập trung vào Spring Boot nền tảng, REST API và cấu hình cho môi trường production.",
    "docker": "Học kiến thức Docker cơ bản, containerize một ứng dụng nhỏ và đưa project vào portfolio.",
    "git": "Sử dụng Git branching, quy trình pull request và xử lý merge conflict.",
    "tensorflow": "Học TensorFlow cơ bản: xây dựng mô hình, huấn luyện, đánh giá và tối ưu.",
    "pandas": "Luyện Pandas cho xử lý dữ liệu: groupby, merge và làm sạch dữ liệu.",
    "html": "Củng cố HTML semantic, form, accessibility cơ bản và cấu trúc trang rõ ràng.",
    "css": "Học CSS Flexbox, Grid, responsive design và dựng lại một giao diện thực tế.",
    "wordpress": "Thực hành dựng website WordPress, tùy chỉnh theme/plugin và tối ưu nội dung cơ bản.",
    "php": "Ôn PHP cơ bản, xử lý form và kết nối database trong một ứng dụng nhỏ.",
    "phpfusion": "Tìm hiểu PHP-Fusion, cài đặt module/theme và ghi lại demo cấu hình.",
    "concrete5": "Tìm hiểu Concrete5 CMS, tạo page type/block cơ bản và chuẩn bị demo ngắn.",
    "aws": "Tìm hiểu AWS cơ bản: EC2, S3, IAM và triển khai ứng dụng đơn giản.",
    "linux": "Luyện Linux cơ bản: shell commands, permissions và quản lý tiến trình.",
    "numpy": "Nâng cao NumPy để tối ưu tính toán ma trận và vector hóa mã nguồn.",
    "scikitlearn": "Học scikit-learn: xây dựng pipeline, chọn mô hình và đánh giá bằng cross-validation.",
    "machinelearning": "Ôn kiến thức machine learning cơ bản và làm một notebook huấn luyện mô hình có giải thích.",
    "pytorch": "Học PyTorch cơ bản để xây dựng mô hình deep learning và custom training loop.",
    "flask": "Xây dựng REST API với Flask, viết test và triển khai ứng dụng cơ bản.",
    "github": "Thực hành quy trình GitHub: pull request, issues, releases và GitHub Actions cơ bản.",
    "excel": "Luyện Excel: công thức, PivotTable và quy trình làm sạch dữ liệu.",
}
