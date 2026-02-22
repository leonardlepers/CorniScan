"""Alembic env.py — configuration async pour CorniScan."""

import asyncio
import re
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.core.config import settings
from app.models.user import metadata

# Objet de configuration Alembic (accès à alembic.ini)
config = context.config

# Neon fournit des URLs avec ?sslmode=require (format psycopg2).
# async_engine_from_config + asyncpg ne comprend pas sslmode= — on le retire.
_sslmode_match = re.search(r"sslmode=(\w+)", settings.database_url)
_db_url = re.sub(r"[?&]sslmode=\w+", "", settings.database_url).rstrip("?&")
_ssl_required = bool(_sslmode_match and _sslmode_match.group(1) in ("require", "verify-ca", "verify-full"))
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
