"""Connexion async SQLAlchemy — Story 1.2."""

import re

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings


def _asyncpg_url(raw: str) -> tuple[str, dict]:
    """Retire sslmode= (paramètre psycopg2) incompatible avec asyncpg.

    Neon fournit des URLs avec ?sslmode=require ; asyncpg utilise ssl=True.
    """
    connect_args: dict = {}
    m = re.search(r"sslmode=(\w+)", raw)
    if m:
        url = re.sub(r"[?&]sslmode=\w+", "", raw).rstrip("?&")
        if m.group(1) in ("require", "verify-ca", "verify-full"):
            connect_args["ssl"] = True
        return url, connect_args
    return raw, connect_args


# pool_size=2 : contrainte Neon free tier (max 5 connexions simultanées)
if settings.database_url:
    _url, _ssl = _asyncpg_url(settings.database_url)
    engine = create_async_engine(_url, pool_size=2, max_overflow=0, connect_args=_ssl)
else:
    engine = None

AsyncSessionLocal = (
    async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    if engine
    else None
)


async def get_db() -> AsyncSession:
    """Dependency FastAPI — fournit une session SQLAlchemy async."""
    if AsyncSessionLocal is None:
        raise RuntimeError("DATABASE_URL non configurée")
    async with AsyncSessionLocal() as session:
        yield session
