"""Database session dependency."""
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield database session and ensure cleanup."""
    async with get_session_factory()() as session:
        try:
            yield session
        finally:
            await session.close()
