"""Bulk operation schemas for batch processing."""
from enum import Enum
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class BulkAction(str, Enum):
    """Type of bulk operation."""

    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class BulkItem(BaseModel, Generic[T]):
    """Single item in a bulk operation request."""

    action: BulkAction
    data: Optional[T] = None  # Required for CREATE/UPDATE, not for DELETE
    id: Optional[int] = None  # Required for UPDATE/DELETE, not for CREATE


class BulkItemResult(BaseModel):
    """Result for a single bulk operation item."""

    index: int
    success: bool
    id: Optional[int] = None  # Set on success
    error: Optional[str] = None  # Set on failure
    warnings: list[str] = []  # Validation warnings (non-blocking)


class BulkRequest(BaseModel, Generic[T]):
    """Request for bulk operations."""

    items: list[BulkItem[T]]


class BulkResponse(BaseModel):
    """Response for bulk operations with per-item results."""

    total: int
    succeeded: int
    failed: int
    results: list[BulkItemResult]
