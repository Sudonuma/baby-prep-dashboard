"""SQLite storage for user accounts, profiles and sessions (stdlib only)."""
import json
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
        db.execute("""CREATE TABLE IF NOT EXISTS user_state(
            user_id INTEGER PRIMARY KEY,
            state_json TEXT NOT NULL,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
        db.execute("""CREATE TABLE IF NOT EXISTS password_resets(
            token_hash TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            expires_at TEXT NOT NULL,
            used INTEGER DEFAULT 0)""")
        # Migration for databases created before email recovery existed.
        try:
            db.execute("ALTER TABLE users ADD COLUMN email TEXT")
        except sqlite3.OperationalError:
            pass  # column already there


def get_state(db, user_id: int) -> dict:
    row = db.execute(
        "SELECT state_json FROM user_state WHERE user_id=?", (user_id,)
    ).fetchone()
    if not row:
        return {}
    try:
        state = json.loads(row["state_json"])
        return state if isinstance(state, dict) else {}
    except (ValueError, TypeError):
        return {}


def save_state(db, user_id: int, state: dict):
    db.execute(
        """INSERT INTO user_state(user_id, state_json, updated_at) VALUES(?,?,CURRENT_TIMESTAMP)
           ON CONFLICT(user_id) DO UPDATE SET state_json=excluded.state_json, updated_at=CURRENT_TIMESTAMP""",
        (user_id, json.dumps(state)),
    )


def create_user(db, username: str, password_hash: str, email=None) -> int:
    cur = db.execute(
        "INSERT INTO users(username, password_hash, email) VALUES(?,?,?)",
        (username, password_hash, email or None),
    )
    return cur.lastrowid


def get_user_by_name(db, username: str):
    return db.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()


def get_user_by_email(db, email: str):
    return db.execute(
        "SELECT * FROM users WHERE lower(email)=lower(?)", (email,)).fetchone()


def set_email(db, user_id: int, email):
    db.execute("UPDATE users SET email=? WHERE id=?", (email or None, user_id))


def set_password_hash(db, user_id: int, password_hash: str):
    db.execute("UPDATE users SET password_hash=? WHERE id=?", (password_hash, user_id))


def destroy_user_sessions(db, user_id: int):
    db.execute("DELETE FROM sessions WHERE user_id=?", (user_id,))


def add_password_reset(db, user_id: int, token_hash: str, expires_at: str):
    db.execute(
        "INSERT INTO password_resets(token_hash, user_id, expires_at) VALUES(?,?,?)",
        (token_hash, user_id, expires_at))


def get_password_reset(db, token_hash: str):
    return db.execute(
        "SELECT * FROM password_resets WHERE token_hash=?", (token_hash,)).fetchone()


def consume_password_reset(db, token_hash: str):
    db.execute("UPDATE password_resets SET used=1 WHERE token_hash=?", (token_hash,))


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
