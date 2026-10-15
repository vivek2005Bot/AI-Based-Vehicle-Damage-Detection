"""Inspection Management & Analysis Endpoints.

Complies with ANTIGRAVITY_PROJECT_SPEC.md Section 6.2 and Section 6.3.
Provides multi-image upload, optional OBD-II CSV upload, asynchronous analysis
job dispatch, status polling, and JSON/PDF report delivery.
"""

from __future__ import annotations

import asyncio
import json
import os
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Response, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.app.api.deps import get_current_user
from backend.app.core.config import settings
from backend.app.db.session import get_db
from backend.app.models_db.models import AnalysisJob, Inspection, InspectionFile, InspectionReport, User
from backend.app.schemas.inspection import (
    AnalysisJobResponse,
    InspectionCreate,
    InspectionResponse,
    InspectionStatusResponse,
)
from backend.app.services.file_storage import file_storage
from backend.app.services.inspection_service import (
    attach_file_to_inspection,
    create_inspection,
    get_user_inspection,
    list_user_inspections,
)
from backend.app.services.job_worker import execute_inspection_job

router = APIRouter(prefix="/inspections", tags=["Inspections"])


@router.post("", response_model=InspectionResponse, status_code=status.HTTP_201_CREATED)
async def create_new_inspection(
    data: InspectionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> InspectionResponse:
    """Create a new draft vehicle inspection."""
    inspection = await create_inspection(db, current_user, data)
    await db.commit()
    # Reload with relations
    loaded = await get_user_inspection(db, inspection.id, current_user)
    return InspectionResponse.model_validate(loaded)


@router.get("", response_model=List[InspectionResponse])
async def list_inspections(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
) -> List[InspectionResponse]:
    """Retrieve history of inspections for the authenticated user."""
    items = await list_user_inspections(db, current_user, limit, offset)
    out = []
    for item in items:
        resp = InspectionResponse.model_validate(item)
        if item.report:
            resp.has_report = True
            resp.risk_class = item.report.risk_class
        out.append(resp)
    return out


@router.get("/{inspection_id}", response_model=InspectionResponse)
async def get_inspection(
    inspection_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> InspectionResponse:
    """Retrieve an inspection by ID."""
    inspection = await get_user_inspection(db, inspection_id, current_user)
    if not inspection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inspection not found.",
        )
    resp = InspectionResponse.model_validate(inspection)
    if inspection.report:
        resp.has_report = True
        resp.risk_class = inspection.report.risk_class
    return resp


@router.post("/{inspection_id}/images")
async def upload_inspection_images(
    inspection_id: str,
    images: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Upload one or more vehicle inspection images (JPEG, PNG)."""
    inspection = await get_user_inspection(db, inspection_id, current_user)
    if not inspection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection not found.")

    uploaded_files = []
    max_bytes = settings.MAX_IMAGE_UPLOAD_MB * 1024 * 1024

    for img in images:
        ext = os.path.splitext(img.filename or "")[1].lower()
        if ext not in settings.ALLOWED_IMAGE_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported image format '{ext}'. Allowed formats: {settings.ALLOWED_IMAGE_EXTENSIONS}",
            )

        storage_rel_path, clean_name, byte_size = await file_storage.save_upload(img, subfolder=f"insp_{inspection.id}")
        if byte_size > max_bytes:
            file_storage.delete_file(storage_rel_path)
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Image {clean_name} exceeds maximum permitted size of {settings.MAX_IMAGE_UPLOAD_MB} MB.",
            )

        db_file = await attach_file_to_inspection(
            db,
            inspection=inspection,
            role="vehicle_image",
            storage_path=storage_rel_path,
            original_filename=clean_name,
            byte_size=byte_size,
            media_type=img.content_type or "image/jpeg",
        )
        uploaded_files.append({"id": db_file.id, "filename": clean_name, "size": byte_size})

    await db.commit()
    return {"uploaded_count": len(uploaded_files), "files": uploaded_files}


@router.post("/{inspection_id}/obd")
async def upload_inspection_obd(
    inspection_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Upload optional OBD-II telemetry CSV."""
    inspection = await get_user_inspection(db, inspection_id, current_user)
    if not inspection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection not found.")

    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in settings.ALLOWED_OBD_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Please upload a standard .csv telemetry file.",
        )

    storage_rel_path, clean_name, byte_size = await file_storage.save_upload(file, subfolder=f"insp_{inspection.id}")
    max_bytes = settings.MAX_OBD_UPLOAD_MB * 1024 * 1024
    if byte_size > max_bytes:
        file_storage.delete_file(storage_rel_path)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Telemetry CSV exceeds maximum size of {settings.MAX_OBD_UPLOAD_MB} MB.",
        )

    # If an existing OBD file was attached, replace it
    existing_obd = [f for f in inspection.files if f.role == "obd_csv"]
    for old_f in existing_obd:
        file_storage.delete_file(old_f.storage_path)
        await db.delete(old_f)

    db_file = await attach_file_to_inspection(
        db,
        inspection=inspection,
        role="obd_csv",
        storage_path=storage_rel_path,
        original_filename=clean_name,
        byte_size=byte_size,
        media_type=file.content_type or "text/csv",
    )
    await db.commit()
    return {"message": "OBD telemetry uploaded successfully.", "file_id": db_file.id, "filename": clean_name}


@router.post("/{inspection_id}/analyze", status_code=status.HTTP_202_ACCEPTED)
async def trigger_analysis(
    inspection_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Validate prerequisites and trigger asynchronous multi-agent inspection workflow."""
    inspection = await get_user_inspection(db, inspection_id, current_user)
    if not inspection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection not found.")

    image_files = [f for f in inspection.files if f.role == "vehicle_image"]
    if not image_files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot start analysis without at least one vehicle image. Please upload images first.",
        )

    # Create Analysis Job record
    job = AnalysisJob(
        inspection_id=inspection.id,
        status="queued",
        current_stage="queued",
    )
    inspection.status = "queued"
    db.add(job)
    await db.commit()
    await db.refresh(job)

    # Dispatch to background task worker
    background_tasks.add_task(execute_inspection_job, job.id, inspection.id)

    return {
        "job_id": job.id,
        "inspection_id": inspection.id,
        "status": "queued",
        "message": "Analysis successfully enqueued. You can poll the status endpoint for progress.",
    }


@router.get("/{inspection_id}/status", response_model=InspectionStatusResponse)
async def get_inspection_status(
    inspection_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> InspectionStatusResponse:
    """Poll current inspection analysis status and current processing stage."""
    inspection = await get_user_inspection(db, inspection_id, current_user)
    if not inspection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection not found.")

    latest_job = inspection.jobs[-1] if inspection.jobs else None
    current_stage = latest_job.current_stage if latest_job else inspection.status

    return InspectionStatusResponse(
        inspection_id=inspection.id,
        job_id=latest_job.id if latest_job else None,
        status=inspection.status,
        current_stage=current_stage,
        completed_stages=[],
        warnings=[],
        created_at=inspection.created_at,
        updated_at=inspection.updated_at,
    )


@router.get("/{inspection_id}/images/{file_id}/content")
async def get_inspection_image_content(
    inspection_id: str,
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Serve original uploaded vehicle image bytes (auth + ownership enforced)."""
    inspection = await get_user_inspection(db, inspection_id, current_user)
    if not inspection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection not found.")
    target = next((f for f in inspection.files if f.id == file_id and f.role == "vehicle_image"), None)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found.")
    try:
        full_path = file_storage.get_full_path(target.storage_path)
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
    if not os.path.exists(full_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image artifact missing.")
    return FileResponse(path=str(full_path), media_type=target.media_type or "image/jpeg")


@router.get("/{inspection_id}/report")
async def get_inspection_report(
    inspection_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Retrieve structured inspection report in JSON format."""
    inspection = await get_user_inspection(db, inspection_id, current_user)
    if not inspection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection not found.")

    if not inspection.report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not yet generated or analysis still in progress.",
        )

    return json.loads(inspection.report.report_json)


@router.get("/{inspection_id}/report.pdf")
async def download_inspection_pdf(
    inspection_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Download the finalized PDF inspection report."""
    inspection = await get_user_inspection(db, inspection_id, current_user)
    if not inspection or not inspection.report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inspection report not found.",
        )

    pdf_path = inspection.report.pdf_storage_path
    if not pdf_path or not os.path.exists(pdf_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF report artifact is not available.",
        )

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=f"vehicle_inspection_report_{inspection.id[:8]}.pdf",
    )
