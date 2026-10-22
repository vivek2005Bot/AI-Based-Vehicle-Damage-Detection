"""Inspection Service Layer.

Complies with ANTIGRAVITY_PROJECT_SPEC.md Section 6.2 & Section 6.3.
Enforces ownership validation, lifecycle state transitions, and file attachments.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.app.models_db.models import AnalysisJob, Inspection, InspectionFile, InspectionReport, User
from backend.app.schemas.inspection import InspectionCreate
from backend.app.services.file_storage import file_storage


def mask_vin(vin: Optional[str]) -> Optional[str]:
    """Mask VIN to preserve privacy in audit logs and API responses."""
    if not vin:
        return None
    clean = vin.strip().upper()
    if len(clean) < 8:
        return "***"
    return f"{clean[:3]}******{clean[-4:]}"


async def create_inspection(
    db: AsyncSession,
    user: User,
    data: InspectionCreate,
) -> Inspection:
    """Create a new draft inspection."""
    inspection = Inspection(
        user_id=user.id,
        make=data.make,
        model=data.model,
        year=data.year,
        mileage=data.mileage,
        mileage_unit=data.mileage_unit,
        vin_masked=mask_vin(data.vin),
        status="draft",
    )
    db.add(inspection)
    await db.flush()
    return inspection


async def get_user_inspection(
    db: AsyncSession,
    inspection_id: str,
    user: User,
) -> Optional[Inspection]:
    """Retrieve an inspection owned by the authenticated user."""
    stmt = (
        select(Inspection)
        .where(Inspection.id == inspection_id, Inspection.user_id == user.id)
        .options(selectinload(Inspection.files), selectinload(Inspection.jobs), selectinload(Inspection.report))
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_user_inspections(
    db: AsyncSession,
    user: User,
    limit: int = 50,
    offset: int = 0,
) -> List[Inspection]:
    """List recent inspections for the authenticated user."""
    stmt = (
        select(Inspection)
        .where(Inspection.user_id == user.id)
        .options(selectinload(Inspection.files), selectinload(Inspection.report))
        .order_by(desc(Inspection.created_at))
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def attach_file_to_inspection(
    db: AsyncSession,
    inspection: Inspection,
    role: str,
    storage_path: str,
    original_filename: str,
    byte_size: int,
    media_type: str,
) -> InspectionFile:
    """Record an uploaded file attachment."""
    f = InspectionFile(
        inspection_id=inspection.id,
        role=role,
        storage_path=storage_path,
        original_filename=original_filename,
        byte_size=byte_size,
        media_type=media_type,
    )
    db.add(f)
    await db.flush()
    return f


async def delete_inspection(
    db: AsyncSession,
    inspection: Inspection,
) -> None:
    """Delete an inspection, all related records, and all stored files from disk."""
    import shutil

    # Remove attached files from storage
    for f in inspection.files:
        if f.storage_path:
            file_storage.delete_file(f.storage_path)

    # Remove generated PDF report if present
    if inspection.report and inspection.report.pdf_storage_path:
        file_storage.delete_file(inspection.report.pdf_storage_path)

    # Clean up inspection directory in storage if it exists
    insp_dir = file_storage.root / f"insp_{inspection.id}"
    if insp_dir.exists() and insp_dir.is_dir():
        shutil.rmtree(insp_dir, ignore_errors=True)

    await db.delete(inspection)
    await db.commit()

