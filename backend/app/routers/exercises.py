"""Public exercise search and retrieval endpoints."""
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.exceptions.exercise import ExerciseNotFound
from app.models.exercice import Exercice
from app.schemas.common import FacetResponse, FacetValue, SearchResponse
from app.schemas.exercise import ExerciseRead
from app.services.search import FuzzySearchService

router = APIRouter(
    prefix="/api/v1/exercises",
    tags=["exercises"],
    responses={
        404: {"description": "Exercise not found"},
    },
)


@router.get(
    "",
    response_model=SearchResponse[ExerciseRead],
    summary="Search or browse exercises",
    description="Search exercises by name with fuzzy matching, or browse alphabetically. Supports multi-field filtering (muscle group, difficulty, equipment) and facets.",
)
async def search_exercises(
    db: Annotated[AsyncSession, Depends(get_db)],
    q: Annotated[Optional[str], Query(min_length=3)] = None,
    muscle_group: Annotated[Optional[str], Query()] = None,
    difficulty: Annotated[Optional[str], Query()] = None,
    equipment: Annotated[Optional[str], Query()] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = 20,
) -> SearchResponse[ExerciseRead]:
    """Search or browse exercises with pagination and facets.

    Args:
        q: Search query (min 3 chars). If not provided, browse mode is used.
        muscle_group: Comma-separated muscle_cible values to filter by
        difficulty: Comma-separated difficulte values to filter by
        equipment: Comma-separated equipement values to filter by
        page: Page number (1-indexed)
        per_page: Items per page (max 100)

    Returns:
        SearchResponse with items, total, pagination info, and facets
    """
    # Parse filters (comma-separated)
    muscle_groups = [m.strip() for m in muscle_group.split(",")] if muscle_group else None
    difficulties = [d.strip() for d in difficulty.split(",")] if difficulty else None
    equipments = [e.strip() for e in equipment.split(",")] if equipment else None

    # Calculate offset
    offset = (page - 1) * per_page

    # Initialize search service
    search_service = FuzzySearchService(db)

    # Execute search or browse
    if q:
        # Search mode: fuzzy matching
        items, total = await search_service.search_exercises(
            query=q,
            muscle_groups=muscle_groups,
            difficulties=difficulties,
            equipments=equipments,
            offset=offset,
            limit=per_page,
        )
    else:
        # Browse mode: alphabetical
        items, total = await search_service.browse_exercises(
            muscle_groups=muscle_groups,
            difficulties=difficulties,
            equipments=equipments,
            offset=offset,
            limit=per_page,
        )

    # Calculate facets (3 separate GROUP BY queries)
    # Base query for facets: not deleted
    base_facet_filter = Exercice.deleted_at.is_(None)

    # Facet 1: muscle_groups
    muscle_stmt = (
        select(
            Exercice.muscle_cible,
            func.count(Exercice.exercice_id).label("count"),
        )
        .where(base_facet_filter)
        .group_by(Exercice.muscle_cible)
        .having(Exercice.muscle_cible.isnot(None))
    )
    if muscle_groups:
        muscle_stmt = muscle_stmt.where(Exercice.muscle_cible.in_(muscle_groups))
    muscle_result = await db.execute(muscle_stmt)
    muscle_facets = [
        FacetValue(name=row.muscle_cible, count=row.count)
        for row in muscle_result.all()
    ]

    # Facet 2: difficulties
    difficulty_stmt = (
        select(
            Exercice.difficulte,
            func.count(Exercice.exercice_id).label("count"),
        )
        .where(base_facet_filter)
        .group_by(Exercice.difficulte)
        .having(Exercice.difficulte.isnot(None))
    )
    if difficulties:
        difficulty_stmt = difficulty_stmt.where(Exercice.difficulte.in_(difficulties))
    difficulty_result = await db.execute(difficulty_stmt)
    difficulty_facets = [
        FacetValue(name=row.difficulte, count=row.count)
        for row in difficulty_result.all()
    ]

    # Facet 3: equipments
    equipment_stmt = (
        select(
            Exercice.equipement,
            func.count(Exercice.exercice_id).label("count"),
        )
        .where(base_facet_filter)
        .group_by(Exercice.equipement)
        .having(Exercice.equipement.isnot(None))
    )
    if equipments:
        equipment_stmt = equipment_stmt.where(Exercice.equipement.in_(equipments))
    equipment_result = await db.execute(equipment_stmt)
    equipment_facets = [
        FacetValue(name=row.equipement, count=row.count)
        for row in equipment_result.all()
    ]

    facets = FacetResponse(
        muscle_groups=muscle_facets,
        difficulties=difficulty_facets,
        equipments=equipment_facets,
    )

    return SearchResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        facets=facets,
    )


@router.get(
    "/{exercise_id}",
    response_model=ExerciseRead,
    summary="Get exercise by ID",
    description="Returns a single exercise by its ID.",
)
async def get_exercise(
    exercise_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ExerciseRead:
    """Get a single exercise by ID.

    Returns:
        ExerciseRead schema

    Raises:
        ExerciseNotFound: If exercise doesn't exist or is deleted
    """
    result = await db.execute(
        select(Exercice).where(
            Exercice.exercice_id == exercise_id,
            Exercice.deleted_at.is_(None),
        )
    )
    exercise = result.scalar_one_or_none()
    if not exercise:
        raise ExerciseNotFound(exercise_id)
    return exercise
