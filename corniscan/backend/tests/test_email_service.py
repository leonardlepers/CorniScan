"""Tests Story 5.2 — email_service.send_scan_email()."""

from unittest.mock import MagicMock, call, patch

import pytest


_KWARGS = dict(
    dxf_bytes=b"DXF_CONTENT",
    png_bytes=b"PNG_CONTENT",
    jpeg_bytes=b"JPEG_CONTENT",
    width_mm=30.5,
    height_mm=20.0,
    thickness=2.5,
    calibration_warning=False,
    operator_name="alice",
    api_key="re_test_key",
    from_email="corniscan@cornille-sa.com",
)


def test_send_scan_email_calls_resend(monkeypatch: pytest.MonkeyPatch) -> None:
    """AC#1 (FR26) — Resend.Emails.send est appelé une fois en cas de succès."""
    import resend
    from app.services.email_service import send_scan_email

    mock_send = MagicMock(return_value=MagicMock(id="msg_123"))
    monkeypatch.setattr(resend.Emails, "send", mock_send)

    send_scan_email(**_KWARGS)

    mock_send.assert_called_once()


def test_send_scan_email_recipient(monkeypatch: pytest.MonkeyPatch) -> None:
    """AC#1 (FR26) — Destinataire = info@cornille-sa.com."""
    import resend
    from app.services.email_service import send_scan_email

    mock_send = MagicMock(return_value=MagicMock(id="msg_123"))
    monkeypatch.setattr(resend.Emails, "send", mock_send)

    send_scan_email(**_KWARGS)

    params = mock_send.call_args[0][0]
    assert params["to"] == ["info@cornille-sa.com"]


def test_send_scan_email_subject_format(monkeypatch: pytest.MonkeyPatch) -> None:
    """AC#2 (FR27) — Sujet suit le format [CorniScan] ..."""
    import resend
    from app.services.email_service import send_scan_email

    mock_send = MagicMock(return_value=MagicMock(id="msg_123"))
    monkeypatch.setattr(resend.Emails, "send", mock_send)

    send_scan_email(**_KWARGS)

    subject = mock_send.call_args[0][0]["subject"]
    assert subject.startswith("[CorniScan]")
    assert "alice" in subject
    assert "30.5" in subject
    assert "20.0" in subject
    assert "2.5mm" in subject


def test_send_scan_email_calibration_warning_in_body(monkeypatch: pytest.MonkeyPatch) -> None:
    """AC#3 (FR29) — Corps inclut le flag avertissement si calibration_warning = True."""
    import resend
    from app.services.email_service import send_scan_email

    mock_send = MagicMock(return_value=MagicMock(id="msg_123"))
    monkeypatch.setattr(resend.Emails, "send", mock_send)

    send_scan_email(**{**_KWARGS, "calibration_warning": True})

    body = mock_send.call_args[0][0]["text"]
    assert "AVERTISSEMENT" in body
    assert "calibration insuffisante" in body


def test_send_scan_email_no_warning_in_body_when_false(monkeypatch: pytest.MonkeyPatch) -> None:
    """AC#3 — Pas d'avertissement dans le corps si calibration_warning = False."""
    import resend
    from app.services.email_service import send_scan_email

    mock_send = MagicMock(return_value=MagicMock(id="msg_123"))
    monkeypatch.setattr(resend.Emails, "send", mock_send)

    send_scan_email(**_KWARGS)

    body = mock_send.call_args[0][0]["text"]
    assert "AVERTISSEMENT" not in body


def test_send_scan_email_has_3_attachments(monkeypatch: pytest.MonkeyPatch) -> None:
    """AC#1 (FR26) — 3 pièces jointes : DXF + PNG + JPEG."""
    import resend
    from app.services.email_service import send_scan_email

    mock_send = MagicMock(return_value=MagicMock(id="msg_123"))
    monkeypatch.setattr(resend.Emails, "send", mock_send)

    send_scan_email(**_KWARGS)

    attachments = mock_send.call_args[0][0]["attachments"]
    assert len(attachments) == 3
    filenames = {a["filename"] for a in attachments}
    assert "joint.dxf" in filenames
    assert "contour.png" in filenames
    assert "original.jpg" in filenames


def test_send_scan_email_retries_on_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    """AC#4 (NFR-I3) — 3 tentatives au total, 2s de délai entre elles."""
    import resend
    from app.services.email_service import send_scan_email

    mock_send = MagicMock(side_effect=Exception("Resend API down"))
    monkeypatch.setattr(resend.Emails, "send", mock_send)
    mock_sleep = MagicMock()
    monkeypatch.setattr("app.services.email_service.time.sleep", mock_sleep)

    with pytest.raises(RuntimeError, match="3 tentatives"):
        send_scan_email(**_KWARGS)

    assert mock_send.call_count == 3
    # 2 retries → 2 appels à sleep avec 2s
    assert mock_sleep.call_count == 2
    mock_sleep.assert_called_with(2)


def test_send_scan_email_succeeds_on_second_attempt(monkeypatch: pytest.MonkeyPatch) -> None:
    """AC#4 (NFR-I3) — Succès à la 2e tentative → pas d'exception."""
    import resend
    from app.services.email_service import send_scan_email

    mock_send = MagicMock(side_effect=[Exception("fail"), MagicMock(id="ok")])
    monkeypatch.setattr(resend.Emails, "send", mock_send)
    monkeypatch.setattr("app.services.email_service.time.sleep", MagicMock())

    send_scan_email(**_KWARGS)  # ne doit pas lever

    assert mock_send.call_count == 2


def test_send_scan_email_thickness_none(monkeypatch: pytest.MonkeyPatch) -> None:
    """AC#1 — thickness None → 'N/A' dans le corps et le sujet."""
    import resend
    from app.services.email_service import send_scan_email

    mock_send = MagicMock(return_value=MagicMock(id="msg_123"))
    monkeypatch.setattr(resend.Emails, "send", mock_send)

    send_scan_email(**{**_KWARGS, "thickness": None})

    params = mock_send.call_args[0][0]
    assert "N/A" in params["subject"]
    assert "N/A" in params["text"]
