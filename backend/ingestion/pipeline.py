"""Data ingestion and normalization pipeline for Elexon BMRS datasets."""

import json
import logging
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple
import pandas as pd
from pydantic import ValidationError

from backend.ingestion.client import ElexonClient
from backend.ingestion.models import (
    NormalizedActual,
    NormalizedForecast,
    RawFuelHHRecord,
    RawWindforRecord,
)

logger = logging.getLogger(__name__)


def parse_utc_timestamp(ts_str: str) -> datetime:
    """Parses an ISO timestamp string into a timezone-aware UTC datetime."""
    # Replace Z with +00:00 if needed for standard fromisoformat
    clean_ts = ts_str.replace("Z", "+00:00")
    dt = datetime.fromisoformat(clean_ts)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


class IngestionPipeline:
    """Orchestrates data fetching, raw caching, validation, normalization, and quality checks."""

    def __init__(
        self,
        client: ElexonClient,
        data_dir: Path,
    ):
        self.client = client
        self.data_dir = data_dir
        self.raw_dir = data_dir / "raw"
        self.norm_dir = data_dir / "normalized"
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.norm_dir.mkdir(parents=True, exist_ok=True)

    def run_actuals_ingestion(
        self,
        settlement_date_from: str = "2026-01-01",
        settlement_date_to: str = "2026-01-31",
        fuel_type: str = "WIND",
    ) -> Tuple[List[NormalizedActual], Dict[str, Any]]:
        """Fetches, caches, validates, and normalizes FUELHH actuals."""
        logger.info("Starting FUELHH ingestion from %s to %s", settlement_date_from, settlement_date_to)
        raw_data = self.client.fetch_fuelhh_stream(
            settlement_date_from=settlement_date_from,
            settlement_date_to=settlement_date_to,
            fuel_type=fuel_type,
        )

        # 1. Preserve raw cache
        raw_file = self.raw_dir / f"fuelhh_{settlement_date_from}_{settlement_date_to}.json"
        with open(raw_file, "w", encoding="utf-8") as f:
            json.dump(raw_data, f, indent=2)
        logger.info("Preserved %d raw FUELHH records at %s", len(raw_data), raw_file)

        # 2. Validate and normalize
        normalized: List[NormalizedActual] = []
        validation_errors = 0
        duplicates = 0
        seen_keys = set()

        for raw_item in raw_data:
            try:
                rec = RawFuelHHRecord.model_validate(raw_item)
                start_dt = parse_utc_timestamp(rec.startTime)
                s_date = date.fromisoformat(rec.settlementDate)
                gen_mw = float(rec.generation if rec.generation is not None else 0.0)

                key = (s_date, rec.settlementPeriod)
                if key in seen_keys:
                    duplicates += 1
                    continue
                seen_keys.add(key)

                norm_record = NormalizedActual(
                    start_time=start_dt,
                    settlement_date=s_date,
                    settlement_period=rec.settlementPeriod,
                    fuel_type=rec.fuelType,
                    generation_mw=gen_mw,
                )
                normalized.append(norm_record)
            except (ValidationError, ValueError, KeyError) as err:
                validation_errors += 1
                logger.warning("Skipping invalid FUELHH record: %s. Error: %s", raw_item, err)

        # Sort chronologically
        normalized.sort(key=lambda x: (x.settlement_date, x.settlement_period))

        # 3. Export normalized formats (Parquet + JSON)
        df_records = [
            {
                "start_time": r.start_time,
                "settlement_date": r.settlement_date.isoformat(),
                "settlement_period": r.settlement_period,
                "fuel_type": r.fuel_type,
                "generation_mw": r.generation_mw,
            }
            for r in normalized
        ]
        df = pd.DataFrame(df_records)
        parquet_file = self.norm_dir / "actuals_jan2026.parquet"
        json_file = self.norm_dir / "actuals_jan2026.json"

        if not df.empty:
            df.to_parquet(parquet_file, index=False)
            df.to_json(json_file, orient="records", date_format="iso", indent=2)

        # 4. Data quality metrics
        report = {
            "dataset": "FUELHH",
            "fuel_type": fuel_type,
            "date_range": [settlement_date_from, settlement_date_to],
            "raw_records_fetched": len(raw_data),
            "valid_normalized_records": len(normalized),
            "duplicates_removed": duplicates,
            "validation_errors": validation_errors,
            "distinct_settlement_dates": len(set(r.settlement_date for r in normalized)),
            "min_generation_mw": min((r.generation_mw for r in normalized), default=None),
            "max_generation_mw": max((r.generation_mw for r in normalized), default=None),
            "mean_generation_mw": (
                sum(r.generation_mw for r in normalized) / len(normalized) if normalized else None
            ),
            "parquet_saved": str(parquet_file),
            "json_saved": str(json_file),
        }
        return normalized, report

    def run_forecasts_ingestion(
        self,
        publish_datetime_from: str = "2025-12-30T00:00:00Z",
        publish_datetime_to: str = "2026-02-01T23:59:59Z",
    ) -> Tuple[List[NormalizedForecast], Dict[str, Any]]:
        """Fetches, caches, validates, and normalizes WINDFOR forecasts."""
        logger.info("Starting WINDFOR ingestion from %s to %s", publish_datetime_from, publish_datetime_to)
        raw_data = self.client.fetch_windfor_stream(
            publish_datetime_from=publish_datetime_from,
            publish_datetime_to=publish_datetime_to,
        )

        # 1. Preserve raw cache
        raw_file = self.raw_dir / "windfor_jan2026.json"
        with open(raw_file, "w", encoding="utf-8") as f:
            json.dump(raw_data, f, indent=2)
        logger.info("Preserved %d raw WINDFOR records at %s", len(raw_data), raw_file)

        # 2. Validate and normalize
        normalized: List[NormalizedForecast] = []
        validation_errors = 0
        duplicates = 0
        seen_keys = set()

        for raw_item in raw_data:
            try:
                rec = RawWindforRecord.model_validate(raw_item)
                pub_dt = parse_utc_timestamp(rec.publishTime)
                start_dt = parse_utc_timestamp(rec.startTime)
                gen_mw = float(rec.generation if rec.generation is not None else 0.0)

                key = (pub_dt, start_dt)
                if key in seen_keys:
                    duplicates += 1
                    continue
                seen_keys.add(key)

                norm_record = NormalizedForecast(
                    publish_time=pub_dt,
                    start_time=start_dt,
                    generation_mw=gen_mw,
                )
                normalized.append(norm_record)
            except (ValidationError, ValueError, KeyError) as err:
                validation_errors += 1
                logger.warning("Skipping invalid WINDFOR record: %s. Error: %s", raw_item, err)

        # Sort chronologically by publish_time, then start_time
        normalized.sort(key=lambda x: (x.publish_time, x.start_time))

        # 3. Export normalized formats (Parquet + JSON)
        df_records = [
            {
                "publish_time": r.publish_time,
                "start_time": r.start_time,
                "generation_mw": r.generation_mw,
            }
            for r in normalized
        ]
        df = pd.DataFrame(df_records)
        parquet_file = self.norm_dir / "forecasts_jan2026.parquet"
        json_file = self.norm_dir / "forecasts_jan2026.json"

        if not df.empty:
            df.to_parquet(parquet_file, index=False)
            df.to_json(json_file, orient="records", date_format="iso", indent=2)

        # 4. Data quality metrics
        pub_times = set(r.publish_time for r in normalized)
        target_times = set(r.start_time for r in normalized)

        report = {
            "dataset": "WINDFOR",
            "publish_range": [publish_datetime_from, publish_datetime_to],
            "raw_records_fetched": len(raw_data),
            "valid_normalized_records": len(normalized),
            "duplicates_removed": duplicates,
            "validation_errors": validation_errors,
            "distinct_publish_runs": len(pub_times),
            "distinct_target_start_times": len(target_times),
            "earliest_publish_time": min(pub_times).isoformat() if pub_times else None,
            "latest_publish_time": max(pub_times).isoformat() if pub_times else None,
            "earliest_target_time": min(target_times).isoformat() if target_times else None,
            "latest_target_time": max(target_times).isoformat() if target_times else None,
            "parquet_saved": str(parquet_file),
            "json_saved": str(json_file),
        }
        return normalized, report
