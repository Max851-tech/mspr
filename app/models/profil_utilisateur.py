"""ProfilUtilisateur model - user biometric profile (1:1 with utilisateur)."""
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import ForeignKey, Integer, JSON, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ProfilUtilisateur(Base):
    """User biometric profile - 1:1 relationship with utilisateur."""

    __tablename__ = "profil_utilisateur"

    utilisateur_id: Mapped[int] = mapped_column(
        ForeignKey("utilisateur.utilisateur_id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
    )
    genre: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    taille_m: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    poids_kg: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    imc: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    categorie_imc: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    objectif_principal: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    objectifs_secondaires: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    cree_le: Mapped[datetime] = mapped_column(nullable=False, server_default="CURRENT_TIMESTAMP")

    def __repr__(self) -> str:
        return f"<ProfilUtilisateur(utilisateur_id={self.utilisateur_id})>"
