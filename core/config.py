import os
try:
    from dotenv import load_dotenv
except Exception:
    # dotenv is optional in some environments (CI or constrained shells)
    def load_dotenv():
        return None

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
DB_PATH = "cv_matching.db"

# --- RAG config (Role: RAG team) ---
# Model đa ngôn ngữ (hỗ trợ tiếng Việt) để embed CV/JD cho semantic search.
# Nhẹ (~120MB), chạy tốt trên CPU, không cần GPU.
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "paraphrase-multilingual-MiniLM-L12-v2")
VECTOR_STORE_DIR = os.getenv("VECTOR_STORE_DIR", "vector_store")

# Danh sách kỹ năng dùng chung cho chức năng trích xuất và phân tích Skill-gap.
SKILL_KEYWORDS = [
    "Python", "Java", "JavaScript", "React", "Node.js", "SQL",
    "FastAPI", "Spring Boot", "Docker", "Git", "TensorFlow", "Pandas",
]

# Mapping from normalized skill name -> short recommendation string.
# Keep keys lowercased. These are used by the skill-gap recommender
# to provide actionable next steps for missing skills.
SKILL_RECOMMENDATIONS = {
    "python": "Nâng cao Python: hướng tới làm project xử lý dữ liệu và web với FastAPI.",
    "java": "Ôn Java core và Spring Boot để xây dựng backend quy mô lớn.",
    "javascript": "Làm các project frontend hoặc động với ES6+ và tư duy bất đồng bộ.",
    "react": "Học React hooks, quản lý state bằng Redux hoặc Context API và làm SPA.",
    "node.js": "Thực hành Node.js với Express hoặc NestJS, hiểu async I/O và viết kiểm thử cơ bản.",
    "sql": "Thực hành SQL với join, indexing và một hệ quản trị dữ liệu như PostgreSQL hoặc MySQL.",
    "fastapi": "Xây API với FastAPI, viết unit test và triển khai bằng Docker.",
    "spring boot": "Tập trung vào Spring Boot nền tảng và cấu hình cho môi trường production.",
    "docker": "Học Docker: containerize ứng dụng, docker-compose và các thực hành tốt nhất.",
    "git": "Sử dụng Git branching, quy trình pull request và xử lý merge conflict.",
    "tensorflow": "Học TensorFlow cơ bản: xây dựng mô hình, huấn luyện, đánh giá và tối ưu.",
    "pandas": "Luyện Pandas cho xử lý dữ liệu: groupby, merge và thao tác chuỗi thời gian.",
    "numpy": "Nâng cao NumPy để tối ưu tính toán ma trận và vector hóa mã nguồn.",
    "scikit-learn": "Học scikit-learn: xây dựng pipeline, chọn mô hình và đánh giá bằng cross-validation.",
    "machine learning": "Ôn kiến thức machine learning cơ bản: mô hình học có giám sát và không giám sát.",
    "github": "Thực hành quy trình GitHub: pull request, issues, releases và GitHub Actions cơ bản.",
    "flask": "Xây dựng REST API với Flask, viết test và triển khai ứng dụng cơ bản.",
    "html": "Củng cố HTML semantic và các nguyên tắc accessibility cơ bản.",
    "css": "Học CSS Flexbox, Grid và thiết kế responsive.",
    "pytorch": "Học PyTorch cơ bản để xây dựng mô hình deep learning và custom training loop.",
    "aws": "Tìm hiểu AWS cơ bản: EC2, S3, IAM và triển khai ứng dụng đơn giản.",
    "linux": "Luyện Linux cơ bản: shell commands, permissions và quản lý tiến trình.",
    "excel": "Luyện Excel: công thức, PivotTable và quy trình làm sạch dữ liệu.",
}
