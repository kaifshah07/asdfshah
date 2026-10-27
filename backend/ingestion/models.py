"""Data models for Elexon BMRS raw API records and normalized domain entities."""

from datetime import date, datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class RawFuelHHRecord(BaseModel):
    """Raw record from /datasets/FUELHH/stream."""
    dataset: Optional[str] = "FUELHH"
    publishTime: Optional[str] = None
    startTime: str
    settlementDate: str
    settlementPeriod: int
    fuelType: str
    generation: Optional[int] = 0

    @field_validator("settlementPeriod")
    @classmethod
    def validate_settlement_period(cls, v: int) -> int:
        if v < 1 or v > 50:
            raise ValueError(f"Settlement period {v} out of valid range [1, 50]")
        return v


class RawWindforRecord(BaseModel):
    """Raw record from /datasets/WINDFOR/stream."""
    dataset: Optional[str] = "WINDFOR"
    publishTime: str
    startTime: str
    generation: Optional[int] = 0


class NormalizedActual(BaseModel):
    """Validated, normalized half-hourly actual wind generation record."""
    start_time: datetime
    settlement_date: date
    settlement_period: int
    fuel_type: str = "WIND"
    generation_mw: float

    @field_validator("start_time")
    @classmethod
    def ensure_utc(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc)


class NormalizedForecast(BaseModel):
    """Validated, normalized wind generation forecast record."""
    publish_time: datetime
    start_time: datetime
    generation_mw: float

    @field_validator("publish_time", "start_time")
    @classmethod
    def ensure_utc(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc)
