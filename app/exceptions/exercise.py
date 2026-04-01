"""Exercise-related exceptions."""
from fastapi import HTTPException, status


class ExerciseException(HTTPException):
    """Base exception for exercise domain with structured error format."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int,
        details: dict | None = None,
    ):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(
            status_code=status_code,
            detail={
                "error": {"code": code, "message": message, "details": self.details}
            },
        )


class ExerciseNotFound(ExerciseException):
    """Raised when an exercise is not found."""

    def __init__(self, exercise_id: int):
        super().__init__(
            code="EXERCISE_NOT_FOUND",
            message=f"Exercise with id {exercise_id} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"exercice_id": exercise_id},
        )


class ExerciseAlreadyExists(ExerciseException):
    """Raised when an exercise with the same name already exists."""

    def __init__(self, nom: str):
        super().__init__(
            code="EXERCISE_ALREADY_EXISTS",
            message=f"Exercise with name '{nom}' already exists",
            status_code=status.HTTP_409_CONFLICT,
            details={"nom": nom},
        )
