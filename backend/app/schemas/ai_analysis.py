"""Pydantic schemas for AI analysis endpoints."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class AIAnalysisRequest(BaseModel):
    complaint_id: UUID
    evidence_ids: List[UUID] = Field(..., min_length=1, max_length=10)
    analysis_type: str = Field("evidence", pattern="^(evidence|repair_verification)$")

    @model_validator(mode="after")
    def validate_repair_verification(self) -> "AIAnalysisRequest":
        if self.analysis_type == "repair_verification" and len(self.evidence_ids) < 2:
            raise ValueError(
                "repair_verification requires at least 2 evidence IDs (before + after)."
            )
        return self


class RepairVerifyRequest(BaseModel):
    complaint_id: UUID
    before_evidence_id: UUID
    after_evidence_id: UUID


class IssueDetected(BaseModel):
    label: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    bounding_box: Optional[Dict[str, float]] = None


class AIAnalysisResponse(BaseModel):
    id: UUID
    complaint_id: UUID
    analysis_type: str
    status: str  # pending | completed | failed
    model_used: str
    issues_detected: List[IssueDetected] = []
    severity_assessment: Optional[str]
    damage_extent: Optional[str]
    recommended_action: Optional[str]
    confidence_overall: Optional[float] = Field(None, ge=0.0, le=1.0)
    raw_response: Optional[Dict[str, Any]] = None
    analysed_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class RepairVerificationResponse(BaseModel):
    id: UUID
    repair_id: UUID
    outcome: str  # verified | failed | inconclusive
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    ai_summary: str
    before_evidence_id: UUID
    after_evidence_id: UUID
    discrepancies: List[str] = []
    verified_at: datetime

    model_config = {"from_attributes": True}
