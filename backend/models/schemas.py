"""API Pydantic Schemas for Request and Response models."""

from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    timestamp_utc: datetime
    version: str = "1.0.0"


class AvailabilityResponse(BaseModel):
    """Available date ranges and cache status."""
    min_date: str = Field(..., description="Earliest available delivery date (YYYY-MM-DD)")
    max_date: str = Field(..., description="Latest available delivery date (YYYY-MM-DD)")
    total_actual_records: int = Field(..., description="Number of half-hourly actuals")
    total_forecast_records: int = Field(..., description="Number of forecast data points")
    distinct_publish_runs: int = Field(..., description="Number of distinct forecast runs")
    dataset_status: str = Field("ready", description="Status of the local data cache")


class SettlementPeriodForecast(BaseModel):
    """Single settlement period (30-min) observation."""
    settlement_period: int = Field(..., ge=1, le=50, description="Settlement period (1-48)")
    start_time: datetime = Field(..., description="Interval start time in UTC")
    actual_generation_mw: Optional[float] = Field(None, description="Actual wind generation (MW)")
    forecast_generation_mw: Optional[float] = Field(None, description="Day-ahead forecasted wind generation (MW)")
    forecast_publish_time: Optional[datetime] = Field(None, description="Timestamp when forecast was published")
    error_mw: Optional[float] = Field(None, description="Forecast - Actual (signed MW)")
    abs_error_mw: Optional[float] = Field(None, description="Absolute error |Forecast - Actual| (MW)")


class ErrorMetrics(BaseModel):
    """Quantitative forecast accuracy metrics."""
    mae_mw: Optional[float] = Field(None, description="Mean Absolute Error (MW)")
    rmse_mw: Optional[float] = Field(None, description="Root Mean Square Error (MW)")
    mean_bias_mw: Optional[float] = Field(None, description="Mean Bias Error (MW), positive indicates over-forecasting")
    wape_percent: Optional[float] = Field(None, description="Weighted Absolute Percentage Error (%)")
    p10_error_mw: Optional[float] = Field(None, description="10th percentile of signed error (MW)")
    p50_error_mw: Optional[float] = Field(None, description="50th percentile / median of signed error (MW)")
    p90_error_mw: Optional[float] = Field(None, description="90th percentile of signed error (MW)")
    observations_count: int = Field(..., description="Number of valid aligned pairs evaluated")
    missing_count: int = Field(0, description="Number of intervals missing actual or forecast data")


class DayAheadComparisonResponse(BaseModel):
    """Day-ahead forecast vs actual comparison response for a single delivery day."""
    delivery_date: str = Field(..., description="Delivery date (YYYY-MM-DD)")
    cutoff_time_utc: datetime = Field(..., description="Decision cutoff timestamp in UTC")
    cutoff_description: str = Field(..., description="Description of decision cutoff logic applied")
    resolution: str = Field("half_hourly", description="Data resolution (30-min settlement periods)")
    periods: List[SettlementPeriodForecast] = Field(..., description="48 half-hour settlement periods")
    metrics: ErrorMetrics = Field(..., description="Day accuracy metrics")


class DiurnalPeriodMetric(BaseModel):
    """Diurnal accuracy profile across a specific settlement period (1-48)."""
    settlement_period: int = Field(..., description="Settlement period (1-48)")
    hour: int = Field(..., description="Clock hour (0-23)")
    time_label: str = Field(..., description="Human-readable half-hour label e.g. 09:30")
    mean_actual_mw: Optional[float] = None
    mean_forecast_mw: Optional[float] = None
    mean_bias_mw: Optional[float] = None
    mae_mw: Optional[float] = None
    count: int = 0


class DailyMetric(BaseModel):
    """Accuracy metrics for a specific delivery date."""
    date: str
    mae_mw: Optional[float]
    rmse_mw: Optional[float]
    mean_bias_mw: Optional[float]
    wape_percent: Optional[float]
    observations_count: int


class AnalyticsResponse(BaseModel):
    """Comprehensive analytical response for a date range."""
    start_date: str
    end_date: str
    cutoff_time_utc: str
    overall_metrics: ErrorMetrics
    peak_metrics: ErrorMetrics
    off_peak_metrics: ErrorMetrics
    diurnal_profile: List[DiurnalPeriodMetric]
    daily_metrics: List[DailyMetric]
