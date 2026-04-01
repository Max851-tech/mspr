"""Aliment model - food reference data with nutritional values."""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, intpk
from app.models.mixins.soft_delete import SoftDeleteMixin


class Aliment(Base, SoftDeleteMixin):
    """Food item with nutritional information (cleaned from ETL)."""

    __tablename__ = "aliment"

    aliment_id: Mapped[intpk]
    nom: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    categorie: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    calories_kcal: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    proteines_g: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    glucides_g: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    lipides_g: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    fibres_g: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    sucres_g: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    sodium_mg: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    cholesterol_mg: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    cree_le: Mapped[datetime] = mapped_column(nullable=False, server_default="CURRENT_TIMESTAMP")

    def __repr__(self) -> str:
        return f"<Aliment(id={self.aliment_id}, nom='{self.nom}')>"
