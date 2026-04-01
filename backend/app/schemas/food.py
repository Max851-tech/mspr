"""Food schemas for API requests and responses."""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class FoodBase(BaseModel):
    """Base schema for food with nutritional data."""

    nom: str
    categorie: Optional[str] = None
    calories_kcal: Optional[Decimal] = None
    proteines_g: Optional[Decimal] = None
    glucides_g: Optional[Decimal] = None
    lipides_g: Optional[Decimal] = None
    fibres_g: Optional[Decimal] = None
    sucres_g: Optional[Decimal] = None
    sodium_mg: Optional[Decimal] = None
    cholesterol_mg: Optional[Decimal] = None


class FoodCreate(FoodBase):
    """Schema for creating a new food."""

    pass


class FoodUpdate(BaseModel):
    """Schema for updating a food (all fields optional for partial update)."""

    nom: Optional[str] = None
    categorie: Optional[str] = None
    calories_kcal: Optional[Decimal] = None
    proteines_g: Optional[Decimal] = None
    glucides_g: Optional[Decimal] = None
    lipides_g: Optional[Decimal] = None
    fibres_g: Optional[Decimal] = None
    sucres_g: Optional[Decimal] = None
    sodium_mg: Optional[Decimal] = None
    cholesterol_mg: Optional[Decimal] = None


class FoodRead(FoodBase):
    """Schema for reading a food from the API."""

    aliment_id: int
    cree_le: datetime
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
