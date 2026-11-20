"""
backend/app/models/location.py
Geographic models: Ward boundaries, raw locations, infrastructure assets.
Uses GeoAlchemy2 for PostGIS geometry columns.
"""
import uuid
import enum

from geoalchemy2 import Geometry
from sqlalchemy import Float, ForeignKey, Index, Integer, String, Text, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from typing import Optional, Any
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin, SoftDeleteMixin


class AssetType(str, enum.Enum):
    ROAD = "road"
    POTHOLE = "pothole"
    STREETLIGHT = "streetlight"
    WATER_PIPE = "water_pipe"
    SEWER = "sewer"
    BRIDGE = "bridge"
    PARK = "park"
    BUILDING = "building"
    DRAINAGE = "drainage"
    ELECTRICITY_POLE = "electricity_pole"
    OTHER = "other"


class AssetCondition(str, enum.Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"
    FAILED = "failed"


class Ward(Base, TimestampMixin):
    __tablename__ = "wards"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    city: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    state: Mapped[str] = mapped_column(String(128), nullable=False)
    country: Mapped[str] = mapped_column(String(64), nullable=False, default="India")
    population: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    area_sq_km: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # PostGIS polygon for the ward boundary (SRID 4326 = WGS84)
    boundary: Mapped[Optional[Any]] = mapped_column(
        Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=True
    )
    centroid: Mapped[Optional[Any]] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326), nullable=True
    )

    # Relationships
    complaints: Mapped[list["Complaint"]] = relationship(  # noqa: F821
        "Complaint", back_populates="ward"
    )
    infrastructure_assets: Mapped[list["InfrastructureAsset"]] = relationship(
        "InfrastructureAsset", back_populates="ward"
    )
    risk_assessments: Mapped[list["RiskAssessment"]] = relationship(  # noqa: F821
        "RiskAssessment", back_populates="ward"
    )

    __table_args__ = (
        Index("ix_wards_boundary_gist", "boundary", postgresql_using="gist"),
        Index("ix_wards_centroid_gist", "centroid", postgresql_using="gist"),
    )

    def __repr__(self) -> str:
        return f"<Ward id={self.id} code={self.code}>"


class GeographicLocation(Base, TimestampMixin):
    """Represents a precise geographic point (attached to complaints, assets, etc.)."""
    __tablename__ = "geographic_locations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    altitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    accuracy_meters: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # PostGIS point
    point: Mapped[Any] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326), nullable=False
    )

    address_line1: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    address_line2: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    locality: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    pincode: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    landmark: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)

    ward_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("wards.id", ondelete="SET NULL"), nullable=True, index=True
    )
    ward: Mapped[Optional["Ward"]] = relationship("Ward")

    __table_args__ = (
        Index("ix_geo_locations_point_gist", "point", postgresql_using="gist"),
    )

    def __repr__(self) -> str:
        return f"<GeographicLocation lat={self.latitude} lng={self.longitude}>"


class InfrastructureAsset(Base, TimestampMixin, SoftDeleteMixin):
    """Tracks physical city infrastructure items."""
    __tablename__ = "infrastructure_assets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    asset_type: Mapped[AssetType] = mapped_column(
        Enum(AssetType, name="asset_type"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    condition: Mapped[AssetCondition] = mapped_column(
        Enum(AssetCondition, name="asset_condition"),
        default=AssetCondition.GOOD,
        nullable=False,
        index=True,
    )
    installation_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    last_maintained_at: Mapped[Optional[Any]] = mapped_column(nullable=True)

    # Location
    location_point: Mapped[Optional[Any]] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326), nullable=True
    )
    location_line: Mapped[Optional[Any]] = mapped_column(
        Geometry(geometry_type="LINESTRING", srid=4326), nullable=True
    )
    location_polygon: Mapped[Optional[Any]] = mapped_column(
        Geometry(geometry_type="POLYGON", srid=4326), nullable=True
    )
    address: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    ward_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("wards.id", ondelete="SET NULL"), nullable=True, index=True
    )
    ward: Mapped[Optional["Ward"]] = relationship("Ward", back_populates="infrastructure_assets")

    external_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    complaints: Mapped[list["Complaint"]] = relationship(  # noqa: F821
        "Complaint", back_populates="asset"
    )

    __table_args__ = (
        Index("ix_assets_location_point_gist", "location_point", postgresql_using="gist"),
        Index("ix_assets_location_line_gist", "location_line", postgresql_using="gist"),
        Index("ix_assets_location_polygon_gist", "location_polygon", postgresql_using="gist"),
    )

    def __repr__(self) -> str:
        return f"<InfrastructureAsset id={self.id} type={self.asset_type}>"
