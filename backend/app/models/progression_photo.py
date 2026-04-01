"""ProgressionPhoto model - photo snapshots linked to a user objective."""
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.objectif_utilisateur import ObjectifUtilisateur
    from app.models.utilisateur import Utilisateur


class ProgressionPhoto(Base):
    """Photo evidence tied to a user and one of their objectives."""

    __tablename__ = "progression_photo"

    photo_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    utilisateur_id: Mapped[int] = mapped_column(
        ForeignKey("utilisateur.utilisateur_id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    objectif_id: Mapped[int] = mapped_column(
        ForeignKey("objectif_utilisateur.objectif_id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    prise_le: Mapped[datetime] = mapped_column(nullable=False)
    cree_le: Mapped[datetime] = mapped_column(nullable=False, server_default="CURRENT_TIMESTAMP")

    __table_args__ = (
        Index("idx_photo_objectif_date", "objectif_id", "prise_le"),
        Index("idx_photo_user_date", "utilisateur_id", "prise_le"),
    )

    utilisateur: Mapped["Utilisateur"] = relationship(
        "Utilisateur",
        back_populates="photos_progression",
    )
    objectif: Mapped["ObjectifUtilisateur"] = relationship(
        "ObjectifUtilisateur",
        back_populates="photos_progression",
    )

    def __repr__(self) -> str:
        return (
            f"<ProgressionPhoto(id={self.photo_id}, utilisateur_id={self.utilisateur_id}, "
            f"objectif_id={self.objectif_id})>"
        )
