"""Exercice model - exercise catalog with instructions and media."""
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import BigInteger, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.mixins.soft_delete import SoftDeleteMixin


class Exercice(Base, SoftDeleteMixin):
    """Exercise with instructions, target muscles, and GIF paths."""

    __tablename__ = "exercice"

    exercice_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    external_id: Mapped[Optional[str]] = mapped_column(String(80), nullable=True, unique=True)
    nom: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    partie_corps: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    muscle_cible: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    equipement: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    difficulte: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, index=True)
    parties_corps_json: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    muscles_secondaires_json: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    equipements_json: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    instructions_json: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    gif_180_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    gif_360_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    gif_720_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    gif_1080_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    cree_le: Mapped[datetime] = mapped_column(nullable=False, server_default="CURRENT_TIMESTAMP")

    def __repr__(self) -> str:
        return f"<Exercice(id={self.exercice_id}, nom='{self.nom}')>"
