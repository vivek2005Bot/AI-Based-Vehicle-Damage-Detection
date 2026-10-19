"""SQLAlchemy 2.0 Persistent Database Models.

Complies with ANTIGRAVITY_PROJECT_SPEC.md Section 7.1.
Enforces non-guessable UUIDs, relationships, and foreign keys.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    inspections: Mapped[List[Inspection]] = relationship("Inspection", back_populates="user", cascade="all, delete-orphan")


class Inspection(Base):
    __tablename__ = "inspections"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True, nullable=False)

    # Vehicle Info (Optional)
    make: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    mileage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    mileage_unit: Mapped[str] = mapped_column(String(10), default="km")
    vin_masked: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Lifecycle Status: draft, queued, processing, completed, completed_with_warnings, failed
    status: Mapped[str] = mapped_column(String(50), default="draft", index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    user: Mapped[User] = relationship("User", back_populates="inspections")
    files: Mapped[List[InspectionFile]] = relationship("InspectionFile", back_populates="inspection", cascade="all, delete-orphan")
    jobs: Mapped[List[AnalysisJob]] = relationship("AnalysisJob", back_populates="inspection", cascade="all, delete-orphan")
    report: Mapped[Optional[InspectionReport]] = relationship("InspectionReport", back_populates="inspection", uselist=False, cascade="all, delete-orphan")
    estimate: Mapped[Optional[VehicleRepairEstimate]] = relationship("VehicleRepairEstimate", back_populates="inspection", uselist=False, cascade="all, delete-orphan")


class InspectionFile(Base):
    __tablename__ = "inspection_files"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    inspection_id: Mapped[str] = mapped_column(String(36), ForeignKey("inspections.id"), index=True, nullable=False)

    role: Mapped[str] = mapped_column(String(50), nullable=False)  # vehicle_image or obd_csv
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    byte_size: Mapped[int] = mapped_column(Integer, nullable=False)
    media_type: Mapped[str] = mapped_column(String(100), default="application/octet-stream")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    inspection: Mapped[Inspection] = relationship("Inspection", back_populates="files")


class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    inspection_id: Mapped[str] = mapped_column(String(36), ForeignKey("inspections.id"), index=True, nullable=False)

    status: Mapped[str] = mapped_column(String(50), default="queued", index=True)
    current_stage: Mapped[str] = mapped_column(String(100), default="queued")
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    inspection: Mapped[Inspection] = relationship("Inspection", back_populates="jobs")


class InspectionReport(Base):
    __tablename__ = "inspection_reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    inspection_id: Mapped[str] = mapped_column(String(36), ForeignKey("inspections.id"), unique=True, index=True, nullable=False)

    risk_class: Mapped[str] = mapped_column(String(50), default="unavailable")
    report_json: Mapped[str] = mapped_column(Text, nullable=False)
    pdf_storage_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    inspection: Mapped[Inspection] = relationship("Inspection", back_populates="report")


class VehicleRepairEstimate(Base):
    __tablename__ = "vehicle_repair_estimates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    inspection_id: Mapped[str] = mapped_column(String(36), ForeignKey("inspections.id"), unique=True, index=True, nullable=False)

    component_id: Mapped[str] = mapped_column(String(100), nullable=False)
    damage_type: Mapped[str] = mapped_column(String(100), nullable=False)
    extent_category: Mapped[str] = mapped_column(String(50), default="unknown")
    recommended_scenario: Mapped[str] = mapped_column(String(50), default="replacement")
    repair_expected: Mapped[float] = mapped_column(Float, default=0.0)
    replace_expected: Mapped[float] = mapped_column(Float, default=0.0)
    currency: Mapped[str] = mapped_column(String(10), default="INR")
    estimate_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    inspection: Mapped[Inspection] = relationship("Inspection", back_populates="estimate")
