"""Service layer for user objectives and progress photos."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.tracking import ObjectiveNotFound, ProgressPhotoNotFound
from app.exceptions.user import UserNotFound
from app.models.objectif_utilisateur import ObjectifUtilisateur
from app.models.progression_photo import ProgressionPhoto
from app.models.utilisateur import Utilisateur


class TrackingService:
    """Business logic for goal tracking resources."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def ensure_user_exists(self, user_id: int) -> None:
        """Ensure the parent user exists before working with nested resources."""
        result = await self.db.execute(
            select(Utilisateur.utilisateur_id).where(Utilisateur.utilisateur_id == user_id)
        )
        if result.scalar_one_or_none() is None:
            raise UserNotFound(user_id)

    async def get_objective(self, user_id: int, objective_id: int) -> ObjectifUtilisateur:
        """Fetch one objective scoped to the given user."""
        result = await self.db.execute(
            select(ObjectifUtilisateur).where(
                ObjectifUtilisateur.utilisateur_id == user_id,
                ObjectifUtilisateur.objectif_id == objective_id,
            )
        )
        objective = result.scalar_one_or_none()
        if objective is None:
            raise ObjectiveNotFound(objective_id)
        return objective

    async def get_progress_photo(self, user_id: int, photo_id: int) -> ProgressionPhoto:
        """Fetch one progress photo scoped to the given user."""
        result = await self.db.execute(
            select(ProgressionPhoto).where(
                ProgressionPhoto.utilisateur_id == user_id,
                ProgressionPhoto.photo_id == photo_id,
            )
        )
        photo = result.scalar_one_or_none()
        if photo is None:
            raise ProgressPhotoNotFound(photo_id)
        return photo

    async def deactivate_other_objectives(
        self,
        user_id: int,
        keep_objective_id: int | None = None,
    ) -> None:
        """Keep a single active objective for a user when requested by the payload."""
        result = await self.db.execute(
            select(ObjectifUtilisateur).where(ObjectifUtilisateur.utilisateur_id == user_id)
        )
        for objective in result.scalars():
            if keep_objective_id is not None and objective.objectif_id == keep_objective_id:
                continue
            if objective.actif_unique:
                objective.actif_unique = False
