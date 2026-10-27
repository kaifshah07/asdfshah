"""Integration tests for FastAPI endpoints."""

from fastapi.testclient import TestClient
import pytest

from backend.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp_utc" in data
    assert data["version"] == "1.0.0"


def test_availability_endpoint():
    response = client.get("/api/wind/availability")
    assert response.status_code == 200
    data = response.json()
    assert data["min_date"] == "2026-01-01"
    assert data["max_date"] == "2026-01-31"
    assert data["total_actual_records"] == 1488
    assert data["total_forecast_records"] == 19856
    assert data["dataset_status"] == "ready"


def test_day_ahead_endpoint_valid():
    response = client.get("/api/wind/day-ahead?delivery_date=2026-01-15&cutoff_time=12:00")
    assert response.status_code == 200
    data = response.json()
    assert data["delivery_date"] == "2026-01-15"
    assert "cutoff_time_utc" in data
    assert data["resolution"] == "half_hourly"
    assert len(data["periods"]) == 48

    # Verify first period structure
    p1 = data["periods"][0]
    assert p1["settlement_period"] == 1
    assert "actual_generation_mw" in p1
    assert "forecast_generation_mw" in p1
    assert "error_mw" in p1
    assert "abs_error_mw" in p1

    # Verify metrics
    metrics = data["metrics"]
    assert metrics["observations_count"] == 48
    assert metrics["mae_mw"] is not None
    assert metrics["rmse_mw"] is not None
    assert metrics["mean_bias_mw"] is not None
    assert metrics["wape_percent"] is not None


def test_day_ahead_endpoint_invalid_date_format():
    response = client.get("/api/wind/day-ahead?delivery_date=15-01-2026")
    assert response.status_code == 422  # FastAPI regex validation fails


def test_day_ahead_endpoint_date_not_found():
    response = client.get("/api/wind/day-ahead?delivery_date=2025-05-01")
    assert response.status_code == 404
    assert "not found in cached dataset" in response.json()["detail"]


def test_analytics_endpoint_valid_range():
    response = client.get("/api/wind/analytics?start_date=2026-01-01&end_date=2026-01-07")
    assert response.status_code == 200
    data = response.json()
    assert data["start_date"] == "2026-01-01"
    assert data["end_date"] == "2026-01-07"
    assert data["overall_metrics"]["observations_count"] == 7 * 48
    assert data["overall_metrics"]["mae_mw"] > 0
    assert len(data["diurnal_profile"]) == 48
    assert len(data["daily_metrics"]) == 7


def test_analytics_endpoint_start_after_end():
    response = client.get("/api/wind/analytics?start_date=2026-01-20&end_date=2026-01-10")
    assert response.status_code == 400
    assert "start_date must be less than or equal to end_date" in response.json()["detail"]


def test_cors_preflight_and_headers():
    """Verify CORS preflight OPTIONS and response headers for allowed origins."""
    headers = {
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "GET",
    }
    response = client.options("/api/wind/availability", headers=headers)
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"

    # Test GET request with origin
    get_res = client.get("/health", headers={"Origin": "http://localhost:5173"})
    assert get_res.status_code == 200
    assert get_res.headers.get("access-control-allow-origin") == "http://localhost:5173"


def test_cors_origin_resolution_logic(monkeypatch):
    """Test get_allowed_origins parser under various environment variables."""
    from backend.main import get_allowed_origins, DEFAULT_CORS_ORIGINS

    # 1. Default (unset)
    monkeypatch.delenv("CORS_ALLOWED_ORIGINS", raising=False)
    assert get_allowed_origins() == DEFAULT_CORS_ORIGINS

    # 2. Wildcard
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "*")
    assert get_allowed_origins() == ["*"]

    # 3. Comma-separated Vercel origins
    monkeypatch.setenv(
        "CORS_ALLOWED_ORIGINS",
        "https://gridbricks.vercel.app, https://preview.vercel.app"
    )
    resolved = get_allowed_origins()
    assert "https://gridbricks.vercel.app" in resolved
    assert "https://preview.vercel.app" in resolved
    assert "http://localhost:3000" in resolved


def test_cors_unallowed_origin_rejected():
    """Verify unauthorized origin does not receive Access-Control-Allow-Origin header."""
    headers = {
        "Origin": "https://unauthorized-domain.com",
        "Access-Control-Request-Method": "GET",
    }
    response = client.options("/health", headers=headers)
    # When origin is not allowed, CORS middleware does not attach access-control-allow-origin
    assert "access-control-allow-origin" not in response.headers
