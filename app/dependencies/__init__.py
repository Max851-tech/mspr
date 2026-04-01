"""FastAPI dependencies for HealthAI Coach API."""
from app.dependencies.database import get_db
from app.dependencies.pagination import PaginationParams

__all__ = [
    "get_db",
    "PaginationParams",
]
