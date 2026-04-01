"""Pydantic schemas for HealthAI Coach API."""
from app.schemas.user import (
    ObjectifSante,
    UserCreate,
    UserRead,
    UserUpdate,
    ProfileRead,
    ProfileUpdate,
)
from app.schemas.tracking import (
    ObjectiveCreate,
    ObjectiveRead,
    ObjectiveUpdate,
    ProgressPhotoCreate,
    ProgressPhotoRead,
)
from app.schemas.pagination import PaginatedResponse
from app.schemas.error import ErrorDetail, ErrorResponse

__all__ = [
    # User schemas
    "ObjectifSante",
    "UserCreate",
    "UserRead",
    "UserUpdate",
    "ProfileRead",
    "ProfileUpdate",
    "ObjectiveCreate",
    "ObjectiveRead",
    "ObjectiveUpdate",
    "ProgressPhotoCreate",
    "ProgressPhotoRead",
    # Pagination
    "PaginatedResponse",
    # Error
    "ErrorDetail",
    "ErrorResponse",
]
