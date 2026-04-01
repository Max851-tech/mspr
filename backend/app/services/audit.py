"""Audit service for tracking data changes."""
from contextvars import ContextVar
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog

# Context variable to track current user (set by future auth middleware)
current_user_id: ContextVar[Optional[int]] = ContextVar("current_user_id", default=None)


class AuditService:
    """Service for logging changes to reference data tables."""

    # Tables that should be audited
    TRACKED_TABLES = {"aliment", "exercice"}

    def __init__(self, db: AsyncSession):
        self.db = db

    def get_model_dict(self, obj: Any) -> dict[str, Any]:
        """Convert SQLAlchemy model to dict for JSON storage.

        Handles special types like Decimal and datetime for JSON serialization.
        """
        result = {}
        for column in obj.__table__.columns:
            value = getattr(obj, column.name, None)
            if value is None:
                result[column.name] = None
            elif isinstance(value, Decimal):
                result[column.name] = float(value)
            elif isinstance(value, datetime):
                result[column.name] = value.isoformat()
            else:
                result[column.name] = value
        return result

    async def log_change(
        self,
        table_name: str,
        record_id: int,
        action: str,
        old_values: Optional[dict[str, Any]] = None,
        new_values: Optional[dict[str, Any]] = None,
    ) -> None:
        """Log a change to the audit trail.

        Args:
            table_name: Name of the table being changed
            record_id: Primary key of the record
            action: Type of change (INSERT, UPDATE, DELETE, RESTORE)
            old_values: Before state (for UPDATE, DELETE)
            new_values: After state (for INSERT, UPDATE, RESTORE)

        Note: Caller is responsible for committing the transaction.
        """
        if table_name not in self.TRACKED_TABLES:
            return  # Skip non-tracked tables

        audit_entry = AuditLog(
            table_name=table_name,
            record_id=record_id,
            action=action,
            changed_by=current_user_id.get(),
            changed_at=datetime.utcnow(),
            old_values=old_values,
            new_values=new_values,
        )
        self.db.add(audit_entry)

    async def log_insert(self, obj: Any) -> None:
        """Log an INSERT operation."""
        table_name = obj.__table__.name
        record_id = getattr(obj, obj.__table__.primary_key.columns.values()[0].name)
        new_values = self.get_model_dict(obj)
        await self.log_change(table_name, record_id, "INSERT", None, new_values)

    async def log_update(self, obj: Any, old_values: dict[str, Any]) -> None:
        """Log an UPDATE operation.

        Args:
            obj: Updated model instance
            old_values: Dictionary of old values before update
        """
        table_name = obj.__table__.name
        record_id = getattr(obj, obj.__table__.primary_key.columns.values()[0].name)
        new_values = self.get_model_dict(obj)
        await self.log_change(table_name, record_id, "UPDATE", old_values, new_values)

    async def log_delete(self, obj: Any) -> None:
        """Log a DELETE (soft delete) operation."""
        table_name = obj.__table__.name
        record_id = getattr(obj, obj.__table__.primary_key.columns.values()[0].name)
        old_values = self.get_model_dict(obj)
        await self.log_change(table_name, record_id, "DELETE", old_values, None)

    async def log_restore(self, obj: Any) -> None:
        """Log a RESTORE operation."""
        table_name = obj.__table__.name
        record_id = getattr(obj, obj.__table__.primary_key.columns.values()[0].name)
        new_values = self.get_model_dict(obj)
        await self.log_change(table_name, record_id, "RESTORE", None, new_values)
