"""Admin API key guard."""
import logging

from fastapi import Header, HTTPException, status

from app.core.settings import get_admin_api_key, is_production

logger = logging.getLogger(__name__)


async def require_admin_api_key(x_api_key: str | None = Header(default=None)) -> None:
    expected = get_admin_api_key()
    if not expected:
        if is_production():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Admin API key is not configured",
            )
        logger.warning("ADMIN_API_KEY is not set; admin routes are open (development only).")
        return

    if not x_api_key or x_api_key != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing admin API key",
        )
