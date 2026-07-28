from pathlib import Path
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import settings
from app.db.base import engine, Base
import app.models  # noqa: F401 — register ORM metadata for create_all
from app.services.seed import seed_admin_user
from app.db.base import AsyncSessionLocal
from app.api.v1.router import router as api_v1_router
from app.middleware.logging_middleware import RequestLoggingMiddleware

scheduler = AsyncIOScheduler()
_static_env = os.environ.get("STATIC_DIR", "").strip()
STATIC_DIR = Path(_static_env).resolve() if _static_env else None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed default admin
    async with AsyncSessionLocal() as db:
        await seed_admin_user(db)

    # Schedule tasks
    from app.tasks.exchange_rate_fetcher import fetch_and_store_exchange_rates

    scheduler.add_job(
        fetch_and_store_exchange_rates,
        CronTrigger(hour=settings.EXCHANGE_RATE_FETCH_HOUR, minute=0),
        id="fetch_exchange_rates",
        replace_existing=True,
    )
    scheduler.start()

    yield

    scheduler.shutdown()


app = FastAPI(
    title="FamilyOrganiser API",
    version="1.0.0",
    description="Prywatna aplikacja do zarządzania finansami rodzinnymi",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestLoggingMiddleware)

# Routers — all endpoints under /api/v1/
app.include_router(api_v1_router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "FamilyOrganiser API"}


def _register_spa(static_dir: Path) -> None:
    """Serve Vite build (same origin as /api) for Fly / single-container deploy."""
    assets = static_dir / "assets"
    if assets.is_dir():
        app.mount("/assets", StaticFiles(directory=assets), name="assets")

    @app.get("/")
    async def spa_index():
        return FileResponse(static_dir / "index.html")

    @app.get("/{full_path:path}")
    async def spa_fallback(full_path: str):
        candidate = (static_dir / full_path).resolve()
        try:
            candidate.relative_to(static_dir)
        except ValueError:
            return FileResponse(static_dir / "index.html")
        if candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(static_dir / "index.html")


if STATIC_DIR is not None and STATIC_DIR.is_dir() and (STATIC_DIR / "index.html").is_file():
    _register_spa(STATIC_DIR)
