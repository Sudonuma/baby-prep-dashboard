"""Password hashing and cookie sessions (stdlib only)."""
import hashlib
import hmac
import secrets

from fastapi import Request

from database import get_db, get_user_by_email, get_users_by_name, user_for_token

PBKDF2_ITERATIONS = 240_000
SESSION_COOKIE = "baby_session"


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), bytes.fromhex(salt), PBKDF2_ITERATIONS
    ).hex()
    return f"{salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt, digest = stored.split("$", 1)
    except ValueError:
        return False
    candidate = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), bytes.fromhex(salt), PBKDF2_ITERATIONS
    ).hex()
    return hmac.compare_digest(candidate, digest)


def authenticate(db, identifier: str, password: str):
    """Log in by email or username. Returns (user, error_message)."""
    identifier = identifier.strip()
    if "@" in identifier:
        user = get_user_by_email(db, identifier)
        if user and verify_password(password, user["password_hash"]):
            return user, None
        return None, "Wrong email or password."
    matches = get_users_by_name(db, identifier)
    if len(matches) > 1:
        return None, "Several accounts use that name — please log in with your email."
    if matches and verify_password(password, matches[0]["password_hash"]):
        return matches[0], None
    return None, "Wrong username or password."


def create_session(db, user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    db.execute("INSERT INTO sessions(token, user_id) VALUES(?,?)", (token, user_id))
    return token


def destroy_session(db, token: str):
    db.execute("DELETE FROM sessions WHERE token=?", (token,))


def current_user(request: Request):
    """Return the logged-in user row (id, username) or None."""
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        return None
    with get_db() as db:
        return user_for_token(db, token)
