"""Food-related exceptions."""
from fastapi import HTTPException, status


class FoodException(HTTPException):
    """Base exception for food domain with structured error format."""

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


class FoodNotFound(FoodException):
    """Raised when a food item is not found."""

    def __init__(self, food_id: int):
        super().__init__(
            code="FOOD_NOT_FOUND",
            message=f"Food with id {food_id} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"food_id": food_id},
        )


class FoodAlreadyExists(FoodException):
    """Raised when a food item with the same name already exists."""

    def __init__(self, nom: str):
        super().__init__(
            code="FOOD_ALREADY_EXISTS",
            message=f"Food with name '{nom}' already exists",
            status_code=status.HTTP_409_CONFLICT,
            details={"nom": nom},
        )
