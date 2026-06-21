"""
Indexer: nối embeddings.py + vector_store.py với CV/JD thật trong hệ thống.
Việc này giúp Task 3 (tích hợp retrieval vào luồng LLM) chỉ cần gọi search_*,
không cần biết chi tiết FAISS/embedding bên dưới.
"""
from rag.embeddings import embed_text, embed_texts
from rag.vector_store import add_documents, search


def index_cv(cv_id: int, candidate_name: str, raw_text: str):
    """Embed 1 CV và thêm vào vector store collection 'cv'."""
    vector = embed_text(raw_text)
    add_documents(
        "cv",
        [vector],
        [{"ref_id": cv_id, "name": candidate_name, "text": raw_text}],
    )


def index_job(job_id: int, title: str, description: str):
    """Embed 1 JD (title + description) và thêm vào vector store collection 'job'."""
    full_text = f"{title}\n{description or ''}"
    vector = embed_text(full_text)
    add_documents(
        "job",
        [vector],
        [{"ref_id": job_id, "name": title, "text": full_text}],
    )


def search_cvs_for_job(job_text: str, top_k: int = 5) -> list[dict]:
    """Tìm các CV liên quan nhất tới 1 JD (dùng job_text làm query)."""
    query_vector = embed_text(job_text)
    return search("cv", query_vector, top_k=top_k)


def search_jobs_for_cv(cv_text: str, top_k: int = 5) -> list[dict]:
    """Tìm các JD liên quan nhất tới 1 CV (dùng cv_text làm query)."""
    query_vector = embed_text(cv_text)
    return search("job", query_vector, top_k=top_k)


def reindex_all():
    """
    Build lại toàn bộ index từ dữ liệu đã có trong SQLite.
    Dùng khi: mới thêm RAG vào dự án đã có data cũ, hoặc đổi embedding model.
    """
    from core.storage import list_cvs, list_jobs
    from rag.vector_store import reset_collection

    reset_collection("cv")
    reset_collection("job")

    cvs = list_cvs()
    if cvs:
        vectors = embed_texts([c["raw_text"] or "" for c in cvs])
        metas = [{"ref_id": c["id"], "name": c["candidate_name"], "text": c["raw_text"]} for c in cvs]
        add_documents("cv", vectors, metas)

    jobs = list_jobs()
    if jobs:
        texts = [f"{j['title']}\n{j['description'] or ''}" for j in jobs]
        vectors = embed_texts(texts)
        metas = [{"ref_id": j["id"], "name": j["title"], "text": t} for j, t in zip(jobs, texts)]
        add_documents("job", vectors, metas)

    return {"cv_count": len(cvs), "job_count": len(jobs)}
