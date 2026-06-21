import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
DB_PATH = "cv_matching.db"

# Role 2 dùng để mở rộng danh sách skill nhận diện
SKILL_KEYWORDS = [
    "Python", "Java", "JavaScript", "React", "Node.js", "SQL",
    "FastAPI", "Spring Boot", "Docker", "Git", "TensorFlow", "Pandas",
]
