"""Pydantic schemas for user objectives and progress photos."""
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class ObjectiveBase(BaseModel):
    """Shared fields for objective payloads."""

    date_debut: date
    actif_unique: bool = True


class ObjectiveCreate(ObjectiveBase):
    """Schema for creating a user objective."""


class ObjectiveUpdate(BaseModel):
    """Schema for partially updating a user objective."""

    date_debut: date | None = None
    actif_unique: bool | None = None


class ObjectiveRead(ObjectiveBase):
    """Schema for reading a user objective."""

    model_config = ConfigDict(from_attributes=True)

    objectif_id: int
    utilisateur_id: int
    cree_le: datetime


class ProgressPhotoBase(BaseModel):
    """Shared fields for progress photo payloads."""

    objectif_id: int = Field(..., gt=0)
    prise_le: datetime


class ProgressPhotoCreate(ProgressPhotoBase):
    """Schema for creating a progress photo."""


class ProgressPhotoRead(ProgressPhotoBase):
    """Schema for reading a progress photo."""

    model_config = ConfigDict(from_attributes=True)

    photo_id: int
    utilisateur_id: int
    cree_le: datetime
