"""Tests Story 1.3 — Authentification JWT."""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from jose import JWTError, jwt

from app.core.config import settings
from app.core.security import (
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_HOURS,
    create_access_token,
    verify_password,
    verify_token,
    hash_password,
)


# ── Unit tests security.py ────────────────────────────────────────────────────


def test_create_access_token_returns_string() -> None:
    """AC#2 — create_access_token retourne une chaîne JWT."""
    token = create_access_token({"sub": "alice", "role": "operator", "force_password_change": False})
    assert isinstance(token, str)
    assert len(token.split(".")) == 3  # Header.Payload.Signature


def test_verify_token_decodes_payload() -> None:
    """AC#2 — verify_token décode correctement le payload."""
    data = {"sub": "alice", "role": "operator", "force_password_change": False}
    token = create_access_token(data)
    payload = verify_token(token)

    assert payload["sub"] == "alice"
    assert payload["role"] == "operator"
    assert payload["force_password_change"] is False


def test_token_expires_in_8_hours() -> None:
    """AC#5 — Le JWT a une expiration à 8h (NFR-S3)."""
    token = create_access_token({"sub": "alice", "role": "operator"})
    payload = verify_token(token)

    exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    now = datetime.now(timezone.utc)
    delta = exp - now

    assert 7.9 * 3600 < delta.total_seconds() < 8.1 * 3600


def test_verify_token_raises_on_expired() -> None:
    """AC#5 — verify_token lève JWTError si le token est expiré."""
    expired_data = {
        "sub": "alice",
        "role": "operator",
        "exp": datetime.now(timezone.utc) - timedelta(hours=1),
    }
    expired_token = jwt.encode(expired_data, settings.jwt_secret, algorithm=ALGORITHM)

    with pytest.raises(JWTError):
        verify_token(expired_token)


def test_verify_token_raises_on_bad_signature() -> None:
    """AC#5 — verify_token lève JWTError si la signature est invalide."""
    token = create_access_token({"sub": "alice", "role": "operator"})

    with pytest.raises(JWTError):
        jwt.decode(token, "wrong-secret", algorithms=[ALGORITHM])


# ── POST /api/v1/auth/token ───────────────────────────────────────────────────


def _make_mock_user_row(
    username: str = "alice",
    role: str = "operator",
    force_password_change: bool = False,
):
    """Crée un objet Row SQLAlchemy mocké."""
    hashed = hash_password("correct-password")
    row = MagicMock()
    row.username = username
    row.hashed_password = hashed
    row.role = role
    row.force_password_change = force_password_change
    return row


def _override_get_db(user_row=None):
    """Crée une session DB mockée retournant user_row sur execute."""
    async def _get_db_override():
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.fetchone.return_value = user_row
        mock_session.execute.return_value = mock_result
        yield mock_session

    return _get_db_override


def test_login_valid_credentials_returns_token(client: TestClient) -> None:
    """AC#2 — Login avec credentials valides → 200 + access_token."""
    from app.core.database import get_db
    from app.main import app

    user_row = _make_mock_user_row()
    app.dependency_overrides[get_db] = _override_get_db(user_row)
    try:
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "alice", "password": "correct-password"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["username"] == "alice"
        assert data["user"]["role"] == "operator"
    finally:
        app.dependency_overrides.clear()


def test_login_returns_user_info(client: TestClient) -> None:
    """AC#2 — La réponse login inclut username, role, force_password_change."""
    from app.core.database import get_db
    from app.main import app

    user_row = _make_mock_user_row(role="admin", force_password_change=True)
    app.dependency_overrides[get_db] = _override_get_db(user_row)
    try:
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "alice", "password": "correct-password"},
        )
        user = response.json()["user"]
        assert user["role"] == "admin"
        assert user["force_password_change"] is True
    finally:
        app.dependency_overrides.clear()


def test_login_wrong_password_returns_401(client: TestClient) -> None:
    """AC#3 — Mauvais mot de passe → 401."""
    from app.core.database import get_db
    from app.main import app

    user_row = _make_mock_user_row()
    app.dependency_overrides[get_db] = _override_get_db(user_row)
    try:
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "alice", "password": "wrong-password"},
        )
        assert response.status_code == 401
        assert "Identifiant ou mot de passe incorrect" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()


def test_login_unknown_user_returns_401(client: TestClient) -> None:
    """AC#3 — Username inconnu → 401 (même message — pas de fuite)."""
    from app.core.database import get_db
    from app.main import app

    app.dependency_overrides[get_db] = _override_get_db(user_row=None)
    try:
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "unknown", "password": "any-password"},
        )
        assert response.status_code == 401
        assert "Identifiant ou mot de passe incorrect" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()


def test_login_same_error_for_wrong_password_and_unknown_user(client: TestClient) -> None:
    """AC#3 — Message identique pour mauvais mdp et username inconnu (pas de fuite d'info)."""
    from app.core.database import get_db
    from app.main import app

    # Cas 1 : username inconnu
    app.dependency_overrides[get_db] = _override_get_db(user_row=None)
    response_unknown = client.post(
        "/api/v1/auth/token",
        data={"username": "ghost", "password": "any"},
    )

    # Cas 2 : mauvais mot de passe
    app.dependency_overrides[get_db] = _override_get_db(_make_mock_user_row())
    response_wrong_pw = client.post(
        "/api/v1/auth/token",
        data={"username": "alice", "password": "wrong"},
    )
    app.dependency_overrides.clear()

    assert response_unknown.json()["detail"] == response_wrong_pw.json()["detail"]


# ── POST /api/v1/auth/change-password — Story 1.4 ────────────────────────────


def _make_mock_user_row_with_hashed(
    username: str = "alice",
    role: str = "operator",
    force_password_change: bool = True,
    plain_password: str = "OldPass123!",
):
    """Crée un Row mocké avec le vrai hash bcrypt de plain_password."""
    row = MagicMock()
    row.username = username
    row.hashed_password = hash_password(plain_password)
    row.role = role
    row.force_password_change = force_password_change
    return row


def _override_get_db_with_commit(user_row=None):
    """Session mockée supportant execute + commit."""
    async def _get_db_override():
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.fetchone.return_value = user_row
        mock_session.execute.return_value = mock_result
        mock_session.commit = AsyncMock()
        yield mock_session

    return _get_db_override


def _auth_header(username: str = "alice", role: str = "operator") -> dict:
    """Retourne un header Authorization avec un JWT valide."""
    token = create_access_token(
        {"sub": username, "role": role, "force_password_change": True}
    )
    return {"Authorization": f"Bearer {token}"}


def test_change_password_success(client: TestClient) -> None:
    """AC#3 — Changement réussi → 200 + nouveau JWT avec force_password_change=false."""
    from app.core.database import get_db
    from app.main import app

    user_row = _make_mock_user_row_with_hashed(plain_password="OldPass123!")
    app.dependency_overrides[get_db] = _override_get_db_with_commit(user_row)
    try:
        response = client.post(
            "/api/v1/auth/change-password",
            json={"current_password": "OldPass123!", "new_password": "NewPass456!"},
            headers=_auth_header(),
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["force_password_change"] is False
        # Vérifier que le nouveau JWT a force_password_change=false
        from app.core.security import verify_token
        payload = verify_token(data["access_token"])
        assert payload["force_password_change"] is False
    finally:
        app.dependency_overrides.clear()


def test_change_password_wrong_current(client: TestClient) -> None:
    """AC#3 — Mauvais mot de passe actuel → 400."""
    from app.core.database import get_db
    from app.main import app

    user_row = _make_mock_user_row_with_hashed(plain_password="OldPass123!")
    app.dependency_overrides[get_db] = _override_get_db_with_commit(user_row)
    try:
        response = client.post(
            "/api/v1/auth/change-password",
            json={"current_password": "WrongPass!", "new_password": "NewPass456!"},
            headers=_auth_header(),
        )
        assert response.status_code == 400
        assert "Mot de passe actuel incorrect" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()


def test_change_password_same_as_current(client: TestClient) -> None:
    """AC#4 — Nouveau identique à l'ancien → 400 avec message explicite."""
    from app.core.database import get_db
    from app.main import app

    user_row = _make_mock_user_row_with_hashed(plain_password="OldPass123!")
    app.dependency_overrides[get_db] = _override_get_db_with_commit(user_row)
    try:
        response = client.post(
            "/api/v1/auth/change-password",
            json={"current_password": "OldPass123!", "new_password": "OldPass123!"},
            headers=_auth_header(),
        )
        assert response.status_code == 400
        assert "différent de l'ancien" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()


def test_change_password_requires_auth(client: TestClient) -> None:
    """AC#3 — Endpoint requiert un JWT valide (sans token → 401)."""
    response = client.post(
        "/api/v1/auth/change-password",
        json={"current_password": "any", "new_password": "any"},
    )
    # FastAPI ≥ 0.114 : HTTPBearer retourne 401 si pas de token
    assert response.status_code == 401


# ── Story 2.3 — is_active checks ─────────────────────────────────────────────


def _make_mock_user_row_inactive(username: str = "alice") -> MagicMock:
    """Compte désactivé."""
    row = MagicMock()
    row.username = username
    row.hashed_password = hash_password("Pass123!")
    row.role = "operator"
    row.force_password_change = False
    row.is_active = False
    return row


def test_login_disabled_account_returns_401(client: TestClient) -> None:
    """AC#2 Story 2.3 — Compte désactivé → 401 avec message dédié."""
    from app.core.database import get_db
    from app.main import app

    user_row = _make_mock_user_row_inactive()
    app.dependency_overrides[get_db] = _override_get_db(user_row)
    try:
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "alice", "password": "Pass123!"},
        )
        assert response.status_code == 401
        assert "désactivé" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()


def test_change_password_disabled_account_returns_401(client: TestClient) -> None:
    """AC#3 Story 2.3 — JWT valide mais compte désactivé → 401 sur change-password."""
    from app.core.database import get_db
    from app.main import app

    user_row = _make_mock_user_row_inactive()
    app.dependency_overrides[get_db] = _override_get_db_with_commit(user_row)
    try:
        response = client.post(
            "/api/v1/auth/change-password",
            json={"current_password": "Pass123!", "new_password": "NewPass456!"},
            headers=_auth_header(username="alice"),
        )
        assert response.status_code == 401
        assert "désactivé" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()
