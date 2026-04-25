"""User CRUD router with profile sub-resource."""
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.database import get_db
from app.api.dependencies.pagination import PaginationParams
from app.exceptions.user import ProfileNotFound, UserNotFound
from app.models.objectif_utilisateur import ObjectifUtilisateur
from app.models.profil_utilisateur import ProfilUtilisateur
from app.models.progression_photo import ProgressionPhoto
from app.models.utilisateur import Utilisateur
from app.schemas.pagination import PaginatedResponse
from app.schemas.tracking import (
    ObjectiveCreate,
    ObjectiveRead,
    ObjectiveUpdate,
    ProgressPhotoCreate,
    ProgressPhotoRead,
)
from app.schemas.user import (
    ProfileRead,
    ProfileUpdate,
    UserCreate,
    UserRead,
    UserUpdate,
)
from app.services.account import create_user_account
from app.services.tracking import TrackingService

router = APIRouter(
    prefix="/api/v1/users",
    tags=["users"],
    responses={
        404: {"description": "User not found"},
        409: {"description": "Email already exists"},
    },
)


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Creates a new user account with email, password, and name.",
)
async def create_user(
    user_data: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserRead:
    """Create a new user.

    - Check email uniqueness
    - Create user with email and nom_utilisateur
    - Store a bcrypt password hash
    """
    user = await create_user_account(db, user_data)
    return user


@router.get(
    "",
    response_model=PaginatedResponse[UserRead],
    summary="List all users",
    description="Returns paginated list of users.",
)
async def list_users(
    pagination: Annotated[PaginationParams, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PaginatedResponse[UserRead]:
    """List all users with pagination."""
    # Get total count
    count_result = await db.execute(select(func.count(Utilisateur.utilisateur_id)))
    total = count_result.scalar() or 0

    # Get paginated results
    result = await db.execute(
        select(Utilisateur)
        .offset(pagination.offset)
        .limit(pagination.limit)
    )
    users = result.scalars().all()

    return PaginatedResponse(
        items=list(users),
        total=total,
        page=pagination.page,
        limit=pagination.limit,
    )


@router.get(
    "/{user_id}",
    response_model=UserRead,
    summary="Get user by ID",
    description="Returns a single user by their ID.",
)
async def get_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserRead:
    """Get a single user by ID."""
    result = await db.execute(
        select(Utilisateur).where(Utilisateur.utilisateur_id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise UserNotFound(user_id)
    return user


@router.put(
    "/{user_id}",
    response_model=UserRead,
    summary="Update user",
    description="Updates user fields. Only provided fields are updated.",
)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserRead:
    """Update user fields."""
    result = await db.execute(
        select(Utilisateur).where(Utilisateur.utilisateur_id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise UserNotFound(user_id)

    # Update only provided fields
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    return user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
    description="Deletes a user by their ID.",
)
async def delete_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete a user by ID."""
    result = await db.execute(
        select(Utilisateur).where(Utilisateur.utilisateur_id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise UserNotFound(user_id)

    await db.delete(user)
    await db.commit()


# ==========================================
# Profile sub-resource
# ==========================================


@router.get(
    "/{user_id}/profile",
    response_model=ProfileRead,
    summary="Get user profile",
    description="Returns the user's profile with biometric data and objectives.",
)
async def get_user_profile(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ProfileRead:
    """Get user profile by user ID."""
    result = await db.execute(
        select(ProfilUtilisateur).where(ProfilUtilisateur.utilisateur_id == user_id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise ProfileNotFound(user_id)
    return profile


@router.put(
    "/{user_id}/profile",
    response_model=ProfileRead,
    summary="Update user profile",
    description="Updates the user's profile. Creates profile if it doesn't exist (upsert).",
)
async def update_user_profile(
    user_id: int,
    profile_data: ProfileUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ProfileRead:
    """Update or create user profile (upsert pattern)."""
    # First verify user exists
    user_result = await db.execute(
        select(Utilisateur).where(Utilisateur.utilisateur_id == user_id)
    )
    if not user_result.scalar_one_or_none():
        raise UserNotFound(user_id)

    # Get or create profile
    result = await db.execute(
        select(ProfilUtilisateur).where(ProfilUtilisateur.utilisateur_id == user_id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        # Create profile if doesn't exist
        profile = ProfilUtilisateur(utilisateur_id=user_id)
        db.add(profile)

    # Update only provided fields
    update_data = profile_data.model_dump(exclude_unset=True)

    # Convert enum values to strings for storage
    if "objectif_principal" in update_data and update_data["objectif_principal"]:
        update_data["objectif_principal"] = update_data["objectif_principal"].value
    if "objectifs_secondaires" in update_data and update_data["objectifs_secondaires"]:
        update_data["objectifs_secondaires"] = [
            obj.value for obj in update_data["objectifs_secondaires"]
        ]

    for field, value in update_data.items():
        setattr(profile, field, value)

    await db.commit()
    await db.refresh(profile)
    return profile


# ==========================================
# Objectives sub-resource
# ==========================================


@router.get(
    "/{user_id}/objectives",
    response_model=list[ObjectiveRead],
    summary="List user objectives",
    description="Returns all objectives for a user, ordered by most recent start date.",
)
async def list_user_objectives(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[ObjectiveRead]:
    """List all objectives for a user."""
    tracking_service = TrackingService(db)
    await tracking_service.ensure_user_exists(user_id)

    result = await db.execute(
        select(ObjectifUtilisateur)
        .where(ObjectifUtilisateur.utilisateur_id == user_id)
        .order_by(ObjectifUtilisateur.date_debut.desc(), ObjectifUtilisateur.objectif_id.desc())
    )
    return list(result.scalars().all())


@router.post(
    "/{user_id}/objectives",
    response_model=ObjectiveRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create user objective",
    description="Creates a new objective for the user. If active, previous active objectives are deactivated.",
)
async def create_user_objective(
    user_id: int,
    objective_data: ObjectiveCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ObjectiveRead:
    """Create a new objective for a user."""
    tracking_service = TrackingService(db)
    await tracking_service.ensure_user_exists(user_id)

    objective = ObjectifUtilisateur(
        utilisateur_id=user_id,
        **objective_data.model_dump(),
    )
    if objective.actif_unique:
        await tracking_service.deactivate_other_objectives(user_id)

    db.add(objective)
    await db.commit()
    await db.refresh(objective)
    return objective


@router.get(
    "/{user_id}/objectives/{objective_id}",
    response_model=ObjectiveRead,
    summary="Get user objective",
    description="Returns one objective belonging to the given user.",
)
async def get_user_objective(
    user_id: int,
    objective_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ObjectiveRead:
    """Get one user objective."""
    tracking_service = TrackingService(db)
    await tracking_service.ensure_user_exists(user_id)
    return await tracking_service.get_objective(user_id, objective_id)


@router.put(
    "/{user_id}/objectives/{objective_id}",
    response_model=ObjectiveRead,
    summary="Update user objective",
    description="Updates an objective. Activating it deactivates other active objectives for the same user.",
)
async def update_user_objective(
    user_id: int,
    objective_id: int,
    objective_data: ObjectiveUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ObjectiveRead:
    """Update one user objective."""
    tracking_service = TrackingService(db)
    await tracking_service.ensure_user_exists(user_id)
    objective = await tracking_service.get_objective(user_id, objective_id)

    update_data = objective_data.model_dump(exclude_unset=True)
    if update_data.get("actif_unique") is True:
        await tracking_service.deactivate_other_objectives(user_id, keep_objective_id=objective_id)

    for field, value in update_data.items():
        setattr(objective, field, value)

    await db.commit()
    await db.refresh(objective)
    return objective


# ==========================================
# Progress photos sub-resource
# ==========================================


@router.get(
    "/{user_id}/progress-photos",
    response_model=list[ProgressPhotoRead],
    summary="List progress photos",
    description="Returns progress photos for a user, optionally filtered by objective.",
)
async def list_progress_photos(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    objective_id: Annotated[
        int | None,
        Query(description="Optional objective filter for progress photos"),
    ] = None,
) -> list[ProgressPhotoRead]:
    """List progress photos for a user."""
    tracking_service = TrackingService(db)
    await tracking_service.ensure_user_exists(user_id)

    stmt = (
        select(ProgressionPhoto)
        .where(ProgressionPhoto.utilisateur_id == user_id)
        .order_by(ProgressionPhoto.prise_le.desc(), ProgressionPhoto.photo_id.desc())
    )
    if objective_id is not None:
        await tracking_service.get_objective(user_id, objective_id)
        stmt = stmt.where(ProgressionPhoto.objectif_id == objective_id)

    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.post(
    "/{user_id}/progress-photos",
    response_model=ProgressPhotoRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create progress photo",
    description="Creates a progress photo linked to one of the user's objectives.",
)
async def create_progress_photo(
    user_id: int,
    photo_data: ProgressPhotoCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ProgressPhotoRead:
    """Create a progress photo for a user."""
    tracking_service = TrackingService(db)
    await tracking_service.ensure_user_exists(user_id)
    await tracking_service.get_objective(user_id, photo_data.objectif_id)

    photo = ProgressionPhoto(
        utilisateur_id=user_id,
        **photo_data.model_dump(),
    )
    db.add(photo)
    await db.commit()
    await db.refresh(photo)
    return photo


@router.get(
    "/{user_id}/progress-photos/{photo_id}",
    response_model=ProgressPhotoRead,
    summary="Get progress photo",
    description="Returns one progress photo belonging to the given user.",
)
async def get_progress_photo(
    user_id: int,
    photo_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ProgressPhotoRead:
    """Get one progress photo."""
    tracking_service = TrackingService(db)
    await tracking_service.ensure_user_exists(user_id)
    return await tracking_service.get_progress_photo(user_id, photo_id)

