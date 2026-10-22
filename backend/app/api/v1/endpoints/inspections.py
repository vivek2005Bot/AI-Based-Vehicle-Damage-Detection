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
from fastapi import APIRouter, BackgroundTasks, Depends, File, Header, HTTPException, Query, Response, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from reports.pdf_renderer import render_inspection_pdf

from backend.app.api.deps import get_current_user
from backend.app.core.config import settings
from backend.app.db.session import get_db
from backend.app.models_db.models import AnalysisJob, Inspection, InspectionFile, InspectionReport, User, VehicleRepairEstimate
from backend.app.schemas.inspection import (
    AnalysisJobResponse,
    EstimateUpdateRequest,
    InspectionCreate,
    InspectionResponse,
    InspectionStatusResponse,
)
from ml.cost_estimation import (
    ComponentDamageSummary,
    ComponentIdentificationMethod,
    ExtentCategory,
    PartTier,
    VehicleCostContext,
    calculate_extent_category,
    get_component_metadata,
    infer_damage_summary_from_detections,
    online_pricing_service,
    repair_cost_estimator,
)
from backend.app.services.file_storage import file_storage
from backend.app.services.inspection_service import (
    attach_file_to_inspection,
    create_inspection,
    delete_inspection,
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


@router.delete("/{inspection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_inspection_endpoint(
    inspection_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete an inspection, its files, reports, and estimates."""
    inspection = await get_user_inspection(db, inspection_id, current_user)
    if not inspection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inspection not found.",
        )
    await delete_inspection(db, inspection)


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
    locale: Optional[str] = Query(None, description="Requested report locale (e.g. 'en', 'hi', 'ta')"),
    accept_language: Optional[str] = Header(None),
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

    report_dict = json.loads(inspection.report.report_json)

    # Ensure repair cost estimate is only attached when damage was genuinely detected
    is_damaged = bool(report_dict.get("overall", {}).get("damage_detected"))
    if not is_damaged:
        report_dict["estimate"] = None
        stmt_del = delete(VehicleRepairEstimate).where(VehicleRepairEstimate.inspection_id == inspection.id)
        await db.execute(stmt_del)
        await db.commit()
    elif not report_dict.get("estimate"):
        stmt = select(VehicleRepairEstimate).where(VehicleRepairEstimate.inspection_id == inspection.id)
        db_est = (await db.execute(stmt)).scalar_one_or_none()
        if db_est:
            report_dict["estimate"] = json.loads(db_est.estimate_json)
        else:
            try:
                images = report_dict.get("images", [])
                (
                    primary_comp,
                    primary_dmg,
                    extent_cat,
                    rel_area,
                    distinct_cnt,
                    top_finding_id,
                    dmg_conf,
                    comp_conf,
                ) = infer_damage_summary_from_detections(images)

                comp_meta = get_component_metadata(primary_comp)
                damage_summary = ComponentDamageSummary(
                    component_id=primary_comp,
                    component_display_name=comp_meta.get("display_name", primary_comp.replace("_", " ").title()),
                    component_confidence=comp_conf,
                    damage_type=primary_dmg,
                    damage_confidence=dmg_conf,
                    component_identification_method=ComponentIdentificationMethod.POSITIONAL_HEURISTIC,
                    component_verification_required=True,
                    extent_category=extent_cat,
                    damage_area_ratio=rel_area,
                    distinct_regions_count=distinct_cnt,
                )

                v_ctx = VehicleCostContext(
                    make=inspection.make,
                    model=inspection.model,
                    year=inspection.year,
                )

                est_resp = repair_cost_estimator.estimate_cost(
                    inspection_id=inspection.id,
                    damage_summary=damage_summary,
                    vehicle_context=v_ctx,
                    finding_id=top_finding_id,
                )
                report_dict["estimate"] = est_resp.model_dump()
                inspection.report.report_json = json.dumps(report_dict)

                new_db_est = VehicleRepairEstimate(
                    inspection_id=inspection.id,
                    component_id=primary_comp,
                    damage_type=primary_dmg,
                    extent_category=extent_cat.value,
                    recommended_scenario="repair" if est_resp.repair_scenario.is_recommended else "replacement",
                    repair_expected=est_resp.repair_scenario.expected,
                    replace_expected=est_resp.replacement_scenario.expected,
                    currency=v_ctx.currency,
                    estimate_json=json.dumps(report_dict["estimate"]),
                )
                db.add(new_db_est)
                await db.commit()
            except Exception:
                pass

    req_locale = locale or (accept_language.split(",")[0].split(";")[0].strip() if accept_language else None) or "en"
    req_locale = req_locale.lower().split("-")[0].split("_")[0]
    report_dict["locale"] = req_locale
    return report_dict


@router.get("/{inspection_id}/report.pdf")
async def download_inspection_pdf(
    inspection_id: str,
    locale: Optional[str] = Query(None, description="Requested report locale (e.g. 'en', 'hi', 'ta')"),
    accept_language: Optional[str] = Header(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Download the finalized PDF inspection report with multilingual localization."""
    inspection = await get_user_inspection(db, inspection_id, current_user)
    if not inspection or not inspection.report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inspection report not found.",
        )

    req_locale = locale or (accept_language.split(",")[0].split(";")[0].strip() if accept_language else None) or "en"
    req_locale = req_locale.lower().split("-")[0].split("_")[0]

    pdf_path = inspection.report.pdf_storage_path
    if req_locale == "en" and pdf_path and os.path.exists(pdf_path):
        return FileResponse(
            path=pdf_path,
            media_type="application/pdf",
            filename=f"vehicle_inspection_report_{inspection.id[:8]}.pdf",
        )

    # Dynamic render with requested locale
    try:
        report_data = json.loads(inspection.report.report_json)
        pdf_bytes = render_inspection_pdf(report_data, locale=req_locale)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="vehicle_inspection_report_{inspection.id[:8]}_{req_locale}.pdf"'
            },
        )
    except Exception as exc:
        if pdf_path and os.path.exists(pdf_path):
            return FileResponse(
                path=pdf_path,
                media_type="application/pdf",
                filename=f"vehicle_inspection_report_{inspection.id[:8]}.pdf",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to render localized PDF report: {exc}",
        )


@router.get("/{inspection_id}/estimate")
async def get_inspection_estimate(
    inspection_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Retrieve the current repair vs replacement cost estimate for this inspection."""
    inspection = await get_user_inspection(db, inspection_id, current_user)
    if not inspection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection not found.")

    # 1. Check direct VehicleRepairEstimate table
    stmt = select(VehicleRepairEstimate).where(VehicleRepairEstimate.inspection_id == inspection.id)
    est_row = (await db.execute(stmt)).scalar_one_or_none()
    if est_row:
        return json.loads(est_row.estimate_json)

    # 2. Check InspectionReport report_json
    if inspection.report and inspection.report.report_json:
        report_data = json.loads(inspection.report.report_json)
        if report_data.get("estimate"):
            return report_data["estimate"]

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Repair cost estimate not yet generated for this inspection.",
    )


@router.post("/{inspection_id}/estimate")
async def update_inspection_estimate(
    inspection_id: str,
    override: EstimateUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Update or recalculate the repair vs replacement cost estimate with user-confirmed overrides.

    Allows technician to specify exact component, extent, make/model, or trigger live online price refresh.
    """
    inspection = await get_user_inspection(db, inspection_id, current_user)
    if not inspection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection not found.")

    # Determine base values from existing report or inspection
    existing_est: Dict[str, Any] = {}
    inferred_comp = "front_bumper"
    inferred_dmg = "scratch"
    inferred_ext = ExtentCategory.MINOR
    if inspection.report and inspection.report.report_json:
        rep_dict = json.loads(inspection.report.report_json)
        is_damaged = bool(rep_dict.get("overall", {}).get("damage_detected"))
        images = rep_dict.get("images", [])
        total_dets = sum(len(img.get("detections", [])) for img in images)
        if not is_damaged or total_dets == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No damage detected on this vehicle. No cost estimation is needed.",
            )
        existing_est = rep_dict.get("estimate") or {}
        if not existing_est.get("damage", {}).get("component_id"):
            inferred_comp, inferred_dmg, inferred_ext, _, _, _, _, _ = infer_damage_summary_from_detections(images)

    cid = (override.component_id or existing_est.get("damage", {}).get("component_id") or inferred_comp).strip().lower()
    dmg_type = (override.damage_type or existing_est.get("damage", {}).get("damage_type") or inferred_dmg).strip().lower()
    extent_str = (override.extent_category or existing_est.get("damage", {}).get("extent_category") or inferred_ext.value).strip().lower()
    extent_cat = ExtentCategory.MINOR
    if extent_str == "moderate":
        extent_cat = ExtentCategory.MODERATE
    elif extent_str == "extensive":
        extent_cat = ExtentCategory.EXTENSIVE

    v_make = override.make or existing_est.get("vehicle", {}).get("make") or inspection.make
    v_model = override.model or existing_est.get("vehicle", {}).get("model") or inspection.model
    v_year = override.year or existing_est.get("vehicle", {}).get("year") or inspection.year
    v_city = override.city or existing_est.get("vehicle", {}).get("city") or "Delhi NCR"

    tier_pref = PartTier.OEM
    if override.oem_preference and override.oem_preference.lower() == "aftermarket":
        tier_pref = PartTier.AFTERMARKET

    v_ctx = VehicleCostContext(
        make=v_make,
        model=v_model,
        year=v_year,
        city=v_city,
        oem_preference=tier_pref,
    )

    comp_meta = get_component_metadata(cid)
    damage_summary = ComponentDamageSummary(
        component_id=cid,
        component_display_name=comp_meta.get("display_name", cid.replace("_", " ").title()),
        component_confidence=1.0 if override.component_id else 0.70,
        damage_type=dmg_type,
        damage_confidence=0.90,
        component_identification_method=ComponentIdentificationMethod.USER_CONFIRMED if override.component_id else ComponentIdentificationMethod.POSITIONAL_HEURISTIC,
        component_verification_required=False if override.component_id else True,
        extent_category=extent_cat,
    )

    if override.refresh_pricing:
        cache_key = online_pricing_service._get_cache_key(v_make, v_model, cid)
        online_pricing_service._memory_cache.pop(cache_key, None)

    est_resp = repair_cost_estimator.estimate_cost(
        inspection_id=inspection.id,
        damage_summary=damage_summary,
        vehicle_context=v_ctx,
    )
    est_dict = est_resp.model_dump()

    # Save to VehicleRepairEstimate table
    stmt = select(VehicleRepairEstimate).where(VehicleRepairEstimate.inspection_id == inspection.id)
    db_est = (await db.execute(stmt)).scalar_one_or_none()
    rep_exp = est_resp.repair_scenario.expected
    repl_exp = est_resp.replacement_scenario.expected
    rec_scen = "repair" if est_resp.repair_scenario.is_recommended else "replacement"

    if db_est:
        db_est.component_id = cid
        db_est.damage_type = dmg_type
        db_est.extent_category = extent_cat.value
        db_est.recommended_scenario = rec_scen
        db_est.repair_expected = rep_exp
        db_est.replace_expected = repl_exp
        db_est.estimate_json = json.dumps(est_dict)
    else:
        db_est = VehicleRepairEstimate(
            inspection_id=inspection.id,
            component_id=cid,
            damage_type=dmg_type,
            extent_category=extent_cat.value,
            recommended_scenario=rec_scen,
            repair_expected=rep_exp,
            replace_expected=repl_exp,
            estimate_json=json.dumps(est_dict),
        )
        db.add(db_est)

    # Update InspectionReport report_json so downstream PDF & GET report delivers it
    if inspection.report and inspection.report.report_json:
        rep_dict = json.loads(inspection.report.report_json)
        rep_dict["estimate"] = est_dict
        inspection.report.report_json = json.dumps(rep_dict)
        # Re-render base PDF
        try:
            pdf_bytes = render_inspection_pdf(rep_dict)
            if inspection.report.pdf_storage_path:
                with open(inspection.report.pdf_storage_path, "wb") as pf:
                    pf.write(pdf_bytes)
        except Exception as e:
            pass

    await db.commit()
    return est_dict
