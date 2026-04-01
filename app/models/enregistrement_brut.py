"""EnregistrementBrut model - raw JSON data storage before transformation."""
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import BigInteger, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class EnregistrementBrut(Base):
    """Raw data record stored as JSON before ETL transformation."""

    __tablename__ = "enregistrement_brut"

    enregistrement_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    lot_id: Mapped[int] = mapped_column(
        ForeignKey("lot_donnees.lot_id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    entite: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    ref_externe: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    payload: Mapped[Any] = mapped_column(JSON, nullable=False)
    cree_le: Mapped[datetime] = mapped_column(nullable=False, server_default="CURRENT_TIMESTAMP")

    def __repr__(self) -> str:
        return f"<EnregistrementBrut(id={self.enregistrement_id}, entite='{self.entite}')>"
