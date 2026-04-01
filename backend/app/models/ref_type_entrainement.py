"""RefTypeEntrainement model - workout type reference table."""
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class RefTypeEntrainement(Base):
    """Reference table for workout/training types."""

    __tablename__ = "ref_type_entrainement"

    type_entrainement: Mapped[str] = mapped_column(String(80), primary_key=True)

    def __repr__(self) -> str:
        return f"<RefTypeEntrainement(type='{self.type_entrainement}')>"
