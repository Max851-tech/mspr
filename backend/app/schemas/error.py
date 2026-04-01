"""Error response schemas."""
from typing import Any

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Structured error detail."""
    code: str
    message: str
    details: dict[str, Any] = {}


class ErrorResponse(BaseModel):
    """Structured error response."""
    error: ErrorDetail
