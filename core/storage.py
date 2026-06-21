"""Lưu trữ Job / CV / MatchResult bằng SQLite (Role: Hil - Lead)."""
import sqlite3
import json
from core.config import DB_PATH


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
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
        interview_questions TEXT
    );
    """)
    conn.commit()
    conn.close()


def add_job(title, description, required_skills: list, required_experience_years: int):
    conn = get_conn()
    cur = conn.execute(
        "INSERT INTO jobs (title, description, required_skills, required_experience_years) VALUES (?,?,?,?)",
        (title, description, json.dumps(required_skills), required_experience_years),
    )
    conn.commit()
    job_id = cur.lastrowid
    conn.close()
    return job_id


def list_jobs():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM jobs").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_cv(candidate_name, raw_text, skills: list, experience_years: int):
    conn = get_conn()
    cur = conn.execute(
        "INSERT INTO cvs (candidate_name, raw_text, skills, experience_years) VALUES (?,?,?,?)",
        (candidate_name, raw_text, json.dumps(skills), experience_years),
    )
    conn.commit()
    cv_id = cur.lastrowid
    conn.close()
    return cv_id


def list_cvs():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM cvs").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_match_result(cv_id, job_id, rule_based_score, final_score, pros, cons, recommendation, interview_questions):
    conn = get_conn()
    conn.execute(
        """INSERT INTO match_results
        (cv_id, job_id, rule_based_score, final_score, pros, cons, recommendation, interview_questions)
        VALUES (?,?,?,?,?,?,?,?)""",
        (cv_id, job_id, rule_based_score, final_score, pros, cons, recommendation,
         json.dumps(interview_questions)),
    )
    conn.commit()
    conn.close()


def list_results_by_job(job_id):
    conn = get_conn()
    rows = conn.execute(
        """SELECT mr.*, c.candidate_name FROM match_results mr
        JOIN cvs c ON c.id = mr.cv_id WHERE mr.job_id = ?
        ORDER BY mr.final_score DESC""",
        (job_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_match_result(cv_id, job_id):
    """Kiểm tra cặp CV-Job đã có kết quả chưa, tránh gọi API trùng lặp."""
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM match_results WHERE cv_id = ? AND job_id = ?",
        (cv_id, job_id),
    ).fetchone()
    conn.close()
    return dict(row) if row else None
