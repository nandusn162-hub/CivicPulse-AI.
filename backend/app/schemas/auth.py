"""Pydantic schemas for authentication."""
from __future__ import annotations

import re
from datetime import datetime
from typing import Optional, Union, Any
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


# ---------------------------------------------------------------------------
# Requests
# ---------------------------------------------------------------------------

class RegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    phone: Optional[str] = None
    password: str = Field(..., min_length=8, max_length=128)
    ward_id: Optional[Union[UUID, str]] = None

    @field_validator("phone", mode="before")
    @classmethod
    def clean_phone(cls, v: Any) -> Optional[str]:
        if not v:
            return None
        v_str = str(v).strip()
        return v_str if v_str else None

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one digit.")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=120)
    phone: Optional[str] = None
    ward_id: Optional[Union[UUID, str]] = None


# ---------------------------------------------------------------------------
# Responses
# ---------------------------------------------------------------------------

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class UserPublic(BaseModel):
    id: Optional[str] = None
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    phone_number: Optional[str] = None
    role: str
    ward_id: Optional[str] = None
    is_active: Optional[bool] = True
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class RegisterResponse(BaseModel):
    user: UserPublic
    tokens: TokenPair


class LoginResponse(BaseModel):
    user: UserPublic
    tokens: TokenPair


class RefreshResponse(BaseModel):
    tokens: TokenPair


class LogoutResponse(BaseModel):
    detail: str = "Successfully logged out."
