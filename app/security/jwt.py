from datetime import UTC, datetime, timedelta
from typing import Any

import jwt

from app.config.settings import settings


def create_access_token(*, subject: str, role: str, expires_minutes: int | None = None) -> str:
    """
    Create a signed JWT access token with subject (user id) and role.
    """
    now = datetime.now(UTC)
    exp_minutes = expires_minutes or settings.JWT_ACCESS_EXPIRES_MINUTES
    expire = now + timedelta(minutes=exp_minutes)
    payload: dict[str, Any] = {
        "sub": subject,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token


def decode_token(token: str) -> dict[str, Any]:
    """
    Decode and validate a JWT. Raises jwt exceptions on failure.
    """
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
