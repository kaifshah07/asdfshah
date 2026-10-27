# Gridbricks SWE Challenge — Final Submission Guide & Video Demo Script

**Candidate Submission Guide & Verification Walkthrough**  
**Role:** Full Stack Software Engineer (0-to-1 Power Systems)  
**Workspace:** `D:\grid bricks`  

---

## 1. Submission Deliverables Summary

| Deliverable | Required Format | Repository Location / Target | Verification Status |
| :--- | :--- | :--- | :--- |
| **1. Public GitHub Repository** | Public repository with clean Git history | Staged for initial commit | Locally verified; ready for remote push |
| **2. Live Application URL** | Hosted frontend reachable on public internet | Vercel (`frontend/vercel.json`) & Render (`render.yaml`) | Pre-configured; requires personal deployment |
| **3. 10-Minute Demo Video** | Unlisted YouTube or Loom video ($\le 10$ min) | Follows timed script in Section 3 below | Script & walkthrough prepared |
| **4. AI Disclosure Statement** | Detailed report of AI tools and prompts used | [`docs/ai-disclosure.md`](ai-disclosure.md) | Complete & transparent |
| **5. Technical Documentation** | System architecture, API docs, and data quality | [`docs/`](.) and [`README.md`](../README.md) | Comprehensive and verified |

---

## 2. Step-by-Step Deployment & Submission Checklist

### Step 1: Push Code to a Public GitHub Repository
1. Open PowerShell in the project root:
   ```powershell
   git add .
   git commit -m "feat: complete Gridbricks UK wind generation forecast & decision support platform"
   git branch -M master
   git remote add origin https://github.com/<your-username>/<your-repo-name>.git
   git push -u origin master
   ```

### Step 2: Deploy Backend to Render (Free Tier)
1. Go to [Render Dashboard](https://dashboard.render.com/) -> **New + -> Web Service** and select your GitHub repository.
2. Select **Python 3** (or Docker, pointing to `backend/Dockerfile` with context `.`).
3. Set Name: `gridbricks-backend`.
4. Build Command: `pip install --no-cache-dir -r backend/requirements.txt`
5. Start Command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
6. Health Check Path: `/health`
7. Environment Variables:
   - `PYTHONPATH` = `.`
   - `PYTHON_VERSION` = `3.11.9`
   - `CORS_ALLOWED_ORIGINS` = `*` (or your specific Vercel URL once deployed)
8. Click **Deploy Web Service** and copy your live URL (e.g., `https://<your-backend>.onrender.com`).
9. Verify in your browser: `https://<your-backend>.onrender.com/health` (returns `{"status":"healthy","version":"1.0.0"}`).

### Step 3: Deploy Frontend to Vercel (Free Tier)
1. Go to [Vercel Dashboard](https://vercel.com/new) and import your GitHub repository.
2. Settings:
   - **Framework Preset:** `Vite`
   - **Root Directory:** Select `frontend` (or leave root)
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
   - **Environment Variables:**
     - Add `VITE_API_BASE_URL` with your Render backend URL (e.g. `https://<your-backend>.onrender.com`).
3. Click **Deploy**.
4. Test in an incognito window: verify KPI cards and the Recharts time-series chart render outturn data immediately.

### Step 4: Record Demo Video & Submit Google Form
1. Record your screen and microphone using Loom or OBS following the 10-minute script below.
2. Upload as an **Unlisted** YouTube video (or copy the public Loom URL).
3. Submit the Google Form link provided in your challenge invitation with your name, GitHub URL, live Vercel URL, and video link.

---

## 3. 10-Minute Video Demonstration Script & Guide

**Total Duration:** Exactly $\le 10$ Minutes  
**Structure:**
- **Part 1 (0:00 – 4:45):** Client Pitch & Trading Desk Value Proposition (Energy Utility / Trading Desk Lead)
- **Part 2 (4:45 – 9:45):** Technical Lead Architecture, Code & Rigour Review (Engineering Lead / CTO)
- **Buffer (9:45 – 10:00):** Wrap-Up & Submission Summary

---

### Part 1: Client Pitch & Commercial Value Proposition ($\le 5$ Minutes)

#### 0:00 – 0:45 | The Commercial Problem in UK Day-Ahead Procurement
- **Visual:** Open live browser dashboard showing January 15, 2026 Day-Ahead view.
- **Narrative:**
  > *"Every morning before the day-ahead power auction closes at 12:00 UTC, UK energy utilities face a multi-million-pound balancing dilemma. Wind power now accounts for over 25% of grid generation, but its intermittency creates severe balancing exposure under Elexon BSC cashout pricing.
  > Over-procuring conventional thermal power leaves you exposed to negative system prices when wind over-delivers. Under-procuring forces you to purchase emergency power from the Balancing Mechanism at penal cashout rates.
  > Today, I'm presenting the Gridbricks UK Wind Forecast & Decision-Support Platform—built to eliminate lookahead bias, quantify forecast error uncertainty, and give power traders confident, data-driven procurement targets."*

#### 0:45 – 2:00 | The Day-Ahead Trading View & Live Walkthrough
- **Visual:** Point to the KPI cards: MAE (1,189.79 MW), RMSE (1,349.52 MW), Mean Bias (+1,189.79 MW), WAPE (16.27%), and the P10/P50/P90 risk spread.
- **Narrative:**
  > *"Here we are looking at January 15, 2026. Notice our decision cutoff gate: D-1 at 12:00 UTC. 
  > In the top row, the platform immediately delivers the five metrics every head of power trading needs:
  > First, Mean Bias: +1,189 MW. The day-ahead forecast consistently over-predicted wind generation across the entire day.
  > Second, WAPE is 16.27%, meaning the utility must prepare for roughly a 16% volume imbalance.
  > Third, the P10 to P90 risk spread: at P10, the forecast error is +484 MW; at P90, it surges to +1,939 MW.
  > Look at the main chart below. The cyan area represents outturn actual generation from Elexon FUELHH across all 48 half-hour settlement periods. The amber stepped line represents the latest WINDFOR forecast published prior to the gate closure cutoff.
  > Hovering over Settlement Period 24 reveals the exact publication audit trail: target delivery hour 11:00 to 12:00 UTC, forecast generation 6,750 MW, actual generation 5,420 MW, giving an immediate signed error of +1,330 MW."*

#### 2:00 – 3:30 | Multi-Day Structural Analytics & Diurnal Risk
- **Visual:** Click the "Multi-Day Analytics" tab. Switch to the full month view (Jan 1 – Jan 31).
- **Narrative:**
  > *"Day-ahead trading isn't just about single days; it's about structural system patterns.
  > Over the complete month of January 2026—evaluating all 1,488 settlement periods—the platform reveals two crucial trading insights:
  > 1. Peak vs. Off-Peak Divergence: During Peak hours (07:00 to 19:00 UTC, Settlement Periods 15 to 38), the forecast is significantly more accurate: WAPE is 16.21% with an MAE of 1,869 MW. But during Off-Peak night hours, WAPE jumps to 18.68% with an MAE of 2,172 MW. This tells the desk to apply a larger risk premium to overnight baseload hedges.
  > 2. Diurnal Error Profile: Looking at our 48-period diurnal curve, notice how forecast bias peaks during the morning ramp-up between SP 16 and 22. Traders can dynamically de-bias their volume submission to avoid costly imbalance settlement penalties."*

#### 3:30 – 4:45 | Gate-Closure Sensitivity & Decision Support
- **Visual:** Switch Cutoff dropdown to `17:00:00` and `09:00:00` to show live recalculation. Click "Methodology & Market Rules" modal.
- **Narrative:**
  > *"Different power exchanges and internal risk committees operate under different gate closures. If your procurement auction closes at 09:00 UTC instead of 12:00 UTC, the platform instantly re-runs the gate closure selection and recomputes the metrics without page refreshes.
  > Furthermore, clicking the Methodology modal provides our traders and compliance team with complete mathematical definitions, Elexon data sources, UTC boundary rules, and transparent disclosures on how hourly forecasts align with half-hourly settlement periods."*

---

### Part 2: Technical Lead Review & Engineering Rigour ($\le 5$ Minutes)

#### 4:45 – 5:45 | Full-Stack Architecture & Data Engineering
- **Visual:** Switch to code/terminal. Show project tree: `backend/`, `frontend/`, `data/`, and `compose.yaml`.
- **Narrative:**
  > *"Now let's examine the engineering architecture that powers this system:
  > - Backend: Python 3.11 with FastAPI, Pydantic v2, and pandas/pyarrow.
  > - Frontend: React 19, TypeScript 5.9, Vite 8, Tailwind CSS v4, and Recharts.
  > - Containerization: Production Docker Compose multi-stage builds with Nginx reverse proxying.
  > In data engineering, we ingested 100% of January 2026 from the official Elexon BMRS API: 1,488 actual generation records from FUELHH and 19,856 forecast records from WINDFOR across 272 publication runs. Zero missing periods, zero nulls. The data is cached locally in normalized Parquet and JSON formats."*

#### 5:45 – 7:00 | Temporal Gate-Closure Logic & Metric Formulation
- **Visual:** Show `matching_service.py` and `analytics_service.py`.
- **Narrative:**
  > *"In `matching_service.py`, for any delivery date D, the cutoff datetime is strictly calculated as D-1 at the configured cutoff time (defaulting to 12:00 UTC). We filter:
  > `publish_time <= cutoff_utc`
  > And select the latest available forecast run per target interval.
  > A key discovery in our data audit was that WINDFOR forecasts are published at hourly resolution, while FUELHH actuals are reported in 30-minute settlement periods. Because power in MW is a continuous rate, hour H applies directly to Settlement Periods 2H+1 and 2H+2 without inventing artificial linear interpolations.
  > In `analytics_service.py`, our metrics are vector-accelerated with pandas/NumPy. We strictly guard against division-by-zero in WAPE if actual generation sums to zero, and we never convert missing forecasts to zeros—we preserve nulls to maintain analytical truth."*

#### 7:00 – 8:15 | Testing Rigour & Automated Test Suite
- **Visual:** Run `pytest -v` in terminal to show all 45 tests passing.
- **Narrative:**
  > *"Running `pytest -v` executes our 45-test suite in under 7 seconds:
  > - 16 ingestion tests: client retries (429 exponential backoff, 500 exhaustion), schema validation, deduplication, UTC timezone parsing.
  > - 13 matching and analytics tests: hand-calculated mathematical fixtures, boundary cutoff eligibility down to the exact second, WAPE zero-division safety, and peak/off-peak partition conservation.
  > - 10 API and CORS contract tests: query parameter validation, invalid dates, and cross-origin security headers.
  > - 6 End-to-End integration scenarios: simulating full trading desk workflows from initial load to cutoff sensitivity."*

#### 8:15 – 9:15 | Frontend Engineering & Docker Architecture
- **Visual:** Show `frontend/src/services/api.ts` and `frontend/nginx.conf`. Show `docker compose ps`.
- **Narrative:**
  > *"On the frontend:
  > - We optimized Vite's build with Rollup manual chunking, splitting Recharts and React into separate chunks to ensure initial bundle loads stay under 60 kB.
  > - In `App.tsx`, we eliminated asynchronous race conditions during rapid date switching using monotonic request sequence IDs (`useRef<number>`).
  > - In `api.ts`, our `buildApiUrl` normalizes slashes and paths across local dev proxy, local Docker Nginx, and cloud Vercel deployments.
  > - We ran `oxlint` across 14 TypeScript files with 0 errors and 0 warnings.
  > For containerization, `frontend/Dockerfile` uses a multi-stage build: Stage 1 builds the Vite bundle; Stage 2 serves it via Nginx Alpine (~26 MB image). Nginx reverse-proxies `/api/` to `http://backend:8000/api/` over Docker's internal bridge network. This guarantees zero CORS issues, no hardcoded IPs, and instant cloud portability."*

#### 9:15 – 10:00 | Conclusion & Wrap-Up
- **Visual:** Return to live dashboard.
- **Narrative:**
  > *"In summary, Gridbricks delivers an end-to-end, tested, containerized, and institutional-grade decision-support platform for UK wind energy procurement. All code, test suites, Docker manifests, and documentation are ready for production deployment. Thank you for your time."*
