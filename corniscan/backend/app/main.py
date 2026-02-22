import os
from contextlib import asynccontextmanager
from pathlib import Path

from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.routers.admin import router as admin_router
from app.routers.auth import router as auth_router

_BACKEND_DIR = Path(__file__).parent.parent


def run_migrations() -> None:
    """Exécute alembic upgrade head via l'API Python Alembic."""
    alembic_cfg = AlembicConfig(str(_BACKEND_DIR / "alembic.ini"))
    alembic_command.upgrade(alembic_cfg, "head")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event — migrations + seed admin au démarrage (Story 1.2)."""
    if settings.database_url:
        run_migrations()
        from app.core.database import engine
        from app.core.seed import seed_admin

        async with engine.connect() as conn:
            await seed_admin(conn)
    yield


app = FastAPI(
    title="CorniScan API",
    version="0.1.0",
    docs_url="/docs" if settings.environment != "production" else None,
    redoc_url=None,
    lifespan=lifespan,
)

# ── Health check endpoint ──────────────────────────────────────────────────────
# ORDRE CRITIQUE : doit être déclaré AVANT le mount StaticFiles
# Sinon StaticFiles capture "/" et l'endpoint n'est jamais atteint


app.include_router(auth_router)
app.include_router(admin_router)


@app.get("/api/v1/health")
def health_check() -> dict:
    """Endpoint de santé — vérifie que le backend répond."""
    return {"status": "ok", "environment": settings.environment}


# ── Serve frontend static files (production) ──────────────────────────────────
# En dev local, frontend/dist/ n'existe pas encore — le backend démarre quand même
FRONTEND_DIST = os.path.join(os.path.dirname(__file__), "../../frontend/dist")

if os.path.exists(FRONTEND_DIST):
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="static")
