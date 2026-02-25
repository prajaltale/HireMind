"""Simple auth: email/password + JWT, with SQLite storage.

Google sign-in is supported via a lightweight endpoint that accepts
verified email/name from the frontend (demo-level).
"""

import os
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Optional, Tuple

from jose import JWTError, jwt
from passlib.context import CryptContext

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data.db"

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

SECRET_KEY = os.getenv("AUTH_SECRET_KEY", "dev-secret-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day


def init_db() -> None:
    """Ensure SQLite DB and users table exist."""
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                password_hash TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ats_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                score INTEGER NOT NULL,
                resume_text TEXT,
                job_description TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS interview_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                question_count INTEGER,
                average_score REAL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def _get_conn() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def get_user_by_email(email: str) -> Optional[Dict]:
    conn = _get_conn()
    try:
        cur = conn.execute(
            "SELECT id, email, name, password_hash, created_at FROM users WHERE email = ?",
            (email.lower(),),
        )
        row = cur.fetchone()
    finally:
        conn.close()
    if not row:
        return None
    return {
        "id": row[0],
        "email": row[1],
        "name": row[2],
        "password_hash": row[3],
        "created_at": row[4],
    }


def create_user(email: str, name: str, password: Optional[str] = None) -> Dict:
    email = email.lower().strip()
    password_hash = pwd_context.hash(password) if password else None
    now = datetime.now(timezone.utc).isoformat()
    conn = _get_conn()
    try:
        conn.execute(
            "INSERT INTO users (email, name, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (email, name.strip() or email, password_hash, now),
        )
        conn.commit()
    finally:
        conn.close()
    return get_user_by_email(email)  # type: ignore[return-value]


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def authenticate_user(email: str, password: str) -> Optional[Dict]:
    user = get_user_by_email(email)
    if not user or not user.get("password_hash"):
        return None
    if not verify_password(password, user["password_hash"]):
        return None
    return user


def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[Dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def get_user_from_token(token: str) -> Optional[Dict]:
    data = decode_token(token)
    if not data or "sub" not in data:
        return None
    return get_user_by_email(str(data["sub"]))


def save_ats_score(email: str, score: int, resume_text: str, job_description: str) -> None:
    """Save ATS score for a user."""
    user = get_user_by_email(email)
    if not user:
        return
    now = datetime.now(timezone.utc).isoformat()
    conn = _get_conn()
    try:
        conn.execute(
            "INSERT INTO ats_scores (user_id, score, resume_text, job_description, created_at) VALUES (?, ?, ?, ?, ?)",
            (user["id"], score, resume_text, job_description, now),
        )
        conn.commit()
    finally:
        conn.close()


def get_last_ats_score(email: str) -> Optional[int]:
    """Get the most recent ATS score for a user."""
    user = get_user_by_email(email)
    if not user:
        return None
    conn = _get_conn()
    try:
        cur = conn.execute(
            "SELECT score FROM ats_scores WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
            (user["id"],),
        )
        row = cur.fetchone()
    finally:
        conn.close()
    return row[0] if row else None


def save_interview_session(email: str, question_count: int, average_score: float) -> None:
    """Save an interview session."""
    user = get_user_by_email(email)
    if not user:
        return
    now = datetime.now(timezone.utc).isoformat()
    conn = _get_conn()
    try:
        conn.execute(
            "INSERT INTO interview_sessions (user_id, question_count, average_score, created_at) VALUES (?, ?, ?, ?)",
            (user["id"], question_count, average_score, now),
        )
        conn.commit()
    finally:
        conn.close()


def get_interview_stats(email: str) -> Tuple[int, float]:
    """Get total interview sessions count and average score."""
    user = get_user_by_email(email)
    if not user:
        return 0, 0.0
    conn = _get_conn()
    try:
        cur = conn.execute(
            "SELECT COUNT(*), AVG(average_score) FROM interview_sessions WHERE user_id = ?",
            (user["id"],),
        )
        row = cur.fetchone()
    finally:
        conn.close()
    count = row[0] or 0
    avg = row[1] or 0.0
    return count, float(avg)

