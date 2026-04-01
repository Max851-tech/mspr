"""Exercise schemas for API requests and responses."""
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class DifficultyLevel(str, Enum):
    """Exercise difficulty levels."""

    DEBUTANT = "DEBUTANT"
    INTERMEDIAIRE = "INTERMEDIAIRE"
    AVANCE = "AVANCE"


class ExerciseBase(BaseModel):
    """Base schema for exercise with instruction data."""

    nom: str
    partie_corps: Optional[str] = None
    muscle_cible: Optional[str] = None
    equipement: Optional[str] = None
    difficulte: Optional[DifficultyLevel] = None
    external_id: Optional[str] = None
    parties_corps_json: Optional[Any] = None
    muscles_secondaires_json: Optional[Any] = None
    equipements_json: Optional[Any] = None
    instructions_json: Optional[Any] = None
    gif_180_path: Optional[str] = None
    gif_360_path: Optional[str] = None
    gif_720_path: Optional[str] = None
    gif_1080_path: Optional[str] = None


class ExerciseCreate(ExerciseBase):
    """Schema for creating a new exercise."""

    pass


class ExerciseUpdate(BaseModel):
    """Schema for updating an exercise (all fields optional for partial update)."""

    nom: Optional[str] = None
    partie_corps: Optional[str] = None
    muscle_cible: Optional[str] = None
    equipement: Optional[str] = None
    difficulte: Optional[DifficultyLevel] = None
    external_id: Optional[str] = None
    parties_corps_json: Optional[Any] = None
    muscles_secondaires_json: Optional[Any] = None
    equipements_json: Optional[Any] = None
    instructions_json: Optional[Any] = None
    gif_180_path: Optional[str] = None
    gif_360_path: Optional[str] = None
    gif_720_path: Optional[str] = None
    gif_1080_path: Optional[str] = None


class ExerciseRead(ExerciseBase):
    """Schema for reading an exercise from the API."""

    exercice_id: int
    cree_le: datetime
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
