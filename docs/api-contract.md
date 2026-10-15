# REST API Contract Specification

All endpoints are hosted at `/api/v1` with JSON request/response payloads (except multipart upload and PDF export endpoints).

## Authentication
JWT Bearer Authentication is required for all endpoints under `/api/v1/inspections`.
Header: `Authorization: Bearer <access_token>`

---

## 1. Authentication Endpoints

### `POST /api/v1/auth/register`
Creates a new inspector or claims adjuster account.

**Request Body:**
```json
{
  "email": "inspector@agency.com",
  "full_name": "Jane Doe",
  "password": "SecurePassword123!"
}
```

**Response (201 Created):**
```json
{
  "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "email": "inspector@agency.com",
  "full_name": "Jane Doe",
  "is_active": true,
  "created_at": "2026-10-14T12:00:00Z"
}
```

### `POST /api/v1/auth/login`
Authenticates user and returns JWT token.

**Request Body:**
```json
{
  "email": "inspector@agency.com",
  "password": "SecurePassword123!"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6...",
  "token_type": "bearer",
  "user": {
    "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "email": "inspector@agency.com",
    "full_name": "Jane Doe"
  }
}
```

---

## 2. Inspection Endpoints

### `POST /api/v1/inspections/`
Creates a new vehicle inspection session.

**Request Body:**
```json
{
  "vehicle_vin": "1HGCR2F83HA******",
  "vehicle_make": "Honda",
  "vehicle_model": "Accord",
  "vehicle_year": 2021,
  "notes": "Driver side frontal impact"
}
```

**Response (201 Created):**
```json
{
  "id": "c9bf9e57-1685-4c89-bafb-ff5af830be8a",
  "vehicle_vin": "1HGCR2F83HA******",
  "status": "pending",
  "created_at": "2026-10-14T12:05:00Z",
  "files_count": 0
}
```

### `POST /api/v1/inspections/{id}/images`
Uploads vehicle exterior photos (multipart/form-data).
Supports up to 20 images per inspection. Maximum size: 25MB per image.

**Response (201 Created):**
```json
{
  "inspection_id": "c9bf9e57-1685-4c89-bafb-ff5af830be8a",
  "uploaded_files": [
    {
      "id": "a1b2c3d4-...",
      "file_type": "image",
      "original_filename": "front_bumper.jpg",
      "file_size": 420769
    }
  ]
}
```

### `POST /api/v1/inspections/{id}/obd`
Uploads vehicle OBD-II diagnostic telemetry CSV file (multipart/form-data).

**Response (201 Created):**
```json
{
  "inspection_id": "c9bf9e57-1685-4c89-bafb-ff5af830be8a",
  "file_id": "e5f6g7h8-...",
  "file_type": "obd_csv",
  "original_filename": "trip_telemetry.csv",
  "file_size": 184500
}
```

### `POST /api/v1/inspections/{id}/analyze`
Dispatches background asynchronous multi-agent inspection pipeline.

**Response (202 Accepted):**
```json
{
  "job_id": "8a3b2c1d-...",
  "inspection_id": "c9bf9e57-1685-4c89-bafb-ff5af830be8a",
  "status": "queued",
  "message": "Analysis pipeline queued for background processing"
}
```

### `GET /api/v1/inspections/{id}/status`
Returns real-time progress of the analysis pipeline.

**Response (200 OK):**
```json
{
  "inspection_id": "c9bf9e57-1685-4c89-bafb-ff5af830be8a",
  "job_id": "8a3b2c1d-...",
  "status": "processing",
  "progress_pct": 75,
  "current_stage": "Stage 4: Polygon Segmentation & Area Analysis"
}
```

### `GET /api/v1/inspections/{id}/report`
Returns structured JSON inspection findings.

**Response (200 OK):**
```json
{
  "inspection_id": "c9bf9e57-1685-4c89-bafb-ff5af830be8a",
  "risk_class": "UNSAFE",
  "risk_summary": "Mandatory risk escalation: active Powertrain / Thermal DTC P0217 and front structural crush.",
  "damage_detected": true,
  "severity_score": 0.48,
  "severity_level": "High",
  "findings": [
    {
      "image_index": 0,
      "damage_detected": true,
      "detections": [
        {
          "damage_class": "bumper_smash",
          "confidence": 0.94,
          "bbox": [120, 240, 890, 760],
          "severity_score": 0.52,
          "severity_level": "High"
        }
      ]
    }
  ],
  "obd_findings": {
    "dtcs": [
      {
        "code": "P0217",
        "description": "Engine Coolant Overtemperature Condition",
        "severity": "CRITICAL"
      }
    ],
    "anomaly_count": 8,
    "quality_metrics": {
      "missing_value_pct": 0.12,
      "mapped_pids_count": 6
    }
  },
  "rag_citations": [
    {
      "source": "NHTSA FMVSS 214",
      "passage": "Vehicular impact compromising bumper structural reinforcements impairs frontal crash energy dissipation."
    }
  ],
  "disclaimer": "Decision-support advisory only. Physical verification required by a certified technician."
}
```

### `GET /api/v1/inspections/{id}/report.pdf`
Streams the generated ReportLab executive PDF report (`application/pdf`).
