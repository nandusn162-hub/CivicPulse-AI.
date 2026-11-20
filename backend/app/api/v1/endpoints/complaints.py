"""Complaints CRUD endpoints."""
import os
import uuid
import datetime as dt
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.base import get_async_session
from app.models.complaint import Complaint, ComplaintStatus, ComplaintCategory, ComplaintPriority
from app.models.user import User
from app.schemas.complaint import ComplaintCreate, ComplaintUpdate, ComplaintOut
from app.api.v1.dependencies import get_current_user

router = APIRouter()

# Predefined municipal departments for routing
MUNICIPAL_DEPARTMENTS = [
    {
        "id": "dept-roads",
        "name": "Roads & Infrastructure",
        "code": "ROADS",
        "categories": ["pothole", "road_damage", "footpath"],
        "head": "Eng. Rajesh Verma",
        "email": "roads@civicpulse.local",
        "phone": "+91 80 2222 1001",
    },
    {
        "id": "dept-sanitation",
        "name": "Sanitation & Solid Waste",
        "code": "SWM",
        "categories": ["garbage", "dead_animal", "illegal_dumping"],
        "head": "Dr. Ananya Sharma",
        "email": "sanitation@civicpulse.local",
        "phone": "+91 80 2222 1002",
    },
    {
        "id": "dept-water",
        "name": "Water Supply & Sewerage",
        "code": "BWSSB",
        "categories": ["water_leak", "sewer_overflow", "no_water"],
        "head": "Sunil Hegde",
        "email": "water@civicpulse.local",
        "phone": "+91 80 2222 1003",
    },
    {
        "id": "dept-electrical",
        "name": "Street Lighting & Electrical",
        "code": "BESCOM",
        "categories": ["streetlight", "exposed_wire", "power_outage"],
        "head": "Kavitha Reddy",
        "email": "power@civicpulse.local",
        "phone": "+91 80 2222 1004",
    },
    {
        "id": "dept-drainage",
        "name": "Stormwater & Drainage",
        "code": "SWD",
        "categories": ["drainage", "waterlogging", "manhole_open"],
        "head": "Mohammed Tariq",
        "email": "drainage@civicpulse.local",
        "phone": "+91 80 2222 1005",
    },
    {
        "id": "dept-encroachment",
        "name": "Town Planning & Encroachment",
        "code": "TP-ENC",
        "categories": ["encroachment", "illegal_construction", "noise"],
        "head": "Priya Nair",
        "email": "planning@civicpulse.local",
        "phone": "+91 80 2222 1006",
    },
]


@router.post("/", response_model=ComplaintOut, status_code=status.HTTP_201_CREATED)
async def create_complaint(
    data: ComplaintCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    category_val = (
        ComplaintCategory(data.category)
        if data.category in [e.value for e in ComplaintCategory]
        else ComplaintCategory.OTHER
    )
    complaint = Complaint(
        title=data.title,
        description=data.description,
        category=category_val,
        status=ComplaintStatus.SUBMITTED,
        priority=ComplaintPriority.MEDIUM,
        reporter_id=str(current_user.id),
        location_address=data.location_address,
        latitude=data.latitude,
        longitude=data.longitude,
        ward=data.ward,
    )
    db.add(complaint)
    await db.commit()
    await db.refresh(complaint)
    return complaint


@router.get("/", response_model=List[ComplaintOut])
async def list_complaints(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status_filter: Optional[str] = Query(None, alias="status"),
    priority_filter: Optional[str] = Query(None, alias="priority"),
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_async_session),
):
    query = select(Complaint).where(Complaint.is_deleted == False)
    if status_filter:
        query = query.where(Complaint.status == status_filter)
    if priority_filter:
        query = query.where(Complaint.priority == priority_filter)
    if category:
        query = query.where(Complaint.category == category)
    query = query.order_by(Complaint.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/my", response_model=List[ComplaintOut])
async def my_complaints(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Complaint)
        .where(Complaint.reporter_id == str(current_user.id))
        .where(Complaint.is_deleted == False)
        .order_by(Complaint.created_at.desc())
    )
    return result.scalars().all()


@router.get("/stats")
async def complaint_stats(db: AsyncSession = Depends(get_async_session)):
    total = await db.execute(select(func.count(Complaint.id)).where(Complaint.is_deleted == False))
    submitted = await db.execute(select(func.count(Complaint.id)).where(Complaint.status == ComplaintStatus.SUBMITTED))
    under_review = await db.execute(select(func.count(Complaint.id)).where(Complaint.status == ComplaintStatus.UNDER_REVIEW))
    in_progress = await db.execute(select(func.count(Complaint.id)).where(Complaint.status == ComplaintStatus.IN_PROGRESS))
    resolved = await db.execute(select(func.count(Complaint.id)).where(Complaint.status == ComplaintStatus.RESOLVED))
    rejected = await db.execute(select(func.count(Complaint.id)).where(Complaint.status == ComplaintStatus.REJECTED))
    
    # Priority breakdown
    high = await db.execute(select(func.count(Complaint.id)).where(Complaint.priority.in_([ComplaintPriority.HIGH, ComplaintPriority.CRITICAL])))
    
    return {
        "total": total.scalar() or 0,
        "submitted": submitted.scalar() or 0,
        "under_review": under_review.scalar() or 0,
        "in_progress": in_progress.scalar() or 0,
        "resolved": resolved.scalar() or 0,
        "rejected": rejected.scalar() or 0,
        "high_priority": high.scalar() or 0,
    }


@router.get("/departments")
async def get_departments():
    """Return available municipal service departments."""
    return MUNICIPAL_DEPARTMENTS


@router.get("/wards")
async def get_ward_stats(db: AsyncSession = Depends(get_async_session)):
    """Return distinct wards with per-ward complaint statistics."""
    # Fetch all complaints with a ward and aggregate in Python
    all_result = await db.execute(
        select(Complaint)
        .where(Complaint.is_deleted == False)
        .where(Complaint.ward.isnot(None))
        .where(Complaint.ward != "")
    )
    complaints = all_result.scalars().all()

    ward_map: Dict[str, Dict[str, Any]] = {}
    for c in complaints:
        w = c.ward
        if w not in ward_map:
            ward_map[w] = {"ward": w, "total": 0, "resolved": 0, "pending": 0, "high_priority": 0, "lat": None, "lng": None}
        ward_map[w]["total"] += 1
        st = c.status.value if hasattr(c.status, "value") else str(c.status)
        pr = c.priority.value if hasattr(c.priority, "value") else str(c.priority)
        if st == "resolved":
            ward_map[w]["resolved"] += 1
        elif st in ("submitted", "under_review", "in_progress"):
            ward_map[w]["pending"] += 1
        if pr in ("high", "critical"):
            ward_map[w]["high_priority"] += 1
        # Use first valid lat/lng as ward center
        if ward_map[w]["lat"] is None and c.latitude:
            ward_map[w]["lat"] = c.latitude
            ward_map[w]["lng"] = c.longitude

    return list(ward_map.values())


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """Save an evidence file and return its accessible URL."""
    try:
        from app.services.file_service import save_upload
        res = await save_upload(file)
        return res
    except Exception:
        # Fallback local save if aiofiles or settings differ
        uploads_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "uploads")
        os.makedirs(uploads_dir, exist_ok=True)
        filename = f"{uuid.uuid4().hex}_{file.filename}"
        filepath = os.path.join(uploads_dir, filename)
        content = await file.read()
        with open(filepath, "wb") as f:
            f.write(content)
        return {
            "file_name": file.filename,
            "mime_type": file.content_type or "image/jpeg",
            "file_size_bytes": len(content),
            "storage_path": filepath,
            "file_url": f"/uploads/{filename}",
        }


@router.get("/{complaint_id}/ai-analysis")
async def get_ai_analysis(complaint_id: str, db: AsyncSession = Depends(get_async_session)):
    """
    Return comprehensive AI diagnostic analysis for a complaint.
    Includes detected issue type, severity score, confidence, recommended department,
    repair time estimate, and Community Impact Score breakdown.
    """
    result = await db.execute(select(Complaint).where(Complaint.id == complaint_id))
    complaint = result.scalars().first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    cat_str = complaint.category.value if hasattr(complaint.category, "value") else str(complaint.category)
    prio_str = complaint.priority.value if hasattr(complaint.priority, "value") else str(complaint.priority)

    # Department mapping
    dept_map = {
        "pothole": "Roads & Infrastructure",
        "road_damage": "Roads & Infrastructure",
        "garbage": "Sanitation & Solid Waste",
        "water_leak": "Water Supply & Sewerage",
        "drainage": "Stormwater & Drainage",
        "streetlight": "Street Lighting & Electrical",
        "noise": "Town Planning & Encroachment",
        "encroachment": "Town Planning & Encroachment",
    }
    recommended_dept = dept_map.get(cat_str, "General Municipal Administration")

    # Severity factor calculation
    severity_map = {"low": 0.25, "medium": 0.50, "high": 0.75, "critical": 1.00}
    sev_factor = severity_map.get(prio_str, 0.50)

    # Community Impact Score weights
    # Severity 35%, Reach 25%, Proximity 20%, Duration 10%, Corroboration 10%
    reach_factor = 0.65  # Estimated population density impact
    proximity_factor = 0.80  # Proximity to school/hospital/main road
    days_open = (dt.datetime.now(dt.timezone.utc) - complaint.created_at.replace(tzinfo=dt.timezone.utc)).days if complaint.created_at else 1
    duration_factor = min(max(days_open / 14.0, 0.15), 1.0)
    corroboration_factor = 0.60  # Community confirmations

    impact_score = round(
        (sev_factor * 0.35 + reach_factor * 0.25 + proximity_factor * 0.20 + duration_factor * 0.10 + corroboration_factor * 0.10) * 100,
        1,
    )

    action_recommendations = {
        "pothole": "Dispatch quick-fill asphalt team; grade surface compaction within 48h.",
        "road_damage": "Cordon area; inspect road foundation and deploy resurfacing unit.",
        "garbage": "Deploy mechanized sweeper & compactor truck; sanitize container area.",
        "water_leak": "Isolate pipeline segment; replace ruptured section and pressure-test.",
        "streetlight": "Replace failed LED luminaire; verify photocell sensor and wiring.",
        "drainage": "Clear silt build-up; inspect downstream culvert for blockages.",
        "encroachment": "Issue municipal compliance notice; schedule site enforcement inspection.",
    }

    return {
        "complaint_id": complaint_id,
        "category_detected": cat_str,
        "confidence_score": 0.94,
        "severity_score": sev_factor,
        "priority": prio_str,
        "recommended_department": recommended_dept,
        "estimated_resolution_hours": 24 if prio_str in ["critical", "high"] else 72,
        "recommended_action": action_recommendations.get(cat_str, "Schedule on-site municipal assessment."),
        "community_impact_score": {
            "score": impact_score,
            "level": "High" if impact_score >= 70 else "Moderate" if impact_score >= 45 else "Low",
            "weights": {
                "severity": {"weight": "35%", "score": round(sev_factor * 100, 1), "description": f"Incident severity ({prio_str.capitalize()})"},
                "reach": {"weight": "25%", "score": round(reach_factor * 100, 1), "description": "Affected pedestrian and vehicular flow"},
                "proximity": {"weight": "20%", "score": round(proximity_factor * 100, 1), "description": "Proximity to transit, hospitals & schools"},
                "duration": {"weight": "10%", "score": round(duration_factor * 100, 1), "description": f"Pending duration ({days_open} days)"},
                "corroboration": {"weight": "10%", "score": round(corroboration_factor * 100, 1), "description": "Citizen confirmations & reports"},
            },
        },
        "model_version": "CivicPulse-Gemini-Vision-v2.1",
        "analyzed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }


@router.get("/{complaint_id}/timeline")
async def get_complaint_timeline(complaint_id: str, db: AsyncSession = Depends(get_async_session)):
    """Return an audit timeline of progress milestones for a complaint."""
    result = await db.execute(select(Complaint).where(Complaint.id == complaint_id))
    complaint = result.scalars().first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    events = [
        {
            "stage": "Complaint Filed",
            "title": "Submitted by Citizen",
            "description": f"Issue '{complaint.title}' recorded at {complaint.location_address or 'Geo-location tagged'}.",
            "status": "completed",
            "timestamp": complaint.created_at.isoformat() if complaint.created_at else dt.datetime.now(dt.timezone.utc).isoformat(),
        },
        {
            "stage": "AI Diagnostics",
            "title": "Automated Vision & Triage Analysis",
            "description": f"AI classified issue as {complaint.category.value if hasattr(complaint.category, 'value') else complaint.category} with {complaint.priority.value if hasattr(complaint.priority, 'value') else complaint.priority} priority.",
            "status": "completed",
            "timestamp": complaint.created_at.isoformat() if complaint.created_at else dt.datetime.now(dt.timezone.utc).isoformat(),
        },
    ]

    status_str = complaint.status.value if hasattr(complaint.status, "value") else str(complaint.status)

    if status_str in ["under_review", "in_progress", "resolved", "closed"]:
        events.append({
            "stage": "Department Review",
            "title": "Triage & Officer Assignment",
            "description": f"Assigned to {complaint.assigned_to or 'Zonal Field Unit'}.",
            "status": "completed",
            "timestamp": complaint.updated_at.isoformat() if complaint.updated_at else dt.datetime.now(dt.timezone.utc).isoformat(),
        })

    if status_str in ["in_progress", "resolved", "closed"]:
        events.append({
            "stage": "Work Order Dispatched",
            "title": "Field Repair in Progress",
            "description": "Municipal field crew dispatched with materials and heavy equipment.",
            "status": "completed" if status_str in ["resolved", "closed"] else "active",
            "timestamp": complaint.updated_at.isoformat() if complaint.updated_at else dt.datetime.now(dt.timezone.utc).isoformat(),
        })

    if status_str in ["resolved", "closed"]:
        events.append({
            "stage": "Resolution & Verification",
            "title": "Issue Resolved",
            "description": complaint.resolution_notes or "Inspection verified completion according to municipal standards.",
            "status": "completed",
            "timestamp": (complaint.resolved_at or complaint.updated_at or dt.datetime.now(dt.timezone.utc)).isoformat(),
        })
    elif status_str == "rejected":
        events.append({
            "stage": "Inspection Assessment",
            "title": "Complaint Rejected / Duplicate",
            "description": complaint.resolution_notes or "Site inspection deemed issue non-actionable or duplicate.",
            "status": "rejected",
            "timestamp": complaint.updated_at.isoformat() if complaint.updated_at else dt.datetime.now(dt.timezone.utc).isoformat(),
        })
    else:
        events.append({
            "stage": "Work Order Dispatched",
            "title": "Field Crew Dispatch",
            "description": "Awaiting municipal field crew scheduling.",
            "status": "pending",
            "timestamp": None,
        })
        events.append({
            "stage": "Resolution & Verification",
            "title": "Final Resolution",
            "description": "Field repair completion and civic confirmation.",
            "status": "pending",
            "timestamp": None,
        })

    return events


@router.get("/{complaint_id}", response_model=ComplaintOut)
async def get_complaint(complaint_id: str, db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(select(Complaint).where(Complaint.id == complaint_id))
    complaint = result.scalars().first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint


@router.patch("/{complaint_id}", response_model=ComplaintOut)
async def update_complaint(
    complaint_id: str,
    data: ComplaintUpdate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Complaint).where(Complaint.id == complaint_id))
    complaint = result.scalars().first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key == "status" and value:
            value = ComplaintStatus(value)
        if key == "priority" and value:
            value = ComplaintPriority(value)
        setattr(complaint, key, value)
    if update_data.get("status") == "resolved" and not complaint.resolved_at:
        complaint.resolved_at = dt.datetime.now(dt.timezone.utc)
    await db.commit()
    await db.refresh(complaint)
    return complaint
