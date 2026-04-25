"""JWT access tokens."""
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from app.core.settings import get_access_token_expire_minutes, get_jwt_algorithm, get_secret_key


def create_access_token(*, subject: str, extra_claims: dict[str, Any] | None = None) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=get_access_token_expire_minutes())
    payload: dict[str, Any] = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": expire,
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, get_secret_key(), algorithm=get_jwt_algorithm())


def decode_access_token(token: str) -> dict[str, Any]:
    return jwt.decode(
        token,
        get_secret_key(),
        algorithms=[get_jwt_algorithm()],
        options={"require": ["exp", "sub"]},
    )
