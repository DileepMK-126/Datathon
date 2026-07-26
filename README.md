# Sentinel — Crime Intelligence Decision-Support MVP

Sentinel is a hackathon-ready, full-stack prototype for investigating emerging crime patterns. It is designed around one coherent officer workflow: detect an anomaly, inspect a hotspot, understand the area-risk drivers, and review a linked-case network.

> **Safety and data notice:** this project ships only deterministic synthetic records. It is a decision-support demonstration, not an enforcement system. Every model result is explicitly presented as a lead that requires human review.

---

## 🛠️ Current Tech Stack

Sentinel is built using a modern, performant, and privacy-conscious stack:

*   **Frontend**:
    *   **React 19 (latest)**: Modern hooks, reactive client-side state management.
    *   **Vite**: High-performance frontend build tool and developer server.
    *   **Vanilla CSS**: Custom design system featuring a premium dark mode, glassmorphism, and responsive dashboard grid layout.
    *   **Lucide React**: Clean, modern iconography.
*   **Backend**:
    *   **Python 3.12+**: Modern backend language execution.
    *   **FastAPI**: Asynchronous, high-performance API framework with automated OpenAPI interactive documentation.
    *   **Uvicorn**: Lightning-fast ASGI web server implementation.
*   **Data, Analytics & Machine Learning**:
    *   **SQLite**: Default light-weight database featuring automatic seeding on first startup.
    *   **PostGIS / PostgreSQL**: Supported for scalable spatial indexing and geometry calculations.
    *   **scikit-learn**:
        *   **DBSCAN** for geospatial crime hotspot clustering.
        *   **Isolation Forest** for time-series incident volume anomaly detection.
        *   **Random Forest Classifier** for area-risk scoring with local feature-attribution drivers.
    *   **NetworkX**: Shared-identifier graph networks for resolved entity case connections.
*   **Security & Governance**:
    *   **PyJWT & Cryptography (Fernet)**: Secure role-based tokens and encrypted ICJS staging records.
    *   **PBKDF2**: High-iteration secure password hashing.
    *   **Audit Logger**: Append-only local storage tracking every user action, roles, and endpoints.

---

## 📋 Implementation Plan Done

The following milestones have been successfully designed, coded, and integrated:

1.  **Synthetic Data Generator**: Automatic database generator modeling diverse, masked FIRs, court records, and CCTV files containing shared phone numbers, vehicle license plates, and names.
2.  **DBSCAN Geospatial Clustering**: API calculates density-based clusters over incident coordinates, linking similar spatial events.
3.  **Random Forest Risk Forecasting**: Predicts incident likelihood per zone using rolling incident histories, night-time concentrations, and patrol coverage indices.
4.  **Isolation Forest Anomaly Analyzer**: Flags dates where crime volume deviates significantly from historical rolling baselines.
5.  **NetworkX Entity Resolution**: Builds a case network graph that links multiple case files together if they share masked phone numbers, vehicle IDs, addresses, or individuals.
6.  **Unified Case Profile Aggregator**: Replaces fragmented data with single case profiles that link CCTV matches, police registers, and prison logs.
7.  **Evidence-Linked Patrol Recommendations**: Generates immediate actions for duty officers based on the calculated risk drivers and contextual events.
8.  **Interactive Single Page Dashboard**: A cohesive frontend showing maps, risk gauges, anomaly alerts, trend lines, and graphs.
9.  **Append-Only Security Audit Middleware**: Automatic logging of access paths, request IDs, user actors, and outcomes.

---

## 🚦 Current Status: Working vs. Pending

### ✅ Working Sections (MVP Features)
*   **Interactive Hotspots Map**: Clicking a hotspot updates the entire dashboard with that zone's live analytics, trend lines, and risk factors.
*   **Explainable AI Risk Panel**: Visual gauge mapping risk level (Critical/High/Elevated/Guarded), top three risk drivers (burglary share, patrol gap, night-time activity), and recommended actions.
*   **Anomaly Trend Graph**: Charts actual vs. expected volumes with Isolation Forest warnings when patterns cross normal limits.
*   **Alerts Queue**: Slide-over list prioritizing active anomalies, networks, and risk alerts.
*   **Connected Case Graph Modal**: Generates dynamic SVGs illustrating resolved links between cases and masking raw identifying identifiers (e.g. phone: `+91•••`, person: `A. Khan`).
*   **Unified Case Profile View**: Displays full source logs, confidence levels, resolved entities, and legal warnings.
*   **SQLite Fallback Mode**: Autodetects database files; if empty, builds tables and seeds them with demo data instantly.
*   **RBAC Authentication Middleware**: API endpoints validate authorization headers, supporting roles (`analyst`, `supervisor`, `admin`).

### ⏳ Pending / Configuration Required (Requires Staging/Production Setup)
*   **ICJS Gateway Live Sync (`/api/integrations/icjs/sync`)**: The connector is coded but intentionally locked. Synchronizing live data requires loading actual client credentials, token URLs, legal authority parameters, and a `DATA_ENCRYPTION_KEY` in the environment secrets.
*   **PostGIS Production Mode**: Local execution defaults to SQLite. Running PostGIS requires setting up a PostgreSQL service container and setting active environment variables.
*   **Authentication Required UI Mode**: The frontend is built to detect `/health` settings. For developer ease, it defaults to login bypass using a development analyst profile unless `AUTH_REQUIRED=true` and a valid `JWT_SECRET` are passed to the backend.
*   **Advanced GIS Map Engine**: The dashboard utilizes a custom-drawn vector schematic map of Northbridge City. Connecting to live Leaflet/Mapbox mapping API layers is left for full product integration.
*   **SIEM Audit Integration**: The audit database logs events locally, but forwarding logs to an external security monitoring system (Splunk/ELK) is pending.

---

## 📐 Architecture

```text
Synthetic FIR + CCTV/lab + court/prison records
                    |
      Entity resolution + unified case profile
                    |
PostGIS/SQLite + FastAPI analytics and review controls
                    |
DBSCAN + Isolation Forest + Random Forest + NetworkX
                    |
  React officer dashboard + review-only recommendations
```

---

## 🚀 Run locally

Prerequisites: Node.js 22+ and Python 3.12+.

In one terminal, install the backend dependencies and start the analytics API:

```powershell
python -m pip install -r backend/requirements.txt
npm run api
```

In a second terminal, install the web dependencies and start the dashboard:

```powershell
npm install
npm run dev
```

Open the address printed by Vite, normally `http://localhost:5173`. The Vite dev server proxies `/api` requests to FastAPI on port 8000.

---

## 🐳 Run with PostGIS, authentication, and Docker

Copy the secret template and replace every placeholder before running:

```powershell
Copy-Item .env.example .env
docker compose --env-file .env up --build
```

Open `http://localhost:8080`. The API remains available at `http://localhost:8000/docs`, including interactive OpenAPI documentation. Docker uses PostGIS and enables JWT authentication by default; sign in using the bootstrap administrator configured in `.env`.

---

## 🧪 Verify

```powershell
npm run build
Invoke-RestMethod http://127.0.0.1:8000/api/health
```

---

## 🧭 Demo path

1. Start on the **anomaly alert** for Sector 7.
2. Click a map hotspot to show its live DBSCAN count and the associated Random Forest risk score.
3. Point to the model driver bars to explain why the score changed.
4. Click **View intelligence**, then **Open case network**, then **Review unified case**.
5. Show the FIR, CCTV/lab, and court/prison source cards, masked resolved entities, and linked cases.
6. Explain that every connection and recommended action is an investigative lead subject to analyst validation.

---

## 🔌 API endpoints

| Endpoint | Purpose |
| --- | --- |
| `GET /api/health` | Service health and data mode |
| `GET /api/dashboard` | Dashboard metrics and ranked risks |
| `GET /api/hotspots` | DBSCAN hotspot clusters |
| `GET /api/risks` | Area risk forecasts and drivers |
| `GET /api/trends?zone_id=sector-7&days=28` | Anomaly trend series |
| `GET /api/alerts` | Prioritized analyst alerts |
| `GET /api/networks` | Masked, focused shared-entity network |
| `GET /api/repeat-offenders` | Review-only repeated-entity candidates |
| `GET /api/cases/{case_id}` | Unified, source-attributed case profile |
| `GET /api/recommendations?zone_id=sector-7` | Evidence-linked, review-only actions |
| `GET /api/investigations/brief` | Detect–locate–connect–act demo narrative |
| `POST /api/auth/login` | JWT sign-in when authentication is enabled |
| `GET /api/audit` | Administrator-only audit-event view |

---

## 🛡️ Data and production next steps

The included data generator models source-system integration without using personal or operational records. Production foundations are included: PostGIS support, JWT role-based access, audit events, encrypted ICJS staging, secret templates, and Kubernetes manifests. Read [GOVERNANCE.md](GOVERNANCE.md) and [DEPLOYMENT.md](DEPLOYMENT.md) before enabling real data. A live ICJS connection still requires an agency-approved API contract, data-sharing authorisation, and credentials; the connector will refuse to operate until those are configured.
