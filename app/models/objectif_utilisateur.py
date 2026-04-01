"""ObjectifUtilisateur model - user goals tracked over time."""
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, intpk

if TYPE_CHECKING:
    from app.models.progression_photo import ProgressionPhoto
    from app.models.utilisateur import Utilisateur


class ObjectifUtilisateur(Base):
    """User objective with start date and active flag."""

    __tablename__ = "objectif_utilisateur"

    objectif_id: Mapped[intpk]
    utilisateur_id: Mapped[int] = mapped_column(
        ForeignKey("utilisateur.utilisateur_id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    date_debut: Mapped[date] = mapped_column(Date, nullable=False)
    actif_unique: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="1",
    )
    cree_le: Mapped[datetime] = mapped_column(nullable=False, server_default="CURRENT_TIMESTAMP")

    __table_args__ = (
        Index("idx_objectif_user_date", "utilisateur_id", "date_debut"),
        Index("idx_objectif_user_active", "utilisateur_id", "actif_unique"),
    )

    utilisateur: Mapped["Utilisateur"] = relationship(
        "Utilisateur",
        back_populates="objectifs_utilisateur",
    )
    photos_progression: Mapped[list["ProgressionPhoto"]] = relationship(
        "ProgressionPhoto",
        back_populates="objectif",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<ObjectifUtilisateur(id={self.objectif_id}, "
            f"utilisateur_id={self.utilisateur_id}, actif={self.actif_unique})>"
        )
