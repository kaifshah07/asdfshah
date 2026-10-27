"""FastAPI REST routes for UK wind generation forecast and decision support."""

from datetime import date, datetime, timezone
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.models.schemas import (
    AnalyticsResponse,
    AvailabilityResponse,
    DayAheadComparisonResponse,
    HealthResponse,
    SettlementPeriodForecast,
)
from backend.services.analytics_service import (
    calculate_daily_metrics,
    calculate_diurnal_profile,
    calculate_error_metrics,
    calculate_peak_offpeak_metrics,
)
from backend.services.data_loader import DataLoader, DataNotFoundError
from backend.services.matching_service import ForecastMatchingService

logger = logging.getLogger(__name__)

router = APIRouter()

# Global loader instance
_data_loader: Optional[DataLoader] = None


def get_data_loader() -> DataLoader:
    global _data_loader
    if _data_loader is None:
        _data_loader = DataLoader()
    return _data_loader


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Service Health Check",
    tags=["System"],
)
def get_health() -> HealthResponse:
    """Returns the operational status and timestamp of the API."""
    return HealthResponse(
        status="healthy",
        timestamp_utc=datetime.now(timezone.utc),
        version="1.0.0",
    )


@router.get(
    "/api/wind/availability",
    response_model=AvailabilityResponse,
    summary="Data Coverage & Availability",
    tags=["Wind Generation"],
)
def get_availability(
    loader: DataLoader = Depends(get_data_loader),
) -> AvailabilityResponse:
    """Returns the temporal boundaries and record counts available in the local cache."""
    try:
        summary = loader.get_availability_summary()
        return AvailabilityResponse(**summary)
    except DataNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Data cache unavailable: {str(e)}",
        )


@router.get(
    "/api/wind/day-ahead",
    response_model=DayAheadComparisonResponse,
    summary="Day-Ahead Wind Forecast vs Actual Comparison",
    tags=["Wind Generation"],
)
def get_day_ahead_comparison(
    delivery_date: str = Query("2026-01-15", description="Target delivery date (YYYY-MM-DD)", pattern=r"^\d{4}-\d{2}-\d{2}$"),
    cutoff_time: str = Query("12:00", description="Cutoff time in UTC (HH:MM)", pattern=r"^\d{2}:\d{2}(:\d{2})?$"),
    cutoff_days_prior: int = Query(1, ge=0, le=7, description="Decision days prior to delivery (default 1 = D-1)"),
    loader: DataLoader = Depends(get_data_loader),
) -> DayAheadComparisonResponse:
    """Reconstructs the pre-auction Day-Ahead wind forecast available at decision cutoff

    and compares it against actual generation across all 48 settlement periods.
    """
    try:
        target_d = date.fromisoformat(delivery_date)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid date format: '{delivery_date}'. Use YYYY-MM-DD.")

    try:
        actuals_df = loader.get_actuals_df()
        forecasts_df = loader.get_forecasts_df()
    except DataNotFoundError as e:
        raise HTTPException(status_code=503, detail=f"Data cache error: {str(e)}")

    # Validate date range
    available_dates = set(actuals_df["settlement_date"].unique())
    if delivery_date not in available_dates:
        raise HTTPException(
            status_code=404,
            detail=f"Delivery date '{delivery_date}' not found in cached dataset. Available range: {min(available_dates)} to {max(available_dates)}.",
        )

    try:
        periods_data, metadata = ForecastMatchingService.match_day_for_date(
            actuals_df=actuals_df,
            forecasts_df=forecasts_df,
            target_date=target_d,
            cutoff_time_str=cutoff_time,
            cutoff_days_prior=cutoff_days_prior,
        )
    except Exception as e:
        logger.error("Error matching day-ahead forecasts for %s: %s", delivery_date, e)
        raise HTTPException(status_code=500, detail="Error reconstructing day-ahead forecasts.")

    # Calculate day accuracy metrics
    metrics = calculate_error_metrics(periods_data)
    period_models = [SettlementPeriodForecast(**p) for p in periods_data]

    return DayAheadComparisonResponse(
        delivery_date=metadata["delivery_date"],
        cutoff_time_utc=metadata["cutoff_time_utc"],
        cutoff_description=metadata["cutoff_description"],
        resolution=metadata["resolution"],
        periods=period_models,
        metrics=metrics,
    )


@router.get(
    "/api/wind/analytics",
    response_model=AnalyticsResponse,
    summary="Forecast Error Analytics & Performance Summary",
    tags=["Analytics"],
)
def get_analytics(
    start_date: str = Query("2026-01-01", description="Start date (YYYY-MM-DD)", pattern=r"^\d{4}-\d{2}-\d{2}$"),
    end_date: str = Query("2026-01-31", description="End date (YYYY-MM-DD)", pattern=r"^\d{4}-\d{2}-\d{2}$"),
    cutoff_time: str = Query("12:00", description="Cutoff time in UTC (HH:MM)", pattern=r"^\d{2}:\d{2}(:\d{2})?$"),
    cutoff_days_prior: int = Query(1, ge=0, le=7, description="Decision days prior to delivery (default 1 = D-1)"),
    loader: DataLoader = Depends(get_data_loader),
) -> AnalyticsResponse:
    """Calculates comprehensive quantitative forecast error analytics (MAE, RMSE, Bias,

    WAPE, P10/P50/P90, diurnal profiles, and peak/off-peak subsets) across the requested period.
    """
    try:
        s_date = date.fromisoformat(start_date)
        e_date = date.fromisoformat(end_date)
        if s_date > e_date:
            raise HTTPException(status_code=400, detail="start_date must be less than or equal to end_date")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    try:
        actuals_df = loader.get_actuals_df()
        forecasts_df = loader.get_forecasts_df()
    except DataNotFoundError as e:
        raise HTTPException(status_code=503, detail=f"Data cache error: {str(e)}")

    available_dates = set(actuals_df["settlement_date"].unique())
    all_observations = []

    # Iterate over requested date range
    from datetime import timedelta
    cur_date = s_date
    while cur_date <= e_date:
        cur_date_str = cur_date.isoformat()
        if cur_date_str in available_dates:
            day_periods, _ = ForecastMatchingService.match_day_for_date(
                actuals_df=actuals_df,
                forecasts_df=forecasts_df,
                target_date=cur_date,
                cutoff_time_str=cutoff_time,
                cutoff_days_prior=cutoff_days_prior,
            )
            # Inject settlement_date for aggregation
            for p in day_periods:
                p["settlement_date"] = cur_date_str
            all_observations.extend(day_periods)
        cur_date += timedelta(days=1)

    if not all_observations:
        raise HTTPException(
            status_code=404,
            detail=f"No data available for date range {start_date} to {end_date}.",
        )

    overall_metrics = calculate_error_metrics(all_observations)
    peak_metrics, off_peak_metrics = calculate_peak_offpeak_metrics(all_observations)
    diurnal_profile = calculate_diurnal_profile(all_observations)
    daily_metrics = calculate_daily_metrics(all_observations)

    return AnalyticsResponse(
        start_date=start_date,
        end_date=end_date,
        cutoff_time_utc=f"D-{cutoff_days_prior} {cutoff_time} UTC",
        overall_metrics=overall_metrics,
        peak_metrics=peak_metrics,
        off_peak_metrics=off_peak_metrics,
        diurnal_profile=diurnal_profile,
        daily_metrics=daily_metrics,
    )
