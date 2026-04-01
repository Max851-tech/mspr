"""Staging models - temporary tables for pandas.to_sql ETL loading."""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import BigInteger, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class StgAlimentation(Base):
    """Staging table for food/nutrition dataset."""

    __tablename__ = "stg_alimentation"

    stg_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    lot_id: Mapped[int] = mapped_column(
        ForeignKey("lot_donnees.lot_id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    food_item: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    calories_kcal: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    protein_g: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    carbohydrates_g: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    fat_g: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    fiber_g: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    sugars_g: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    sodium_mg: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    cholesterol_mg: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    meal_type: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    water_intake_ml: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    cree_le: Mapped[datetime] = mapped_column(nullable=False, server_default="CURRENT_TIMESTAMP")


class StgSalleSport(Base):
    """Staging table for gym/fitness dataset."""

    __tablename__ = "stg_salle_sport"

    stg_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    lot_id: Mapped[int] = mapped_column(
        ForeignKey("lot_donnees.lot_id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    weight_kg: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    height_m: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    max_bpm: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    avg_bpm: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    resting_bpm: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    session_duration_hours: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    calories_burned: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    workout_type: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    fat_percentage: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    water_intake_l: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    workout_frequency_days_week: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    experience_level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    bmi: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    cree_le: Mapped[datetime] = mapped_column(nullable=False, server_default="CURRENT_TIMESTAMP")


class StgSommeilSante(Base):
    """Staging table for sleep/health dataset."""

    __tablename__ = "stg_sommeil_sante"

    stg_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    lot_id: Mapped[int] = mapped_column(
        ForeignKey("lot_donnees.lot_id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    person_id: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    gender: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    occupation: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    sleep_duration: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    quality_of_sleep: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    physical_activity_level: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    stress_level: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    bmi_category: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    blood_pressure: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    heart_rate: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    daily_steps: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sleep_disorder: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    cree_le: Mapped[datetime] = mapped_column(nullable=False, server_default="CURRENT_TIMESTAMP")
