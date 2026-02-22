"""Connexion async SQLAlchemy — Story 1.2."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

# pool_size=2 : contrainte Neon free tier (max 5 connexions simultanées)
engine = (
    create_async_engine(settings.database_url, pool_size=2, max_overflow=0)
    if settings.database_url
    else None
)

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
