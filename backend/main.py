"""FastAPI Application Entrypoint for Gridbricks UK Wind Forecast Platform."""

import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import get_data_loader, router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("backend.main")

DEFAULT_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


def get_allowed_origins() -> list[str]:
    """Resolves allowed CORS origins from the CORS_ALLOWED_ORIGINS environment variable.

    Supports:
    - Comma-separated origins: e.g. "https://my-app.vercel.app, https://preview.vercel.app"
    - Wildcard origin: "*" for public open access (without credentials)
    - Default localhost origins for local development when unset
    """
    custom_origins = os.environ.get("CORS_ALLOWED_ORIGINS", "").strip()
    if not custom_origins:
        return DEFAULT_CORS_ORIGINS

    if custom_origins == "*":
        return ["*"]

    parsed = [orig.strip() for orig in custom_origins.split(",") if orig.strip()]
    return list(dict.fromkeys(DEFAULT_CORS_ORIGINS + parsed))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Eagerly initialize in-memory cached datasets on application startup."""
    logger.info("Initializing Gridbricks DAM Forecast API...")
    try:
        loader = get_data_loader()
        summary = loader.get_availability_summary()
        logger.info(
            "Cache verified: %s to %s (%d actuals, %d forecasts, %d runs)",
            summary["min_date"],
            summary["max_date"],
            summary["total_actual_records"],
            summary["total_forecast_records"],
            summary["distinct_publish_runs"],
        )
    except Exception as exc:
        logger.warning("Could not pre-warm data cache on startup: %s", exc)
    yield
    logger.info("Shutting down Gridbricks DAM Forecast API.")


app = FastAPI(
    title="Gridbricks UK Wind Forecast & Procurement API",
    description=(
        "Production-grade decision-support backend for UK Day-Ahead electricity procurement. "
        "Reconstructs historical Elexon wind forecasts published before pre-auction decision gate-closure "
        "and quantifies forecast accuracy (MAE, RMSE, Bias, WAPE, P10/P50/P90) against outturn generation."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration supporting Local Dev, Local Docker, and Cross-Origin Vercel deployments
allowed_origins = get_allowed_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
