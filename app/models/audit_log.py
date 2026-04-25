"""Audit log model for tracking data changes."""
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import JSON, BigInteger, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AuditLog(Base):
    """Audit trail for tracking changes to reference data.

    Records INSERT, UPDATE, DELETE, and RESTORE operations with before/after values.
    """

    __tablename__ = "audit_log"

    audit_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )
    table_name: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
        index=True
    )
    record_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        index=True
    )
    action: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )
    changed_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("utilisateur.utilisateur_id", ondelete="SET NULL"),
        nullable=True,
    )
    changed_at: Mapped[datetime] = mapped_column(
        nullable=False,
        index=True
    )
    old_values: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True
    )
    new_values: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True
    )

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.audit_id}, table={self.table_name}, action={self.action})>"
