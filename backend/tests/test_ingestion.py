"""Unit tests for Elexon BMRS ingestion client, models, and normalization pipeline."""

from datetime import date, datetime, timezone
from pathlib import Path
import json
import httpx
import pytest
from pydantic import ValidationError

from backend.ingestion.client import ElexonClient, ElexonAPIError, ElexonRateLimitError
from backend.ingestion.models import (
    NormalizedActual,
    NormalizedForecast,
    RawFuelHHRecord,
    RawWindforRecord,
)
from backend.ingestion.pipeline import IngestionPipeline, parse_utc_timestamp


# ---------------------------------------------------------------------------
# Client Tests (using Mock Transport)
# ---------------------------------------------------------------------------

def test_client_successful_list_response():
    sample_payload = [
        {
            "dataset": "FUELHH",
            "publishTime": "2026-01-01T00:30:00Z",
            "startTime": "2026-01-01T00:00:00Z",
            "settlementDate": "2026-01-01",
            "settlementPeriod": 1,
            "fuelType": "WIND",
            "generation": 12500,
        }
    ]

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=sample_payload)

    transport = httpx.MockTransport(handler)
    client = ElexonClient(transport=transport)
    result = client.fetch_fuelhh_stream("2026-01-01", "2026-01-01")
    assert len(result) == 1
    assert result[0]["fuelType"] == "WIND"
    assert result[0]["generation"] == 12500


def test_client_dict_with_data_key():
    sample_payload = {
        "data": [
            {
                "dataset": "WINDFOR",
                "publishTime": "2025-12-31T11:30:00Z",
                "startTime": "2026-01-01T00:00:00Z",
                "generation": 11000,
            }
        ]
    }

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=sample_payload)

    transport = httpx.MockTransport(handler)
    client = ElexonClient(transport=transport)
    result = client.fetch_windfor_stream("2025-12-31T00:00:00Z", "2025-12-31T12:00:00Z")
    assert len(result) == 1
    assert result[0]["generation"] == 11000


def test_client_empty_response():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=[])

    transport = httpx.MockTransport(handler)
    client = ElexonClient(transport=transport)
    result = client.fetch_fuelhh_stream("2026-01-01", "2026-01-01")
    assert result == []


def test_client_malformed_response_type():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="12345")

    transport = httpx.MockTransport(handler)
    client = ElexonClient(transport=transport, max_retries=1)
    with pytest.raises(ElexonAPIError) as exc_info:
        client.fetch_fuelhh_stream("2026-01-01", "2026-01-01")
    assert "Unexpected response structure" in str(exc_info.value)


def test_client_http_400_bad_request():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, text="Invalid settlementDate format")

    transport = httpx.MockTransport(handler)
    client = ElexonClient(transport=transport, max_retries=1)
    with pytest.raises(ElexonAPIError) as exc_info:
        client.fetch_fuelhh_stream("bad-date", "bad-date")
    assert "Bad Request (HTTP 400)" in str(exc_info.value)


def test_client_retry_on_429_then_succeed():
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            return httpx.Response(429, text="Too Many Requests")
        return httpx.Response(200, json=[{"test": "ok"}])

    transport = httpx.MockTransport(handler)
    client = ElexonClient(transport=transport, max_retries=3, backoff_factor=0.01)
    res = client._request_with_retry("/test")
    assert attempts == 2
    assert res == [{"test": "ok"}]


def test_client_exhausts_retries_on_500():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="Internal Server Error")

    transport = httpx.MockTransport(handler)
    client = ElexonClient(transport=transport, max_retries=2, backoff_factor=0.01)
    with pytest.raises(ElexonAPIError) as exc_info:
        client._request_with_retry("/test")
    assert "Failed to fetch" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Model Validation Tests
# ---------------------------------------------------------------------------

def test_raw_fuelhh_valid():
    rec = RawFuelHHRecord(
        dataset="FUELHH",
        publishTime="2026-01-01T00:30:00Z",
        startTime="2026-01-01T00:00:00Z",
        settlementDate="2026-01-01",
        settlementPeriod=1,
        fuelType="WIND",
        generation=15000,
    )
    assert rec.settlementPeriod == 1
    assert rec.generation == 15000


def test_raw_fuelhh_invalid_settlement_period():
    with pytest.raises(ValidationError):
        RawFuelHHRecord(
            startTime="2026-01-01T00:00:00Z",
            settlementDate="2026-01-01",
            settlementPeriod=55,  # Out of range 1-50
            fuelType="WIND",
        )


def test_raw_windfor_valid():
    rec = RawWindforRecord(
        publishTime="2025-12-31T11:30:00Z",
        startTime="2026-01-01T00:00:00Z",
        generation=14200,
    )
    assert rec.publishTime == "2025-12-31T11:30:00Z"
    assert rec.generation == 14200


# ---------------------------------------------------------------------------
# Timestamp Normalization Tests
# ---------------------------------------------------------------------------

def test_parse_utc_timestamp_with_z():
    ts = "2026-01-01T12:00:00Z"
    dt = parse_utc_timestamp(ts)
    assert dt.tzinfo == timezone.utc
    assert dt.hour == 12
    assert dt.day == 1


def test_parse_utc_timestamp_naive():
    ts = "2026-01-01T12:00:00"
    dt = parse_utc_timestamp(ts)
    assert dt.tzinfo == timezone.utc
    assert dt.hour == 12


def test_normalized_models_ensure_utc():
    naive_dt = datetime(2026, 1, 1, 12, 0)
    actual = NormalizedActual(
        start_time=naive_dt,
        settlement_date=date(2026, 1, 1),
        settlement_period=25,
        generation_mw=8500.0,
    )
    assert actual.start_time.tzinfo == timezone.utc


# ---------------------------------------------------------------------------
# Ingestion Pipeline Tests
# ---------------------------------------------------------------------------

def test_pipeline_deduplication(tmp_path: Path):
    duplicate_payload = [
        {
            "dataset": "FUELHH",
            "publishTime": "2026-01-01T00:30:00Z",
            "startTime": "2026-01-01T00:00:00Z",
            "settlementDate": "2026-01-01",
            "settlementPeriod": 1,
            "fuelType": "WIND",
            "generation": 10000,
        },
        {
            "dataset": "FUELHH",
            "publishTime": "2026-01-01T00:30:00Z",
            "startTime": "2026-01-01T00:00:00Z",
            "settlementDate": "2026-01-01",
            "settlementPeriod": 1,
            "fuelType": "WIND",
            "generation": 10000,
        },
    ]

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=duplicate_payload)

    transport = httpx.MockTransport(handler)
    client = ElexonClient(transport=transport)
    pipeline = IngestionPipeline(client=client, data_dir=tmp_path)

    actuals, report = pipeline.run_actuals_ingestion("2026-01-01", "2026-01-01")
    assert len(actuals) == 1
    assert report["raw_records_fetched"] == 2
    assert report["duplicates_removed"] == 1
    assert report["valid_normalized_records"] == 1


def test_pipeline_invalid_records_skipped(tmp_path: Path):
    mixed_payload = [
        {
            "dataset": "FUELHH",
            "startTime": "2026-01-01T00:00:00Z",
            "settlementDate": "2026-01-01",
            "settlementPeriod": 1,
            "fuelType": "WIND",
            "generation": 12000,
        },
        {
            "dataset": "FUELHH",
            "startTime": "2026-01-01T00:30:00Z",
            "settlementDate": "2026-01-01",
            "settlementPeriod": 999,  # Invalid period
            "fuelType": "WIND",
            "generation": 12000,
        },
    ]

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=mixed_payload)

    transport = httpx.MockTransport(handler)
    client = ElexonClient(transport=transport)
    pipeline = IngestionPipeline(client=client, data_dir=tmp_path)

    actuals, report = pipeline.run_actuals_ingestion("2026-01-01", "2026-01-01")
    assert len(actuals) == 1
    assert report["validation_errors"] == 1
    assert report["valid_normalized_records"] == 1


def test_pipeline_idempotence(tmp_path: Path):
    sample_payload = [
        {
            "dataset": "FUELHH",
            "startTime": "2026-01-01T00:00:00Z",
            "settlementDate": "2026-01-01",
            "settlementPeriod": 1,
            "fuelType": "WIND",
            "generation": 10000,
        }
    ]

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=sample_payload)

    transport = httpx.MockTransport(handler)
    client = ElexonClient(transport=transport)
    pipeline = IngestionPipeline(client=client, data_dir=tmp_path)

    # First run
    actuals_1, report_1 = pipeline.run_actuals_ingestion("2026-01-01", "2026-01-01")
    # Second run
    actuals_2, report_2 = pipeline.run_actuals_ingestion("2026-01-01", "2026-01-01")

    assert len(actuals_1) == len(actuals_2) == 1
    assert report_1["valid_normalized_records"] == report_2["valid_normalized_records"] == 1
    # Check output files exist and are not corrupted
    assert (tmp_path / "normalized" / "actuals_jan2026.parquet").exists()
    assert (tmp_path / "normalized" / "actuals_jan2026.json").exists()
