"""User-related exceptions."""
from fastapi import HTTPException, status


class UserException(HTTPException):
    """Base exception for user domain with structured error format."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int,
        details: dict | None = None
    ):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(
            status_code=status_code,
            detail={
                "error": {
                    "code": code,
                    "message": message,
                    "details": self.details
                }
            }
        )


class UserNotFound(UserException):
    """Raised when a user is not found."""

    def __init__(self, user_id: int):
        super().__init__(
            code="USER_NOT_FOUND",
            message=f"User with id {user_id} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"user_id": user_id}
        )


class EmailAlreadyExists(UserException):
    """Raised when an email is already registered."""

    def __init__(self, email: str):
        super().__init__(
            code="EMAIL_ALREADY_EXISTS",
            message=f"Email {email} is already registered",
            status_code=status.HTTP_409_CONFLICT,
            details={"email": email}
        )


class ProfileNotFound(UserException):
    """Raised when a user profile is not found."""

    def __init__(self, user_id: int):
        super().__init__(
            code="PROFILE_NOT_FOUND",
            message=f"Profile for user {user_id} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"user_id": user_id}
        )
