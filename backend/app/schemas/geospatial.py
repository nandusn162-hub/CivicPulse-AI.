"""Pydantic schemas for GeoJSON types used in geospatial endpoints."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from pydantic import BaseModel, Field


class GeoPoint(BaseModel):
    type: str = "Point"
    coordinates: Tuple[float, float]  # [lon, lat]


class GeoPolygon(BaseModel):
    type: str = "Polygon"
    coordinates: List[List[Tuple[float, float]]]


class GeoFeatureProperties(BaseModel):
    complaint_id: Optional[str] = None
    title: Optional[str] = None
    category: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    impact_score: Optional[float] = None
    ward_name: Optional[str] = None


class GeoFeature(BaseModel):
    type: str = "Feature"
    geometry: Dict[str, Any]
    properties: Dict[str, Any]


class GeoFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[GeoFeature]


class HeatmapCell(BaseModel):
    latitude: float
    longitude: float
    weight: float  # normalised 0–1
    complaint_count: int
    avg_severity_score: float


class HeatmapResponse(BaseModel):
    cells: List[HeatmapCell]
    max_weight: float


class RepeatFailureZone(BaseModel):
    zone_id: str
    centroid_lat: float
    centroid_lon: float
    radius_meters: float
    recurrence_count: int
    dominant_category: str
    geojson_feature: GeoFeature


class RepeatFailureZonesResponse(BaseModel):
    type: str = "FeatureCollection"
    features: List[GeoFeature]
    summary: List[RepeatFailureZone]


class NearbyComplaintsRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    radius_meters: float = Field(500.0, ge=50, le=50000)
    limit: int = Field(50, ge=1, le=200)


class WardStats(BaseModel):
    ward_id: str
    ward_name: str
    complaint_count: int
    unresolved_count: int
    avg_impact_score: Optional[float]
    centroid_lat: Optional[float]
    centroid_lon: Optional[float]


class WardStatsResponse(BaseModel):
    items: List[WardStats]
