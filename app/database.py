"""Async database session factory for HealthAI Coach API."""
import os
from functools import lru_cache
from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+aiomysql://root:password@localhost/healthai_coach"
)


@lru_cache(maxsize=1)
def get_engine() -> "AsyncEngine":
    """Create and cache the async engine (lazy initialization)."""
    return create_async_engine(DATABASE_URL, echo=False)


@lru_cache(maxsize=1)
def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Create and cache the async session factory (lazy initialization)."""
    return async_sessionmaker(
        get_engine(),
        class_=AsyncSession,
        expire_on_commit=False
    )


# Convenience alias for backward compatibility
def AsyncSessionLocal() -> AsyncSession:
    """Get a new async session from the factory."""
    return get_session_factory()()


__all__ = ["get_engine", "get_session_factory", "AsyncSessionLocal", "DATABASE_URL"]
