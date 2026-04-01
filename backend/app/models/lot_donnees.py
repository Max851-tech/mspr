"""LotDonnees model - data batches with traceability."""
from datetime import datetime
from typing import Optional

from sqlalchemy import Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, intpk


class LotDonnees(Base):
    """Data batch imported with full traceability."""

    __tablename__ = "lot_donnees"
    __table_args__ = (
        UniqueConstraint("source_id", "nom_lot", name="uq_lot_nom_source"),
    )

    lot_id: Mapped[intpk]
    source_id: Mapped[int] = mapped_column(
        ForeignKey("source_donnees.source_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    nom_lot: Mapped[str] = mapped_column(String(200), nullable=False)
    statut: Mapped[str] = mapped_column(
        Enum("TELEVERSE", "VALIDE", "NETTOYE", "REJETE", name="statut_lot_enum"),
        nullable=False,
        server_default="TELEVERSE",
        index=True,
    )
    cree_par: Mapped[Optional[int]] = mapped_column(
        ForeignKey("utilisateur.utilisateur_id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
    )
    cree_le: Mapped[datetime] = mapped_column(nullable=False, server_default="CURRENT_TIMESTAMP")

    def __repr__(self) -> str:
        return f"<LotDonnees(id={self.lot_id}, nom='{self.nom_lot}', statut={self.statut})>"
