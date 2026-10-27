"""End-to-End integration tests validating full system workflows, edge cases, and client simulation."""

from datetime import date
from fastapi.testclient import TestClient
import pytest

from backend.main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# Workflow Scenario A: Initial Page Load Flow
# ---------------------------------------------------------------------------

def test_e2e_initial_page_load_flow():
    """Simulates the three initial requests made by the frontend on mount:
    1. /api/wind/availability
    2. /api/wind/day-ahead for default date 2026-01-15 (Cutoff: D-1 12:00 UTC)
    3. /api/wind/analytics for full month 2026-01-01 to 2026-01-31
    """
    # 1. Availability
    res_avail = client.get("/api/wind/availability")
    assert res_avail.status_code == 200
    avail = res_avail.json()
    assert avail["min_date"] == "2026-01-01"
    assert avail["max_date"] == "2026-01-31"
    assert avail["total_actual_records"] == 1488
    assert avail["total_forecast_records"] == 19856
    assert avail["dataset_status"] == "ready"

    # 2. Initial Day-Ahead
    res_da = client.get("/api/wind/day-ahead?delivery_date=2026-01-15&cutoff_time=12:00&cutoff_days_prior=1")
    assert res_da.status_code == 200
    da = res_da.json()
    assert da["delivery_date"] == "2026-01-15"
    assert da["resolution"] == "half_hourly"
    assert len(da["periods"]) == 48
    assert da["metrics"]["observations_count"] == 48
    assert da["metrics"]["missing_count"] == 0
    assert da["metrics"]["mae_mw"] == 1189.79
    assert da["metrics"]["mean_bias_mw"] == 1189.79

    # 3. Initial Analytics (Full Month)
    res_an = client.get("/api/wind/analytics?start_date=2026-01-01&end_date=2026-01-31&cutoff_time=12:00&cutoff_days_prior=1")
    assert res_an.status_code == 200
    an = res_an.json()
    assert an["start_date"] == "2026-01-01"
    assert an["end_date"] == "2026-01-31"
    assert an["overall_metrics"]["observations_count"] == 1488
    assert an["overall_metrics"]["mae_mw"] == 2020.64
    assert an["overall_metrics"]["mean_bias_mw"] == 1806.23
    assert len(an["diurnal_profile"]) == 48
    assert len(an["daily_metrics"]) == 31


# ---------------------------------------------------------------------------
# Workflow Scenario B: Date Navigation & Day-to-Day Switching
# ---------------------------------------------------------------------------

def test_e2e_date_switching():
    """Tests switching between consecutive days (Jan 15 to Jan 16, Jan 1 to Jan 31)."""
    # Jan 15
    res15 = client.get("/api/wind/day-ahead?delivery_date=2026-01-15&cutoff_time=12:00")
    # Jan 16
    res16 = client.get("/api/wind/day-ahead?delivery_date=2026-01-16&cutoff_time=12:00")

    assert res15.status_code == 200
    assert res16.status_code == 200

    data15 = res15.json()
    data16 = res16.json()

    assert data15["delivery_date"] == "2026-01-15"
    assert data16["delivery_date"] == "2026-01-16"
    assert data15["periods"][0]["start_time"] != data16["periods"][0]["start_time"]
    assert data15["metrics"]["mae_mw"] != data16["metrics"]["mae_mw"]

    # Month Boundaries: Jan 01 and Jan 31
    res01 = client.get("/api/wind/day-ahead?delivery_date=2026-01-01&cutoff_time=12:00")
    res31 = client.get("/api/wind/day-ahead?delivery_date=2026-01-31&cutoff_time=12:00")

    assert res01.status_code == 200
    assert res31.status_code == 200
    assert len(res01.json()["periods"]) == 48
    assert len(res31.json()["periods"]) == 48


# ---------------------------------------------------------------------------
# Workflow Scenario C: Cutoff Time Sensitivity
# ---------------------------------------------------------------------------

def test_e2e_cutoff_sensitivity():
    """Tests changing decision cutoff times (e.g. 09:00 vs 11:30 vs 17:00).

    Verifies that the matched forecast publish times and values update accurately.
    """
    # 09:00 UTC cutoff on D-1
    res_09 = client.get("/api/wind/day-ahead?delivery_date=2026-01-15&cutoff_time=09:00")
    # 12:00 UTC cutoff on D-1
    res_12 = client.get("/api/wind/day-ahead?delivery_date=2026-01-15&cutoff_time=12:00")

    assert res_09.status_code == 200
    assert res_12.status_code == 200

    d09 = res_09.json()
    d12 = res_12.json()

    # The 09:00 cutoff selects an earlier forecast run (published <= 09:00)
    pub09 = d09["periods"][0]["forecast_publish_time"]
    pub12 = d12["periods"][0]["forecast_publish_time"]

    assert pub09 <= pub12
    assert "2026-01-14T09:00:00Z" >= pub09
    assert "2026-01-14T12:00:00Z" >= pub12


# ---------------------------------------------------------------------------
# Workflow Scenario D: Analytics Sub-Ranges & Presets
# ---------------------------------------------------------------------------

def test_e2e_analytics_presets():
    """Tests Week 1 (Jan 1-7) and Week 2 (Jan 8-14) presets."""
    # Week 1
    res_w1 = client.get("/api/wind/analytics?start_date=2026-01-01&end_date=2026-01-07")
    assert res_w1.status_code == 200
    w1 = res_w1.json()
    assert w1["overall_metrics"]["observations_count"] == 7 * 48
    assert len(w1["daily_metrics"]) == 7

    # Week 2
    res_w2 = client.get("/api/wind/analytics?start_date=2026-01-08&end_date=2026-01-14")
    assert res_w2.status_code == 200
    w2 = res_w2.json()
    assert w2["overall_metrics"]["observations_count"] == 7 * 48
    assert len(w2["daily_metrics"]) == 7


# ---------------------------------------------------------------------------
# Workflow Scenario E: Edge Cases & Error Handling
# ---------------------------------------------------------------------------

def test_e2e_invalid_dates_and_out_of_bounds():
    # Invalid format
    res_bad_fmt = client.get("/api/wind/day-ahead?delivery_date=2026/01/15")
    assert res_bad_fmt.status_code == 422

    # Out of range date (2025-12-25)
    res_out_of_range = client.get("/api/wind/day-ahead?delivery_date=2025-12-25")
    assert res_out_of_range.status_code == 404
    assert "not found in cached dataset" in res_out_of_range.json()["detail"]

    # Start date after end date
    res_inverted = client.get("/api/wind/analytics?start_date=2026-01-20&end_date=2026-01-10")
    assert res_inverted.status_code == 400
    assert "start_date must be less than or equal to end_date" in res_inverted.json()["detail"]

    # Negative cutoff_days_prior
    res_neg_days = client.get("/api/wind/day-ahead?delivery_date=2026-01-15&cutoff_days_prior=-1")
    assert res_neg_days.status_code == 422


# ---------------------------------------------------------------------------
# Workflow Scenario F: Peak vs Off-Peak Correctness
# ---------------------------------------------------------------------------

def test_e2e_peak_offpeak_partition():
    """Verifies that Peak (SP 15-38, 24 periods) and Off-Peak (24 periods)

    strictly partition the 48 settlement periods without overlap or omission.
    """
    res = client.get("/api/wind/analytics?start_date=2026-01-01&end_date=2026-01-01")
    assert res.status_code == 200
    data = res.json()

    peak = data["peak_metrics"]
    offpeak = data["off_peak_metrics"]
    overall = data["overall_metrics"]

    assert peak["observations_count"] == 24
    assert offpeak["observations_count"] == 24
    assert peak["observations_count"] + offpeak["observations_count"] == overall["observations_count"] == 48
