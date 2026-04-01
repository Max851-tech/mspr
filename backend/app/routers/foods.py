"""Public food search and retrieval endpoints."""
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.exceptions.food import FoodNotFound
from app.models.aliment import Aliment
from app.schemas.common import FacetResponse, FacetValue, SearchResponse
from app.schemas.food import FoodRead
from app.services.search import FuzzySearchService

router = APIRouter(
    prefix="/api/v1/foods",
    tags=["foods"],
    responses={
        404: {"description": "Food not found"},
    },
)


@router.get(
    "",
    response_model=SearchResponse[FoodRead],
    summary="Search or browse foods",
    description="Search foods by name with fuzzy matching, or browse alphabetically. Supports category filtering and facets.",
)
async def search_foods(
    db: Annotated[AsyncSession, Depends(get_db)],
    q: Annotated[Optional[str], Query(min_length=3)] = None,
    category: Annotated[Optional[str], Query()] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = 20,
) -> SearchResponse[FoodRead]:
    """Search or browse foods with pagination and facets.

    Args:
        q: Search query (min 3 chars). If not provided, browse mode is used.
        category: Comma-separated category names to filter by
        page: Page number (1-indexed)
        per_page: Items per page (max 100)

    Returns:
        SearchResponse with items, total, pagination info, and category facets
    """
    # Parse category filter (comma-separated)
    categories = [c.strip() for c in category.split(",")] if category else None

    # Calculate offset
    offset = (page - 1) * per_page

    # Initialize search service
    search_service = FuzzySearchService(db)

    # Execute search or browse
    if q:
        # Search mode: fuzzy matching
        items, total = await search_service.search_foods(
            query=q,
            categories=categories,
            offset=offset,
            limit=per_page,
        )
    else:
        # Browse mode: alphabetical
        items, total = await search_service.browse_foods(
            categories=categories,
            offset=offset,
            limit=per_page,
        )

    # Calculate facets (category counts)
    facet_stmt = (
        select(
            Aliment.categorie,
            func.count(Aliment.aliment_id).label("count"),
        )
        .where(Aliment.deleted_at.is_(None))
        .group_by(Aliment.categorie)
        .having(Aliment.categorie.isnot(None))
    )

    # Apply category filter to facets if provided
    if categories:
        facet_stmt = facet_stmt.where(Aliment.categorie.in_(categories))

    facet_result = await db.execute(facet_stmt)
    facet_rows = facet_result.all()

    facets = FacetResponse(
        categories=[
            FacetValue(name=row.categorie, count=row.count) for row in facet_rows
        ]
    )

    return SearchResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        facets=facets,
    )


@router.get(
    "/{food_id}",
    response_model=FoodRead,
    summary="Get food by ID",
    description="Returns a single food item by its ID.",
)
async def get_food(
    food_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> FoodRead:
    """Get a single food by ID.

    Returns:
        FoodRead schema

    Raises:
        FoodNotFound: If food doesn't exist or is deleted
    """
    result = await db.execute(
        select(Aliment).where(
            Aliment.aliment_id == food_id,
            Aliment.deleted_at.is_(None),
        )
    )
    food = result.scalar_one_or_none()
    if not food:
        raise FoodNotFound(food_id)
    return food
