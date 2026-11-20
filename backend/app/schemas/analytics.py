"""Pydantic schemas for analytics endpoints."""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class OverviewStats(BaseModel):
    total_complaints: int
    unresolved_complaints: int
    resolved_last_30_days: int
    avg_resolution_days: float
    recurrence_rate_pct: float  # % of complaints that recurred within 6 months
    community_confirmations: int
    pending_inspections: int
    active_repairs: int


class DepartmentWorkload(BaseModel):
    department_id: str
    department_name: str
    assigned_complaints: int
    resolved_complaints: int
    pending_inspections: int
    active_repairs: int
    avg_resolution_days: Optional[float]


class DepartmentWorkloadResponse(BaseModel):
    items: List[DepartmentWorkload]


class RepairEffectivenessItem(BaseModel):
    department_name: str
    total_repairs: int
    verified_ok: int
    verified_failed: int
    inconclusive: int
    success_rate_pct: float


class RepairEffectivenessResponse(BaseModel):
    items: List[RepairEffectivenessItem]


class SeasonalBucket(BaseModel):
    period: str  # e.g. "2024-Q1" or "2024-01"
    complaint_count: int
    top_category: Optional[str]


class SeasonalPatternsResponse(BaseModel):
    buckets: List[SeasonalBucket]
    granularity: str  # month | quarter


class WardDistributionItem(BaseModel):
    ward_id: str
    ward_name: str
    complaint_count: int
    unresolved_count: int
    avg_impact_score: Optional[float]
    top_category: Optional[str]


class WardDistributionResponse(BaseModel):
    items: List[WardDistributionItem]
