"""Service d'envoi email — Story 5.2 (FR26, FR27, FR29, NFR-I3, NFR-S4).

Envoie le dossier scan complet à info@cornille-sa.com via le SDK Resend.
3 tentatives au total (1 initiale + 2 retries) avec 2s d'intervalle (NFR-I3).
Aucun fichier n'est persisté sur le serveur (NFR-S4).
"""

import time
from datetime import datetime

import resend

_RECIPIENT = "info@cornille-sa.com"
_MAX_ATTEMPTS = 3
_RETRY_DELAY_S = 2


def send_scan_email(
    *,
    dxf_bytes: bytes,
    png_bytes: bytes,
    jpeg_bytes: bytes,
    width_mm: float,
    height_mm: float,
    thickness: float | None,
    calibration_warning: bool,
    operator_name: str,
    api_key: str,
    from_email: str,
) -> None:
    """Envoie le dossier scan par email via Resend (Story 5.2 — FR26).

    Args:
        dxf_bytes: Fichier DXF généré (Story 5.1).
        png_bytes: PNG contour superposé.
        jpeg_bytes: JPEG original soumis par l'opérateur.
        width_mm: Largeur du joint en mm.
        height_mm: Hauteur du joint en mm.
        thickness: Épaisseur saisie en mm, ou None si non renseignée.
        calibration_warning: True si calibration insuffisante.
        operator_name: Nom d'utilisateur de l'opérateur (JWT sub).
        api_key: Clé API Resend.
        from_email: Adresse expéditeur vérifiée dans Resend.

    Raises:
        RuntimeError: Si toutes les tentatives d'envoi échouent.
    """
    resend.api_key = api_key

    now = datetime.now()
    thickness_str = f"{thickness}mm" if thickness is not None else "N/A"

    # Format sujet structuré (FR27, NFR-I4)
    subject = (
        f"[CorniScan] {now.strftime('%Y-%m-%d %H:%M')} — {operator_name}"
        f" — {width_mm:.1f}×{height_mm:.1f}mm — ép.{thickness_str}"
    )

    body_lines = [
        f"Opérateur : {operator_name}",
        f"Date : {now.strftime('%Y-%m-%d %H:%M')}",
        f"Dimensions : {width_mm:.1f} × {height_mm:.1f} mm",
        f"Épaisseur : {thickness_str}",
    ]

    # Flag calibration insuffisante (FR29)
    if calibration_warning:
        body_lines.insert(
            0,
            "⚠️ AVERTISSEMENT : scan envoyé malgré une calibration insuffisante"
            " (moins de 4 coins de la carte détectés)",
        )

    body = "\n".join(body_lines)

    params: resend.Emails.SendParams = {
        "from": from_email,
        "to": [_RECIPIENT],
        "subject": subject,
        "text": body,
        "attachments": [
            {"filename": "joint.dxf", "content": list(dxf_bytes)},
            {"filename": "contour.png", "content": list(png_bytes)},
            {"filename": "original.jpg", "content": list(jpeg_bytes)},
        ],
    }

    last_exc: Exception | None = None
    for attempt in range(_MAX_ATTEMPTS):
        try:
            resend.Emails.send(params)
            return  # Succès
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            if attempt < _MAX_ATTEMPTS - 1:
                time.sleep(_RETRY_DELAY_S)

    raise RuntimeError(
        f"Envoi email échoué après {_MAX_ATTEMPTS} tentatives : {last_exc}"
    ) from last_exc
