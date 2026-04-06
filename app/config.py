import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    env: str
    secret_key: str
    admin_api_key: str
    cors_allowed_origins: list[str]


def _split_csv(value: str) -> list[str]:
    return [v.strip() for v in value.split(",") if v.strip()]


def get_settings() -> Settings:
    env = os.getenv("ENV", "development").lower()
    secret_key = os.getenv("SECRET_KEY", "change-me")
    admin_api_key = os.getenv("ADMIN_API_KEY", "dev-admin-key")
    cors_allowed_origins = _split_csv(os.getenv("CORS_ALLOWED_ORIGINS", ""))

    return Settings(
        env=env,
        secret_key=secret_key,
        admin_api_key=admin_api_key,
        cors_allowed_origins=cors_allowed_origins,
    )

