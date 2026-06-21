import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
DB_PATH = "cv_matching.db"

# --- RAG config (Role: RAG team) ---
# Model đa ngôn ngữ (hỗ trợ tiếng Việt) để embed CV/JD cho semantic search.
# Nhẹ (~120MB), chạy tốt trên CPU, không cần GPU.
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "paraphrase-multilingual-MiniLM-L12-v2")
VECTOR_STORE_DIR = os.getenv("VECTOR_STORE_DIR", "vector_store")

# Role 2 dùng để mở rộng danh sách skill nhận diện
SKILL_KEYWORDS = [
    "Python", "Java", "JavaScript", "React", "Node.js", "SQL",
    "FastAPI", "Spring Boot", "Docker", "Git", "TensorFlow", "Pandas",
]
