"""FastAPI application entry point."""
import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.db import models  # noqa: F401
from app.routes import auth, repos, scan, graph, chat, nlq

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

# Route inclusion
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(repos.router, prefix="/repos", tags=["repos"])
app.include_router(scan.router, prefix="/scan", tags=["scan"])
app.include_router(graph.router, prefix="/graph", tags=["graph"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(nlq.router, prefix="/nlq", tags=["nlq"])


@app.on_event("startup")
async def startup() -> None:
    logger.info("AppLens backend starting (environment=%s)", settings.environment)
    logger.info("Database schema is managed via Alembic migrations")


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
