# AI Tool Usage Disclosure

**Company:** Gridbricks  
**Role:** Full Stack Software Engineer Challenge  
**Candidate Submission Disclosure**  
**Date:** October 27, 2026  

---

## 1. Transparency & Philosophy Statement

In accordance with Gridbricks' evaluation principles of engineering discipline, technical ownership, and transparency, this document discloses all AI tools, models, and workflows utilized during the design, implementation, and verification of the UK Wind Generation Forecast and Procurement Platform.

AI was used as an **accelerator, pair programmer, and rigorous auditor**, but **not as an unverified generator of untested code**. Every architectural decision, statistical equation, API contract, and edge-case guard was vetted against official Elexon market documentation, mathematical first principles, and automated test fixtures.

---

## 2. Tools & Models Used

| Tool / Model | Context & Purpose | Scope of Work |
| :--- | :--- | :--- |
| **Google Antigravity / Gemini 2.5 Pro** | Autonomous agentic coding assistant & pair programming partner | End-to-end project scaffolding, unit and integration test development, statistical formulation, frontend component assembly, and Docker containerization. |
| **GitHub Copilot / IDE Completion** | Inline code typing and syntax completion | Routine boilerplate typing in TypeScript interfaces and Pydantic validation schemas. |

---

## 3. Detailed Work Breakdown by Stage

### Stage 1: Problem Definition & Roadmap Formulation
- **AI Role:** Assisted in breaking down the challenge document into a verification-first, 8-step roadmap (`PROJECT_MASTER_PLAN.md` and `PROJECT_PROGRESS.md`).
- **Human Verification:** Confirmed market mechanics, half-hour settlement periods (1–48), and the pre-auction gate closure cutoff timeline ($D-1$ 12:00 UTC).

### Stage 2: Data Ingestion & Schema Exploration
- **AI Role:** Parsed the official Elexon OpenAPI 3.0 specification (`https://data.elexon.co.uk/swagger/v1/swagger.json`) to map the `FUELHH` and `WINDFOR` schemas.
- **Human Verification:** Audited the discrepancy between `FUELHH`'s 30-minute settlement period resolution and `WINDFOR`'s 60-minute forecast target resolution. Validated that power (MW) is a continuous rate, verifying that an hourly forecast applies directly across both half-hours in that hour without artificial interpolation. Confirmed 100% completeness for January 2026 (1,488 actual observations, 19,856 forecast records).

### Stage 3: Statistical Formulation & FastAPI Engine
- **AI Role:** Implemented vector-accelerated calculations for MAE, RMSE, Mean Bias Error (MBE = $F - A$), and WAPE using pandas/NumPy.
- **Human Verification:** Verified numerical edge cases: division-by-zero protection in WAPE ($\sum A_i = 0$), non-zeroing of missing forecasts, second-level cutoff boundary eligibility, and peak (SP 15–38, 07:00–19:00 UTC) vs. off-peak conservation ($744 + 744 = 1,488$). Tested against hand-calculated fixtures.

### Stage 4: Frontend Development
- **AI Role:** Generated React 19 + TypeScript + Tailwind CSS v4 + Recharts dashboard components based on institutional energy trading layouts.
- **Human Verification:** Enforced strict type-mirroring with backend Pydantic models, audited chart tooltips for publication timestamps, and implemented monotonic request sequence tracking (`useRef<number>`) to eliminate asynchronous race conditions during rapid date switching.

### Stage 5: End-to-End Hardening & Bundle Optimization
- **AI Role:** Authored multi-step trading desk integration tests in `backend/tests/test_e2e_integration.py` and configured Rollup manual chunking in `frontend/vite.config.ts`.
- **Human Verification:** Verified that all 42 backend tests pass, bundle chunk sizes remain under 500 kB, and `oxlint` reports 0 warnings and 0 errors.

### Stage 6: Docker Containerization
- **AI Role:** Created `backend/Dockerfile` (Python 3.11-slim), `frontend/Dockerfile` (multi-stage Node + Nginx), `frontend/nginx.conf`, and `compose.yaml`.
- **Human Verification:** Audited Docker layer caching, verified volume mounts and healthcheck endpoints, and ensured zero leakage of host virtual environments or secrets.

---

## 4. Engineering Verification Discipline

To ensure complete reliability, the following rules were enforced throughout development:
1. **Never claim a test passes without executing it:** All 42 tests were run in Python 3.11 with pytest, achieving a 100% pass rate.
2. **Never claim a build works without compiling:** The frontend was built with `tsc -b && vite build` and linted with `oxlint`.
3. **Preserve data integrity:** Normalized Parquet and JSON files were strictly cached and never modified or fabricated.
4. **Transparent limitations:** The platform is explicitly positioned as a forecast error analysis and procurement decision-support tool, acknowledging that full procurement optimization requires demand, market prices, and grid constraints.
