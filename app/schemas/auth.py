"""Authentication-related schemas."""
from pydantic import BaseModel

from app.schemas.user import UserRead


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RegisterResponse(BaseModel):
    """Returned after self-service signup (user created + JWT for immediate use)."""

    user: UserRead
    access_token: str
    token_type: str = "bearer"
