import sqlite3
import json
from contextlib import contextmanager
from core.config import DB_PATH


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def _connection():
    """Vấn đề 2 (fix): đảm bảo conn.close() luôn được gọi, kể cả khi exception
    xảy ra giữa execute và close -> tránh leak connection."""
    conn = get_conn()
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    with _connection() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            required_skills TEXT,
            required_experience_years INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS cvs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_name TEXT NOT NULL,
            raw_text TEXT,
            skills TEXT,
            experience_years INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS match_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cv_id INTEGER,
            job_id INTEGER,
            rule_based_score REAL,
            final_score REAL,
            pros TEXT,
            cons TEXT,
            recommendation TEXT,
            interview_questions TEXT,
            job_prediction TEXT,
            job_requirements_hash TEXT,
            UNIQUE(cv_id, job_id)
        );
        """)
        conn.commit()
        _migrate_add_job_requirements_hash(conn)


def _migrate_add_job_requirements_hash(conn):
    """Migration nhẹ cho DB cũ (tạo trước khi có cột job_requirements_hash
    và UNIQUE constraint). SQLite không cho ALTER TABLE thêm UNIQUE trực tiếp,
    nên: thêm cột nếu thiếu, rồi rebuild bảng nếu UNIQUE constraint chưa tồn tại."""
    cols = [row["name"] for row in conn.execute("PRAGMA table_info(match_results)").fetchall()]
    if "job_prediction" not in cols:
        conn.execute("ALTER TABLE match_results ADD COLUMN job_prediction TEXT")
        conn.commit()

    if "job_requirements_hash" not in cols:
        conn.execute("ALTER TABLE match_results ADD COLUMN job_requirements_hash TEXT")
        conn.commit()

    # Kiểm tra UNIQUE(cv_id, job_id) đã có chưa
    indexes = conn.execute("PRAGMA index_list(match_results)").fetchall()
    has_unique_cv_job = False
    for idx in indexes:
        if idx["unique"]:
            idx_cols = [r["name"] for r in conn.execute(f"PRAGMA index_info({idx['name']})").fetchall()]
            if set(idx_cols) == {"cv_id", "job_id"}:
                has_unique_cv_job = True
                break

    if not has_unique_cv_job:
        # Rebuild bảng với UNIQUE constraint, giữ lại dòng mới nhất cho mỗi (cv_id, job_id)
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS match_results_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cv_id INTEGER,
            job_id INTEGER,
            rule_based_score REAL,
            final_score REAL,
            pros TEXT,
            cons TEXT,
            recommendation TEXT,
            interview_questions TEXT,
            job_prediction TEXT,
            job_requirements_hash TEXT,
            UNIQUE(cv_id, job_id)
        );
        INSERT OR IGNORE INTO match_results_new
            SELECT id, cv_id, job_id, rule_based_score, final_score, pros, cons,
                   recommendation, interview_questions, job_prediction, job_requirements_hash
            FROM match_results
            ORDER BY id DESC;
        DROP TABLE match_results;
        ALTER TABLE match_results_new RENAME TO match_results;
        """)
        conn.commit()


def add_job(title, description, required_skills: list, required_experience_years: int):
    with _connection() as conn:
        cur = conn.execute(
            "INSERT INTO jobs (title, description, required_skills, required_experience_years) VALUES (?,?,?,?)",
            (title, description, json.dumps(required_skills), required_experience_years),
        )
        conn.commit()
        return cur.lastrowid


def list_jobs():
    with _connection() as conn:
        rows = conn.execute("SELECT * FROM jobs").fetchall()
        return [dict(r) for r in rows]


def add_cv(candidate_name, raw_text, skills: list, experience_years: int):
    with _connection() as conn:
        cur = conn.execute(
            "INSERT INTO cvs (candidate_name, raw_text, skills, experience_years) VALUES (?,?,?,?)",
            (candidate_name, raw_text, json.dumps(skills), experience_years),
        )
        conn.commit()
        return cur.lastrowid


def list_cvs():
    with _connection() as conn:
        rows = conn.execute("SELECT * FROM cvs").fetchall()
        return [dict(r) for r in rows]


def save_match_result(cv_id, job_id, rule_based_score, final_score, pros, cons,
                       recommendation, interview_questions, job_prediction=None,
                       job_requirements_hash=None):
    """Vấn đề 1 (fix): upsert thay cho INSERT thuần, dựa trên UNIQUE(cv_id, job_id).
    'Chạy lại từ đầu' giờ sẽ cập nhật dòng cũ thay vì tạo thêm dòng trùng."""
    with _connection() as conn:
        conn.execute(
            """INSERT INTO match_results
            (cv_id, job_id, rule_based_score, final_score, pros, cons, recommendation,
             interview_questions, job_prediction, job_requirements_hash)
            VALUES (?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(cv_id, job_id) DO UPDATE SET
                rule_based_score = excluded.rule_based_score,
                final_score = excluded.final_score,
                pros = excluded.pros,
                cons = excluded.cons,
                recommendation = excluded.recommendation,
                interview_questions = excluded.interview_questions,
                job_prediction = excluded.job_prediction,
                job_requirements_hash = excluded.job_requirements_hash""",
            (cv_id, job_id, rule_based_score, final_score, pros, cons, recommendation,
             json.dumps(interview_questions), job_prediction, job_requirements_hash),
        )
        conn.commit()


def list_results_by_job(job_id):
    with _connection() as conn:
        rows = conn.execute(
            """SELECT mr.*, c.candidate_name, c.skills, c.raw_text FROM match_results mr
            JOIN cvs c ON c.id = mr.cv_id WHERE mr.job_id = ?
            ORDER BY mr.final_score DESC""",
            (job_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_match_result(cv_id, job_id):
    """Kiểm tra cặp CV-Job đã có kết quả chưa, tránh gọi API trùng lặp."""
    with _connection() as conn:
        row = conn.execute(
            "SELECT * FROM match_results WHERE cv_id = ? AND job_id = ?",
            (cv_id, job_id),
        ).fetchone()
        return dict(row) if row else None

def delete_cv(cv_id):
    try:
        from rag.indexer import delete_cv_index
        delete_cv_index(cv_id)
    except Exception as e:
        print(f"[WARN] Không xoá được embedding cho cv_id={cv_id}: {type(e).__name__}: {e}")

    with _connection() as conn:
        conn.execute("DELETE FROM match_results WHERE cv_id = ?", (cv_id,))
        conn.execute("DELETE FROM cvs WHERE id = ?", (cv_id,))
        conn.commit()


def delete_job(job_id):
    try:
        from rag.indexer import delete_job_index
        delete_job_index(job_id)
    except Exception as e:
        print(f"[WARN] Không xoá được embedding cho job_id={job_id}: {type(e).__name__}: {e}")

    with _connection() as conn:
        conn.execute("DELETE FROM match_results WHERE job_id = ?", (job_id,))
        conn.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
        conn.commit()