"""Soft delete mixin for SQLAlchemy models."""
from datetime import datetime
from typing import Optional

from sqlalchemy import Index
from sqlalchemy.orm import Mapped, mapped_column


class SoftDeleteMixin:
    """Mixin providing soft delete functionality.

    Adds deleted_at timestamp column and methods for soft delete operations.
    Models using this mixin can be marked as deleted without actual removal.
    """

    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
        index=True,
        default=None
    )

    def soft_delete(self) -> None:
        """Mark this record as deleted by setting deleted_at to current UTC time."""
        self.deleted_at = datetime.utcnow()

    def restore(self) -> None:
        """Restore a soft-deleted record by clearing deleted_at."""
        self.deleted_at = None

    @property
    def is_deleted(self) -> bool:
        """Check if this record is soft-deleted."""
        return self.deleted_at is not None
