"""Unit tests for ForecastMatchingService and Analytics Engine."""

from datetime import date, datetime, time, timezone
from typing import Any, Dict, List
import numpy as np
import pandas as pd
import pytest

from backend.services.analytics_service import (
    calculate_daily_metrics,
    calculate_diurnal_profile,
    calculate_error_metrics,
    calculate_peak_offpeak_metrics,
)
from backend.services.matching_service import (
    ForecastMatchingService,
    calculate_cutoff_datetime,
    parse_cutoff_time,
)


# ---------------------------------------------------------------------------
# Cutoff & Boundary Tests
# ---------------------------------------------------------------------------

def test_parse_cutoff_time():
    t1 = parse_cutoff_time("12:00")
    assert t1 == time(12, 0, 0)
    t2 = parse_cutoff_time("09:30:15")
    assert t2 == time(9, 30, 15)
    with pytest.raises(ValueError):
        parse_cutoff_time("invalid")


def test_calculate_cutoff_datetime_d_minus_1():
    target_date = date(2026, 1, 15)
    cutoff = calculate_cutoff_datetime(target_date, cutoff_time_str="12:00", days_prior=1)
    assert cutoff == datetime(2026, 1, 14, 12, 0, 0, tzinfo=timezone.utc)


def test_calculate_cutoff_datetime_same_day():
    target_date = date(2026, 1, 15)
    cutoff = calculate_cutoff_datetime(target_date, cutoff_time_str="06:00", days_prior=0)
    assert cutoff == datetime(2026, 1, 15, 6, 0, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# Matching Engine Unit Tests with Synthetic Fixtures
# ---------------------------------------------------------------------------

def test_matching_selects_latest_prior_to_cutoff_and_excludes_future():
    """Verifies:

    - Forecast published before cutoff is selected.
    - Forecast published exactly at cutoff is selected.
    - Forecast published AFTER cutoff is excluded.
    - Later eligible forecast supersedes earlier eligible forecast.
    """
    target_d = date(2026, 1, 10)
    cutoff_time = "12:00"  # Cutoff: 2026-01-09 12:00:00 UTC

    # Actuals for target day: 48 periods
    actuals_data = []
    for sp in range(1, 49):
        h = (sp - 1) // 2
        m = 30 if (sp % 2 == 0) else 0
        actuals_data.append({
            "start_time": datetime(2026, 1, 10, h, m, tzinfo=timezone.utc),
            "settlement_date": "2026-01-10",
            "settlement_period": sp,
            "fuel_type": "WIND",
            "generation_mw": 1000.0,
        })
    df_actuals = pd.DataFrame(actuals_data)

    # Forecasts for hour 0 (00:00 UTC):
    # Run 1: 2026-01-09 06:00 UTC -> 500 MW (eligible, but superseded)
    # Run 2: 2026-01-09 11:30 UTC -> 700 MW (eligible, LATEST before cutoff!)
    # Run 3: 2026-01-09 12:00 UTC -> 750 MW (exactly at cutoff! Should be selected over 11:30)
    # Run 4: 2026-01-09 14:00 UTC -> 900 MW (POST cutoff, MUST be excluded!)
    forecasts_data = [
        {
            "publish_time": datetime(2026, 1, 9, 6, 0, tzinfo=timezone.utc),
            "start_time": datetime(2026, 1, 10, 0, 0, tzinfo=timezone.utc),
            "generation_mw": 500.0,
        },
        {
            "publish_time": datetime(2026, 1, 9, 11, 30, tzinfo=timezone.utc),
            "start_time": datetime(2026, 1, 10, 0, 0, tzinfo=timezone.utc),
            "generation_mw": 700.0,
        },
        {
            "publish_time": datetime(2026, 1, 9, 12, 0, tzinfo=timezone.utc),
            "start_time": datetime(2026, 1, 10, 0, 0, tzinfo=timezone.utc),
            "generation_mw": 750.0,
        },
        {
            "publish_time": datetime(2026, 1, 9, 14, 0, tzinfo=timezone.utc),
            "start_time": datetime(2026, 1, 10, 0, 0, tzinfo=timezone.utc),
            "generation_mw": 900.0,
        },
    ]
    df_forecasts = pd.DataFrame(forecasts_data)

    periods, meta = ForecastMatchingService.match_day_for_date(
        df_actuals, df_forecasts, target_d, cutoff_time_str="12:00", cutoff_days_prior=1
    )

    # Check Period 1 and Period 2 (which correspond to Hour 0: 00:00 - 01:00 UTC)
    p1 = periods[0]
    p2 = periods[1]

    assert p1["settlement_period"] == 1
    assert p1["actual_generation_mw"] == 1000.0
    # Selected forecast should be the 12:00 UTC one (750.0 MW), NOT the post-cutoff 14:00 (900 MW)
    assert p1["forecast_generation_mw"] == 750.0
    assert p1["forecast_publish_time"] == datetime(2026, 1, 9, 12, 0, tzinfo=timezone.utc)
    assert p1["error_mw"] == 750.0 - 1000.0  # -250.0 MW

    # Both half-hours in Hour 0 get the same hourly forecast
    assert p2["settlement_period"] == 2
    assert p2["forecast_generation_mw"] == 750.0

    # Periods for hours with no forecast should have None
    p3 = periods[2]  # Hour 1
    assert p3["forecast_generation_mw"] is None
    assert p3["error_mw"] is None


def test_deterministic_tie_breaking():
    """If two forecast records share the exact same publish_time and target start_time."""
    target_d = date(2026, 1, 10)
    df_actuals = pd.DataFrame([{
        "start_time": datetime(2026, 1, 10, 0, 0, tzinfo=timezone.utc),
        "settlement_date": "2026-01-10",
        "settlement_period": 1,
        "fuel_type": "WIND",
        "generation_mw": 1000.0,
    }])
    df_forecasts = pd.DataFrame([
        {
            "publish_time": datetime(2026, 1, 9, 11, 0, tzinfo=timezone.utc),
            "start_time": datetime(2026, 1, 10, 0, 0, tzinfo=timezone.utc),
            "generation_mw": 600.0,
        },
        {
            "publish_time": datetime(2026, 1, 9, 11, 0, tzinfo=timezone.utc),
            "start_time": datetime(2026, 1, 10, 0, 0, tzinfo=timezone.utc),
            "generation_mw": 800.0,
        },
    ])

    periods1, _ = ForecastMatchingService.match_day_for_date(
        df_actuals, df_forecasts, target_d, cutoff_time_str="12:00", cutoff_days_prior=1
    )
    periods2, _ = ForecastMatchingService.match_day_for_date(
        df_actuals, df_forecasts, target_d, cutoff_time_str="12:00", cutoff_days_prior=1
    )

    assert periods1[0]["forecast_generation_mw"] == periods2[0]["forecast_generation_mw"]
    assert periods1[0]["forecast_generation_mw"] is not None


# ---------------------------------------------------------------------------
# Analytics Engine Mathematical Tests (Hand-Calculated Fixtures)
# ---------------------------------------------------------------------------

def test_analytics_mathematical_hand_calculated_fixture():
    """Known fixture with 4 observations:

    Actual:   [100, 200, 300, 400]
    Forecast: [110, 190, 330, 360]

    Errors:
    e1 = 110 - 100 = +10
    e2 = 190 - 200 = -10
    e3 = 330 - 300 = +30
    e4 = 360 - 400 = -40

    Absolute Errors: [10, 10, 30, 40]
    MAE = (10 + 10 + 30 + 40) / 4 = 90 / 4 = 22.50
    Squared Errors: [100, 100, 900, 1600] -> Mean = 2700 / 4 = 675.0
    RMSE = sqrt(675) = 25.98076... -> 25.98
    Mean Bias = (10 - 10 + 30 - 40) / 4 = -10 / 4 = -2.50
    Sum Actual = 100 + 200 + 300 + 400 = 1000
    WAPE = (90 / 1000) * 100 = 9.00%
    """
    obs = [
        {"actual_generation_mw": 100.0, "forecast_generation_mw": 110.0},
        {"actual_generation_mw": 200.0, "forecast_generation_mw": 190.0},
        {"actual_generation_mw": 300.0, "forecast_generation_mw": 330.0},
        {"actual_generation_mw": 400.0, "forecast_generation_mw": 360.0},
    ]

    metrics = calculate_error_metrics(obs)
    assert metrics.mae_mw == 22.50
    assert metrics.rmse_mw == 25.98
    assert metrics.mean_bias_mw == -2.50
    assert metrics.wape_percent == 9.00
    assert metrics.observations_count == 4
    assert metrics.missing_count == 0


def test_analytics_zero_actual_sum_protects_wape():
    """If actual sum is 0, WAPE should return None instead of dividing by zero."""
    obs = [
        {"actual_generation_mw": 0.0, "forecast_generation_mw": 10.0},
        {"actual_generation_mw": 0.0, "forecast_generation_mw": 20.0},
    ]
    metrics = calculate_error_metrics(obs)
    assert metrics.mae_mw == 15.0
    assert metrics.wape_percent is None


def test_analytics_missing_observations_are_excluded_not_zeroed():
    """Observations with None actual or None forecast must NOT be treated as 0 error."""
    obs = [
        {"actual_generation_mw": 100.0, "forecast_generation_mw": 120.0},  # err = 20
        {"actual_generation_mw": None, "forecast_generation_mw": 150.0},   # missing
        {"actual_generation_mw": 200.0, "forecast_generation_mw": None},   # missing
    ]
    metrics = calculate_error_metrics(obs)
    assert metrics.observations_count == 1
    assert metrics.missing_count == 2
    assert metrics.mae_mw == 20.0
    assert metrics.mean_bias_mw == 20.0


def test_analytics_empty_observations():
    metrics = calculate_error_metrics([])
    assert metrics.observations_count == 0
    assert metrics.missing_count == 0
    assert metrics.mae_mw is None
    assert metrics.rmse_mw is None


def test_second_level_cutoff_boundary_eligibility():
    """Ultra-granular regression test verifying:
    - 11:59:59 UTC (1 second before cutoff) is eligible.
    - 12:00:00 UTC (exactly at cutoff) is eligible.
    - 12:00:01 UTC (1 second after cutoff) is EXCLUDED.
    """
    target_d = date(2026, 1, 15)
    # Cutoff is D-1 12:00:00 UTC -> 2026-01-14 12:00:00 UTC
    df_actuals = pd.DataFrame([{
        "start_time": datetime(2026, 1, 15, 0, 0, tzinfo=timezone.utc),
        "settlement_date": "2026-01-15",
        "settlement_period": 1,
        "fuel_type": "WIND",
        "generation_mw": 5000.0,
    }])

    # 1. Test forecast published at 11:59:59 (eligible)
    df_fc_before = pd.DataFrame([{
        "publish_time": datetime(2026, 1, 14, 11, 59, 59, tzinfo=timezone.utc),
        "start_time": datetime(2026, 1, 15, 0, 0, tzinfo=timezone.utc),
        "generation_mw": 5200.0,
    }])
    p_before, _ = ForecastMatchingService.match_day_for_date(
        df_actuals, df_fc_before, target_d, cutoff_time_str="12:00:00", cutoff_days_prior=1
    )
    assert p_before[0]["forecast_generation_mw"] == 5200.0

    # 2. Test forecast published at 12:00:00 (eligible, exactly at cutoff)
    df_fc_exact = pd.DataFrame([{
        "publish_time": datetime(2026, 1, 14, 12, 0, 0, tzinfo=timezone.utc),
        "start_time": datetime(2026, 1, 15, 0, 0, tzinfo=timezone.utc),
        "generation_mw": 5300.0,
    }])
    p_exact, _ = ForecastMatchingService.match_day_for_date(
        df_actuals, df_fc_exact, target_d, cutoff_time_str="12:00:00", cutoff_days_prior=1
    )
    assert p_exact[0]["forecast_generation_mw"] == 5300.0

    # 3. Test forecast published at 12:00:01 (EXCLUDED, 1 second after cutoff)
    df_fc_after = pd.DataFrame([{
        "publish_time": datetime(2026, 1, 14, 12, 0, 1, tzinfo=timezone.utc),
        "start_time": datetime(2026, 1, 15, 0, 0, tzinfo=timezone.utc),
        "generation_mw": 5400.0,
    }])
    p_after, _ = ForecastMatchingService.match_day_for_date(
        df_actuals, df_fc_after, target_d, cutoff_time_str="12:00:00", cutoff_days_prior=1
    )
    assert p_after[0]["forecast_generation_mw"] is None
    assert p_after[0]["error_mw"] is None


def test_hourly_to_half_hourly_complete_mapping():
    """Verifies that all 24 clock hours map cleanly to 48 settlement periods

    without interpolation or distortion of values.
    """
    target_d = date(2026, 1, 20)
    actuals_list = []
    for sp in range(1, 49):
        h = (sp - 1) // 2
        m = 30 if (sp % 2 == 0) else 0
        actuals_list.append({
            "start_time": datetime(2026, 1, 20, h, m, tzinfo=timezone.utc),
            "settlement_date": "2026-01-20",
            "settlement_period": sp,
            "fuel_type": "WIND",
            "generation_mw": float(sp * 100),
        })
    df_actuals = pd.DataFrame(actuals_list)

    # 24 hourly forecasts
    forecasts_list = []
    for h in range(24):
        forecasts_list.append({
            "publish_time": datetime(2026, 1, 19, 11, 0, tzinfo=timezone.utc),
            "start_time": datetime(2026, 1, 20, h, 0, tzinfo=timezone.utc),
            "generation_mw": float(h * 250 + 1000),
        })
    df_forecasts = pd.DataFrame(forecasts_list)

    periods, meta = ForecastMatchingService.match_day_for_date(
        df_actuals, df_forecasts, target_d, cutoff_time_str="12:00", cutoff_days_prior=1
    )

    assert len(periods) == 48
    for sp in range(1, 49):
        h = (sp - 1) // 2
        expected_fc = float(h * 250 + 1000)
        expected_act = float(sp * 100)
        p = periods[sp - 1]
        assert p["settlement_period"] == sp
        assert p["forecast_generation_mw"] == expected_fc
        assert p["actual_generation_mw"] == expected_act
        assert p["error_mw"] == expected_fc - expected_act


def test_error_sign_convention_and_percentiles():
    """Validates:
    - error = forecast - actual (over-forecast > 0, under-forecast < 0)
    - P10, P50, P90 quantiles of signed error
    """
    # 5 observations
    # 1. Over-forecast: fc=1200, act=1000 -> err = +200
    # 2. Over-forecast: fc=1500, act=1000 -> err = +500
    # 3. Exact match: fc=1000, act=1000 -> err = 0
    # 4. Under-forecast: fc=800, act=1000 -> err = -200
    # 5. Under-forecast: fc=500, act=1000 -> err = -500
    obs = [
        {"actual_generation_mw": 1000.0, "forecast_generation_mw": 1200.0},
        {"actual_generation_mw": 1000.0, "forecast_generation_mw": 1500.0},
        {"actual_generation_mw": 1000.0, "forecast_generation_mw": 1000.0},
        {"actual_generation_mw": 1000.0, "forecast_generation_mw": 800.0},
        {"actual_generation_mw": 1000.0, "forecast_generation_mw": 500.0},
    ]
    metrics = calculate_error_metrics(obs)
    # Sorted errors: [-500, -200, 0, 200, 500]
    # Median / P50 should be 0.0
    assert metrics.p50_error_mw == 0.0
    # P10 should be negative (between -500 and -200)
    assert metrics.p10_error_mw < 0.0
    # P90 should be positive (between 200 and 500)
    assert metrics.p90_error_mw > 0.0
    # Mean bias should be 0.0
    assert metrics.mean_bias_mw == 0.0
    # MAE should be (500 + 200 + 0 + 200 + 500) / 5 = 280.0
    assert metrics.mae_mw == 280.0


def test_peak_offpeak_split():
    obs = [
        {"settlement_period": 10, "actual_generation_mw": 100.0, "forecast_generation_mw": 110.0},  # off-peak
        {"settlement_period": 20, "actual_generation_mw": 200.0, "forecast_generation_mw": 220.0},  # peak
        {"settlement_period": 30, "actual_generation_mw": 300.0, "forecast_generation_mw": 330.0},  # peak
        {"settlement_period": 45, "actual_generation_mw": 400.0, "forecast_generation_mw": 440.0},  # off-peak
    ]
    peak, offpeak = calculate_peak_offpeak_metrics(obs)
    assert peak.observations_count == 2
    assert offpeak.observations_count == 2
    assert peak.mae_mw == 25.0  # (|20| + |30|) / 2 = 25
    assert offpeak.mae_mw == 25.0  # (|10| + |40|) / 2 = 25


