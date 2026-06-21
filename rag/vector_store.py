"""
Setup FAISS vector store cho CV và JD (Task 1 - RAG).

Thiết kế:
- 2 collection riêng: "cv" và "job" (lưu 2 file index khác nhau), vì khi search
  ta thường muốn tìm CV liên quan tới 1 JD (hoặc ngược lại), không trộn chung.
- Dùng IndexFlatIP (Inner Product) trên vector đã normalize -> tương đương cosine
  similarity, đơn giản và đủ nhanh với quy mô CV/JD của 1 đồ án (vài trăm-vài nghìn
  document). Không cần index phức tạp (IVF/HNSW) ở quy mô này.
- Metadata (id, loại, tên/tiêu đề, text gốc) lưu riêng ở file JSON song song với
  FAISS index, vì FAISS chỉ lưu vector, không lưu được dữ liệu kèm theo.
"""
import json
import os

import numpy as np
import faiss

from core.config import VECTOR_STORE_DIR

VALID_COLLECTIONS = ("cv", "job")


def _paths(collection: str):
    assert collection in VALID_COLLECTIONS, f"Collection không hợp lệ: {collection}"
    os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
    index_path = os.path.join(VECTOR_STORE_DIR, f"{collection}.index")
    meta_path = os.path.join(VECTOR_STORE_DIR, f"{collection}.meta.json")
    return index_path, meta_path


def load_index(collection: str):
    """Trả về (index, metadata_list). Nếu chưa từng tạo, trả về (None, [])."""
    index_path, meta_path = _paths(collection)
    if os.path.exists(index_path) and os.path.exists(meta_path):
        index = faiss.read_index(index_path)
        with open(meta_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        return index, metadata
    return None, []


def save_index(collection: str, index, metadata: list[dict]):
    index_path, meta_path = _paths(collection)
    faiss.write_index(index, index_path)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False)


def add_documents(collection: str, vectors: list[list[float]], metadata_list: list[dict]):
    """
    Thêm document mới vào vector store.
    vectors: list các embedding vector (đã normalize).
    metadata_list: list dict cùng độ dài với vectors, vd:
        {"ref_id": cv_id, "name": "Nguyen Van A", "text": "..."}
    """
    if len(vectors) != len(metadata_list):
        raise ValueError("Số lượng vectors và metadata phải bằng nhau")

    index, metadata = load_index(collection)
    arr = np.array(vectors, dtype="float32")

    if index is None:
        dim = arr.shape[1]
        index = faiss.IndexFlatIP(dim)

    index.add(arr)
    metadata.extend(metadata_list)
    save_index(collection, index, metadata)
    return index.ntotal


def search(collection: str, query_vector: list[float], top_k: int = 5) -> list[dict]:
    """Tìm top_k document gần nhất với query_vector. Trả về list metadata kèm score."""
    index, metadata = load_index(collection)
    if index is None or index.ntotal == 0:
        return []

    arr = np.array([query_vector], dtype="float32")
    k = min(top_k, index.ntotal)
    scores, ids = index.search(arr, k)

    results = []
    for score, idx in zip(scores[0], ids[0]):
        if idx == -1 or idx >= len(metadata):
            continue
        item = dict(metadata[idx])
        item["score"] = float(score)
        results.append(item)
    return results


def reset_collection(collection: str):
    """Xoá toàn bộ index của 1 collection (dùng khi cần build lại từ đầu)."""
    index_path, meta_path = _paths(collection)
    for p in (index_path, meta_path):
        if os.path.exists(p):
            os.remove(p)

def remove_by_ref_id(collection: str, ref_id):
    """
    Xoá 1 document khỏi vector store theo ref_id (vd: cv_id hoặc job_id).
    FAISS IndexFlatIP không hỗ trợ xoá trực tiếp theo vị trí, nên phải
    reconstruct lại toàn bộ vector còn giữ và build index mới.
    """
    index, metadata = load_index(collection)
    if index is None:
        return

    keep_idx = [i for i, m in enumerate(metadata) if m.get("ref_id") != ref_id]
    if len(keep_idx) == len(metadata):
        return  # không tìm thấy ref_id này, không có gì để xoá

    if not keep_idx:
        reset_collection(collection)
        return

    vectors = [index.reconstruct(i).tolist() for i in keep_idx]
    new_metadata = [metadata[i] for i in keep_idx]
    dim = len(vectors[0])
    new_index = faiss.IndexFlatIP(dim)
    new_index.add(np.array(vectors, dtype="float32"))
    save_index(collection, new_index, new_metadata)

def collection_stats() -> dict:
    """Thống kê số document hiện có trong mỗi collection, để hiển thị debug/UI."""
    stats = {}
    for c in VALID_COLLECTIONS:
        index, metadata = load_index(c)
        stats[c] = index.ntotal if index is not None else 0
    return stats
