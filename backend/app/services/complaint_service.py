"""Complaint domain service."""
from __future__ import annotations

import datetime as dt
import uuid
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.services.audit_service import record_event
from app.services.notification_service import send_notification


# ---------------------------------------------------------------------------
# Valid status transitions
# ---------------------------------------------------------------------------
VALID_TRANSITIONS: Dict[str, List[str]] = {
    "submitted": ["under_review", "rejected"],
    "under_review": ["inspection_scheduled", "rejected"],
    "inspection_scheduled": ["inspected", "under_review"],
    "inspected": ["repair_scheduled", "rejected", "closed_no_action"],
    "repair_scheduled": ["repair_in_progress"],
    "repair_in_progress": ["repair_completed", "repair_failed"],
    "repair_completed": ["verification_pending"],
    "repair_failed": ["repair_scheduled", "closed_no_action"],
    "verification_pending": ["resolved", "repair_scheduled"],
    "resolved": ["reopened"],
    "reopened": ["under_review"],
    "rejected": [],
    "closed_no_action": [],
}


# ---------------------------------------------------------------------------
# Complaint number generation
# ---------------------------------------------------------------------------
def _generate_complaint_number() -> str:
    now = dt.datetime.now(dt.timezone.utc)
    suffix = uuid.uuid4().hex[:6].upper()
    return f"CP-{now.year}{now.month:02d}-{suffix}"


# ---------------------------------------------------------------------------
# Impact score weights
# ---------------------------------------------------------------------------
IMPACT_WEIGHTS = {
    "severity": 0.35,
    "reach": 0.25,
    "proximity": 0.20,
    "duration": 0.10,
    "corroboration": 0.10,
}

SEVERITY_SCORES = {
    "low": 0.25,
    "medium": 0.50,
    "high": 0.75,
    "critical": 1.00,
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def create_complaint(
    db: AsyncSession,
    *,
    reporter_id: UUID,
    title: str,
    description: str,
    category: str,
    severity: str,
    latitude: float,
    longitude: float,
    address: Optional[str] = None,
    ward_id: Optional[UUID] = None,
    asset_id: Optional[UUID] = None,
) -> Any:
    """Create a new complaint and emit an audit event."""
    from app.models.complaint import Complaint

    complaint_number = _generate_complaint_number()

    complaint = Complaint(
        complaint_number=complaint_number,
        reporter_id=reporter_id,
        title=title,
        description=description,
        category=category,
        severity=severity,
        status="submitted",
        latitude=latitude,
        longitude=longitude,
        address=address,
        ward_id=ward_id,
        asset_id=asset_id,
    )
    db.add(complaint)
    await db.flush()

    await record_event(
        db,
        entity_type="complaint",
        entity_id=complaint.id,
        action="submitted",
        actor_id=reporter_id,
        metadata={"complaint_number": complaint_number, "category": category, "severity": severity},
    )

    return complaint


async def get_complaint_timeline(db: AsyncSession, complaint_id: UUID) -> List[Dict[str, Any]]:
    """
    Return an ordered unified timeline of all events related to a complaint.
    Sources: audit events, inspections, repairs, verifications, community.
    """
    from app.models.audit import AuditEvent
    from app.models.community import CommunityConfirmation, Comment
    from app.models.inspection import Inspection
    from app.models.repair import RepairIntervention

    events: List[Dict[str, Any]] = []

    # Audit events
    audit_rows = (
        await db.execute(
            select(AuditEvent)
            .where(AuditEvent.entity_type == "complaint", AuditEvent.entity_id == complaint_id)
            .order_by(AuditEvent.occurred_at)
        )
    ).scalars().all()
    for row in audit_rows:
        events.append(
            {
                "event_type": "audit",
                "actor_name": str(row.actor_id),
                "description": row.action,
                "metadata": row.metadata,
                "occurred_at": row.occurred_at,
            }
        )

    # Inspections
    insp_rows = (
        await db.execute(
            select(Inspection).where(Inspection.complaint_id == complaint_id).order_by(Inspection.created_at)
        )
    ).scalars().all()
    for row in insp_rows:
        events.append(
            {
                "event_type": "inspection",
                "actor_name": str(row.inspector_id),
                "description": f"Inspection {row.status}",
                "metadata": {"findings": row.findings, "scheduled_at": str(row.scheduled_at)},
                "occurred_at": row.created_at,
            }
        )

    # Repairs
    repair_rows = (
        await db.execute(
            select(RepairIntervention)
            .where(RepairIntervention.complaint_id == complaint_id)
            .order_by(RepairIntervention.created_at)
        )
    ).scalars().all()
    for row in repair_rows:
        events.append(
            {
                "event_type": "repair",
                "actor_name": str(row.department_id),
                "description": f"Repair {row.status}: {row.description[:80]}",
                "metadata": {"status": row.status, "cost_estimate": str(row.cost_estimate)},
                "occurred_at": row.created_at,
            }
        )

    # Community confirmations
    conf_rows = (
        await db.execute(
            select(CommunityConfirmation)
            .where(CommunityConfirmation.complaint_id == complaint_id)
            .order_by(CommunityConfirmation.created_at)
        )
    ).scalars().all()
    for row in conf_rows:
        events.append(
            {
                "event_type": "community",
                "actor_name": str(row.user_id),
                "description": f"Community {row.vote}",
                "metadata": {"comment": row.comment},
                "occurred_at": row.created_at,
            }
        )

    # Sort unified timeline
    events.sort(key=lambda e: e["occurred_at"])
    return events


async def update_complaint_status(
    db: AsyncSession,
    *,
    complaint_id: UUID,
    new_status: str,
    actor_id: UUID,
    note: Optional[str] = None,
) -> Any:
    """
    Validate status transition, apply it, and record an audit event.
    Raises ValueError for invalid transitions.
    """
    from app.models.complaint import Complaint

    result = await db.execute(select(Complaint).where(Complaint.id == complaint_id))
    complaint = result.scalar_one_or_none()
    if complaint is None:
        raise ValueError(f"Complaint {complaint_id} not found.")

    allowed = VALID_TRANSITIONS.get(complaint.status, [])
    if new_status not in allowed:
        raise ValueError(
            f"Transition from '{complaint.status}' to '{new_status}' is not permitted. "
            f"Allowed: {allowed}."
        )

    old_status = complaint.status
    complaint.status = new_status
    if new_status == "resolved":
        complaint.resolved_at = dt.datetime.now(dt.timezone.utc)

    await db.flush()

    await record_event(
        db,
        entity_type="complaint",
        entity_id=complaint_id,
        action="status_changed",
        actor_id=actor_id,
        metadata={"from": old_status, "to": new_status, "note": note},
    )

    return complaint


def calculate_impact_score(
    *,
    severity: str,
    affected_population: Optional[int],
    proximity_score: Optional[float],
    days_open: Optional[int],
    corroboration_count: int,
) -> Dict[str, float]:
    """
    Weighted impact score breakdown.

    Weights:
        severity      35%
        reach         25%
        proximity     20%
        duration      10%
        corroboration 10%

    Missing data is NOT silently treated as 0 — it is flagged as None in the
    breakdown so callers know the total is a partial estimate.
    """
    breakdown: Dict[str, Optional[float]] = {}

    # Severity (0–1 scale)
    sev_score = SEVERITY_SCORES.get(severity.lower())
    breakdown["severity"] = sev_score

    # Reach — normalised per 10 000 residents, capped at 1
    if affected_population is not None:
        reach = min(affected_population / 10_000, 1.0)
    else:
        reach = None
    breakdown["reach"] = reach

    # Proximity — already 0–1 from caller
    breakdown["proximity"] = proximity_score

    # Duration — 1 day → 0.1; 30+ days → 1.0
    if days_open is not None:
        duration = min(days_open / 30.0, 1.0)
    else:
        duration = None
    breakdown["duration"] = duration

    # Corroboration — 1 confirmation → 0.2; 5+ → 1.0
    corr = min(corroboration_count / 5.0, 1.0)
    breakdown["corroboration"] = corr

    # Total — only sum factors that are present
    total = 0.0
    for key, weight in IMPACT_WEIGHTS.items():
        val = breakdown[key]
        if val is not None:
            total += val * weight

    return {
        "severity": breakdown["severity"],
        "reach": breakdown["reach"],
        "proximity": breakdown["proximity"],
        "duration": breakdown["duration"],
        "corroboration": breakdown["corroboration"],
        "total": round(total, 4),
    }


async def assign_department(
    db: AsyncSession,
    *,
    complaint_id: UUID,
    department_id: Optional[UUID],
    inspector_id: Optional[UUID],
    actor_id: UUID,
    note: Optional[str] = None,
) -> Any:
    """Assign department and/or inspector to a complaint; record audit event."""
    from app.models.complaint import Complaint

    result = await db.execute(select(Complaint).where(Complaint.id == complaint_id))
    complaint = result.scalar_one_or_none()
    if complaint is None:
        raise ValueError(f"Complaint {complaint_id} not found.")

    changes: Dict[str, Any] = {}
    if department_id is not None:
        complaint.assigned_department_id = department_id
        changes["department_id"] = str(department_id)
    if inspector_id is not None:
        complaint.assigned_inspector_id = inspector_id
        changes["inspector_id"] = str(inspector_id)

    await db.flush()

    await record_event(
        db,
        entity_type="complaint",
        entity_id=complaint_id,
        action="assigned",
        actor_id=actor_id,
        metadata={**changes, "note": note},
    )

    return complaint
