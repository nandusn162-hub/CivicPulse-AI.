"""Pydantic schemas for community confirmations and comments."""
from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ConfirmationCreate(BaseModel):
    complaint_id: UUID
    vote: str  # confirm | dispute
    comment: Optional[str] = Field(None, max_length=1000)


class ConfirmationResponse(BaseModel):
    id: UUID
    complaint_id: UUID
    user_id: UUID
    vote: str
    comment: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class CommentCreate(BaseModel):
    complaint_id: UUID
    body: str = Field(..., min_length=2, max_length=2000)
    parent_comment_id: Optional[UUID] = None


class CommentResponse(BaseModel):
    id: UUID
    complaint_id: UUID
    author_id: UUID
    author_name: str
    body: str
    parent_comment_id: Optional[UUID]
    created_at: datetime

    model_config = {"from_attributes": True}


class CommunityStats(BaseModel):
    complaint_id: UUID
    confirmations: int
    disputes: int
    comments: int
    net_score: int  # confirmations - disputes
