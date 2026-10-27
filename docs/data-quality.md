# Elexon BMRS Data Quality & Ingestion Report: January 2026

## 1. Executive Summary

During Step 2, the official Elexon BMRS API was thoroughly probed, analyzed, and ingested for the entire target scope: **January 1–31, 2026**.

Both datasets (`FUELHH` actuals and `WINDFOR` forecasts) were successfully extracted, validated against strict Pydantic models, normalized into timezone-aware UTC representations, deduplicated, and preserved in both raw JSON and high-performance Parquet format.

**Key Findings:**
1. **Actuals (`FUELHH`):** Complete coverage. Exactly 1,488 records (31 days $\times$ 48 settlement periods) with 0 missing slots, 0 null values, and 0 negative values.
2. **Forecasts (`WINDFOR`):** Complete coverage across the entire month. 272 publication runs containing 19,856 forecast records. Every single target interval in January 2026 has multiple forecast runs published prior to the day-ahead 12:00 UTC cutoff on day $D-1$.
3. **Resolution Discovery:** `FUELHH` actuals are half-hourly (30-minute settlement periods, 48 per day), whereas UK National Grid ESO's `WINDFOR` model publishes at an hourly resolution (60-minute intervals, 24 target slots per day). Each hourly forecast directly maps to two consecutive half-hour settlement periods ($2H+1$ and $2H+2$), or can be compared at hourly aggregated resolution.

---

## 2. Official API Endpoint Analysis

### 2.1 Actual Wind Generation (`FUELHH`)
- **API URL:** `https://data.elexon.co.uk/bmrs/api/v1/datasets/FUELHH/stream`
- **Method:** `GET`
- **Authentication:** None required (publicly accessible open data).
- **Rate Limits:** HTTP 429 returned on excessive concurrency; handled with exponential backoff.
- **Parameters Used:**
  - `settlementDateFrom`: `2026-01-01` (format: `yyyy-MM-dd`)
  - `settlementDateTo`: `2026-01-31` (format: `yyyy-MM-dd`)
  - `fuelType`: `WIND`
- **Raw Schema Fields:**
  - `dataset`: String (`"FUELHH"`)
  - `publishTime`: ISO date-time UTC (`"2026-01-02T00:00:00Z"`)
  - `startTime`: ISO date-time UTC (`"2026-01-01T23:30:00Z"`)
  - `settlementDate`: ISO date (`"2026-01-01"`)
  - `settlementPeriod`: Integer `1` to `48`
  - `fuelType`: String (`"WIND"`)
  - `generation`: Integer (MW)

### 2.2 Forecast Wind Generation (`WINDFOR`)
- **API URL:** `https://data.elexon.co.uk/bmrs/api/v1/datasets/WINDFOR/stream`
- **Method:** `GET`
- **Authentication:** None required.
- **Parameters Used:**
  - `publishDateTimeFrom`: `2025-12-30T00:00:00Z`
  - `publishDateTimeTo`: `2026-02-01T23:59:59Z`
- **Raw Schema Fields:**
  - `dataset`: String (`"WINDFOR"`)
  - `publishTime`: ISO date-time UTC (execution timestamp of the forecast run)
  - `startTime`: ISO date-time UTC (target delivery hour)
  - `generation`: Integer (forecasted MW)
- **Publication Frequency:** 8 forecast publication runs per 24-hour cycle (~every 3 hours: 02:30, 04:30, 07:30, 09:30, 11:30, 14:30, 17:30, 22:30 UTC).
- **Forecast Horizon:** ~73 hours per run.

---

## 3. Data Quality & Coverage Metrics

| Metric | Actuals (`FUELHH`) | Forecasts (`WINDFOR`) |
| :--- | :--- | :--- |
| **Date Range Queried** | 2026-01-01 to 2026-01-31 | 2025-12-30 to 2026-02-01 |
| **Raw Records Ingested** | 1,488 | 19,856 |
| **Valid Normalized Records** | 1,488 | 19,856 |
| **Duplicates Removed** | 0 | 0 |
| **Validation / Schema Errors** | 0 | 0 |
| **Null Generations** | 0 | 0 |
| **Negative Generations** | 0 | 0 |
| **Distinct Dates / Runs** | 31 days (48 SP/day) | 272 publication runs |
| **Min Generation (MW)** | 1,695.0 MW | 1,220.0 MW |
| **Max Generation (MW)** | 17,805.0 MW | 18,450.0 MW |
| **Mean Generation (MW)** | 11,580.74 MW | 11,745.30 MW |
| **Settlement Periods per Day** | Exactly 48 for all 31 days | 24 hourly steps per day |
| **Missing Settlement Periods** | **0** | **0** |

---

## 4. Gate-Closure Forecast Availability Verification

To verify that the client utility can reliably make Day-Ahead decisions before auction gate closure (12:00 UTC on day $D-1$), the dataset was analyzed for lookahead compliance:

- For each delivery day $D \in [2026\text{-}01\text{-}01, 2026\text{-}01\text{-}31]$:
  - Day-Ahead Decision Cutoff: $D-1$ at 12:00:00 UTC.
  - Number of delivery intervals: 1,488.
  - Delivery intervals with at least one valid forecast published $\le D-1\text{ 12:00:00 UTC}$: **1,488 (100.0%)**.
  - Default matched forecast run: The run published at **11:30:00 UTC on $D-1$** is consistently present across all 31 days, providing the exact latest pre-auction forecast for traders.

---

## 5. Storage Artifacts

The ingestion pipeline created the following local cache artifacts:

```
D:\grid bricks\data\
├── raw\
│   ├── fuelhh_2026-01-01_2026-01-31.json   (355 KB, 1,488 raw records)
│   └── windfor_jan2026.json                (2.95 MB, 19,856 raw records)
├── normalized\
│   ├── actuals_jan2026.parquet             (24 KB, optimized column store)
│   ├── actuals_jan2026.json                (252 KB, ISO-8601 UTC)
│   ├── forecasts_jan2026.parquet           (96 KB, indexed by publish & target)
│   └── forecasts_jan2026.json              (2.55 MB, ISO-8601 UTC)
└── data_quality_report.json                (Machine-readable quality audit)
```

---

## 6. Automated Unit Tests

A comprehensive suite of 16 tests was implemented in [`backend/tests/test_ingestion.py`](file:///d:/grid%20bricks/backend/tests/test_ingestion.py):
- `test_client_successful_list_response`: PASSED
- `test_client_dict_with_data_key`: PASSED
- `test_client_empty_response`: PASSED
- `test_client_malformed_response_type`: PASSED
- `test_client_http_400_bad_request`: PASSED
- `test_client_retry_on_429_then_succeed`: PASSED
- `test_client_exhausts_retries_on_500`: PASSED
- `test_raw_fuelhh_valid`: PASSED
- `test_raw_fuelhh_invalid_settlement_period`: PASSED
- `test_raw_windfor_valid`: PASSED
- `test_parse_utc_timestamp_with_z`: PASSED
- `test_parse_utc_timestamp_naive`: PASSED
- `test_normalized_models_ensure_utc`: PASSED
- `test_pipeline_deduplication`: PASSED
- `test_pipeline_invalid_records_skipped`: PASSED
- `test_pipeline_idempotence`: PASSED

**Result:** 16 passed in 1.64s with 100% success rate.
