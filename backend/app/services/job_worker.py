"""Asynchronous Inspection Job Worker.

Complies with ANTIGRAVITY_PROJECT_SPEC.md Section 6.2 & Section 11.
Executes the LangGraph supervisor workflow, compiles structured reports,
renders PDF artifacts, and updates database records asynchronously.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from agents.state import InspectionGraphState, VehicleMetadata
from agents.supervisor import InspectionSupervisor
from backend.app.core.config import settings
from backend.app.db.session import AsyncSessionLocal
from backend.app.models_db.models import AnalysisJob, Inspection, InspectionFile, InspectionReport, VehicleRepairEstimate
from backend.app.services.file_storage import file_storage
from reports.pdf_renderer import render_inspection_pdf

logger = logging.getLogger(__name__)


async def execute_inspection_job(job_id: str, inspection_id: str) -> None:
    """Run full agentic inspection workflow in the background."""
    async with AsyncSessionLocal() as db:
        stmt = (
            select(Inspection)
            .where(Inspection.id == inspection_id)
            .options(selectinload(Inspection.files), selectinload(Inspection.jobs))
        )
        res = await db.execute(stmt)
        inspection = res.scalar_one_or_none()

        job_stmt = select(AnalysisJob).where(AnalysisJob.id == job_id)
        job_res = await db.execute(job_stmt)
        job = job_res.scalar_one_or_none()

        if not inspection or not job:
            logger.error(f"Job {job_id} or Inspection {inspection_id} not found.")
            return

        job.status = "processing"
        job.current_stage = "loading_inputs"
        inspection.status = "processing"
        await db.commit()

        try:
            # 1. Gather image files & optional OBD file
            image_files = [f for f in inspection.files if f.role == "vehicle_image"]
            obd_files = [f for f in inspection.files if f.role == "obd_csv"]

            if not image_files:
                raise ValueError("Cannot analyze inspection without at least one vehicle image.")

            image_bytes_list = []
            image_names = []
            image_file_ids = []
            for img_f in image_files:
                b = file_storage.read_bytes(img_f.storage_path)
                image_bytes_list.append(b)
                image_names.append(img_f.original_filename)
                image_file_ids.append(img_f.id)

            obd_bytes: Optional[bytes] = None
            obd_name: Optional[str] = None
            if obd_files:
                obd_bytes = file_storage.read_bytes(obd_files[0].storage_path)
                obd_name = obd_files[0].original_filename

            # 2. Build Typed State
            state = InspectionGraphState(
                inspection_id=inspection.id,
                job_id=job.id,
                user_id=inspection.user_id,
                image_filenames=image_names,
                image_file_ids=image_file_ids,
                obd_filename=obd_name,
                vehicle_info=VehicleMetadata(
                    make=inspection.make,
                    model=inspection.model,
                    year=inspection.year,
                    mileage=inspection.mileage,
                    mileage_unit=inspection.mileage_unit,
                    vin_masked=inspection.vin_masked,
                ),
            )

            # 3. Execute LangGraph Supervisor
            supervisor = InspectionSupervisor(
                filter_threshold=settings.FILTER_THRESHOLD,
                top_k_rag=settings.RAG_TOP_K,
            )

            job.current_stage = "multi_agent_workflow"
            await db.commit()

            # Execute workflow
            processed_state = supervisor.run_workflow(
                state=state,
                image_objects=image_bytes_list,
                csv_bytes=obd_bytes,
            )

            # 4. Render PDF Report
            report_data = processed_state.report_payload or {}
            pdf_rel_path = None
            try:
                pdf_bytes = render_inspection_pdf(report_data)
                pdf_filename = f"report_{inspection.id}.pdf"
                pdf_full_path = Path(settings.REPORTS_DIR) / pdf_filename
                with open(pdf_full_path, "wb") as pf:
                    pf.write(pdf_bytes)
                pdf_rel_path = str(pdf_full_path)
            except Exception as pe:
                logger.warning(f"PDF generation failed: {pe}")
                processed_state.warnings.append(f"PDF generation failed: {pe}")

            # 5. Persist Report & Update Job State
            risk_class = (
                processed_state.risk_result.risk_class.value
                if processed_state.risk_result
                else "unavailable"
            )

            # Check if report already exists for idempotency
            existing_rep_stmt = select(InspectionReport).where(InspectionReport.inspection_id == inspection.id)
            existing_rep = (await db.execute(existing_rep_stmt)).scalar_one_or_none()

            if existing_rep:
                existing_rep.report_json = json.dumps(report_data)
                existing_rep.risk_class = risk_class
                existing_rep.pdf_storage_path = pdf_rel_path
            else:
                db_report = InspectionReport(
                    inspection_id=inspection.id,
                    risk_class=risk_class,
                    report_json=json.dumps(report_data),
                    pdf_storage_path=pdf_rel_path,
                )
                db.add(db_report)

            # Persist Repair Cost Estimate if generated
            est_dict = report_data.get("estimate")
            if est_dict:
                existing_est_stmt = select(VehicleRepairEstimate).where(VehicleRepairEstimate.inspection_id == inspection.id)
                existing_est = (await db.execute(existing_est_stmt)).scalar_one_or_none()
                dmg_info = est_dict.get("damage") or {}
                rep_scen = est_dict.get("repair_scenario") or {}
                rep_exp = rep_scen.get("expected", 0.0)
                repl_scen = est_dict.get("replacement_scenario") or {}
                repl_exp = repl_scen.get("expected", 0.0)
                rec_scen = "repair" if rep_scen.get("is_recommended") else "replacement"

                if existing_est:
                    existing_est.component_id = dmg_info.get("component_id", "unknown")
                    existing_est.damage_type = dmg_info.get("damage_type", "unknown")
                    existing_est.extent_category = dmg_info.get("extent_category", "unknown")
                    existing_est.recommended_scenario = rec_scen
                    existing_est.repair_expected = rep_exp
                    existing_est.replace_expected = repl_exp
                    existing_est.currency = est_dict.get("vehicle", {}).get("currency", "INR")
                    existing_est.estimate_json = json.dumps(est_dict)
                else:
                    db_est = VehicleRepairEstimate(
                        inspection_id=inspection.id,
                        component_id=dmg_info.get("component_id", "unknown"),
                        damage_type=dmg_info.get("damage_type", "unknown"),
                        extent_category=dmg_info.get("extent_category", "unknown"),
                        recommended_scenario=rec_scen,
                        repair_expected=rep_exp,
                        replace_expected=repl_exp,
                        currency=est_dict.get("vehicle", {}).get("currency", "INR"),
                        estimate_json=json.dumps(est_dict),
                    )
                    db.add(db_est)

            inspection.status = processed_state.status
            job.status = "completed"
            job.current_stage = "completed"
            job.finished_at = datetime.now(timezone.utc)
            await db.commit()
            logger.info(f"Inspection {inspection.id} successfully completed.")

        except Exception as e:
            logger.exception(f"Inspection analysis failed: {e}")
            inspection.status = "failed"
            job.status = "failed"
            job.current_stage = "failed"
            job.error_message = str(e)
            job.finished_at = datetime.now(timezone.utc)
            await db.commit()
