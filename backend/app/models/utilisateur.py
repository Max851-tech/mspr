"""Utilisateur model - user accounts with roles."""
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, intpk

if TYPE_CHECKING:
    from app.models.objectif_utilisateur import ObjectifUtilisateur
    from app.models.progression_photo import ProgressionPhoto


class Utilisateur(Base):
    """User account with authentication and role management."""

    __tablename__ = "utilisateur"

    utilisateur_id: Mapped[intpk]
    organisation_id: Mapped[int] = mapped_column(
        ForeignKey("organisation.organisation_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    nom_utilisateur: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, unique=True)
    mot_de_passe_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(
        Enum("ADMIN", "UTILISATEUR", name="role_enum"),
        nullable=False,
        server_default="UTILISATEUR",
    )
    statut: Mapped[str] = mapped_column(
        Enum("ACTIF", "INACTIF", name="statut_enum"),
        nullable=False,
        server_default="ACTIF",
    )
    cree_le: Mapped[datetime] = mapped_column(nullable=False, server_default="CURRENT_TIMESTAMP")

    objectifs_utilisateur: Mapped[list["ObjectifUtilisateur"]] = relationship(
        "ObjectifUtilisateur",
        back_populates="utilisateur",
        cascade="all, delete-orphan",
    )
    photos_progression: Mapped[list["ProgressionPhoto"]] = relationship(
        "ProgressionPhoto",
        back_populates="utilisateur",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Utilisateur(id={self.utilisateur_id}, nom='{self.nom_utilisateur}', role={self.role})>"
