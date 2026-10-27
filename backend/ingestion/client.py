"""HTTP Client for querying Elexon BMRS API with retries, timeouts, and rate-limit handling."""

import logging
import time
from typing import Any, Dict, List, Optional
import httpx

logger = logging.getLogger(__name__)


class ElexonAPIError(Exception):
    """Base exception for Elexon API failures."""
    pass


class ElexonRateLimitError(ElexonAPIError):
    """Raised when rate limit (HTTP 429) is hit."""
    pass


class ElexonClient:
    """Robust HTTP client for Elexon BMRS datasets."""

    def __init__(
        self,
        base_url: str = "https://data.elexon.co.uk/bmrs/api/v1",
        timeout_seconds: float = 30.0,
        max_retries: int = 3,
        backoff_factor: float = 1.0,
        transport: Optional[httpx.BaseTransport] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout_seconds
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self._transport = transport

    def _get_client(self) -> httpx.Client:
        headers = {
            "User-Agent": "Gridbricks-DAM-Forecast-App/1.0",
            "Accept": "application/json",
        }
        return httpx.Client(
            base_url=self.base_url,
            headers=headers,
            timeout=self.timeout,
            transport=self._transport,
        )

    def _request_with_retry(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Executes a GET request with bounded retries and exponential backoff."""
        attempt = 0
        last_exception: Optional[Exception] = None

        with self._get_client() as client:
            while attempt < self.max_retries:
                attempt += 1
                try:
                    logger.debug("Requesting %s with params %s (attempt %d/%d)", endpoint, params, attempt, self.max_retries)
                    resp = client.get(endpoint, params=params)

                    if resp.status_code == 200:
                        data = resp.json()
                        if isinstance(data, list):
                            return data
                        elif isinstance(data, dict) and "data" in data:
                            return data["data"]
                        else:
                            raise ElexonAPIError(f"Unexpected response structure from {endpoint}: {type(data)}")

                    elif resp.status_code == 429:
                        wait_time = self.backoff_factor * (2 ** (attempt - 1))
                        logger.warning("HTTP 429 Rate Limit hit. Retrying in %.1f seconds...", wait_time)
                        time.sleep(wait_time)
                        last_exception = ElexonRateLimitError(f"Rate limited on {endpoint} (HTTP 429)")

                    elif resp.status_code >= 500:
                        wait_time = self.backoff_factor * (2 ** (attempt - 1))
                        logger.warning("HTTP %d Server Error on %s. Retrying in %.1f seconds...", resp.status_code, endpoint, wait_time)
                        time.sleep(wait_time)
                        last_exception = ElexonAPIError(f"Server error {resp.status_code}: {resp.text[:200]}")

                    elif resp.status_code == 400:
                        raise ElexonAPIError(f"Bad Request (HTTP 400) on {endpoint}: {resp.text[:300]}")

                    else:
                        raise ElexonAPIError(f"Unexpected HTTP {resp.status_code} on {endpoint}: {resp.text[:200]}")

                except (httpx.TimeoutException, httpx.NetworkError) as exc:
                    wait_time = self.backoff_factor * (2 ** (attempt - 1))
                    logger.warning("Network/Timeout error on attempt %d: %s. Retrying in %.1f seconds...", attempt, exc, wait_time)
                    time.sleep(wait_time)
                    last_exception = exc

        raise ElexonAPIError(f"Failed to fetch {endpoint} after {self.max_retries} attempts: {last_exception}")

    def fetch_fuelhh_stream(
        self,
        settlement_date_from: str,
        settlement_date_to: str,
        fuel_type: str = "WIND",
    ) -> List[Dict[str, Any]]:
        """Fetches half-hourly actual generation for given settlement date range."""
        endpoint = "/datasets/FUELHH/stream"
        params = {
            "settlementDateFrom": settlement_date_from,
            "settlementDateTo": settlement_date_to,
            "fuelType": fuel_type,
        }
        return self._request_with_retry(endpoint, params=params)

    def fetch_windfor_stream(
        self,
        publish_datetime_from: str,
        publish_datetime_to: str,
    ) -> List[Dict[str, Any]]:
        """Fetches wind generation forecasts for given publish time range."""
        endpoint = "/datasets/WINDFOR/stream"
        params = {
            "publishDateTimeFrom": publish_datetime_from,
            "publishDateTimeTo": publish_datetime_to,
        }
        return self._request_with_retry(endpoint, params=params)
