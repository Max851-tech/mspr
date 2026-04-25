"""HTTP routes (FastAPI routers)."""

from app.api.routes import admin, auth, exercises, foods, users

__all__ = ["admin", "auth", "exercises", "foods", "users"]

