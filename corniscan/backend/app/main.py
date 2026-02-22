import asyncio
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.routers.admin import router as admin_router
from app.routers.auth import router as auth_router
from app.routers.scan import router as scan_router

_BACKEND_DIR = Path(__file__).parent.parent
_logger = logging.getLogger("uvicorn")


async def _run_migrations() -> None:
    """Lance alembic upgrade head dans un sous-processus async.

    asyncio.run() dans alembic/env.py est incompatible avec la boucle uvicorn.
    asyncio.create_subprocess_exec() crée un processus fils indépendant —
    aucun conflit d'event loop, sortie capturée pour les logs.
    """
    alembic_bin = _BACKEND_DIR / ".venv" / "bin" / "alembic"
    proc = await asyncio.create_subprocess_exec(
        str(alembic_bin),
        "upgrade",
        "head",
        cwd=str(_BACKEND_DIR),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    stdout, _ = await proc.communicate()
    output = stdout.decode(errors="replace") if stdout else ""
    if output.strip():
        _logger.info("Alembic:\n%s", output.strip())
    if proc.returncode != 0:
        raise RuntimeError(f"alembic upgrade head a échoué (code {proc.returncode})")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event — migrations + seed admin au démarrage."""
    if settings.database_url:
        await _run_migrations()

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
app.include_router(scan_router)


@app.get("/api/v1/health")
def health_check() -> dict:
    """Endpoint de santé — vérifie que le backend répond."""
    return {"status": "ok", "environment": settings.environment}


# ── Serve frontend static files (production) ──────────────────────────────────
# En dev local, frontend/dist/ n'existe pas encore — le backend démarre quand même
FRONTEND_DIST = os.path.join(os.path.dirname(__file__), "../../frontend/dist")

if os.path.exists(FRONTEND_DIST):
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="static")
