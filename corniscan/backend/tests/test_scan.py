"""Tests Story 3.2 + Story 4.1 + Story 4.5 — POST /api/v1/scan/detect-card + /process + /submit + vision_service."""

import io
from unittest.mock import MagicMock, patch

import numpy as np
import cv2
import pytest
from fastapi.testclient import TestClient

from app.core.security import create_access_token


# ── Helpers ───────────────────────────────────────────────────────────────────


def _auth_header(role: str = "operator") -> dict:
    token = create_access_token({"sub": "alice", "role": role, "force_password_change": False})
    return {"Authorization": f"Bearer {token}"}


def _make_jpeg(width: int = 640, height: int = 480, color: tuple = (128, 128, 128)) -> bytes:
    """Génère un JPEG vierge de la taille demandée."""
    img = np.full((height, width, 3), color, dtype=np.uint8)
    _, encoded = cv2.imencode(".jpg", img)
    return encoded.tobytes()


def _make_jpeg_with_card(width: int = 640, height: int = 480) -> bytes:
    """Génère un JPEG avec un rectangle blanc simulant une carte bancaire."""
    img = np.zeros((height, width, 3), dtype=np.uint8)
    # Carte ≈ 40% de la largeur, ratio 1.586
    card_w = int(width * 0.50)
    card_h = int(card_w / 1.586)
    x0 = (width - card_w) // 2
    y0 = (height - card_h) // 2
    cv2.rectangle(img, (x0, y0), (x0 + card_w, y0 + card_h), (255, 255, 255), -1)
    _, encoded = cv2.imencode(".jpg", img)
    return encoded.tobytes()


# ── Tests vision_service.detect_card ─────────────────────────────────────────


def test_detect_card_returns_not_detected_on_blank_image() -> None:
    """Image vide → card_detected = False."""
    from app.services.vision_service import detect_card

    result = detect_card(_make_jpeg())
    assert result["card_detected"] is False
    assert isinstance(result["confidence"], float)


def test_detect_card_returns_detected_on_card_image() -> None:
    """Image avec rectangle carte → card_detected = True."""
    from app.services.vision_service import detect_card

    result = detect_card(_make_jpeg_with_card())
    assert result["card_detected"] is True
    assert result["confidence"] > 0.0


def test_detect_card_returns_not_detected_on_invalid_bytes() -> None:
    """Données invalides (non JPEG) → card_detected = False sans exception."""
    from app.services.vision_service import detect_card

    result = detect_card(b"not-an-image")
    assert result["card_detected"] is False


# ── Tests POST /api/v1/scan/detect-card ──────────────────────────────────────


def test_detect_card_endpoint_returns_200(client: TestClient) -> None:
    """AC#1 — Upload JPEG valide → 200 + card_detected bool."""
    jpeg_bytes = _make_jpeg()
    response = client.post(
        "/api/v1/scan/detect-card",
        files={"file": ("frame.jpg", io.BytesIO(jpeg_bytes), "image/jpeg")},
        headers=_auth_header(),
    )
    assert response.status_code == 200
    data = response.json()
    assert "card_detected" in data
    assert isinstance(data["card_detected"], bool)
    assert "confidence" in data


def test_detect_card_endpoint_requires_auth(client: TestClient) -> None:
    """Sans token → 401."""
    jpeg_bytes = _make_jpeg()
    response = client.post(
        "/api/v1/scan/detect-card",
        files={"file": ("frame.jpg", io.BytesIO(jpeg_bytes), "image/jpeg")},
    )
    assert response.status_code == 401


def test_detect_card_endpoint_detects_card(client: TestClient) -> None:
    """AC#2 — Image avec carte → card_detected = True."""
    jpeg_bytes = _make_jpeg_with_card()
    response = client.post(
        "/api/v1/scan/detect-card",
        files={"file": ("frame.jpg", io.BytesIO(jpeg_bytes), "image/jpeg")},
        headers=_auth_header(),
    )
    assert response.status_code == 200
    assert response.json()["card_detected"] is True


def test_detect_card_endpoint_no_card_blank_image(client: TestClient) -> None:
    """AC#3 — Image vide → card_detected = False."""
    jpeg_bytes = _make_jpeg()
    response = client.post(
        "/api/v1/scan/detect-card",
        files={"file": ("frame.jpg", io.BytesIO(jpeg_bytes), "image/jpeg")},
        headers=_auth_header(),
    )
    assert response.status_code == 200
    assert response.json()["card_detected"] is False


# ── Tests vision_service.process_image (Story 4.1) ───────────────────────────


def test_process_image_raises_on_invalid_bytes() -> None:
    """Données non JPEG → ValueError."""
    from app.services.vision_service import process_image

    with pytest.raises(ValueError, match="Impossible de décoder"):
        process_image(b"not-an-image")


def test_process_image_returns_expected_keys_on_blank_image() -> None:
    """AC#2 — Image vide → dict avec les 3 clés attendues."""
    from app.services.vision_service import process_image

    result = process_image(_make_jpeg())

    assert "contour_points" in result
    assert "dimensions" in result
    assert "calibration_warning" in result
    assert isinstance(result["contour_points"], list)
    assert isinstance(result["dimensions"]["width_mm"], float)
    assert isinstance(result["dimensions"]["height_mm"], float)
    assert isinstance(result["calibration_warning"], bool)


def test_process_image_calibration_warning_on_blank_image() -> None:
    """AC#3 — Aucune carte détectée → calibration_warning = True."""
    from app.services.vision_service import process_image

    result = process_image(_make_jpeg())

    assert result["calibration_warning"] is True


def test_process_image_no_calibration_warning_with_card() -> None:
    """AC#3 — Carte détectée → calibration_warning = False."""
    from app.services.vision_service import process_image

    result = process_image(_make_jpeg_with_card())

    assert result["calibration_warning"] is False


def test_process_image_dimensions_positive() -> None:
    """AC#2 — Les dimensions retournées sont > 0."""
    from app.services.vision_service import process_image

    result = process_image(_make_jpeg())

    assert result["dimensions"]["width_mm"] > 0
    assert result["dimensions"]["height_mm"] > 0


def test_process_image_contour_points_normalized() -> None:
    """AC#2 — Les coordonnées du contour sont normalisées [0, 1]."""
    from app.services.vision_service import process_image

    result = process_image(_make_jpeg_with_card())

    for pt in result["contour_points"]:
        assert 0.0 <= pt[0] <= 1.0, f"x hors [0,1]: {pt[0]}"
        assert 0.0 <= pt[1] <= 1.0, f"y hors [0,1]: {pt[1]}"


# ── Tests POST /api/v1/scan/process (Story 4.1) ───────────────────────────────


def test_process_endpoint_returns_200_on_blank_image(client: TestClient) -> None:
    """AC#1 — Upload JPEG valide → 200 + structure attendue."""
    jpeg_bytes = _make_jpeg()
    response = client.post(
        "/api/v1/scan/process",
        files={"file": ("photo.jpg", io.BytesIO(jpeg_bytes), "image/jpeg")},
        headers=_auth_header(),
    )
    assert response.status_code == 200
    data = response.json()
    assert "contour_points" in data
    assert "dimensions" in data
    assert "calibration_warning" in data


def test_process_endpoint_requires_auth(client: TestClient) -> None:
    """AC#4 — Sans token → 401."""
    jpeg_bytes = _make_jpeg()
    response = client.post(
        "/api/v1/scan/process",
        files={"file": ("photo.jpg", io.BytesIO(jpeg_bytes), "image/jpeg")},
    )
    assert response.status_code == 401


def test_process_endpoint_calibration_warning_on_blank_image(client: TestClient) -> None:
    """AC#3 — Image sans carte → calibration_warning = True."""
    jpeg_bytes = _make_jpeg()
    response = client.post(
        "/api/v1/scan/process",
        files={"file": ("photo.jpg", io.BytesIO(jpeg_bytes), "image/jpeg")},
        headers=_auth_header(),
    )
    assert response.status_code == 200
    assert response.json()["calibration_warning"] is True


def test_process_endpoint_no_calibration_warning_with_card(client: TestClient) -> None:
    """AC#3 — Image avec carte → calibration_warning = False."""
    jpeg_bytes = _make_jpeg_with_card()
    response = client.post(
        "/api/v1/scan/process",
        files={"file": ("photo.jpg", io.BytesIO(jpeg_bytes), "image/jpeg")},
        headers=_auth_header(),
    )
    assert response.status_code == 200
    assert response.json()["calibration_warning"] is False


def test_process_endpoint_returns_422_on_invalid_bytes(client: TestClient) -> None:
    """AC#1 — Données non JPEG → 422."""
    response = client.post(
        "/api/v1/scan/process",
        files={"file": ("photo.jpg", io.BytesIO(b"not-an-image"), "image/jpeg")},
        headers=_auth_header(),
    )
    assert response.status_code == 422


# ── Tests POST /api/v1/scan/submit (Story 4.5) ───────────────────────────────


@pytest.fixture()
def mock_email(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Neutralise l'appel Resend dans le routeur submit."""
    mock = MagicMock()
    monkeypatch.setattr("app.routers.scan.send_scan_email", mock)
    return mock


def _submit_payload(jpeg_bytes: bytes, *, calibration_warning: bool = False, thickness: float | None = None) -> dict:
    """Construit le payload multipart pour POST /submit."""
    import json as _json

    data = {
        "contour_points": _json.dumps([[0.1, 0.2], [0.9, 0.2], [0.9, 0.8], [0.1, 0.8]]),
        "width_mm": "30.5",
        "height_mm": "20.0",
        "calibration_warning": str(calibration_warning).lower(),
    }
    if thickness is not None:
        data["thickness"] = str(thickness)
    return {
        "files": {"file": ("photo.jpg", io.BytesIO(jpeg_bytes), "image/jpeg")},
        "data": data,
    }


def test_submit_endpoint_returns_200_accepted(client: TestClient, mock_email: MagicMock) -> None:
    """AC#1 — Payload valide → 200 + {"status": "accepted"}."""
    payload = _submit_payload(_make_jpeg())
    response = client.post(
        "/api/v1/scan/submit",
        files=payload["files"],
        data=payload["data"],
        headers=_auth_header(),
    )
    assert response.status_code == 200
    assert response.json() == {"status": "accepted"}


def test_submit_endpoint_requires_auth(client: TestClient) -> None:
    """AC#1 — Sans token → 401."""
    payload = _submit_payload(_make_jpeg())
    response = client.post(
        "/api/v1/scan/submit",
        files=payload["files"],
        data=payload["data"],
    )
    assert response.status_code == 401


def test_submit_endpoint_accepts_calibration_warning_true(client: TestClient, mock_email: MagicMock) -> None:
    """AC#2 — calibration_warning = true accepté sans erreur."""
    payload = _submit_payload(_make_jpeg(), calibration_warning=True)
    response = client.post(
        "/api/v1/scan/submit",
        files=payload["files"],
        data=payload["data"],
        headers=_auth_header(),
    )
    assert response.status_code == 200


def test_submit_endpoint_accepts_thickness(client: TestClient, mock_email: MagicMock) -> None:
    """AC#1 — thickness optionnel transmis."""
    payload = _submit_payload(_make_jpeg(), thickness=2.5)
    response = client.post(
        "/api/v1/scan/submit",
        files=payload["files"],
        data=payload["data"],
        headers=_auth_header(),
    )
    assert response.status_code == 200


def test_submit_endpoint_returns_422_on_invalid_contour(client: TestClient) -> None:
    """AC#1 — contour_points JSON invalide → 422."""
    jpeg_bytes = _make_jpeg()
    response = client.post(
        "/api/v1/scan/submit",
        files={"file": ("photo.jpg", io.BytesIO(jpeg_bytes), "image/jpeg")},
        data={
            "contour_points": "not-json",
            "width_mm": "30.5",
            "height_mm": "20.0",
            "calibration_warning": "false",
        },
        headers=_auth_header(),
    )
    assert response.status_code == 422
