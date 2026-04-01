"""AnomalieDonnee model - ETL error and warning log."""
from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AnomalieDonnee(Base):
    """ETL anomaly/error log entry."""

    __tablename__ = "anomalie_donnee"

    anomalie_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    execution_id: Mapped[int] = mapped_column(
        ForeignKey("execution_etl.execution_id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    severite: Mapped[str] = mapped_column(
        Enum("AVERT", "ERREUR", name="severite_enum"),
        nullable=False,
        index=True,
    )
    entite: Mapped[str] = mapped_column(String(80), nullable=False)
    ref_ligne: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    nom_champ: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    code_anomalie: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str] = mapped_column(String(250), nullable=False)
    cree_le: Mapped[datetime] = mapped_column(nullable=False, server_default="CURRENT_TIMESTAMP")

    def __repr__(self) -> str:
        return f"<AnomalieDonnee(id={self.anomalie_id}, code='{self.code_anomalie}')>"
