# Gridbricks SWE Challenge — Final Submission Guide & Video Demo Script

**Candidate Submission Guide & Verification Walkthrough**  
**Role:** Full Stack Software Engineer (0-to-1 Power Systems)  
**Workspace:** `D:\grid bricks`  

---

## 1. Submission Deliverables Summary

| Deliverable | Required Format | Repository Location / Target | Verification Status |
| :--- | :--- | :--- | :--- |
| **1. Public GitHub Repository** | Public repository (anonymous name recommended) | [https://github.com/kaifshah07/uk-wind-forecast](https://github.com/kaifshah07/uk-wind-forecast) | Pushed and verified |
| **2. Live Application URL** | Hosted frontend reachable on public internet | [https://uk-wind-forecast.vercel.app/](https://uk-wind-forecast.vercel.app/) | Deployed and verified |
| **3. Live Backend API URL** | Hosted FastAPI web service on Render | [https://uk-wind-forecast-76jb.onrender.com](https://uk-wind-forecast-76jb.onrender.com) | Deployed and verified |
| **4. 10-Minute Demo Video** | Unlisted YouTube video ($\le 10$ min) | Follows timed script in Section 3 below | Script prepared; pending recording & upload |
| **5. AI Disclosure Statement** | Detailed report of AI tools used | [`docs/ai-disclosure.md`](ai-disclosure.md) | Complete & transparent |
| **6. Official Submission Form** | Microsoft Forms submission | [https://forms.cloud.microsoft/r/Ljmf1aWESK](https://forms.cloud.microsoft/r/Ljmf1aWESK) | Form URL ready for final submission |

---

## 2. Deployment Verification & Final Submission Steps

The application has been deployed to production:
- **Frontend:** Vercel static deployment at `https://uk-wind-forecast.vercel.app/`
- **Backend:** Render Python 3.11 web service at `https://uk-wind-forecast-76jb.onrender.com`
- **CORS & Integration:** Verified end-to-end with live Elexon January 2026 data.

### Step 1: Anonymous Repository Check / Rename (If Desired)
If you wish to satisfy the anonymous repository name requirement:
1. In your GitHub browser window, go to **Settings** -> **General** -> **Repository name**.
2. Rename from `uk-wind-forecast` to a non-descriptive string such as `q7m2vk9p` or `q7m2vk9p-wind-forecast`.
3. GitHub automatically creates redirects for all web and git traffic.
4. Update your local git remote:
   ```bash
   git remote set-url origin https://github.com/kaifshah07/<new-repo-name>.git
   ```

### Step 2: Record Demo Video
1. Use OBS Studio or Loom to record your screen and audio following the timed script below.
2. Total duration must be $\le 10$ minutes (Part 1: $\le 5$ min; Part 2: $\le 5$ min).
3. Upload to YouTube as **Unlisted**.

### Step 3: Incognito Verification
Before submitting, open each link in a clean Incognito/Private browser window:
- [ ] Deployed app: `https://uk-wind-forecast.vercel.app/`
- [ ] GitHub repository: `https://github.com/kaifshah07/<repo-name>`
- [ ] YouTube demo video: `https://youtu.be/<video-id>`

### Step 4: Submit Official Form
Submit the official form at [https://forms.cloud.microsoft/r/Ljmf1aWESK](https://forms.cloud.microsoft/r/Ljmf1aWESK) with:
- Candidate Name
- Repository URL
- Live Deployment URL
- Video Demo Link

## 3. 10-Minute Video Demonstration Script & Guide

**Total Duration:** Exactly $\le 10$ Minutes (Target: ~9 minutes 30 seconds)  
**Structure:**
- **Part 1 (0:00 – 4:45):** Client Pitch & Commercial Value Proposition (Energy Utility / Trading Desk Lead)
- **Part 2 (4:45 – 9:30):** Technical Lead Architecture, Code & Rigour Review (Engineering Lead / CTO)
- **Buffer (9:30 – 10:00):** Wrap-Up & Submission Sign-Off

---

### Part 1: Client Pitch & Commercial Value Proposition ($\le 5$ Minutes)

#### 0:00 – 0:50 | The Commercial Problem in UK Day-Ahead Procurement
- **On Screen:** Live dashboard open at `https://uk-wind-forecast.vercel.app/` showing January 15, 2026 Day-Ahead view.
- **Tone:** Confident, professional, clear, focused on financial and trading risk.
- **Narrative:**
  > *"Good morning. In the UK wholesale electricity market, wind forecast error is not just a statistical variance—it is a multi-million-pound balance sheet risk.
  > Under Elexon BSC market rules, day-ahead power auction bids must be committed by 12:00 UTC on day D-1. Every single megawatt of forecast error you carry into delivery day D gets settled in the Balancing Mechanism at penal cashout prices.
  > If you over-forecast wind by 1,000 MW, you are caught 'short' in the Balancing Mechanism and must purchase emergency replacement power at cashout buy prices that routinely spike above £300/MWh. If you under-forecast, you over-procure expensive thermal baseload, leaving you 'long' and forced to dump spill power at depressed or even negative system sell prices.
  > Worse yet, most internal trading tools suffer from a fatal flaw: **lookahead bias**. They evaluate accuracy using forecasts published after the 12:00 UTC auction gate had already shut.
  > Today, I am presenting **Gridbricks**: the first institutional-grade UK wind forecast analytics and decision-support platform built to eliminate lookahead bias, quantify volume tail risk, and protect utility trading margins for day-ahead procurement."*

#### 0:50 – 2:15 | The Day-Ahead Trading View & Live Walkthrough
- **On Screen:** Point to the top KPI cards for January 15, 2026 with cutoff `12:00:00`. Then hover over the main chart.
- **Visual Action:**
  1. Hover cursor over the KPI cards: MAE (`1,189.79 MW`), RMSE (`1,304.38 MW`), Mean Bias (`+1,189.79 MW`), WAPE (`11.26%`), and the P10/P50/P90 risk spread (`555.1 MW` to `1,794.6 MW`).
  2. Move cursor along the Recharts interactive curve. Hover over Settlement Period 24 (11:30–12:00 UTC).
- **Narrative:**
  > *"Here we are looking at January 15, 2026 on our live Vercel production deployment. Notice our gate-closure cutoff: strictly set to D-1 at 12:00 UTC.
  > Immediately, the top row delivers the five core metrics every head of power trading needs:
  > First, **Mean Bias: +1,189.79 MW**. The day-ahead forecast was systematically over-predicting wind generation across the entire 24-hour cycle.
  > Second, **WAPE is 11.26%**, indicating that the utility needed to prepare for an 11% portfolio volume deviation.
  > Third, the **P10 to P90 Risk Spread**: at P10, error is +555 MW; at P90, it surges to +1,795 MW. This gives our quantitative risk desk the exact volumetric confidence intervals required to size financial hedging collars.
  > Now look at the main visualization. The cyan area represents outturn actual generation from Elexon FUELHH across all 48 half-hour settlement periods. The amber stepped line represents the latest WINDFOR forecast published prior to the gate closure cutoff.
  > Hovering over Settlement Period 24 reveals the exact audit trail: target delivery hour 11:00 to 12:00 UTC, forecast generation 6,750 MW, actual generation 5,420 MW, giving an immediate signed error of +1,330 MW. A power trader seeing this profile knows in advance to procure supplemental peaking capacity to avoid imbalance penalties."*

#### 2:15 – 3:35 | Multi-Day Structural Analytics & Diurnal Risk
- **On Screen:** Click the **"Multi-Day Analytics"** tab. View the full month range (`2026-01-01` to `2026-01-31`).
- **Visual Action:**
  1. Click the tab; point out the 1,488 settlement periods evaluated.
  2. Point to the Peak vs. Off-Peak KPI comparison cards.
  3. Scroll down slightly to show the 48-period Diurnal Error Profile bar/line chart.
- **Narrative:**
  > *"Day-ahead trading isn't just about single days; it's about identifying structural system biases across the entire month.
  > Evaluating all 1,488 settlement periods in January 2026, Gridbricks reveals two critical trading discoveries:
  > Discovery 1: **Peak vs. Off-Peak Divergence**. During Peak hours (07:00 to 19:00 UTC, Settlement Periods 15 to 38), forecast accuracy is relatively tight: WAPE is 16.21% with an MAE of 1,869 MW. But during Off-Peak night hours, WAPE climbs to 18.68% with an MAE of 2,172 MW. This informs the desk that overnight baseload positions require a higher risk premium and wider hedging margins than daytime trades.
  > Discovery 2: **Diurnal Error Profile**. Looking at our 48-period diurnal curve, notice how forecast bias peaks during the morning ramp-up between SP 16 and SP 22. Traders can dynamically de-bias their volume bids during morning peak demand to avoid costly cashout penalties."*

#### 3:35 – 4:45 | Gate-Closure Sensitivity & Decision Support
- **On Screen:** Return to Day-Ahead tab. Change the **Cutoff Time** dropdown from `12:00:00` to `09:00:00`, then to `17:00:00`. Then click the **"Methodology & Market Rules"** button.
- **Visual Action:**
  1. Switch cutoff dropdown; show the KPIs and chart recalculate instantly without any page reload.
  2. Click the Methodology modal; scroll through the mathematical definitions.
- **Narrative:**
  > *"Different power exchanges and internal risk committees operate under different gate closures. If an auction closes at 09:00 UTC instead of 12:00 UTC, the platform instantly re-filters all 19,856 forecast publication runs and recomputes the metrics without page refreshes.
  > Furthermore, clicking the Methodology modal provides our traders and compliance team with complete mathematical definitions, Elexon data sources, UTC boundary rules, and transparent disclosures on how hourly forecasts align with half-hourly settlement periods.
  > In short: Gridbricks replaces guesswork with quantitative, back-tested certainty."*

---

### Part 2: Technical Lead Review & Engineering Rigour ($\le 5$ Minutes)

#### 4:45 – 5:45 | Full-Stack Architecture & Data Engineering
- **On Screen:** Switch to VS Code or terminal showing repository structure: `backend/`, `frontend/`, `data/`, and `compose.yaml`.
- **Tone:** Methodical, precise, engineering-focused.
- **Narrative:**
  > *"Now let's examine the engineering architecture that powers Gridbricks:
  > - **Backend:** Python 3.11 with FastAPI, Pydantic v2 validation, and vectorized pandas/pyarrow computation.
  > - **Frontend:** React 19, TypeScript 5.9, Vite 8, Tailwind CSS v4, and Recharts.
  > - **Containerization:** Multi-stage Docker builds orchestrated via Docker Compose with an Nginx Alpine reverse proxy.
  > In data engineering, we ingested 100% of January 2026 from the official Elexon BMRS API:
  > - 1,488 actual generation records from FUELHH (`fuelType == WIND`).
  > - 19,856 forecast records from WINDFOR across 272 publication runs.
  > We audited the dataset thoroughly: **zero missing settlement periods, zero nulls, zero negative generation**. To guarantee zero cold-start latency and zero external API downtime during evaluation, data is stored in normalized Parquet format with JSON fallback."*

#### 5:45 – 7:00 | Temporal Gate-Closure Logic & Metric Formulation
- **On Screen:** Open `backend/app/services/matching_service.py` and `backend/app/services/analytics_service.py`.
- **Visual Action:** Highlight the cutoff filter query and the hourly-to-half-hourly mapping function.
- **Narrative:**
  > *"Let's look at `matching_service.py`. For any delivery date D, the cutoff datetime is strictly calculated as D-1 at the configured cutoff time (defaulting to 12:00:00 UTC). We filter:
  > `publish_time <= cutoff_utc`
  > And select the latest available forecast run per target interval, with deterministic tie-breaking on `publish_time`. Forecasts published at 12:00:01 UTC or later are strictly excluded, eliminating lookahead bias down to the exact second.
  > A key domain challenge is **Dual-Grain Alignment**: WINDFOR forecasts are published at 60-minute hourly intervals ($H \in [0, 23]$), while FUELHH actuals are reported in 30-minute settlement periods ($SP \in [1, 48]$).
  > Because power (MW) is an instantaneous rate, an expected average rate of G megawatts over hour H applies directly to both Settlement Periods 2H+1 and 2H+2. We preserve the authentic Elexon schema without inventing artificial linear interpolations.
  > In `analytics_service.py`, all error metrics—MAE, RMSE, Signed Bias ($F_i - A_i$), WAPE, and P10/P50/P90 quantiles—are fully vectorized. We strictly guard against division-by-zero in WAPE if actual generation sums to zero, and missing forecasts remain explicit nulls rather than artificial zeros."*

#### 7:00 – 8:15 | Automated Testing & QA Evidence
- **On Screen:** Open PowerShell terminal in project root and run `.\.venv\Scripts\pytest.exe -v`.
- **Visual Action:** Let the tests execute live on screen (finishing in ~7.5 seconds with 45 passed).
- **Narrative:**
  > *"Reliability is enforced through comprehensive automated testing. Running `pytest -v` executes our 45-test backend suite:
  > - **16 Ingestion Tests:** Validating HTTP client resilience, exponential backoff on HTTP 429 rate limits, retry exhaustion on 500s, schema validation, and strict UTC timezone conversion.
  > - **13 Analytics & Matching Tests:** Verified against hand-calculated mathematical fixtures, second-level cutoff boundary eligibility, WAPE zero-division safety, and peak/off-peak partition conservation.
  > - **10 API & CORS Tests:** Endpoint contracts, input validation, date-range bounds, and cross-origin security headers.
  > - **6 End-to-End Integration Tests:** Simulating multi-step trading desk workflows.
  > On the frontend, we ran `npm test` verifying 12 API URL resolution cases, `oxlint` across 14 TypeScript files with zero errors and zero warnings, and a clean Vite production build with Rollup code-splitting."*

#### 8:15 – 9:15 | Docker Architecture & Multi-Environment Compatibility
- **On Screen:** Show `compose.yaml`, `frontend/nginx.conf`, and terminal output of `docker compose ps`.
- **Narrative:**
  > *"The platform is engineered for seamless operation across three distinct environments:
  > 1. **Local Development:** Vite dev server with proxy routing to FastAPI on port 8000.
  > 2. **Local Docker:** Multi-stage Docker Compose deployment. As shown here in `docker compose ps`, both `gridbricks-backend` and `gridbricks-frontend` are running and healthy. The Nginx reverse proxy routes `/api/` and `/health` over Docker's internal bridge network, completely eliminating CORS issues.
  > 3. **Cloud Production:** Deployed live with Vercel serving the React SPA and Render hosting the FastAPI web service, connected via secure cross-origin headers.
  > Security hygiene is verified: zero hardcoded secrets, zero personal machine paths, and `.env` files strictly git-ignored."*

#### 9:15 – 9:45 | Conclusion & Submission Sign-Off
- **On Screen:** Return to the live deployed application at `https://uk-wind-forecast.vercel.app/`.
- **Narrative:**
  > *"In conclusion, Gridbricks delivers an institutional-grade, fully tested, containerized, and deployed decision-support platform for UK wind energy procurement. It solves the real-world challenge of lookahead bias, respects Elexon market rules, and equips power trading desks with rigorous quantitative risk analytics.
  > All source code, Docker configurations, and documentation are available in the public GitHub repository. Thank you for your time."*
