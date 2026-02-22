"""Alembic env.py — configuration async pour CorniScan."""

import asyncio
from logging.config import fileConfig
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.core.config import settings
from app.models.user import metadata

# Objet de configuration Alembic (accès à alembic.ini)
config = context.config

# Neon fournit des URLs avec ?sslmode=require&channel_binding=require (libpq).
# async_engine_from_config + asyncpg ne comprend pas ces paramètres — on les
# retire proprement via urllib.parse pour ne pas corrompre le nom de la base.
_LIBPQ_ONLY = {"sslmode", "channel_binding", "connect_timeout", "options"}

_parsed = urlparse(settings.database_url)
_params = parse_qs(_parsed.query, keep_blank_values=True)
_sslmode = _params.pop("sslmode", [None])[0]
_ssl_required = _sslmode in ("require", "verify-ca", "verify-full")
for _p in _LIBPQ_ONLY - {"sslmode"}:
    _params.pop(_p, None)
_db_url = urlunparse(_parsed._replace(query=urlencode({k: v[0] for k, v in _params.items()})))

config.set_main_option("sqlalchemy.url", _db_url)

# Configurer le logging depuis alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata cible pour les migrations autogénérées (non utilisé ici — migration manuelle)
target_metadata = metadata


def run_migrations_offline() -> None:
    """Exécute les migrations en mode "offline" (sans connexion active)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Exécute les migrations en mode "online" (connexion async)."""
    extra: dict = {"connect_args": {"ssl": True}} if _ssl_required else {}
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        **extra,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
