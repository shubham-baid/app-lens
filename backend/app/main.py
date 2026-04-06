"""FastAPI application entry point."""
import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.db.base import Base, engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AppLens API",
    description="Microservice Dependency Visualization API",
    version="0.1.0",
    redirect_slashes=False,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup() -> None:
    logger.info("AppLens backend starting (environment=%s)", settings.environment)
    try:
        # Keep startup resilient before Alembic revisions are introduced.
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database metadata initialization completed")
    except Exception as exc:  # noqa: BLE001
        logger.warning("Database initialization skipped: %s", exc)


@app.get("/health", tags=["ops"])
async def health() -> JSONResponse:
    return JSONResponse(
        content={
            "status": "healthy",
            "service": "applens-backend",
            "version": "0.1.0",
        }
    )


@app.get("/", tags=["ops"])
async def root() -> dict:
    return {"message": "AppLens API", "docs": "/docs"}
