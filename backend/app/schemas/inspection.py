"""Pydantic schemas for inspections."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class InspectionCreate(BaseModel):
    complaint_id: UUID
    inspector_id: UUID
    scheduled_at: datetime
    notes: Optional[str] = Field(None, max_length=2000)


class InspectionFindingsUpdate(BaseModel):
    status: str  # e.g. in_progress | completed | cancelled
    findings: Optional[str] = Field(None, max_length=4000)
    severity_confirmed: Optional[str] = None
    recommended_action: Optional[str] = Field(None, max_length=2000)
    completed_at: Optional[datetime] = None


class InspectionResponse(BaseModel):
    id: UUID
    complaint_id: UUID
    inspector_id: UUID
    inspector_name: str
    status: str
    scheduled_at: datetime
    completed_at: Optional[datetime]
    findings: Optional[str]
    severity_confirmed: Optional[str]
    recommended_action: Optional[str]
    evidence_files: List[Dict[str, Any]] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class InspectionListResponse(BaseModel):
    items: List[InspectionResponse]
    total: int
    page: int
    page_size: int
