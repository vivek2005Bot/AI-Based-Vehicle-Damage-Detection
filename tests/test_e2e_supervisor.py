"""End-to-end integration test for the multi-agent inspection supervisor and PDF report generator."""

from pathlib import Path
from PIL import Image

from agents.state import InspectionGraphState, VehicleMetadata
from agents.supervisor import InspectionSupervisor
from reports.pdf_renderer import render_inspection_pdf


def test_supervisor_e2e_workflow_and_pdf_generation(tmp_path):
    supervisor = InspectionSupervisor(filter_threshold=0.85, top_k_rag=2)

    img_path = "private_uploads/insp_0079e9eb-040c-429d-b8d7-ae8fcf7ac724/9674b2077a7243228116b24977e6cf5d.jpg"
    images = [Image.open(img_path)]

    obd_path = "obdiidata/2018-03-01_Seat_Leon_RT_S_Normal.csv"
    obd_bytes = Path(obd_path).read_bytes()

    state = InspectionGraphState(
        inspection_id="insp_test_e2e_supervisor",
        job_id="job_test_e2e_supervisor",
        user_id="user_test",
        image_paths=[img_path],
        image_filenames=["damaged_mirror.jpg"],
        image_file_ids=["file_1"],
        obd_csv_path=obd_path,
        obd_filename="telemetry.csv",
        vehicle_info=VehicleMetadata(
            make="BMW",
            model="330i",
            year=2021,
            vin_masked="WBA33AY08MFS*****"
        ),
    )

    final_state = supervisor.run_workflow(state, image_objects=images, csv_bytes=obd_bytes)

    assert final_state.status in ("completed", "completed_with_warnings")
    assert "vision_analysis" in final_state.completed_stages
    assert "obd_analysis" in final_state.completed_stages
    assert "knowledge_retrieval" in final_state.completed_stages
    assert "risk_assessment" in final_state.completed_stages
    assert "report_generation" in final_state.completed_stages

    # Vision check
    assert final_state.vision_result is not None
    assert final_state.vision_result.overall_damage_detected is True
    assert len(final_state.vision_result.images[0].detections) > 0

    # OBD check
    assert final_state.obd_result is not None
    assert final_state.obd_result.data_quality.total_rows > 0

    # RAG check
    assert final_state.rag_result is not None
    assert len(final_state.rag_result.citations) > 0

    # Risk check
    assert final_state.risk_result is not None
    assert final_state.risk_result.risk_class.value in ("safe", "caution", "unsafe")

    # Report & PDF rendering check
    assert final_state.report_payload is not None
    pdf_out = tmp_path / "inspection_report.pdf"
    pdf_bytes = render_inspection_pdf(final_state.report_payload, output_target=pdf_out)
    assert len(pdf_bytes) > 1000
    assert pdf_out.is_file()
