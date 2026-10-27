# Gridbricks Backend API & Analytical Engine Documentation

## 1. Architecture Overview

The backend is built with **Python 3.11** and **FastAPI**, following a modular service-oriented architecture:

```
backend/
├── api/
│   ├── __init__.py
│   └── routes.py               # REST API route handlers (/health, /availability, /day-ahead, /analytics)
├── ingestion/
│   ├── __init__.py
│   ├── client.py               # Elexon BMRS API client with exponential backoff
│   ├── models.py               # Raw and normalized Pydantic models
│   └── pipeline.py             # Normalization and Parquet/JSON export
├── models/
│   ├── __init__.py
│   └── schemas.py              # Strongly-typed API Request & Response Pydantic models
├── services/
│   ├── __init__.py
│   ├── data_loader.py          # Cached data access for normalized datasets
│   ├── matching_service.py     # Pre-auction Day-Ahead forecast selection & alignment
│   └── analytics_service.py    # Vectorized statistical error engine (MAE, RMSE, Bias, WAPE, quantiles)
├── tests/
│   ├── test_ingestion.py       # 16 unit tests for Elexon ingestion pipeline
│   ├── test_matching_analytics.py # 10 unit tests for matching & statistical math
│   └── test_api.py             # 7 integration tests for FastAPI endpoints
├── main.py                     # Application entrypoint & CORS middleware
└── requirements.txt            # Python dependencies
```

---

## 2. Decision-Time Gate-Closure Matching Engine

### 2.1 Day-Ahead Decision Mechanics
- In the UK wholesale electricity market (EPEX SPOT / Nord Pool), Day-Ahead auctions for delivery on day $D$ close around 11:00–12:00 UTC on day $D-1$.
- Any weather forecast published *after* this cutoff is unavailable to the procurement desk at bidding time.
- **Decision Cutoff Timestamp:**
  $$\text{Cutoff} = \text{datetime}(D - \text{days\_prior}, \text{cutoff\_time}, \text{UTC})$$
  Default: $D-1$ at `12:00:00 UTC` (configurable down to seconds).

### 2.2 Selection Algorithm
1. Filter candidates where $\text{publish\_time} \le \text{Cutoff}$ and delivery date is $D$.
2. For each delivery interval, select the candidate with $\max(\text{publish\_time})$.
3. **Deterministic Tie-Breaking:** If multiple records share identical publication timestamps and targets, sort deterministically by generation.
4. **Missing Data Policy:** If no eligible forecast exists prior to the cutoff, `forecast_generation_mw` is set to `None`. Future forecasts are never substituted.

---

## 3. Hourly-to-Half-Hourly Settlement Alignment

### 3.1 Source Data Discrepancy
- **Actuals (`FUELHH`):** Published every 30 minutes for 48 half-hour settlement periods per day ($p \in [1, 48]$).
- **Forecasts (`WINDFOR`):** Published by National Grid ESO at an hourly resolution (60-minute intervals, $H \in [0, 23]$).

### 3.2 Alignment Formulation
- Wind power generation is an instantaneous rate of energy flow (Megawatts, MW).
- An hourly forecast of $X$ MW for hour $[H, H+1)$ indicates an expected average rate of $X$ MW throughout that 60-minute interval.
- Each settlement period $p \in [1, 48]$ corresponds to clock hour $H = \lfloor(p - 1) / 2\rfloor$:
  - $p=1$ (00:00–00:30 UTC) $\rightarrow H=0$ (00:00 UTC forecast)
  - $p=2$ (00:30–01:00 UTC) $\rightarrow H=0$ (00:00 UTC forecast)
  - ...
  - $p=48$ (23:30–00:00 UTC) $\rightarrow H=23$ (23:00 UTC forecast)
- The original publication timestamp and target interval are retained on each period observation for full auditability.

---

## 4. Quantitative Accuracy Metrics

All metrics are computed exclusively across valid paired observations $(A_i, F_i)$ where neither value is missing. Missing observations are reported in `missing_count`.

| Metric | Formula | Interpretation |
| :--- | :--- | :--- |
| **Signed Error ($e_i$)** | $e_i = F_i - A_i$ | **Positive:** Over-forecasting (short risk).<br>**Negative:** Under-forecasting (spill risk). |
| **MAE** | $\frac{1}{N} \sum_{i=1}^N \|F_i - A_i\|$ | Average absolute magnitude of forecast miss (MW). |
| **RMSE** | $\sqrt{\frac{1}{N} \sum_{i=1}^N (F_i - A_i)^2}$ | Penalizes large errors disproportionately (vital for grid risk). |
| **Mean Bias Error (MBE)** | $\frac{1}{N} \sum_{i=1}^N (F_i - A_i)$ | Systemic directional bias across the horizon (MW). |
| **WAPE (%)** | $\frac{\sum \|F_i - A_i\|}{\sum A_i} \times 100$ | Weighted percentage error; safe against zero-generation periods. |
| **P10, P50, P90** | Linear percentiles of $e_i$ | P10 represents severe under-prediction; P90 represents severe over-prediction. |

### Peak vs. Off-Peak Definition
- **Peak Hours:** 07:00 to 19:00 UTC (Settlement Periods 15 to 38, inclusive).
- **Off-Peak Hours:** 00:00 to 07:00 and 19:00 to 24:00 UTC (Settlement Periods 1–14 and 39–48).

---

## 5. API Endpoints & Contracts

### 5.1 `GET /health`
Returns service health and UTC timestamp.

### 5.2 `GET /api/wind/availability`
Returns temporal boundaries of the cached dataset.
**Example Response:**
```json
{
  "min_date": "2026-01-01",
  "max_date": "2026-01-31",
  "total_actual_records": 1488,
  "total_forecast_records": 19856,
  "distinct_publish_runs": 272,
  "dataset_status": "ready"
}
```

### 5.3 `GET /api/wind/day-ahead`
**Query Parameters:**
- `delivery_date` (string, `YYYY-MM-DD`, default: `2026-01-15`)
- `cutoff_time` (string, `HH:MM`, default: `12:00`)
- `cutoff_days_prior` (int, default: `1`)

**Example Response Snippet:**
```json
{
  "delivery_date": "2026-01-15",
  "cutoff_time_utc": "2026-01-14T12:00:00Z",
  "cutoff_description": "Latest forecast published <= 2026-01-14 12:00:00 UTC (D-1 12:00 UTC)",
  "resolution": "half_hourly",
  "periods": [
    {
      "settlement_period": 1,
      "start_time": "2026-01-15T00:00:00Z",
      "actual_generation_mw": 14602.0,
      "forecast_generation_mw": 15813.0,
      "forecast_publish_time": "2026-01-14T11:30:00Z",
      "error_mw": 1211.0,
      "abs_error_mw": 1211.0
    }
  ],
  "metrics": {
    "mae_mw": 1189.79,
    "rmse_mw": 1304.38,
    "mean_bias_mw": 1189.79,
    "wape_percent": 11.26,
    "p10_error_mw": 555.1,
    "p50_error_mw": 1164.0,
    "p90_error_mw": 1794.6,
    "observations_count": 48,
    "missing_count": 0
  }
}
```

### 5.4 `GET /api/wind/analytics`
**Query Parameters:**
- `start_date` (string, default: `2026-01-01`)
- `end_date` (string, default: `2026-01-31`)
- `cutoff_time` (string, default: `12:00`)
- `cutoff_days_prior` (int, default: `1`)

Returns overall metrics, peak metrics, off-peak metrics, 48-period diurnal profile, and daily breakdown.

---

## 6. How to Run Locally

```powershell
# 1. Activate environment and run tests
cd "D:\grid bricks"
.\.venv\Scripts\pytest.exe -v

# 2. Start the FastAPI application with Uvicorn
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
Interactive Swagger UI will be available at: `http://127.0.0.1:8000/docs`
