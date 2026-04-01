"""JournalAlimentaire model - user meal journal entries."""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import BigInteger, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class JournalAlimentaire(Base):
    """User food consumption journal entry."""

    __tablename__ = "journal_alimentaire"

    journal_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    utilisateur_id: Mapped[int] = mapped_column(
        ForeignKey("utilisateur.utilisateur_id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    consomme_le: Mapped[datetime] = mapped_column(nullable=False)
    type_repas: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    aliment_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("aliment.aliment_id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
    )
    aliment_nom_libre: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    quantite: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    unite_quantite: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    calories_kcal: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    eau_ml: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    source_tag: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    cree_le: Mapped[datetime] = mapped_column(nullable=False, server_default="CURRENT_TIMESTAMP")

    # Composite index on (utilisateur_id, consomme_le) defined in __table_args__
    __table_args__ = (
        # Index handled by MySQL schema
    )

    def __repr__(self) -> str:
        return f"<JournalAlimentaire(id={self.journal_id}, utilisateur_id={self.utilisateur_id})>"
