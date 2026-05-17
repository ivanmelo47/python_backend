from datetime import datetime, timedelta, timezone

import jwt

from app.core.settings import settings


def create_access_token(*, subject: str, email: str) -> tuple[str, int]:
    expires_minutes = settings.jwt_access_token_expire_minutes
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)

    payload = {
        "sub": subject,
        "email": email,
        "exp": expires_at,
        "type": "access",
    }

    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token, expires_minutes * 60


def create_refresh_token(*, subject: str, email: str, session_id: int | None = None) -> tuple[str, int]:
    expires_minutes = settings.jwt_refresh_token_expire_minutes
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)

    payload = {
        "sub": subject,
        "email": email,
        "exp": expires_at,
        "type": "refresh",
    }
    if session_id is not None:
        payload["session_id"] = session_id

    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token, expires_minutes * 60


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
