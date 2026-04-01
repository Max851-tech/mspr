"""SourceDonnees model - ETL data source catalog."""
from datetime import datetime
from typing import Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, intpk


class SourceDonnees(Base):
    """Catalog of data sources for ETL pipeline."""

    __tablename__ = "source_donnees"

    source_id: Mapped[intpk]
    nom: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    cree_le: Mapped[datetime] = mapped_column(nullable=False, server_default="CURRENT_TIMESTAMP")

    def __repr__(self) -> str:
        return f"<SourceDonnees(id={self.source_id}, nom='{self.nom}')>"
