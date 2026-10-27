"""Day-Ahead Forecast Matching Service.

Aligns historical Elexon WINDFOR forecasts with FUELHH actual generation
strictly enforcing pre-auction decision gate-closure cutoffs.
"""

from datetime import date, datetime, time, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd


def parse_cutoff_time(cutoff_str: str) -> time:
    """Parses HH:MM or HH:MM:SS string into a datetime.time object."""
    parts = [int(p) for p in cutoff_str.strip().split(":")]
    if len(parts) == 2:
        return time(hour=parts[0], minute=parts[1], second=0)
    elif len(parts) == 3:
        return time(hour=parts[0], minute=parts[1], second=parts[2])
    raise ValueError(f"Invalid cutoff time format: '{cutoff_str}'. Expected HH:MM or HH:MM:SS")


def calculate_cutoff_datetime(
    delivery_date: date,
    cutoff_time_str: str = "12:00",
    days_prior: int = 1,
) -> datetime:
    """Calculates timezone-aware UTC cutoff timestamp for decision making on D-days_prior."""
    parsed_time = parse_cutoff_time(cutoff_time_str)
    decision_date = delivery_date - timedelta(days=days_prior)
    return datetime(
        year=decision_date.year,
        month=decision_date.month,
        day=decision_date.day,
        hour=parsed_time.hour,
        minute=parsed_time.minute,
        second=parsed_time.second,
        tzinfo=timezone.utc,
    )


class ForecastMatchingService:
    """Matches delivery intervals to the latest valid forecast published before decision cutoff."""

    @staticmethod
    def match_day_for_date(
        actuals_df: pd.DataFrame,
        forecasts_df: pd.DataFrame,
        target_date: date,
        cutoff_time_str: str = "12:00",
        cutoff_days_prior: int = 1,
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Reconstructs the day-ahead forecast vs actual for all 48 settlement periods.

        Args:
            actuals_df: DataFrame containing FUELHH records.
            forecasts_df: DataFrame containing WINDFOR records.
            target_date: Target delivery date.
            cutoff_time_str: UTC cutoff time on D-cutoff_days_prior (default '12:00').
            cutoff_days_prior: Number of days prior to delivery (default 1 = D-1).

        Returns:
            Tuple of (list of period dicts, metadata dict).
        """
        cutoff_dt = calculate_cutoff_datetime(target_date, cutoff_time_str, cutoff_days_prior)
        date_str = target_date.isoformat()

        # 1. Filter actuals for the target delivery date
        day_actuals = actuals_df[actuals_df["settlement_date"] == date_str].copy()
        day_actuals = day_actuals.sort_values("settlement_period")

        # 2. Filter eligible forecasts published on or before the cutoff
        day_start = datetime(target_date.year, target_date.month, target_date.day, 0, 0, tzinfo=timezone.utc)
        day_end = datetime(target_date.year, target_date.month, target_date.day, 23, 59, 59, tzinfo=timezone.utc)

        eligible_forecasts = forecasts_df[
            (forecasts_df["publish_time"] <= cutoff_dt) &
            (forecasts_df["start_time"] >= day_start) &
            (forecasts_df["start_time"] <= day_end)
        ].copy()

        # 3. For each target delivery hour (0 to 23), select latest publication
        # Deterministic tie-breaking: sort by publish_time ascending, then generation_mw ascending
        matched_hourly: Dict[int, Dict[str, Any]] = {}
        if not eligible_forecasts.empty:
            sorted_candidates = eligible_forecasts.sort_values(
                by=["start_time", "publish_time", "generation_mw"],
                ascending=[True, True, True],
            )
            latest_per_target = sorted_candidates.groupby("start_time").last().reset_index()

            for _, row in latest_per_target.iterrows():
                target_hour = row["start_time"].hour
                matched_hourly[target_hour] = {
                    "publish_time": row["publish_time"],
                    "generation_mw": float(row["generation_mw"]),
                }

        # 4. Map to the 48 settlement periods
        period_results: List[Dict[str, Any]] = []
        actuals_by_sp = {
            r["settlement_period"]: r for _, r in day_actuals.iterrows()
        }

        for sp in range(1, 49):
            target_hour = (sp - 1) // 2
            target_minute = 30 if (sp % 2 == 0) else 0
            interval_start = day_start + timedelta(hours=target_hour, minutes=target_minute)

            actual_record = actuals_by_sp.get(sp)
            actual_mw = float(actual_record["generation_mw"]) if actual_record is not None else None

            forecast_info = matched_hourly.get(target_hour)
            forecast_mw = forecast_info["generation_mw"] if forecast_info else None
            forecast_pub = forecast_info["publish_time"] if forecast_info else None

            # Calculate errors if both are present
            if actual_mw is not None and forecast_mw is not None:
                error_mw = forecast_mw - actual_mw
                abs_error_mw = abs(error_mw)
            else:
                error_mw = None
                abs_error_mw = None

            period_results.append({
                "settlement_period": sp,
                "start_time": interval_start,
                "actual_generation_mw": actual_mw,
                "forecast_generation_mw": forecast_mw,
                "forecast_publish_time": forecast_pub,
                "error_mw": error_mw,
                "abs_error_mw": abs_error_mw,
            })

        metadata = {
            "delivery_date": date_str,
            "cutoff_time_utc": cutoff_dt,
            "cutoff_description": f"Latest forecast published <= {cutoff_dt.strftime('%Y-%m-%d %H:%M:%S UTC')} (D-{cutoff_days_prior} {cutoff_time_str} UTC)",
            "resolution": "half_hourly",
            "matched_hours_count": len(matched_hourly),
            "expected_hours_count": 24,
        }

        return period_results, metadata
