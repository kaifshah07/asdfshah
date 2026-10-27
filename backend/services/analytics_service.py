"""Statistical Forecast Error Analytics Engine.

Calculates standard forecast evaluation metrics: MAE, RMSE, Mean Bias Error (MBE),
WAPE, error distributions (P10/P50/P90), diurnal profiles, and peak/off-peak subsets.
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from backend.models.schemas import (
    DailyMetric,
    DiurnalPeriodMetric,
    ErrorMetrics,
)


def calculate_error_metrics(observations: List[Dict[str, Any]]) -> ErrorMetrics:
    """Calculates quantitative forecast error metrics from paired observations.

    Missing observations (None values) are strictly excluded from mathematical calculations
    and tracked in `missing_count`. Missing values are never silently treated as zero.
    """
    valid_pairs = [
        (obs["actual_generation_mw"], obs["forecast_generation_mw"])
        for obs in observations
        if obs.get("actual_generation_mw") is not None and obs.get("forecast_generation_mw") is not None
    ]

    total_count = len(observations)
    valid_count = len(valid_pairs)
    missing_count = total_count - valid_count

    if valid_count == 0:
        return ErrorMetrics(
            observations_count=0,
            missing_count=missing_count,
        )

    actuals = np.array([p[0] for p in valid_pairs], dtype=float)
    forecasts = np.array([p[1] for p in valid_pairs], dtype=float)

    errors = forecasts - actuals
    abs_errors = np.abs(errors)

    mae = float(np.mean(abs_errors))
    rmse = float(np.sqrt(np.mean(errors ** 2)))
    mean_bias = float(np.mean(errors))

    # WAPE: Sum(|Forecast - Actual|) / Sum(Actual)
    sum_actuals = float(np.sum(actuals))
    if sum_actuals > 0:
        wape = float((np.sum(abs_errors) / sum_actuals) * 100.0)
    else:
        wape = None  # Protect against division by zero

    # Percentiles of signed forecast error (P10, P50 / median, P90)
    p10 = float(np.percentile(errors, 10, method="linear"))
    p50 = float(np.percentile(errors, 50, method="linear"))
    p90 = float(np.percentile(errors, 90, method="linear"))

    return ErrorMetrics(
        mae_mw=round(mae, 2),
        rmse_mw=round(rmse, 2),
        mean_bias_mw=round(mean_bias, 2),
        wape_percent=round(wape, 2) if wape is not None else None,
        p10_error_mw=round(p10, 2),
        p50_error_mw=round(p50, 2),
        p90_error_mw=round(p90, 2),
        observations_count=valid_count,
        missing_count=missing_count,
    )


def calculate_diurnal_profile(observations: List[Dict[str, Any]]) -> List[DiurnalPeriodMetric]:
    """Calculates diurnal error profile across the 48 half-hour settlement periods."""
    from collections import defaultdict
    grouped = defaultdict(list)

    for obs in observations:
        sp = obs.get("settlement_period")
        act = obs.get("actual_generation_mw")
        fc = obs.get("forecast_generation_mw")
        if sp is not None and act is not None and fc is not None:
            grouped[sp].append((float(act), float(fc)))

    profile: List[DiurnalPeriodMetric] = []
    for sp in range(1, 49):
        hour = (sp - 1) // 2
        minute = 30 if (sp % 2 == 0) else 0
        time_label = f"{hour:02d}:{minute:02d}"

        pairs = grouped.get(sp, [])
        if pairs:
            act_arr = np.array([p[0] for p in pairs])
            fc_arr = np.array([p[1] for p in pairs])
            err_arr = fc_arr - act_arr
            abs_err_arr = np.abs(err_arr)

            profile.append(
                DiurnalPeriodMetric(
                    settlement_period=sp,
                    hour=hour,
                    time_label=time_label,
                    mean_actual_mw=round(float(np.mean(act_arr)), 2),
                    mean_forecast_mw=round(float(np.mean(fc_arr)), 2),
                    mean_bias_mw=round(float(np.mean(err_arr)), 2),
                    mae_mw=round(float(np.mean(abs_err_arr)), 2),
                    count=len(pairs),
                )
            )
        else:
            profile.append(
                DiurnalPeriodMetric(
                    settlement_period=sp,
                    hour=hour,
                    time_label=time_label,
                    count=0,
                )
            )

    return profile


def calculate_peak_offpeak_metrics(
    observations: List[Dict[str, Any]]
) -> Tuple[ErrorMetrics, ErrorMetrics]:
    """Splits observations into Peak (SP 15-38, 07:00-19:00 UTC) and Off-Peak subsets."""
    peak_obs = [obs for obs in observations if 15 <= obs.get("settlement_period", 0) <= 38]
    off_peak_obs = [obs for obs in observations if obs.get("settlement_period", 0) < 15 or obs.get("settlement_period", 0) > 38]

    return (
        calculate_error_metrics(peak_obs),
        calculate_error_metrics(off_peak_obs),
    )


def calculate_daily_metrics(observations: List[Dict[str, Any]]) -> List[DailyMetric]:
    """Calculates accuracy metrics aggregated per delivery date."""
    from collections import defaultdict
    grouped = defaultdict(list)

    for obs in observations:
        s_date = obs.get("settlement_date")
        if s_date:
            grouped[s_date].append(obs)

    daily_metrics: List[DailyMetric] = []
    for s_date in sorted(grouped.keys()):
        day_obs = grouped[s_date]
        metrics = calculate_error_metrics(day_obs)
        daily_metrics.append(
            DailyMetric(
                date=s_date,
                mae_mw=metrics.mae_mw,
                rmse_mw=metrics.rmse_mw,
                mean_bias_mw=metrics.mean_bias_mw,
                wape_percent=metrics.wape_percent,
                observations_count=metrics.observations_count,
            )
        )

    return daily_metrics
