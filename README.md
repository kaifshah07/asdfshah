# Gridbricks — UK Wind Generation Forecast & Day-Ahead Procurement Dashboard

[![Python](https://img.shields.io/badge/python-3.11-blue.svg)]()
[![FastAPI](https://img.shields.io/badge/fastapi-v0.110-teal.svg)]()
[![React](https://img.shields.io/badge/react-19.3-cyan.svg)]()
[![TypeScript](https://img.shields.io/badge/typescript-5.9-blue.svg)]()
[![Docker](https://img.shields.io/badge/docker-compose%20ready-2496ed.svg)]()
[![Pytest](https://img.shields.io/badge/pytest-45%20passed-brightgreen.svg)]()

A production-grade decision-support platform for UK Day-Ahead electricity procurement. Reconstructs historical Elexon wind power forecasts published prior to the pre-auction gate-closure deadline, strictly eliminates lookahead bias, and quantifies forecast error risk across half-hour settlement periods against outturn actual generation for January 2026.

---

## Live Deployment

The application is deployed and publicly accessible:

- **Frontend Application (Vercel):** [https://uk-wind-forecast.vercel.app/](https://uk-wind-forecast.vercel.app/)
- **Backend REST API (Render):** [https://uk-wind-forecast-76jb.onrender.com](https://uk-wind-forecast-76jb.onrender.com)
  - **Interactive API Documentation (Swagger UI):** [https://uk-wind-forecast-76jb.onrender.com/docs](https://uk-wind-forecast-76jb.onrender.com/docs)
  - **Healthcheck Endpoint:** [https://uk-wind-forecast-76jb.onrender.com/health](https://uk-wind-forecast-76jb.onrender.com/health)

---

## 1. Problem Context & Commercial Value

In the UK electricity market, day-ahead power auctions require energy utilities and power trading desks to commit their generation bids and procurement volumes before knowing the true wind output on delivery day $D$. 

- **Over-Forecasting (Positive Bias):** The utility procures too little backup power. If wind under-delivers, the utility is "short" in the Balancing Mechanism and must pay penal system buy prices (cashout penalty).
- **Under-Forecasting (Negative Bias):** The utility over-procures thermal or interconnector power. If wind over-delivers, the utility is "long" and must sell spill power at depressed or negative system sell prices.

### Intended Users
- **Power Trading Desks:** Optimizing volume bids and avoiding imbalance cashout penalties.
- **Risk Managers:** Evaluating P10/P50/P90 volume spread and tail-risk exposure across delivery days.
- **Settlement & Procurement Analysts:** Investigating structural peak vs. off-peak forecast errors and diurnal bias patterns.

### Core Capabilities
1. **Decision Gate-Closure Selection:** Reconstructs the exact latest eligible forecast available at decision time ($D-1$ 12:00 UTC default), completely eliminating lookahead bias.
2. **Dual-Grain Alignment:** Preserves official Elexon resolution (30-min FUELHH actuals mapped directly to 60-min WINDFOR forecasts) without inventing artificial interpolated generation.
3. **Institutional Risk Analytics:** Real-time calculation of MAE, RMSE, Mean Bias, WAPE, P10/P50/P90 quantiles, 48-period diurnal error profiles, and Peak vs. Off-Peak partitions.

---

## 2. System Architecture & Tech Stack

```
                       ┌────────────────────────────────────────┐
                       │          Host Browser (Port 3000)      │
                       └───────────────────┬────────────────────┘
                                           │
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ Docker Network (gridbricks-net)                                                       │
│                                                                                        │
│   ┌───────────────────────────────────┐        ┌───────────────────────────────────┐   │
│   │   Frontend Container (Nginx)      │        │   Backend Container (FastAPI)     │   │
│   │   Port: 80 (Mapped to 3000)       │        │   Port: 8000 (Mapped to 8000)     │   │
│   │                                   │        │                                   │   │
│   │   - React 19 + TypeScript SPA    │        │   - FastAPI async REST API        │   │
│   │   - Recharts Visualizations      │        │   - Pydantic v2 validation        │   │
│   │   - Tailwind CSS v4 styling      │        │   - Vectorized pandas / pyarrow   │   │
│   │   - Reverse proxy for /api/ ─────┼───────>│   - In-memory Parquet cache       │   │
│   │   - Reverse proxy for /health ───┼───────>│   - Temporal Matching Engine      │   │
│   │   - SPA fallback (try_files)      │        │   - Statistical Analytics Engine  │   │
│   └───────────────────────────────────┘        └─────────────────┬─────────────────┘   │
│                                                                  │                     │
│                                                                  ▼                     │
│                                                ┌───────────────────────────────────┐   │
│                                                │ Normalized Data Directory         │   │
│                                                │ - actuals_jan2026.parquet         │   │
│                                                │ - forecasts_jan2026.parquet       │   │
│                                                │ (1,488 actuals, 19,856 forecasts) │   │
│                                                └───────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### Technology Stack
- **Frontend:** React 19, TypeScript 5.9, Vite 8, Tailwind CSS v4, Recharts, Lucide React.
- **Backend:** Python 3.11, FastAPI, Pydantic v2, Pandas, PyArrow, Uvicorn, HTTPX.
- **Containerization:** Docker multi-stage builds, Docker Compose, Nginx Alpine reverse proxy.
- **Cloud Hosting:** Vercel (Frontend static SPA), Render (Backend Python 3.11 web service).

For in-depth architectural and state-management designs, see [**`docs/architecture.md`**](docs/architecture.md).

---

## 3. Directory & File Structure

```
.
├── backend/                       # Python / FastAPI backend application
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py          # REST endpoints (/health, /availability, /day-ahead, /analytics)
│   │   ├── config.py              # Application settings, path resolution & CORS origins
│   │   ├── models/
│   │   │   └── schemas.py         # Pydantic v2 request/response validation schemas
│   │   └── services/
│   │       ├── analytics_service.py # Vectorized statistical metrics & diurnal profiles
│   │       ├── data_loader.py     # Parquet/JSON multi-tier data ingestion & memory cache
│   │       ├── ingestion_service.py # Elexon BMRS API client with exponential backoff
│   │       └── matching_service.py  # Temporal cutoff filtering & hourly-to-SP mapping
│   ├── tests/                     # Automated pytest suite (45 tests)
│   │   ├── test_api.py            # API routing, status codes, CORS validation
│   │   ├── test_e2e_integration.py # Multi-step E2E trading workflows
│   │   ├── test_ingestion.py      # Client retries, deduplication, UTC timezone parsing
│   │   └── test_matching_analytics.py # Mathematical fixtures & boundary edge cases
│   ├── Dockerfile                 # Multi-stage Python 3.11-slim container definition
│   ├── main.py                    # FastAPI application initialization & middleware
│   └── requirements.txt           # Pinned production backend dependencies
├── frontend/                      # React 19 + TypeScript + Vite frontend application
│   ├── src/
│   │   ├── components/            # UI components (KPI cards, charts, filters, modals)
│   │   ├── services/
│   │   │   └── api.ts             # Multi-environment API client with URL normalization
│   │   ├── types/
│   │   │   └── api.ts             # TypeScript domain interfaces matching backend models
│   │   ├── App.tsx                # Main trading dashboard shell & async state management
│   │   └── main.tsx               # Application bootstrap
│   ├── Dockerfile                 # Multi-stage Node 22 builder + Nginx Alpine runner
│   ├── nginx.conf                 # Nginx reverse proxy configuration for Docker
│   ├── package.json               # Frontend dependencies & scripts
│   ├── test-api-url.js            # Automated unit tests for api.ts URL resolution
│   ├── vercel.json                # Vercel deployment routing & headers configuration
│   └── vite.config.ts             # Vite configuration with Rollup code-splitting chunks
├── data/                          # Historical Elexon January 2026 datasets
│   ├── normalized/                # Primary Parquet cache (actuals & forecasts)
│   └── raw/                       # Raw source data from initial ingestion
├── docs/                          # Comprehensive technical documentation & guides
│   ├── ai-disclosure.md           # Transparent AI tool usage disclosure (ChatGPT)
│   ├── api.md                     # Complete API endpoint reference and JSON schemas
│   ├── architecture.md            # System architecture, data flow & component contracts
│   ├── data-quality.md            # Elexon data profiling, validation & audit findings
│   ├── deployment.md              # Local, Docker, and Cloud deployment instructions
│   └── submission-guide.md        # 10-minute video presentation script & review checklist
├── compose.yaml                   # Docker Compose orchestration file
├── render.yaml                    # Infrastructure-as-Code blueprint for Render web service
└── README.md                      # Primary project documentation
```

---

## 4. Data Sources & Data-Processing Methodology

The platform analyzes official Elexon Balancing Mechanism Reporting Service (BMRS) datasets for the complete month of **January 2026**:

1. **Actual Outturn Generation (`FUELHH`):**
   - Filtered for `fuelType == "WIND"`.
   - Reported across 48 half-hour Settlement Periods ($SP \in [1, 48]$) per delivery day.
   - Total records: **1,488 half-hour observations** (31 days $\times$ 48 SPs).
   - Validation: **0 missing periods, 0 null values, 0 negative generation values**.

2. **Forecast Wind Generation (`WINDFOR`):**
   - Forecast expected wind power output published on a rolling basis.
   - Total records: **19,856 forecast records** across **272 distinct publication runs**.
   - Preserved with complete publication timestamps (`publishTime`) and target intervals (`startTime`).

For detailed data profiling and audit tables, see [**`docs/data-quality.md`**](docs/data-quality.md).

---

## 5. Forecast Selection & Cutoff Methodology

### Implemented Analysis Rule
In UK day-ahead power trading practice, utilities submit auction bids ahead of delivery day $D$. For this project, an implemented decision cutoff rule of **$D-1$ at 12:00 UTC** (configurable) is enforced to ensure that only forecasts published prior to gate closure are eligible, completely eliminating lookahead bias. *(Note: this is an implemented analysis rule for decision cutoff simulation, not a statutory BSC rule).*

For any delivery date $D$:
$$\text{Cutoff Datetime} = (D - 1)\text{ at } 12:00:00\text{ UTC}$$

### Selection & Deterministic Tie-Breaking
1. All forecast publication runs are filtered:
   $$\text{Eligible Runs} = \{ r \mid \text{publish\_time}(r) \le \text{Cutoff Datetime} \}$$
2. For each delivery hour $H \in [0, 23]$ on day $D$, the system selects the latest eligible forecast run.
3. If two records share the exact same publish timestamp, deterministic tie-breaking selects the record with the latest update.

### Dual-Grain Alignment (Hourly to Half-Hourly)
- Elexon `WINDFOR` forecasts report average expected power (MW) over 60-minute target intervals ($H \in [0, 23]$).
- Elexon `FUELHH` actuals report outturn generation in 30-minute settlement periods ($SP \in [1, 48]$).
- Because power (MW) represents an instantaneous rate of energy flow, an expected average rate of $G$ MW over hour $H$ applies directly to both Settlement Period $2H+1$ and $2H+2$ without inventing artificial linear interpolations.

---

## 6. Statistical & Mathematical Methodology

All metrics are calculated according to institutional energy trading standards:

| Metric | Formula | Interpretation |
| :--- | :--- | :--- |
| **Signed Forecast Error ($e_i$)** | $e_i = F_i - A_i$ | Positive indicates over-forecast (utility short); negative indicates under-forecast (utility long). |
| **Mean Absolute Error (MAE)** | $\text{MAE} = \frac{1}{N} \sum_{i=1}^N \|F_i - A_i\|$ | Expected volume deviation magnitude in MW. |
| **Root Mean Squared Error (RMSE)** | $\text{RMSE} = \sqrt{\frac{1}{N} \sum_{i=1}^N (F_i - A_i)^2}$ | Heavily penalizes large volumetric forecast misses. |
| **Mean Bias Error (MBE)** | $\text{Bias} = \frac{1}{N} \sum_{i=1}^N (F_i - A_i)$ | Systematic tendency to over- or under-predict generation. |
| **Weighted Absolute Percentage Error (WAPE)** | $\text{WAPE} = \frac{\sum_{i=1}^N \|F_i - A_i\|}{\sum_{i=1}^N A_i} \times 100\%$ | Normalized portfolio error percentage (protected against zero-division). |
| **P10 / P50 / P90 Quantiles** | 10th, 50th, 90th percentiles of $e_i$ | Probabilistic risk spread for volumetric hedging. |
| **Diurnal Profile** | Aggregated by $SP \in [1, 48]$ across days | Reveals recurring intra-day morning ramp or evening bias patterns. |
| **Peak vs. Off-Peak Partitions** | Peak: SP 15–38 (07:00–19:00 UTC)<br>Off-Peak: SP 1–14 & SP 39–48 | Quantifies accuracy divergence between high-value trading hours and overnight baseload. |

---

## 7. Local Setup Prerequisites

Ensure you have the following installed on your host system:
- **For Docker Deployment (Option A):** Docker Desktop (with WSL 2 on Windows) and Docker Compose.
- **For Native Local Development (Option B):**
  - Python 3.11+
  - Node.js 20+ or 22+ and npm

---

## 8. Startup Instructions

### Option A: Run with Docker Compose (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/kaifshah07/uk-wind-forecast.git
cd uk-wind-forecast

# 2. Build and start both containers in detached mode
docker compose up -d

# 3. Verify container status and health
docker compose ps

# 4. Open in browser:
# Frontend Trading UI: http://localhost:3000
# Backend API Docs:    http://localhost:8000/docs
# Service Healthcheck: http://localhost:8000/health (or http://localhost:3000/health)
```

To stop containers cleanly:
```bash
docker compose down
```

---

### Option B: Run Locally (Native Development)

#### 1. Start the Backend API
In your first terminal:
```bash
# Navigate to project root
cd uk-wind-forecast

# Create and activate Python virtual environment
python -m venv .venv

# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# On macOS/Linux:
source .venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt

# Start FastAPI development server with hot-reload
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
The backend API is now running at `http://127.0.0.1:8000`. Test via `http://127.0.0.1:8000/health`.

#### 2. Start the Frontend Dashboard
In a second terminal:
```bash
# Navigate to frontend directory
cd uk-wind-forecast/frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```
Open `http://localhost:5173` in your browser. The Vite dev server automatically proxies `/api` and `/health` requests to `http://127.0.0.1:8000`.

---

## 9. Environment Variables & Safe Configuration

The application is pre-configured to run out-of-the-box in local development and Docker without requiring manual `.env` file creation. All sensitive variables and keys are strictly excluded.

| Variable | Scope | Default Value | Description / Purpose |
| :--- | :--- | :--- | :--- |
| `VITE_API_BASE_URL` | Frontend (Build-time) | `""` (Empty string) | In local dev and Docker, defaults to empty so requests use relative `/api/*` and `/health`. On Vercel, set to `https://uk-wind-forecast-76jb.onrender.com`. |
| `CORS_ALLOWED_ORIGINS` | Backend (Runtime) | `http://localhost:5173,http://localhost:3000...` | Comma-separated list of allowed origins or `*`. Set to `*` on Render for production. |
| `PORT` | Backend (Runtime) | `8000` | HTTP listening port for Uvicorn (Render dynamically injects `$PORT`). |
| `PYTHONPATH` | Backend (Runtime) | `.` | Ensures Python cleanly resolves the `backend` module hierarchy. |

> **Security Note:** No third-party API keys, passwords, or database credentials are required or stored in this repository. Historical Elexon data is pre-ingested and bundled directly in normalized Parquet format (`data/normalized/`).

---

## 10. API Reference

The backend provides four high-performance REST endpoints:

| Method | Endpoint | Query Parameters | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | None | Container and service health check (returns status, version, UTC timestamp) |
| `GET` | `/api/wind/availability` | None | Summary of dataset date range (`2026-01-01` to `2026-01-31`), record counts, and run counts |
| `GET` | `/api/wind/day-ahead` | `delivery_date` (YYYY-MM-DD), `cutoff_time` (HH:MM:SS) | 48 settlement periods forecast vs. actual for day $D$ with period-level audit and daily summary KPIs |
| `GET` | `/api/wind/analytics` | `start_date`, `end_date`, `cutoff_time` | Multi-day aggregated metrics, Peak vs. Off-Peak partitions, 48-period diurnal profile, and daily breakdown |

For full JSON schemas and payload examples, see [**`docs/api.md`**](docs/api.md) or explore the interactive Swagger UI at `/docs`.

---

## 11. Testing & Quality Assurance

Automated test suites verify every layer of the system:

```bash
# 1. Run complete backend pytest suite (45 tests passed)
.\.venv\Scripts\pytest.exe -v

# 2. Run frontend API client unit tests (12 tests passed)
cd frontend
npm test

# 3. Run frontend static analysis & linting (0 warnings, 0 errors)
npm run lint

# 4. Run frontend production build & TypeScript validation
npm run build
```

### Verified Test Coverage
- **16 Ingestion Tests:** Client retries (HTTP 429 exponential backoff, 500 exhaustion), schema validation, deduplication, UTC timezone parsing.
- **13 Analytics & Matching Tests:** Hand-calculated mathematical fixtures, boundary cutoff eligibility down to the exact second, WAPE zero-division safety, and peak/off-peak partition conservation.
- **10 API & CORS Tests:** Endpoint contracts, input validation, invalid dates, and cross-origin security headers.
- **6 End-to-End Integration Tests:** Full simulated trading desk workflows from initial load to cutoff sensitivity.
- **12 Frontend URL Tests:** Path normalization, relative dev proxy handling, and absolute cloud URL construction.

---

## 12. Cloud Deployment & Environment Compatibility

The codebase is engineered to function seamlessly across three target environments without code changes:

| Environment | Frontend URL Resolution | Backend Routing | CORS Policy |
| :--- | :--- | :--- | :--- |
| **1. Local Dev** | Relative `/api/*` and `/health` | Vite dev proxy (`localhost:5173` -> `127.0.0.1:8000`) | Disabled / Same-origin via proxy |
| **2. Local Docker** | Relative `/api/*` and `/health` | Nginx reverse proxy (`localhost:3000` -> `backend:8000`) | Same-origin via Nginx proxy |
| **3. Cloud Production** | Absolute (`VITE_API_BASE_URL` -> Render origin) | Direct browser `fetch()` to Render web service | Managed via `CORS_ALLOWED_ORIGINS` |

For deployment guides and configuration files, see [**`docs/deployment.md`**](docs/deployment.md).

---

## 13. Project Verification Status & Limitations

### Verified Status
- **Local Native Execution:** Fully verified (Python 3.11 + Vite 8).
- **Automated Test Suites:** 45 of 45 backend tests passed; 12 of 12 frontend URL tests passed.
- **Docker Compose Containers:** Built and actively running (`gridbricks-backend:healthy` on port 8000, `gridbricks-frontend` on port 3000).
- **Public Cloud Deployment:** Live and verified on Vercel and Render.
- **Secret & License Hygiene:** Zero credentials committed; unverified licenses removed.

### Intended Scope & Limitations
This platform is an institutional **forecast error analysis and procurement decision-support tool**. It provides quantitative uncertainty bounds, diurnal risk profiles, and historical bias indicators to inform day-ahead volume purchasing. It is **not** a full autonomous procurement optimizer, as full procurement optimization requires real-time consumer load profiles, half-hourly wholesale power prices, interconnector flows, and generator ramp-rate constraints.

---

## 14. AI Assistance Disclosure

In compliance with challenge transparency requirements, all AI tools and workflows used during development are documented with full honesty in [**`docs/ai-disclosure.md`**](docs/ai-disclosure.md).
- **Tool Used:** ChatGPT (OpenAI).
- **Role:** Conceptual understanding, technical explanations, troubleshooting build errors, exploring implementation approaches, and architectural guidance.
- **Model Version:** The exact ChatGPT model/version used during development was not consistently recorded.
