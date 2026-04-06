"""FastAPI dependencies for HealthAI Coach API."""
from app.dependencies.database import get_db
from app.dependencies.pagination import PaginationParams
from app.dependencies.security import require_admin_api_key

__all__ = [
    "get_db",
    "PaginationParams",
    "require_admin_api_key",
]
