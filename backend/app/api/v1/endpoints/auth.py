# backend/app/api/v1/endpoints/auth.py
"""Authentication endpoints: register, login, token refresh.
Uses the JWT utilities from ``app.core.security`` and the ``User`` model.
All passwords are stored hashed with bcrypt.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core import security
from app.core.config import settings
from app.api.v1.dependencies import oauth2_scheme
from app.db.base import get_async_session
from app.models.user import User, UserRole
from app.schemas.auth import (
    TokenPair,
    RegisterRequest,
    LoginRequest,
    UserPublic,
)

router = APIRouter()


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register(user_in: RegisterRequest, db: AsyncSession = Depends(get_async_session)):
    clean_email = str(user_in.email).lower().strip()
    # Check for existing email (case-insensitive)
    result = await db.execute(select(User).where(func.lower(User.email) == clean_email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed = security.get_password_hash(user_in.password)
    new_user = User(
        email=clean_email,
        hashed_password=hashed,
        full_name=user_in.full_name.strip(),
        phone_number=user_in.phone.strip() if user_in.phone else None,
        ward_id=str(user_in.ward_id) if user_in.ward_id else None,
        role=UserRole.CITIZEN,
        is_active=True,
        is_verified=True,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.post("/token", response_model=TokenPair)
async def login(form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_async_session)):
    """OAuth2 Form-encoded login (for Swagger UI and standard form submissions)."""
    clean_username = form.username.lower().strip()
    result = await db.execute(select(User).where(func.lower(User.email) == clean_username))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")
    if not security.verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    role_str = user.role.value if hasattr(user.role, "value") else str(user.role)
    access_token = security.create_access_token({"sub": str(user.id), "role": role_str})
    refresh_token = security.create_refresh_token({"sub": str(user.id)})
    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60),
    )


@router.post("/login", response_model=TokenPair)
async def login_json(creds: LoginRequest, db: AsyncSession = Depends(get_async_session)):
    """JSON body login endpoint for modern client apps."""
    clean_username = str(creds.email).lower().strip()
    result = await db.execute(select(User).where(func.lower(User.email) == clean_username))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")
    if not security.verify_password(creds.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    role_str = user.role.value if hasattr(user.role, "value") else str(user.role)
    access_token = security.create_access_token({"sub": str(user.id), "role": role_str})
    refresh_token = security.create_refresh_token({"sub": str(user.id)})
    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60),
    )


@router.post("/refresh", response_model=TokenPair)
async def refresh(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_async_session)):
    payload = security.decode_token(token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    role_str = user.role.value if hasattr(user.role, "value") else str(user.role)
    access_token = security.create_access_token({"sub": str(user.id), "role": role_str})
    return TokenPair(
        access_token=access_token,
        refresh_token=token,
        token_type="bearer",
        expires_in=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60),
    )


@router.get("/me", response_model=UserPublic)
async def get_me(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_async_session)):
    """Get the currently authenticated user."""
    payload = security.decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
