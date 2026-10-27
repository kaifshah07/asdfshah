/**
 * TypeScript definitions matching FastAPI backend schemas exactly.
 */

export interface HealthResponse {
  status: string;
  timestamp_utc: string;
  version: string;
}

export interface AvailabilityResponse {
  min_date: string;
  max_date: string;
  total_actual_records: number;
  total_forecast_records: number;
  distinct_publish_runs: number;
  dataset_status: string;
}

export interface SettlementPeriodForecast {
  settlement_period: number;
  start_time: string;
  actual_generation_mw: number | null;
  forecast_generation_mw: number | null;
  forecast_publish_time: string | null;
  error_mw: number | null;
  abs_error_mw: number | null;
}

export interface ErrorMetrics {
  mae_mw: number | null;
  rmse_mw: number | null;
  mean_bias_mw: number | null;
  wape_percent: number | null;
  p10_error_mw: number | null;
  p50_error_mw: number | null;
  p90_error_mw: number | null;
  observations_count: number;
  missing_count: number;
}

export interface DayAheadComparisonResponse {
  delivery_date: string;
  cutoff_time_utc: string;
  cutoff_description: string;
  resolution: string;
  periods: SettlementPeriodForecast[];
  metrics: ErrorMetrics;
}

export interface DiurnalPeriodMetric {
  settlement_period: number;
  hour: number;
  time_label: string;
  mean_actual_mw: number | null;
  mean_forecast_mw: number | null;
  mean_bias_mw: number | null;
  mae_mw: number | null;
  count: number;
}

export interface DailyMetric {
  date: string;
  mae_mw: number | null;
  rmse_mw: number | null;
  mean_bias_mw: number | null;
  wape_percent: number | null;
  observations_count: number;
}

export interface AnalyticsResponse {
  start_date: string;
  end_date: string;
  cutoff_time_utc: string;
  overall_metrics: ErrorMetrics;
  peak_metrics: ErrorMetrics;
  off_peak_metrics: ErrorMetrics;
  diurnal_profile: DiurnalPeriodMetric[];
  daily_metrics: DailyMetric[];
}

export interface FilterParams {
  deliveryDate: string;
  startDate: string;
  endDate: string;
  cutoffTime: string;
  cutoffDaysPrior: number;
}
