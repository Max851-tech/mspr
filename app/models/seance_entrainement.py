"""SeanceEntrainement model - user workout sessions."""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import BigInteger, Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class SeanceEntrainement(Base):
    """User workout/training session record."""

    __tablename__ = "seance_entrainement"

    seance_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    utilisateur_id: Mapped[int] = mapped_column(
        ForeignKey("utilisateur.utilisateur_id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    date_seance: Mapped[date] = mapped_column(Date, nullable=False)
    type_entrainement: Mapped[str] = mapped_column(
        ForeignKey("ref_type_entrainement.type_entrainement", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    duree_seance_h: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    calories_brulees: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    frequence_entrainement_j_sem: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    niveau_experience: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    eau_l: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    source_tag: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    cree_le: Mapped[datetime] = mapped_column(nullable=False, server_default="CURRENT_TIMESTAMP")

    def __repr__(self) -> str:
        return f"<SeanceEntrainement(id={self.seance_id}, date={self.date_seance})>"
