"""Pagination dependency."""
from typing import Annotated

from fastapi import Query


class PaginationParams:
    """Pagination query parameters dependency."""

    def __init__(
        self,
        page: Annotated[int, Query(ge=1, description="Page number")] = 1,
        limit: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 20,
    ):
        self.page = page
        self.limit = limit
        self.offset = (page - 1) * limit
