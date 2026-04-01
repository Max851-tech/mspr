"""Fuzzy search service using two-stage filtering."""
from typing import Optional

from rapidfuzz import fuzz
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.aliment import Aliment
from app.models.exercice import Exercice


class FuzzySearchService:
    """Two-stage fuzzy search: SQL pre-filter + RapidFuzz scoring.

    Stage 1: MySQL LIKE query reduces candidates to manageable set
    Stage 2: RapidFuzz ranks results by relevance
    """

    MIN_QUERY_LENGTH = 3  # Minimum chars required for search
    FUZZY_THRESHOLD = 60  # Minimum RapidFuzz score (0-100)
    CANDIDATE_LIMIT = 500  # Max candidates from SQL pre-filter

    def __init__(self, db: AsyncSession):
        self.db = db

    async def search_foods(
        self,
        query: str,
        categories: Optional[list[str]] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Aliment], int]:
        """Search foods by name with fuzzy matching and optional category filter.

        Args:
            query: Search query (min 3 chars)
            categories: Optional list of category names to filter by
            offset: Pagination offset
            limit: Pagination limit

        Returns:
            Tuple of (items, total_count)
        """
        # Require minimum query length
        if len(query) < self.MIN_QUERY_LENGTH:
            return [], 0

        # Stage 1: SQL pre-filter with LIKE (case-insensitive)
        stmt = (
            select(Aliment)
            .where(Aliment.deleted_at.is_(None))
            .where(
                or_(
                    Aliment.nom.ilike(f"%{query}%"),
                    Aliment.categorie.ilike(f"%{query}%"),
                )
            )
        )

        # Apply category filter if provided
        if categories:
            stmt = stmt.where(Aliment.categorie.in_(categories))

        # Limit candidates for performance
        stmt = stmt.limit(self.CANDIDATE_LIMIT)

        result = await self.db.execute(stmt)
        candidates = list(result.scalars().all())

        # If no candidates, return empty
        if not candidates:
            return [], 0

        # Stage 2: RapidFuzz scoring
        scored_results = []
        for food in candidates:
            # Score against nom (primary)
            nom_score = fuzz.partial_ratio(query.lower(), (food.nom or "").lower())
            # Score against categorie (secondary)
            cat_score = (
                fuzz.partial_ratio(query.lower(), (food.categorie or "").lower())
                if food.categorie
                else 0
            )
            # Take max score
            best_score = max(nom_score, cat_score)

            if best_score >= self.FUZZY_THRESHOLD:
                scored_results.append((food, best_score))

        # Sort by score descending
        scored_results.sort(key=lambda x: x[1], reverse=True)

        # Apply pagination
        total = len(scored_results)
        items = [food for food, _ in scored_results[offset : offset + limit]]

        return items, total

    async def browse_foods(
        self,
        categories: Optional[list[str]] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Aliment], int]:
        """Browse foods alphabetically without search query.

        Args:
            categories: Optional list of category names to filter by
            offset: Pagination offset
            limit: Pagination limit

        Returns:
            Tuple of (items, total_count)
        """
        # Base query: not deleted, alphabetical order
        stmt = (
            select(Aliment)
            .where(Aliment.deleted_at.is_(None))
            .order_by(Aliment.nom)
        )

        # Apply category filter if provided
        if categories:
            stmt = stmt.where(Aliment.categorie.in_(categories))

        # Get total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar() or 0

        # Get paginated results
        stmt = stmt.offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        items = list(result.scalars().all())

        return items, total

    async def search_exercises(
        self,
        query: str,
        muscle_groups: Optional[list[str]] = None,
        difficulties: Optional[list[str]] = None,
        equipments: Optional[list[str]] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Exercice], int]:
        """Search exercises by name with fuzzy matching and optional filters.

        Args:
            query: Search query (min 3 chars)
            muscle_groups: Optional list of muscle_cible values to filter by
            difficulties: Optional list of difficulte values to filter by
            equipments: Optional list of equipement values to filter by
            offset: Pagination offset
            limit: Pagination limit

        Returns:
            Tuple of (items, total_count)
        """
        # Require minimum query length
        if len(query) < self.MIN_QUERY_LENGTH:
            return [], 0

        # Stage 1: SQL pre-filter with LIKE (case-insensitive)
        stmt = (
            select(Exercice)
            .where(Exercice.deleted_at.is_(None))
            .where(Exercice.nom.ilike(f"%{query}%"))
        )

        # Apply filters (multi-select with IN clause, AND logic between fields)
        if muscle_groups:
            stmt = stmt.where(Exercice.muscle_cible.in_(muscle_groups))
        if difficulties:
            stmt = stmt.where(Exercice.difficulte.in_(difficulties))
        if equipments:
            stmt = stmt.where(Exercice.equipement.in_(equipments))

        # Limit candidates for performance
        stmt = stmt.limit(self.CANDIDATE_LIMIT)

        result = await self.db.execute(stmt)
        candidates = list(result.scalars().all())

        # If no candidates, return empty
        if not candidates:
            return [], 0

        # Stage 2: RapidFuzz scoring
        scored_results = []
        for exercise in candidates:
            # Score against nom only
            nom_score = fuzz.partial_ratio(query.lower(), (exercise.nom or "").lower())

            if nom_score >= self.FUZZY_THRESHOLD:
                scored_results.append((exercise, nom_score))

        # Sort by score descending
        scored_results.sort(key=lambda x: x[1], reverse=True)

        # Apply pagination
        total = len(scored_results)
        items = [exercise for exercise, _ in scored_results[offset : offset + limit]]

        return items, total

    async def browse_exercises(
        self,
        muscle_groups: Optional[list[str]] = None,
        difficulties: Optional[list[str]] = None,
        equipments: Optional[list[str]] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Exercice], int]:
        """Browse exercises alphabetically without search query.

        Args:
            muscle_groups: Optional list of muscle_cible values to filter by
            difficulties: Optional list of difficulte values to filter by
            equipments: Optional list of equipement values to filter by
            offset: Pagination offset
            limit: Pagination limit

        Returns:
            Tuple of (items, total_count)
        """
        # Base query: not deleted, alphabetical order
        stmt = (
            select(Exercice)
            .where(Exercice.deleted_at.is_(None))
            .order_by(Exercice.nom)
        )

        # Apply filters
        if muscle_groups:
            stmt = stmt.where(Exercice.muscle_cible.in_(muscle_groups))
        if difficulties:
            stmt = stmt.where(Exercice.difficulte.in_(difficulties))
        if equipments:
            stmt = stmt.where(Exercice.equipement.in_(equipments))

        # Get total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar() or 0

        # Get paginated results
        stmt = stmt.offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        items = list(result.scalars().all())

        return items, total
