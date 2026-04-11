"""User account creation (shared by public register and users API)."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.user import EmailAlreadyExists
from app.models.organisation import Organisation
from app.models.utilisateur import Utilisateur
from app.schemas.user import UserCreate
from app.security.passwords import hash_password


async def _default_organisation_id(db: AsyncSession) -> int:
    """Migrations ne seedent pas `organisation` : sans ligne, FK organisation_id=1 provoque 500."""
    r = await db.execute(select(Organisation.organisation_id).order_by(Organisation.organisation_id).limit(1))
    oid = r.scalar_one_or_none()
    if oid is not None:
        return oid
    org = Organisation(nom="Défaut")
    db.add(org)
    await db.flush()
    return org.organisation_id


async def create_user_account(db: AsyncSession, user_data: UserCreate) -> Utilisateur:
    existing = await db.execute(select(Utilisateur).where(Utilisateur.email == user_data.email))
    if existing.scalar_one_or_none():
        raise EmailAlreadyExists(user_data.email)

    org_id = await _default_organisation_id(db)

    user = Utilisateur(
        email=user_data.email,
        nom_utilisateur=user_data.nom,
        mot_de_passe_hash=hash_password(user_data.mot_de_passe),
        organisation_id=org_id,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
