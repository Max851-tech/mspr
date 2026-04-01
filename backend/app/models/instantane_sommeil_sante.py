"""InstantaneSommeilSante model - daily sleep and health snapshot."""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import BigInteger, Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class InstantaneSommeilSante(Base):
    """Daily sleep and health data snapshot."""

    __tablename__ = "instantane_sommeil_sante"

    instantane_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    utilisateur_id: Mapped[int] = mapped_column(
        ForeignKey("utilisateur.utilisateur_id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    date_instantane: Mapped[date] = mapped_column(Date, nullable=False)
    identifiant_personne_externe: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    genre: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    profession: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    duree_sommeil_h: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    qualite_sommeil_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    activite_physique_min_jour: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    stress_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    categorie_imc: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    tension_arterielle_brut: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    frequence_cardiaque_bpm: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    pas_jour: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    trouble_sommeil: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    source_tag: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    cree_le: Mapped[datetime] = mapped_column(nullable=False, server_default="CURRENT_TIMESTAMP")

    def __repr__(self) -> str:
        return f"<InstantaneSommeilSante(id={self.instantane_id}, date={self.date_instantane})>"
