"""Tests Story 1.2 — Base de données et table utilisateurs."""

import importlib.util
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest


# ── AC#3 : Hachage bcrypt cost ≥ 12 ──────────────────────────────────────────


def test_hash_password_returns_bcrypt_hash() -> None:
    """AC#3 — hash_password retourne un hash bcrypt, jamais le texte en clair."""
    from app.core.seed import hash_password

    plain = "TestPassword123!"
    hashed = hash_password(plain)

    assert hashed != plain
    assert hashed.startswith("$2b$")  # Prefix bcrypt


def test_hash_password_cost_12() -> None:
    """AC#3 — Le hash bcrypt utilise un salt cost ≥ 12 (NFR-S1)."""
    from app.core.seed import hash_password

    hashed = hash_password("SomePassword!")
    # Format bcrypt : $2b$<cost>$...
    parts = hashed.split("$")
    cost = int(parts[2])
    assert cost >= 12


def test_verify_password_correct() -> None:
    """AC#3 — verify_password retourne True pour le bon mot de passe."""
    from app.core.seed import hash_password, verify_password

    plain = "CorrectPassword!"
    hashed = hash_password(plain)
    assert verify_password(plain, hashed) is True


def test_verify_password_wrong() -> None:
    """AC#3 — verify_password retourne False pour un mauvais mot de passe."""
    from app.core.seed import hash_password, verify_password

    hashed = hash_password("CorrectPassword!")
    assert verify_password("WrongPassword!", hashed) is False


def test_admin_default_password_documented() -> None:
    """AC#4 — Le mot de passe provisoire admin est documenté dans seed.py."""
    from app.core.seed import ADMIN_DEFAULT_PASSWORD

    assert ADMIN_DEFAULT_PASSWORD != ""
    assert len(ADMIN_DEFAULT_PASSWORD) >= 8  # Mot de passe non trivial


# ── AC#4 : Seed admin conditionnel ───────────────────────────────────────────


@pytest.mark.asyncio
async def test_seed_admin_inserts_when_absent() -> None:
    """AC#4 — seed_admin INSERT le compte admin si absent."""
    from app.core.seed import seed_admin

    mock_conn = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar.return_value = 0  # Pas d'admin existant
    mock_conn.execute.return_value = mock_result

    await seed_admin(mock_conn)

    # Vérifie qu'un INSERT a été effectué (2 appels : SELECT COUNT + INSERT)
    assert mock_conn.execute.call_count == 2
    mock_conn.commit.assert_called_once()


@pytest.mark.asyncio
async def test_seed_admin_skips_when_present() -> None:
    """AC#4 — seed_admin ne réinsère pas si admin déjà existant (idempotent)."""
    from app.core.seed import seed_admin

    mock_conn = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar.return_value = 1  # Admin déjà présent
    mock_conn.execute.return_value = mock_result

    await seed_admin(mock_conn)

    # Un seul appel execute (le SELECT COUNT) — pas d'INSERT
    assert mock_conn.execute.call_count == 1
    mock_conn.commit.assert_not_called()


# ── Migration file structure ──────────────────────────────────────────────────


def _load_migration():
    """Charge le fichier de migration via importlib.util (fichier 001_.py)."""
    backend_dir = Path(__file__).parent.parent
    migration_path = backend_dir / "alembic" / "versions" / "001_create_users_table.py"
    spec = importlib.util.spec_from_file_location("migration_001", migration_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_migration_file_exists() -> None:
    """AC#2 — Le fichier de migration initiale existe."""
    backend_dir = Path(__file__).parent.parent
    migration_path = backend_dir / "alembic" / "versions" / "001_create_users_table.py"
    assert migration_path.exists()


def test_migration_revision() -> None:
    """AC#2 — La migration initiale a le bon identifiant de révision."""
    migration = _load_migration()
    assert migration.revision == "001"
    assert migration.down_revision is None


def test_migration_has_upgrade_downgrade() -> None:
    """AC#2 — La migration définit les fonctions upgrade() et downgrade()."""
    migration = _load_migration()
    assert callable(migration.upgrade)
    assert callable(migration.downgrade)


# ── database.py — comportement sans DATABASE_URL ─────────────────────────────


def test_engine_none_without_database_url() -> None:
    """AC#1 — Sans DATABASE_URL, l'engine est None (pas d'erreur au démarrage dev)."""
    from app.core.config import settings
    import app.core.database as db_module

    if not settings.database_url:
        assert db_module.engine is None
        assert db_module.AsyncSessionLocal is None
    else:
        # DATABASE_URL configurée → engine non None
        assert db_module.engine is not None


@pytest.mark.asyncio
async def test_get_db_raises_without_engine() -> None:
    """AC#1 — get_db() lève RuntimeError si AsyncSessionLocal est None."""
    import app.core.database as db_module
    from app.core.database import get_db

    original = db_module.AsyncSessionLocal
    db_module.AsyncSessionLocal = None
    try:
        with pytest.raises(RuntimeError, match="DATABASE_URL"):
            async for _ in get_db():
                pass
    finally:
        db_module.AsyncSessionLocal = original


# ── Table users — structure ───────────────────────────────────────────────────


def test_users_table_columns() -> None:
    """AC#2 — La table users a exactement les colonnes requises."""
    from app.models.user import users

    col_names = {col.name for col in users.columns}
    expected = {"id", "username", "hashed_password", "role", "force_password_change", "is_active", "created_at"}
    assert col_names == expected


def test_users_table_username_unique() -> None:
    """AC#2 — username a une contrainte UNIQUE."""
    from app.models.user import users

    username_col = users.c.username
    # Soit contrainte directe sur colonne, soit via UniqueConstraint
    has_unique = username_col.unique or any(
        "username" in [c.name for c in uc.columns]
        for uc in users.constraints
        if hasattr(uc, "columns")
    )
    assert has_unique


def test_users_table_name() -> None:
    """AC#2 — La table s'appelle bien 'users'."""
    from app.models.user import users

    assert users.name == "users"


def test_users_id_is_uuid() -> None:
    """AC#2 — id est de type UUID (NFR — pas d'entier séquentiel prédictible)."""
    from sqlalchemy.dialects.postgresql import UUID
    from app.models.user import users

    id_col = users.c.id
    assert isinstance(id_col.type, UUID)
