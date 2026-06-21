"""
Embedding model + pipeline tạo embedding cho CV/JD (Task 2 - RAG).

Model đã chọn: paraphrase-multilingual-MiniLM-L12-v2 (sentence-transformers)
Lý do chọn:
- Hỗ trợ tiếng Việt (multilingual) — CV/JD trong dự án chủ yếu là tiếng Việt.
- Nhẹ (~120MB), chạy được trên CPU, không cần GPU -> phù hợp máy cá nhân của nhóm.
- Miễn phí, chạy local, không tốn API quota như embedding qua OpenAI.

Lưu ý: lần chạy đầu tiên cần internet để model tự tải về (cache tại
~/.cache/huggingface). Từ lần 2 trở đi chạy offline được.
"""
from functools import lru_cache

from core.config import EMBEDDING_MODEL_NAME


@lru_cache(maxsize=1)
def get_model():
    """Lazy-load model, chỉ load 1 lần (singleton) để tránh tốn RAM/thời gian."""
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(EMBEDDING_MODEL_NAME)


def embed_text(text: str) -> list[float]:
    """Embed 1 đoạn text -> vector (đã normalize để dùng cosine similarity qua dot product)."""
    model = get_model()
    vector = model.encode(text, normalize_embeddings=True)
    return vector.tolist()


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed nhiều đoạn text cùng lúc (nhanh hơn gọi lẻ từng cái)."""
    model = get_model()
    vectors = model.encode(texts, normalize_embeddings=True, batch_size=16)
    return vectors.tolist()


def get_embedding_dim() -> int:
    """Số chiều của vector embedding, cần để khởi tạo FAISS index."""
    return len(embed_text("test"))


def is_model_available() -> bool:
    """
    Kiểm tra model có sẵn sàng dùng không (đã tải/cache hoặc có internet để tải).
    Dùng để UI báo lỗi rõ ràng thay vì crash, vd khi máy chưa có internet lần đầu.
    """
    try:
        get_model()
        return True
    except Exception:
        return False
