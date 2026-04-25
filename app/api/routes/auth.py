"""Authentication endpoints (login, current user)."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.database import get_db
from app.models.utilisateur import Utilisateur
from app.schemas.auth import RegisterResponse, Token
from app.schemas.user import UserCreate, UserRead
from app.security.passwords import verify_password
from app.security.tokens import create_access_token
from app.services.account import create_user_account

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an account",
    description="Public signup: same payload as `POST /api/v1/users` (email, mot_de_passe, nom). Returns JWT.",
    responses={409: {"description": "Email already registered"}},
)
async def register(
    user_data: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> RegisterResponse:
    user = await create_user_account(db, user_data)
    access_token = create_access_token(
        subject=str(user.utilisateur_id),
        extra_claims={"email": user.email, "role": user.role},
    )
    return RegisterResponse(user=user, access_token=access_token)


@router.post(
    "/token",
    response_model=Token,
    summary="Obtain an access token",
    description="OAuth2 password flow: send `username` (email) + `password` as form fields.",
)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Token:
    result = await db.execute(select(Utilisateur).where(Utilisateur.email == form_data.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.mot_de_passe_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.statut != "ACTIF":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive")

    access_token = create_access_token(
        subject=str(user.utilisateur_id),
        extra_claims={"email": user.email, "role": user.role},
    )
    return Token(access_token=access_token)


@router.get(
    "/me",
    response_model=UserRead,
    summary="Current user",
    description="Returns the authenticated user derived from the Bearer token.",
)
async def read_me(current_user: Annotated[Utilisateur, Depends(get_current_user)]) -> UserRead:
    return current_user

