"""Connexion async SQLAlchemy — Story 1.2."""

from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

# Paramètres libpq/psycopg2 que asyncpg ne comprend pas — à retirer de l'URL.
_LIBPQ_ONLY_PARAMS = {"sslmode", "channel_binding", "connect_timeout", "options"}


def _asyncpg_url(raw: str) -> tuple[str, dict]:
    """Retire les paramètres libpq incompatibles avec asyncpg.

    Neon fournit des URLs avec ?sslmode=require&channel_binding=require.
    asyncpg ne connaît ni sslmode ni channel_binding — on les retire via
    urllib.parse pour ne pas corrompre le nom de la base, et on passe
    ssl=True dans connect_args si SSL était requis.
    """
    parsed = urlparse(raw)
    params = parse_qs(parsed.query, keep_blank_values=True)

    connect_args: dict = {}
    sslmode = params.pop("sslmode", [None])[0]
    if sslmode in ("require", "verify-ca", "verify-full"):
        connect_args["ssl"] = True

    # Retirer les autres paramètres libpq non supportés par asyncpg
    for p in _LIBPQ_ONLY_PARAMS - {"sslmode"}:
        params.pop(p, None)

    new_query = urlencode({k: v[0] for k, v in params.items()})
    url = urlunparse(parsed._replace(query=new_query))
    return url, connect_args


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
