"""Admin router for user management - read-only operations."""
import csv
import io
from datetime import date
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.dependencies.database import get_db
from app.dependencies.pagination import PaginationParams
from app.exceptions.user import UserNotFound
from app.models.profil_utilisateur import ProfilUtilisateur
from app.models.utilisateur import Utilisateur
from app.schemas.pagination import PaginatedResponse
from app.schemas.user import UserRead

router = APIRouter(
    prefix="/api/v1/admin/users",
    tags=["admin"],
    responses={
        404: {"description": "User not found"},
    },
)


@router.get(
    "",
    response_model=PaginatedResponse[UserRead],
    summary="List all users",
    description="Admin endpoint to list all users with optional filters.",
)
async def list_all_users(
    pagination: Annotated[PaginationParams, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
    role: Annotated[
        Optional[str],
        Query(description="Filter by role (ADMIN or UTILISATEUR)")
    ] = None,
    created_after: Annotated[
        Optional[date],
        Query(description="Filter by creation date (cree_le >= date)")
    ] = None,
    objectif: Annotated[
        Optional[str],
        Query(description="Filter by objectif_principal (requires profile)")
    ] = None,
) -> PaginatedResponse[UserRead]:
    """List all users with filters.

    - role: Filter by ADMIN or UTILISATEUR
    - created_after: Filter by cree_le >= date
    - objectif: Filter by objectif_principal (joins with profil_utilisateur)
    """
    # Build base query
    query = select(Utilisateur)

    # Apply role filter
    if role:
        query = query.where(Utilisateur.role == role)

    # Apply date filter
    if created_after:
        query = query.where(Utilisateur.cree_le >= created_after)

    # Apply objectif filter (requires join with profil_utilisateur)
    if objectif:
        query = query.join(
            ProfilUtilisateur,
            Utilisateur.utilisateur_id == ProfilUtilisateur.utilisateur_id
        ).where(ProfilUtilisateur.objectif_principal == objectif)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    # Get paginated results
    result = await db.execute(
        query.offset(pagination.offset).limit(pagination.limit)
    )
    users = result.scalars().all()

    return PaginatedResponse(
        items=list(users),
        total=total,
        page=pagination.page,
        limit=pagination.limit,
    )


@router.get(
    "/export",
    response_class=StreamingResponse,
    summary="Export users as CSV",
    description="Export all users as a downloadable CSV file.",
)
async def export_users_csv(
    db: Annotated[AsyncSession, Depends(get_db)],
    role: Annotated[
        Optional[str],
        Query(description="Filter by role (ADMIN or UTILISATEUR)")
    ] = None,
) -> StreamingResponse:
    """Export all users as CSV file.

    CSV columns: id, email, nom, role, statut, cree_le
    """
    query = select(Utilisateur)
    if role:
        query = query.where(Utilisateur.role == role)

    result = await db.execute(query)
    users = result.scalars().all()

    def generate_csv():
        output = io.StringIO()
        writer = csv.writer(output)

        # Header row
        writer.writerow(["id", "email", "nom", "role", "statut", "cree_le"])
        yield output.getvalue()
        output.seek(0)
        output.truncate(0)

        # Data rows
        for user in users:
            writer.writerow([
                user.utilisateur_id,
                user.email or "",
                user.nom_utilisateur,
                user.role,
                user.statut,
                user.cree_le.isoformat() if user.cree_le else "",
            ])
            yield output.getvalue()
            output.seek(0)
            output.truncate(0)

    return StreamingResponse(
        generate_csv(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=users.csv"},
    )


@router.get(
    "/{user_id}",
    response_model=UserRead,
    summary="Get user by ID (admin view)",
    description="Admin endpoint to get a single user by ID.",
)
async def get_user_admin(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserRead:
    """Get a single user by ID (admin view)."""
    result = await db.execute(
        select(Utilisateur).where(Utilisateur.utilisateur_id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise UserNotFound(user_id)
    return user
