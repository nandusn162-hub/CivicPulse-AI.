"""Pydantic schemas for complaints."""
from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ComplaintCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=256)
    description: str = Field(..., min_length=10)
    category: str = "other"
    location_address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    ward: Optional[str] = None


class ComplaintUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[str] = None
    resolution_notes: Optional[str] = None


class ComplaintOut(BaseModel):
    id: str
    title: str
    description: str
    category: str
    status: str
    priority: str
    reporter_id: str
    location_address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    ward: Optional[str] = None
    assigned_to: Optional[str] = None
    resolution_notes: Optional[str] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
