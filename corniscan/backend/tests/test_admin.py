"""Tests Story 2.1 + 2.2 — GET/POST /api/v1/admin/users."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.core.security import create_access_token


# ── helpers ───────────────────────────────────────────────────────────────────


def _admin_header() -> dict:
    token = create_access_token({"sub": "admin", "role": "admin", "force_password_change": False})
    return {"Authorization": f"Bearer {token}"}


def _operator_header() -> dict:
    token = create_access_token({"sub": "alice", "role": "operator", "force_password_change": False})
    return {"Authorization": f"Bearer {token}"}


def _make_user_row(
    username: str = "alice",
    role: str = "operator",
    is_active: bool = True,
    force_password_change: bool = False,
    created_at: datetime | None = None,
):
    row = MagicMock()
    row.username = username
    row.role = role
    row.is_active = is_active
    row.force_password_change = force_password_change
    row.created_at = created_at or datetime(2026, 2, 22, 10, 0, 0, tzinfo=timezone.utc)
    return row


def _override_get_db(rows: list):
    """Session mockée retournant rows sur execute().fetchall()."""
    async def _get_db_override():
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = rows
        mock_session.execute.return_value = mock_result
        yield mock_session

    return _get_db_override


# ── Tests GET /api/v1/admin/users ─────────────────────────────────────────────


def test_list_users_returns_200_for_admin(client: TestClient) -> None:
    """AC#1 — Admin peut lister les comptes → 200."""
    from app.core.database import get_db
    from app.main import app

    rows = [_make_user_row("admin", "admin")]
    app.dependency_overrides[get_db] = _override_get_db(rows)
    try:
        response = client.get("/api/v1/admin/users", headers=_admin_header())
        assert response.status_code == 200
    finally:
        app.dependency_overrides.clear()


def test_list_users_returns_all_fields(client: TestClient) -> None:
    """AC#1 — Chaque compte expose username, role, is_active, created_at, force_password_change."""
    from app.core.database import get_db
    from app.main import app

    rows = [_make_user_row("alice", "operator", is_active=True, force_password_change=True)]
    app.dependency_overrides[get_db] = _override_get_db(rows)
    try:
        response = client.get("/api/v1/admin/users", headers=_admin_header())
        data = response.json()
        assert len(data) == 1
        user = data[0]
        assert user["username"] == "alice"
        assert user["role"] == "operator"
        assert user["is_active"] is True
        assert user["force_password_change"] is True
        assert "created_at" in user
    finally:
        app.dependency_overrides.clear()


def test_list_users_admin_appears_with_admin_role(client: TestClient) -> None:
    """AC#2 — Le compte admin apparaît avec rôle 'admin'."""
    from app.core.database import get_db
    from app.main import app

    rows = [
        _make_user_row("admin", "admin"),
        _make_user_row("alice", "operator"),
    ]
    app.dependency_overrides[get_db] = _override_get_db(rows)
    try:
        response = client.get("/api/v1/admin/users", headers=_admin_header())
        data = response.json()
        admin_entries = [u for u in data if u["username"] == "admin"]
        assert len(admin_entries) == 1
        assert admin_entries[0]["role"] == "admin"
    finally:
        app.dependency_overrides.clear()


def test_list_users_operator_gets_403(client: TestClient) -> None:
    """AC#3 — Un opérateur reçoit 403 (accès refusé)."""
    response = client.get("/api/v1/admin/users", headers=_operator_header())
    assert response.status_code == 403
    assert "administrateurs" in response.json()["detail"]


def test_list_users_no_token_gets_401(client: TestClient) -> None:
    """AC#3 — Sans token → 401."""
    response = client.get("/api/v1/admin/users")
    assert response.status_code == 401


def test_list_users_empty_list(client: TestClient) -> None:
    """AC#1 — Retourne une liste vide si aucun compte."""
    from app.core.database import get_db
    from app.main import app

    app.dependency_overrides[get_db] = _override_get_db([])
    try:
        response = client.get("/api/v1/admin/users", headers=_admin_header())
        assert response.status_code == 200
        assert response.json() == []
    finally:
        app.dependency_overrides.clear()


def test_list_users_inactive_account_visible(client: TestClient) -> None:
    """AC#1 — Les comptes inactifs apparaissent avec is_active=false."""
    from app.core.database import get_db
    from app.main import app

    rows = [_make_user_row("bob", "operator", is_active=False)]
    app.dependency_overrides[get_db] = _override_get_db(rows)
    try:
        response = client.get("/api/v1/admin/users", headers=_admin_header())
        data = response.json()
        assert data[0]["is_active"] is False
    finally:
        app.dependency_overrides.clear()


# ── Tests migration 002 ────────────────────────────────────────────────────────


def test_migration_002_exists() -> None:
    """Migration 002 existe et a le bon down_revision."""
    import importlib.util
    from pathlib import Path

    migration_path = (
        Path(__file__).parent.parent
        / "alembic"
        / "versions"
        / "002_add_is_active_to_users.py"
    )
    assert migration_path.exists(), "Fichier migration 002 manquant"

    spec = importlib.util.spec_from_file_location("migration_002", migration_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert module.revision == "002"
    assert module.down_revision == "001"


def test_users_model_has_is_active() -> None:
    """Le modèle users contient la colonne is_active."""
    from app.models.user import users

    column_names = [c.name for c in users.columns]
    assert "is_active" in column_names


# ── Tests POST /api/v1/admin/users (Story 2.2) ────────────────────────────────


def _override_get_db_create(existing_username: str | None = None):
    """Session mockée pour la création : vérifie unicité + INSERT RETURNING."""

    async def _get_db_override():
        mock_session = AsyncMock()

        # Premier execute → SELECT pour unicité
        select_result = MagicMock()
        select_result.fetchone.return_value = (
            MagicMock(username=existing_username) if existing_username else None
        )

        # Deuxième execute → INSERT RETURNING
        insert_result = MagicMock()
        new_row = MagicMock()
        new_row.username = "alice"
        new_row.role = "operator"
        new_row.is_active = True
        new_row.force_password_change = True
        new_row.created_at = datetime(2026, 2, 22, 10, 0, 0, tzinfo=timezone.utc)
        insert_result.fetchone.return_value = new_row

        mock_session.execute.side_effect = [select_result, insert_result]
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()
        yield mock_session

    return _get_db_override


def test_create_user_success_returns_201(client: TestClient) -> None:
    """AC#1 — Création réussie → 201 + données du compte."""
    from app.core.database import get_db
    from app.main import app

    app.dependency_overrides[get_db] = _override_get_db_create()
    try:
        response = client.post(
            "/api/v1/admin/users",
            json={"username": "alice", "password": "ProvPass123!"},
            headers=_admin_header(),
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "alice"
        assert data["role"] == "operator"
        assert data["force_password_change"] is True
        assert data["is_active"] is True
    finally:
        app.dependency_overrides.clear()


def test_create_user_duplicate_returns_409(client: TestClient) -> None:
    """AC#3 — Username déjà pris → 409 avec message explicite."""
    from app.core.database import get_db
    from app.main import app

    app.dependency_overrides[get_db] = _override_get_db_create(existing_username="alice")
    try:
        response = client.post(
            "/api/v1/admin/users",
            json={"username": "alice", "password": "ProvPass123!"},
            headers=_admin_header(),
        )
        assert response.status_code == 409
        assert "existe déjà" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()


def test_create_user_operator_gets_403(client: TestClient) -> None:
    """AC#1 — Opérateur ne peut pas créer de compte → 403."""
    response = client.post(
        "/api/v1/admin/users",
        json={"username": "bob", "password": "Pass123!"},
        headers=_operator_header(),
    )
    assert response.status_code == 403


def test_create_user_no_token_gets_401(client: TestClient) -> None:
    """AC#1 — Sans token → 401."""
    response = client.post(
        "/api/v1/admin/users",
        json={"username": "bob", "password": "Pass123!"},
    )
    assert response.status_code == 401


# ── Tests PATCH /api/v1/admin/users/{username}/deactivate (Story 2.3) ─────────


def _override_get_db_deactivate(user_exists: bool = True):
    """Session mockée pour la désactivation."""

    async def _get_db_override():
        mock_session = AsyncMock()

        # SELECT pour vérifier existence
        select_result = MagicMock()
        if user_exists:
            row = MagicMock()
            row.username = "alice"
            row.role = "operator"
            row.is_active = True
            row.force_password_change = False
            row.created_at = datetime(2026, 2, 22, 10, 0, 0, tzinfo=timezone.utc)
            select_result.fetchone.return_value = row
        else:
            select_result.fetchone.return_value = None

        mock_session.execute.return_value = select_result
        mock_session.commit = AsyncMock()
        yield mock_session

    return _get_db_override


def test_deactivate_user_success(client: TestClient) -> None:
    """AC#1 — Désactivation réussie → 200 + is_active=false."""
    from app.core.database import get_db
    from app.main import app

    app.dependency_overrides[get_db] = _override_get_db_deactivate(user_exists=True)
    try:
        response = client.patch(
            "/api/v1/admin/users/alice/deactivate",
            headers=_admin_header(),
        )
        assert response.status_code == 200
        assert response.json()["is_active"] is False
        assert response.json()["username"] == "alice"
    finally:
        app.dependency_overrides.clear()


def test_deactivate_own_account_returns_400(client: TestClient) -> None:
    """AC#4 — Admin ne peut pas désactiver son propre compte → 400."""
    from app.core.database import get_db
    from app.main import app

    app.dependency_overrides[get_db] = _override_get_db_deactivate(user_exists=True)
    try:
        response = client.patch(
            "/api/v1/admin/users/admin/deactivate",
            headers=_admin_header(),
        )
        assert response.status_code == 400
        assert "propre compte" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()


def test_deactivate_unknown_user_returns_404(client: TestClient) -> None:
    """AC#1 — Utilisateur introuvable → 404."""
    from app.core.database import get_db
    from app.main import app

    app.dependency_overrides[get_db] = _override_get_db_deactivate(user_exists=False)
    try:
        response = client.patch(
            "/api/v1/admin/users/ghost/deactivate",
            headers=_admin_header(),
        )
        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()


def test_deactivate_operator_not_allowed(client: TestClient) -> None:
    """AC#1 — Opérateur ne peut pas désactiver → 403."""
    response = client.patch(
        "/api/v1/admin/users/alice/deactivate",
        headers=_operator_header(),
    )
    assert response.status_code == 403
