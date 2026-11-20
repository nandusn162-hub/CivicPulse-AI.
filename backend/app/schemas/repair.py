"""Pydantic schemas for repairs."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class RepairCreate(BaseModel):
    complaint_id: UUID
    department_id: UUID
    description: str = Field(..., min_length=10, max_length=4000)
    cost_estimate: Optional[float] = Field(None, ge=0)
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None


class RepairStatusUpdate(BaseModel):
    status: str  # scheduled | in_progress | completed | failed
    notes: Optional[str] = Field(None, max_length=2000)
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    final_cost: Optional[float] = Field(None, ge=0)


class VerificationResult(BaseModel):
    id: UUID
    repair_id: UUID
    outcome: str  # verified | failed | inconclusive
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    ai_summary: str
    before_evidence_id: Optional[UUID]
    after_evidence_id: Optional[UUID]
    verified_at: datetime

    model_config = {"from_attributes": True}


class RepairResponse(BaseModel):
    id: UUID
    complaint_id: UUID
    department_id: UUID
    department_name: str
    description: str
    status: str
    cost_estimate: Optional[float]
    final_cost: Optional[float]
    scheduled_start: Optional[datetime]
    scheduled_end: Optional[datetime]
    actual_start: Optional[datetime]
    actual_end: Optional[datetime]
    verification: Optional[VerificationResult]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RepairListResponse(BaseModel):
    items: List[RepairResponse]
    total: int
