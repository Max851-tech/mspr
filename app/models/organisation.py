"""Organisation model - root tenant entity."""
from datetime import datetime
from typing import Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, intpk, str150, timestamp_now


class Organisation(Base):
    """Organisation/tenant for multi-tenant isolation."""

    __tablename__ = "organisation"

    organisation_id: Mapped[intpk]
    nom: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    cree_le: Mapped[datetime] = mapped_column(nullable=False, server_default="CURRENT_TIMESTAMP")

    def __repr__(self) -> str:
        return f"<Organisation(id={self.organisation_id}, nom='{self.nom}')>"
