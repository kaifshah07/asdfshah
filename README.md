# Gridbricks — UK Wind Generation Forecast & Day-Ahead Procurement Dashboard

[![Python](https://img.shields.io/badge/python-3.11-blue.svg)]()
[![FastAPI](https://img.shields.io/badge/fastapi-v0.110-teal.svg)]()
[![React](https://img.shields.io/badge/react-19.3-cyan.svg)]()
[![TypeScript](https://img.shields.io/badge/typescript-5.9-blue.svg)]()
[![Docker](https://img.shields.io/badge/docker-compose%20ready-2496ed.svg)]()
[![Pytest](https://img.shields.io/badge/pytest-45%20passed-brightgreen.svg)]()

A production-grade decision-support platform for UK Day-Ahead electricity procurement. Reconstructs historical Elexon wind power forecasts published prior to the pre-auction gate-closure deadline, strictly eliminates lookahead bias, and quantifies forecast error risk across half-hour settlement periods against outturn actual generation for January 2026.

---

## 1. Problem Context & Commercial Value

In the UK electricity market (governed by the BSC / Elexon), day-ahead power auctions close daily at **12:00 UTC on day $D-1$**. Energy utilities and power trading desks must commit their generation bids and procurement volumes before knowing the true wind output on delivery day $D$.

- **Over-Forecasting (Positive Bias):** The utility procures too little backup power. If wind under-delivers, the utility is "short" in the Balancing Mechanism and must pay penal system buy prices (cashout penalty).
- **Under-Forecasting (Negative Bias):** The utility over-procures thermal/interconnector power. If wind over-delivers, the utility is "long" and sells spill power at depressed or negative system sell prices.

**This platform provides:**
1. **Gate-Closure Temporal Selection:** Reconstructs the exact forecast available to traders at decision time ($D-1$ 12:00 UTC default), completely eliminating lookahead bias.
2. **Dual-Grain Alignment:** Preserves the official Elexon schema (30-min FUELHH actuals mapped to 60-min WINDFOR forecasts) without inventing artificial interpolated generation.
3. **Institutional Risk Metrics:** Instant calculation of MAE, RMSE, Mean Bias, WAPE, P10/P50/P90 risk bands, 48-period diurnal error profiles, and Peak vs. Off-Peak partitions.

---

## 2. System Architecture

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
│   │   - Recharts Visualizations      │        │   - Pydantic v2 schemas           │   │
│   │   - Tailwind CSS v4 styling      │        │   - Vectorized pandas/pyarrow     │   │
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

For complete technical specifications and state-management designs, see [**`docs/architecture.md`**](docs/architecture.md).

---

## 3. Quick Start

### Option A: Run with Docker Compose (Recommended)

**Prerequisites:** Docker Desktop running with WSL 2.

```bash
# 1. Clone the repository
git clone <repo-url>
cd <repo-folder>

# 2. Build and start both services
docker compose up -d

# 3. Verify services are healthy
docker compose ps

# 4. Open the application in your browser:
# Frontend Trading UI: http://localhost:3000
# Backend API Docs:    http://localhost:8000/docs
# Healthcheck:         http://localhost:8000/health
```

To stop the application:
```bash
docker compose down
```

---

### Option B: Run Locally (Native Development)

**Prerequisites:** Python 3.11+, Node.js 22+, npm.

#### 1. Start the Backend API
```bash
# Create and activate Python virtual environment
python -m venv .venv
# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Start FastAPI development server
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
The API is now live at `http://127.0.0.1:8000/docs`.

#### 2. Start the Frontend Dashboard
In a separate terminal:
```bash
cd frontend

# Install Node dependencies
npm install

# Start Vite development server
npm run dev
```
Open `http://localhost:5173` in your browser. The Vite dev server automatically proxies `/api` and `/health` requests to `http://127.0.0.1:8000`.

---

## 4. Statistical & Mathematical Methodology

All metrics are calculated according to strict energy trading standards:

| Metric | Formula | Interpretation |
| :--- | :--- | :--- |
| **Signed Forecast Error ($e_i$)** | $e_i = F_i - A_i$ | Positive means over-forecast; negative means under-forecast. |
| **Mean Absolute Error (MAE)** | $\text{MAE} = \frac{1}{N} \sum_{i=1}^N \|F_i - A_i\|$ | Magnitude of expected volume deviation in MW. |
| **Root Mean Squared Error (RMSE)** | $\text{RMSE} = \sqrt{\frac{1}{N} \sum_{i=1}^N (F_i - A_i)^2}$ | Heavily penalizes large forecast outliers. |
| **Mean Bias Error (MBE)** | $\text{Bias} = \frac{1}{N} \sum_{i=1}^N (F_i - A_i)$ | Systematic over- or under-prediction tendency. |
| **Weighted Absolute Percentage Error (WAPE)** | $\text{WAPE} = \frac{\sum_{i=1}^N \|F_i - A_i\|}{\sum_{i=1}^N A_i} \times 100\%$ | Normalized portfolio error percentage (zero-division protected). |
| **P10 / P50 / P90 Quantiles** | 10th, 50th, 90th percentiles of $e_i$ | Probabilistic risk bounds for volume hedging. |

### Decision Cutoff & Temporal Selection
For target delivery date $D$, the decision gate closure is set to:
$$\text{Cutoff} = (D - 1)\text{ at } 12:00:00\text{ UTC (configurable)}$$
The matching engine filters all historical publication runs:
$$\text{Eligible Runs} = \{ r \mid \text{publish\_time}(r) \le \text{Cutoff} \}$$
For each target delivery hour, the latest eligible forecast run is selected. If two runs share the exact same publish time, deterministic tie-breaking selects the record with the latest update.

### Dual-Grain Alignment (Hourly to Half-Hourly)
Elexon `WINDFOR` forecasts report average expected power (MW) over 60-minute target intervals ($H \in [0, 23]$). Elexon `FUELHH` actuals report outturn generation in 30-minute settlement periods ($p \in [1, 48]$).  
Since power (MW) is an instantaneous rate, an expected average rate of $G$ MW over hour $H$ applies directly to both Settlement Period $2H+1$ and $2H+2$ without inventing artificial linear interpolations.

For complete data profiles and validation results, see [**`docs/data-quality.md`**](docs/data-quality.md) and [**`data/README.md`**](data/README.md).

---

## 5. API Reference

| Method | Endpoint | Description | Query Parameters |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Container & service healthcheck | None |
| `GET` | `/api/wind/availability` | Summary of dataset date range and record counts | None |
| `GET` | `/api/wind/day-ahead` | 48 settlement periods forecast vs. actual for delivery day $D$ | `delivery_date` (YYYY-MM-DD), `cutoff_time` (HH:MM) |
| `GET` | `/api/wind/analytics` | Aggregated metrics, diurnal profile, and daily breakdown | `start_date`, `end_date`, `cutoff_time` |

For complete request schemas, response models, and examples, see [**`docs/api.md`**](docs/api.md).

---

## 6. Testing & Quality Assurance

The project enforces automated testing across data ingestion, statistical calculations, API routing, and multi-step E2E flows:

```bash
# Run complete backend test suite (45 tests)
pytest -v

# Run frontend unit tests (API URL construction)
cd frontend
npm test

# Run frontend linting & static analysis
npm run lint    # Oxlint (0 warnings, 0 errors)

# Run frontend production build
npm run build   # TypeScript 5.9 + Vite 8 (clean chunk splitting)
```

---

## 7. Cloud Deployment & Environment Compatibility

The application is engineered to operate seamlessly across three environments without modifying source code:

| Environment | Frontend URL Resolution | Backend Routing | CORS Policy |
| :--- | :--- | :--- | :--- |
| **1. Local Dev** | Relative `/api/*` and `/health` | Vite dev proxy (`localhost:5173` -> `127.0.0.1:8000`) | Disabled / Same-origin via proxy |
| **2. Local Docker** | Relative `/api/*` and `/health` | Nginx reverse proxy (`localhost:3000` -> `backend:8000`) | Same-origin via Nginx proxy |
| **3. Cloud Production** | Absolute (`VITE_API_BASE_URL` -> Render origin) | Direct browser `fetch()` to Render web service | Managed via `CORS_ALLOWED_ORIGINS` |

For step-by-step deployment instructions for Vercel and Render, see [**`docs/deployment.md`**](docs/deployment.md).

---

## 8. Project Verification Status & Limitations

### Status
- **Local Native Execution:** Fully verified (Python 3.11 + Vite).
- **Automated Test Suites:** 45 of 45 backend tests passed; 12 of 12 frontend URL tests passed.
- **Docker Compose Containers:** Built and running locally (`gridbricks-backend:healthy` on port 8000, `gridbricks-frontend` on port 3000).
- **Public Cloud Deployment:** Pre-configured via `render.yaml` and `vercel.json`; ready for personal deployment.

### Intended Scope & Limitations
This platform is an institutional **forecast error analysis and procurement decision-support tool**. It provides quantitative uncertainty bounds, diurnal risk profiles, and historical bias indicators to inform day-ahead volume purchasing. It is **not** a full autonomous procurement optimizer, as full procurement optimization requires real-time consumer load profiles, half-hourly wholesale power prices, interconnector flows, and generator ramp-rate constraints.

---

## 9. AI Usage Disclosure

All AI tools and workflows used during development are documented with full transparency in [**`docs/ai-disclosure.md`**](docs/ai-disclosure.md).
