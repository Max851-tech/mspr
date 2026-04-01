"""MesureBiometrique model - historical biometric measurements."""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import BigInteger, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class MesureBiometrique(Base):
    """Historical biometric measurement record."""

    __tablename__ = "mesure_biometrique"

    mesure_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    utilisateur_id: Mapped[int] = mapped_column(
        ForeignKey("utilisateur.utilisateur_id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    mesure_le: Mapped[datetime] = mapped_column(nullable=False)
    poids_kg: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    taille_m: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    imc: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    taux_masse_grasse: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    bpm_repos: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    bpm_moyen: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    bpm_max: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    eau_l: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    source_tag: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    cree_le: Mapped[datetime] = mapped_column(nullable=False, server_default="CURRENT_TIMESTAMP")

    def __repr__(self) -> str:
        return f"<MesureBiometrique(id={self.mesure_id}, utilisateur_id={self.utilisateur_id})>"
