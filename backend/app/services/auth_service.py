from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hmac
import secrets

from ..data import ACTIVE_SESSIONS, STUDENTS, USERS, hash_password


SESSION_TTL_HOURS = 12


def find_user_by_email(email: str) -> dict | None:
    lowered_email = email.strip().lower()
    for user in USERS.values():
        if user["email"].lower() == lowered_email:
            return user
    return None


def verify_password(password: str, expected_hash: str) -> bool:
    return hmac.compare_digest(hash_password(password), expected_hash)


def authenticate_user(email: str, password: str) -> dict | None:
    user = find_user_by_email(email)
    if not user:
        return None

    if not verify_password(password, user["password_hash"]):
        return None

    return user


def create_session(user_id: str) -> str:
    token = secrets.token_urlsafe(32)
    ACTIVE_SESSIONS[token] = {
        "user_id": user_id,
        "created_at": datetime.now(timezone.utc),
        "expires_at": datetime.now(timezone.utc) + timedelta(hours=SESSION_TTL_HOURS),
    }
    return token


def revoke_session(token: str) -> None:
    ACTIVE_SESSIONS.pop(token, None)


def get_user_by_id(user_id: str) -> dict | None:
    return USERS.get(user_id)


def get_user_from_token(token: str) -> dict | None:
    session = ACTIVE_SESSIONS.get(token)
    if not session:
        return None

    if session["expires_at"] < datetime.now(timezone.utc):
        ACTIVE_SESSIONS.pop(token, None)
        return None

    return get_user_by_id(session["user_id"])


def serialize_user(user: dict) -> dict:
    student = STUDENTS.get(user.get("student_id")) if user.get("student_id") else None
    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "student_id": user.get("student_id"),
        "course_id": student["course_id"] if student else None,
        "skill_level": student["skill_level"] if student else None,
    }
