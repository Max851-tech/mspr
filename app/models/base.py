"""SQLAlchemy declarative base with naming convention for MySQL."""
from datetime import datetime
from decimal import Decimal
from typing import Annotated

from sqlalchemy import MetaData, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Naming convention ensures Alembic generates predictable constraint names
naming_convention = {
    "ix": "idx_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    metadata = MetaData(naming_convention=naming_convention)


# Reusable type annotations
intpk = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]
bigintpk = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]
str120 = Annotated[str, mapped_column(String(120))]
str150 = Annotated[str, mapped_column(String(150))]
str200 = Annotated[str, mapped_column(String(200))]
str255 = Annotated[str, mapped_column(String(255))]
str500 = Annotated[str, mapped_column(String(500))]
timestamp_now = Annotated[datetime, mapped_column(server_default=func.now())]
