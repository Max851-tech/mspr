"""Pagination schemas for API responses."""
from typing import Generic, TypeVar

from pydantic import BaseModel, computed_field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response schema."""
    items: list[T]
    total: int
    page: int
    limit: int

    @computed_field
    @property
    def pages(self) -> int:
        """Total number of pages."""
        if self.limit <= 0:
            return 0
        return (self.total + self.limit - 1) // self.limit

    @computed_field
    @property
    def has_next(self) -> bool:
        """Whether there is a next page."""
        return self.page < self.pages

    @computed_field
    @property
    def has_prev(self) -> bool:
        """Whether there is a previous page."""
        return self.page > 1
