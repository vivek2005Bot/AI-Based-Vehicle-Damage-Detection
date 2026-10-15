"""Integration tests for FastAPI endpoints: Auth, Inspections, Uploads, Analysis, and Reports."""

import io
import pytest
from httpx import ASGITransport, AsyncClient
from PIL import Image

from backend.app.db.session import init_db
from backend.app.main import app


@pytest.fixture(autouse=True)
async def setup_test_db():
    await init_db()
    yield


@pytest.mark.asyncio
async def test_health_and_meta_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r_live = await client.get("/health/live")
        assert r_live.status_code == 200
        assert r_live.json()["status"] == "alive"

        r_ready = await client.get("/health/ready")
        assert r_ready.status_code == 200
        assert r_ready.json()["status"] == "ready"

        r_meta = await client.get("/api/v1/meta")
        assert r_meta.status_code == 200
        assert "capabilities" in r_meta.json()


@pytest.mark.asyncio
async def test_complete_inspection_workflow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Register User
        email = "inspector@example.com"
        password = "securePassword123!"
        r_reg = await client.post("/api/v1/auth/register", json={"email": email, "password": password})
        if r_reg.status_code != 201:
            assert r_reg.status_code == 409  # Already registered

        # 2. Login
        r_login = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
        assert r_login.status_code == 200
        token = r_login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Create Draft Inspection
        insp_payload = {
            "make": "BMW",
            "model": "330i",
            "year": 2021,
            "mileage": 35420.0,
            "mileage_unit": "km",
            "vin": "WBA33AY08MFS12345",
        }
        r_insp = await client.post("/api/v1/inspections", json=insp_payload, headers=headers)
        assert r_insp.status_code == 201
        insp_data = r_insp.json()
        insp_id = insp_data["id"]
        assert insp_data["vin_masked"] == "WBA******2345"

        # 4. Upload Vehicle Image
        img_buf = io.BytesIO()
        test_img = Image.new("RGB", (300, 300), (200, 50, 50))
        test_img.save(img_buf, format="JPEG")
        img_buf.seek(0)

        files = [("images", ("test_car.jpg", img_buf.getvalue(), "image/jpeg"))]
        r_up = await client.post(f"/api/v1/inspections/{insp_id}/images", files=files, headers=headers)
        assert r_up.status_code == 200
        assert r_up.json()["uploaded_count"] == 1

        # 5. Trigger Analysis Job
        r_analyze = await client.post(f"/api/v1/inspections/{insp_id}/analyze", headers=headers)
        assert r_analyze.status_code == 202
        job_data = r_analyze.json()
        assert job_data["status"] == "queued"
        assert "job_id" in job_data

        # 6. Check Status
        r_status = await client.get(f"/api/v1/inspections/{insp_id}/status", headers=headers)
        assert r_status.status_code == 200
        assert r_status.json()["inspection_id"] == insp_id
