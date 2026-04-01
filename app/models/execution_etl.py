"""ExecutionEtl model - ETL execution history and metrics."""
from datetime import datetime
from typing import Optional

from sqlalchemy import Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, intpk


class ExecutionEtl(Base):
    """ETL execution run with status and quality metrics."""

    __tablename__ = "execution_etl"

    execution_id: Mapped[intpk]
    source_id: Mapped[int] = mapped_column(
        ForeignKey("source_donnees.source_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    statut: Mapped[str] = mapped_column(
        Enum("EN_COURS", "SUCCES", "ECHEC", name="statut_etl_enum"),
        nullable=False,
        server_default="EN_COURS",
        index=True,
    )
    demarre_le: Mapped[datetime] = mapped_column(nullable=False, server_default="CURRENT_TIMESTAMP")
    termine_le: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    lignes_lues: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    lignes_valides: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    lignes_invalides: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    message: Mapped[Optional[str]] = mapped_column(String(250), nullable=True)

    def __repr__(self) -> str:
        return f"<ExecutionEtl(id={self.execution_id}, statut={self.statut})>"
