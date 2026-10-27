"""Data loader service for accessing cached normalized Elexon datasets."""

import logging
from pathlib import Path
from typing import Optional, Tuple
import pandas as pd

logger = logging.getLogger(__name__)


class DataNotFoundError(Exception):
    """Raised when normalized data files are not found."""
    pass


class DataLoader:
    """Manages loading and in-memory caching of normalized actuals and forecasts."""

    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            # Default to root / data
            self.data_dir = Path(__file__).resolve().parent.parent.parent / "data"
        else:
            self.data_dir = Path(data_dir)
            
        self.norm_dir = self.data_dir / "normalized"
        self._actuals_df: Optional[pd.DataFrame] = None
        self._forecasts_df: Optional[pd.DataFrame] = None

    def get_actuals_df(self) -> pd.DataFrame:
        """Returns normalized actual wind generation DataFrame."""
        if self._actuals_df is None:
            parquet_path = self.norm_dir / "actuals_jan2026.parquet"
            json_path = self.norm_dir / "actuals_jan2026.json"

            if parquet_path.exists():
                df = pd.read_parquet(parquet_path)
            elif json_path.exists():
                df = pd.read_json(json_path)
                df["start_time"] = pd.to_datetime(df["start_time"], utc=True)
            else:
                raise DataNotFoundError(f"Actuals data file not found in {self.norm_dir}")

            # Ensure UTC datetime
            df["start_time"] = pd.to_datetime(df["start_time"], utc=True)
            self._actuals_df = df
            logger.info("Loaded %d actuals records into memory", len(df))

        return self._actuals_df

    def get_forecasts_df(self) -> pd.DataFrame:
        """Returns normalized wind forecasts DataFrame."""
        if self._forecasts_df is None:
            parquet_path = self.norm_dir / "forecasts_jan2026.parquet"
            json_path = self.norm_dir / "forecasts_jan2026.json"

            if parquet_path.exists():
                df = pd.read_parquet(parquet_path)
            elif json_path.exists():
                df = pd.read_json(json_path)
                df["publish_time"] = pd.to_datetime(df["publish_time"], utc=True)
                df["start_time"] = pd.to_datetime(df["start_time"], utc=True)
            else:
                raise DataNotFoundError(f"Forecasts data file not found in {self.norm_dir}")

            # Ensure UTC datetime
            df["publish_time"] = pd.to_datetime(df["publish_time"], utc=True)
            df["start_time"] = pd.to_datetime(df["start_time"], utc=True)
            self._forecasts_df = df
            logger.info("Loaded %d forecast records into memory", len(df))

        return self._forecasts_df

    def get_availability_summary(self) -> dict:
        """Returns summary of data availability and dates."""
        actuals = self.get_actuals_df()
        forecasts = self.get_forecasts_df()

        min_date = str(actuals["settlement_date"].min())
        max_date = str(actuals["settlement_date"].max())

        return {
            "min_date": min_date,
            "max_date": max_date,
            "total_actual_records": len(actuals),
            "total_forecast_records": len(forecasts),
            "distinct_publish_runs": int(forecasts["publish_time"].nunique()),
            "dataset_status": "ready",
        }
