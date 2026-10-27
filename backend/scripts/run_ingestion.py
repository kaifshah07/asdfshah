"""CLI execution script to run the Elexon BMRS data ingestion pipeline."""

import json
import logging
import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

from backend.ingestion.client import ElexonClient
from backend.ingestion.pipeline import IngestionPipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("run_ingestion")


def main():
    data_dir = root_dir / "data"
    client = ElexonClient()
    pipeline = IngestionPipeline(client=client, data_dir=data_dir)

    print("\n=======================================================")
    print("STEP 2: ELEXON BMRS DATA INGESTION & QUALITY PIPELINE")
    print("=======================================================\n")

    # 1. Ingest FUELHH
    print(">>> 1. Ingesting FUELHH Actuals (2026-01-01 to 2026-01-31, WIND)...")
    actuals, actuals_report = pipeline.run_actuals_ingestion(
        settlement_date_from="2026-01-01",
        settlement_date_to="2026-01-31",
        fuel_type="WIND",
    )
    print(f"    Raw records fetched: {actuals_report['raw_records_fetched']}")
    print(f"    Normalized valid records: {actuals_report['valid_normalized_records']}")
    print(f"    Settlement dates covered: {actuals_report['distinct_settlement_dates']}")
    print(f"    Generation range: {actuals_report['min_generation_mw']} to {actuals_report['max_generation_mw']} MW")
    print(f"    Mean generation: {actuals_report['mean_generation_mw']:.2f} MW")

    # 2. Ingest WINDFOR
    print("\n>>> 2. Ingesting WINDFOR Forecasts (2025-12-30 to 2026-02-01)...")
    forecasts, forecasts_report = pipeline.run_forecasts_ingestion(
        publish_datetime_from="2025-12-30T00:00:00Z",
        publish_datetime_to="2026-02-01T23:59:59Z",
    )
    print(f"    Raw records fetched: {forecasts_report['raw_records_fetched']}")
    print(f"    Normalized valid records: {forecasts_report['valid_normalized_records']}")
    print(f"    Distinct publish runs: {forecasts_report['distinct_publish_runs']}")
    print(f"    Distinct target hours: {forecasts_report['distinct_target_start_times']}")
    print(f"    Target range: {forecasts_report['earliest_target_time']} to {forecasts_report['latest_target_time']}")

    # 3. Save combined data quality report
    full_report = {
        "timestamp_utc": str(Path(__file__).stat().st_mtime),
        "actuals": actuals_report,
        "forecasts": forecasts_report,
    }
    report_path = data_dir / "data_quality_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(full_report, f, indent=2)

    print(f"\n>>> Combined Data Quality Report saved to: {report_path}")
    print("\nIngestion and validation pipeline finished successfully.\n")


if __name__ == "__main__":
    main()
