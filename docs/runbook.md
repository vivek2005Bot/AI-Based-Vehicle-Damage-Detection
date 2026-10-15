# Operations & Deployment Runbook

## 1. Quick Start (Local Development)

### Prerequisites
- Python 3.11+ (Python 3.14 verified)
- Flutter 3.27+ with iOS toolchain / Xcode
- Git, Docker & Docker Compose (optional for containerized deployment)

### Local Environment Setup
```bash
# 1. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install Python project dependencies
pip install --upgrade pip setuptools wheel
pip install .

# 3. Initialize SQLite database & inspect dataset
python ml/data/inspect_dataset.py
python ml/data/build_splits.py

# 4. Run automated test suite
PYTHONPATH=. pytest -v tests/

# 5. Start FastAPI local server
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## 2. Flutter iOS Client Setup

```bash
cd apps/ios

# Install Flutter dependencies
flutter pub get

# Run static analysis & widget tests
flutter analyze
flutter test

# Launch on iOS Simulator or connected device
flutter run
```

---

## 3. Production Docker Deployment

Deploy the full container stack (PostgreSQL + pgvector, Redis, FastAPI Backend, Background Worker, and Nginx reverse proxy):

```bash
# Copy and configure environment variables
cp .env.example .env

# Build and start all services
docker compose up -d --build

# Verify container health
docker compose ps
curl http://localhost/health/live
curl http://localhost/health/ready
```

---

## 4. Diagnostics & Troubleshooting

| Symptom | Root Cause | Remediation |
|---|---|---|
| `502 Bad Gateway` from Nginx | API service starting up or failing healthcheck | Inspect logs with `docker compose logs -f api` |
| `Upload file exceeds 50M` | Batch images/CSVs exceed HTTP payload size | Compress photos or increase `client_max_body_size` in `infra/nginx/nginx.conf` |
| `JWT Token Invalid / Expired` | Expired session | Re-authenticate via `/api/v1/auth/login` |
| Flutter network error | iOS simulator cannot reach backend | Configure backend URL in Settings screen to `http://127.0.0.1:8000` or host LAN IP |

---

## 5. Maintenance Procedures

- **EDA Chart Regeneration:** `PYTHONPATH=. python ml/data/generate_eda.py`
- **Database Backup:** `pg_dump -U vehicle_admin vehicle_damage_db > backup.sql`
- **Storage Cleanup:** Prune temporary report files older than 30 days in `storage/reports/`.
