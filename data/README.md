# Gridbricks Data Directory & Specification

This directory stores the official Elexon BMRS historical wind power datasets covering the complete month of **January 2026** (2026-01-01 to 2026-01-31).

---

## 1. Directory Structure

```
data/
├── data_quality_report.json          # Programmatic data validation summary
├── normalized/                       # Processed datasets used by the FastAPI backend
│   ├── actuals_jan2026.parquet       # High-speed columnar actuals (1,488 rows, 24 KB)
│   ├── actuals_jan2026.json          # JSON fallback actuals (1,488 rows, 252 KB)
│   ├── forecasts_jan2026.parquet     # Columnar wind forecasts (19,856 rows, 96 KB)
│   └── forecasts_jan2026.json        # JSON fallback forecasts (19,856 rows, 2.55 MB)
└── raw/                              # Original API response archives from Elexon BMRS
    ├── fuelhh_2026-01-01_2026-01-31.json # Raw FUELHH wind stream payload
    └── windfor_jan2026.json          # Raw WINDFOR forecast runs payload
```

---

## 2. Dataset Overview

| Dataset | Elexon API Stream | Grain | Jan 2026 Records | Key Fields | Purpose |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Outturn Actuals** | `FUELHH` (`fuelType == "WIND"`) | 30-minute Settlement Period (1–48) | **1,488** | `start_time`, `settlement_date`, `settlement_period`, `generation` | Ground-truth outturn generation for error calculations. |
| **Wind Forecasts** | `WINDFOR` | 60-minute target interval (Hours 0–23) | **19,856** (across 272 publication runs) | `start_time`, `publish_time`, `generation` | Historical published forecast runs evaluated against pre-auction cutoffs. |

### Data Quality & Completeness
- **Actuals Completeness:** Exactly $31 \times 48 = 1,488$ records. Zero missing settlement periods. Zero null generation values.
- **Forecasts Completeness:** 272 distinct publication runs (average ~8 runs/day) providing full delivery interval coverage.
- **Timezone Standard:** Strict ISO 8601 UTC with explicit `Z` designator across all timestamps.

---

## 3. Reproducibility & Regeneration

To regenerate the normalized Parquet and JSON datasets from the raw archives or re-ingest directly from the live Elexon BMRS API:

```bash
# Run the ingestion and normalization pipeline
python backend/scripts/run_ingestion.py
```

The pipeline validates schemas, removes duplicates, checks settlement period constraints (1–48), ensures UTC timezone awareness, and writes the output to `data/normalized/`.
