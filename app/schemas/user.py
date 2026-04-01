"""User and Profile Pydantic schemas."""
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ObjectifSante(str, Enum):
    """Health objectives enum."""
    PERTE_POIDS = "PERTE_POIDS"
    MUSCLE = "MUSCLE"
    SOMMEIL = "SOMMEIL"
    FORME = "FORME"


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    email: EmailStr
    mot_de_passe: str = Field(..., min_length=8)
    nom: str = Field(..., min_length=1, max_length=120)


class UserRead(BaseModel):
    """Schema for reading user data."""
    model_config = ConfigDict(from_attributes=True)

    utilisateur_id: int
    email: Optional[str] = None
    nom_utilisateur: str
    role: str
    statut: str
    cree_le: datetime


class UserUpdate(BaseModel):
    """Schema for updating user data."""
    nom_utilisateur: Optional[str] = Field(None, min_length=1, max_length=120)


class ProfileRead(BaseModel):
    """Schema for reading user profile data."""
    model_config = ConfigDict(from_attributes=True)

    utilisateur_id: int
    genre: Optional[str] = None
    age: Optional[int] = None
    poids_kg: Optional[Decimal] = None
    taille_m: Optional[Decimal] = None
    imc: Optional[Decimal] = None
    categorie_imc: Optional[str] = None
    objectif_principal: Optional[str] = None
    objectifs_secondaires: Optional[list[str]] = None
    cree_le: datetime


class ProfileUpdate(BaseModel):
    """Schema for updating user profile data."""
    genre: Optional[str] = Field(None, max_length=20)
    age: Optional[int] = Field(None, ge=13, le=120)
    poids_kg: Optional[Decimal] = Field(None, ge=20, le=300)
    taille_m: Optional[Decimal] = Field(None, ge=0.5, le=2.5)
    objectif_principal: Optional[ObjectifSante] = None
    objectifs_secondaires: Optional[list[ObjectifSante]] = None
