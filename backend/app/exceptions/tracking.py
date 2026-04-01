"""Objective and progress photo exceptions."""
from fastapi import status

from app.exceptions.user import UserException


class TrackingException(UserException):
    """Base exception for user tracking resources."""


class ObjectiveNotFound(TrackingException):
    """Raised when a user objective is not found."""

    def __init__(self, objective_id: int):
        super().__init__(
            code="OBJECTIVE_NOT_FOUND",
            message=f"Objective with id {objective_id} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"objectif_id": objective_id},
        )


class ProgressPhotoNotFound(TrackingException):
    """Raised when a progress photo is not found."""

    def __init__(self, photo_id: int):
        super().__init__(
            code="PROGRESS_PHOTO_NOT_FOUND",
            message=f"Progress photo with id {photo_id} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"photo_id": photo_id},
        )
