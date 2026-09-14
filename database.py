"""SQLite storage for user accounts, profiles and sessions (stdlib only)."""
import os
import sqlite3
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "app.db")


@contextmanager
def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_db() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
        db.execute("""CREATE TABLE IF NOT EXISTS profiles(
            user_id INTEGER PRIMARY KEY,
            baby_name TEXT,
            due_date TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id))""")
        db.execute("""CREATE TABLE IF NOT EXISTS sessions(
            token TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")


def create_user(db, username: str, password_hash: str) -> int:
    cur = db.execute(
        "INSERT INTO users(username, password_hash) VALUES(?,?)",
        (username, password_hash),
    )
    return cur.lastrowid


def get_user_by_name(db, username: str):
    return db.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()


def user_for_token(db, token: str):
    return db.execute(
        """SELECT u.id, u.username FROM sessions s
           JOIN users u ON u.id = s.user_id WHERE s.token=?""",
        (token,),
    ).fetchone()


def get_profile(db, user_id: int) -> dict:
    row = db.execute(
        "SELECT baby_name, due_date FROM profiles WHERE user_id=?", (user_id,)
    ).fetchone()
    return {
        "baby_name": row["baby_name"] if row else None,
        "due_date": row["due_date"] if row else None,
    }


def save_profile(db, user_id: int, baby_name, due_date):
    db.execute(
        """INSERT INTO profiles(user_id, baby_name, due_date) VALUES(?,?,?)
           ON CONFLICT(user_id) DO UPDATE SET baby_name=excluded.baby_name, due_date=excluded.due_date""",
        (user_id, baby_name or None, due_date or None),
    )
