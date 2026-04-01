"""Custom exceptions for HealthAI Coach API."""
from app.exceptions.user import (
    UserException,
    UserNotFound,
    EmailAlreadyExists,
    ProfileNotFound,
)
from app.exceptions.tracking import (
    TrackingException,
    ObjectiveNotFound,
    ProgressPhotoNotFound,
)

__all__ = [
    "UserException",
    "UserNotFound",
    "EmailAlreadyExists",
    "ProfileNotFound",
    "TrackingException",
    "ObjectiveNotFound",
    "ProgressPhotoNotFound",
]
