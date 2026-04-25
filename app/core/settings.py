"""Runtime configuration loaded from environment variables."""
import os


def get_env() -> str:
    """Return deployment environment name (development, production, etc.)."""
    return os.getenv("ENV", "development").lower()


def is_production() -> bool:
    return get_env() in {"production", "prod"}


def get_secret_key() -> str:
    key = os.getenv("SECRET_KEY", "").strip()
    if not key:
        if is_production():
            raise RuntimeError("SECRET_KEY must be set in production")
        # Long enough for HS256 libraries that warn on short HMAC secrets (dev only).
        return "dev-insecure-secret-change-me-please-use-32plus-chars"
    if is_production() and key in {
        "change-me",
        "dev-insecure-secret-change-me",
        "dev-insecure-secret-change-me-please-use-32plus-chars",
    }:
        raise RuntimeError("SECRET_KEY must be changed from the default in production")
    return key


def get_admin_api_key() -> str | None:
    key = os.getenv("ADMIN_API_KEY", "").strip()
    return key or None


def get_access_token_expire_minutes() -> int:
    raw = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080").strip()
    try:
        value = int(raw)
    except ValueError:
        return 10080
    return max(5, min(value, 60 * 24 * 365))


def get_jwt_algorithm() -> str:
    return os.getenv("JWT_ALGORITHM", "HS256").strip() or "HS256"
