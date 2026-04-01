"""Common schemas shared across the API."""
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class FacetValue(BaseModel):
    """Single facet value with count."""

    name: str
    count: int


class FacetResponse(BaseModel):
    """Facets for filtering search results."""

    categories: list[FacetValue] = []
    muscle_groups: list[FacetValue] = []
    difficulties: list[FacetValue] = []
    equipments: list[FacetValue] = []


class Warning(BaseModel):
    """Validation warning (non-blocking)."""

    field: str
    message: str
    code: str


class SearchResponse(BaseModel, Generic[T]):
    """Search response with items, pagination, and facets."""

    items: list[T]
    total: int
    page: int
    per_page: int
    facets: FacetResponse = FacetResponse()


class ResponseWithWarnings(BaseModel, Generic[T]):
    """Wrapper for responses that include validation warnings."""

    data: T
    warnings: list[Warning] = []
