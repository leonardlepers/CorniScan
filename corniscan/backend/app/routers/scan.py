# Routeur scan — Story 3.2 + Story 4.1 + Story 4.5 + Epic 5
# POST /api/v1/scan/detect-card   → détection carte live (synchrone, thread pool)
# POST /api/v1/scan/process       → pipeline complet (Stories 4.x)
# POST /api/v1/scan/submit        → DXF + PNG contour + email Resend (Stories 4.5, 5.1, 5.2)

import asyncio
import json

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.core.config import settings
from app.core.security import get_current_user
from app.services.dxf_service import generate_dxf
from app.services.email_service import send_scan_email
from app.services.vision_service import detect_card, generate_contour_png, pdf_to_image_bytes, process_image

router = APIRouter(prefix="/api/v1/scan", tags=["scan"])

_MAX_IMAGE_SIZE = 20 * 1024 * 1024  # 20 Mo (PDF inclus)


def _normalise_to_image_bytes(file: UploadFile, raw: bytes) -> bytes:
    """Convertit en JPEG si le fichier est un PDF, sinon renvoie raw tel quel."""
    ct = (file.content_type or "").lower()
    fn = (file.filename or "").lower()
    if "pdf" in ct or fn.endswith(".pdf"):
        return pdf_to_image_bytes(raw)
    return raw


@router.post("/detect-card")
async def detect_card_endpoint(
    file: UploadFile = File(...),
    _: dict = Depends(get_current_user),
) -> dict:
    """Détecte une carte bancaire dans la frame JPEG reçue (Story 3.2 — FR10).

    Appelé toutes les 500ms par le frontend pendant le flux caméra.
    La détection OpenCV tourne dans un thread pool pour ne pas bloquer l'event loop.

    Returns:
        {"card_detected": bool, "confidence": float}
    """
    image_bytes = await file.read()

    if len(image_bytes) > _MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Image trop volumineuse (max 10 Mo).",
        )

    # Exécution synchrone dans un thread pool — ne bloque pas l'event loop (NFR-P4)
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, detect_card, image_bytes)

    return result


@router.post("/process")
def process_image_endpoint(
    file: UploadFile = File(...),
    _: dict = Depends(get_current_user),
) -> dict:
    """Pipeline complet d'analyse : homographie + perspective + contour joint + dimensions (Story 4.1 — FR14-18).

    Déclaré `def` synchrone — Uvicorn l'exécute dans son thread pool,
    adapté au code CPU-bound OpenCV sans bloquer l'event loop (NFR-P4).
    Aucune donnée n'est persistée côté serveur (NFR-S4).

    Returns:
        {
            "contour_points": list[list[float]],
            "dimensions": {"width_mm": float, "height_mm": float},
            "calibration_warning": bool,
        }
    """
    image_bytes = file.file.read()

    if len(image_bytes) > _MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Fichier trop volumineux (max 20 Mo).",
        )

    image_bytes = _normalise_to_image_bytes(file, image_bytes)

    try:
        result = process_image(image_bytes)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return result


@router.post("/submit")
def submit_scan_endpoint(
    file: UploadFile = File(...),
    contour_points: str = Form(...),
    width_mm: float = Form(...),
    height_mm: float = Form(...),
    thickness: float | None = Form(None),
    calibration_warning: bool = Form(False),
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Pipeline complet de livraison : DXF R2018 + PNG contour + email Resend (Stories 4.5, 5.1, 5.2 — FR24–27).

    Exécuté en `def` synchrone (thread pool Uvicorn).
    Aucune donnée n'est persistée côté serveur (NFR-S4).

    Returns:
        {"status": "accepted"}
    """
    image_bytes = file.file.read()

    if len(image_bytes) > _MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Fichier trop volumineux (max 20 Mo).",
        )

    image_bytes = _normalise_to_image_bytes(file, image_bytes)

    try:
        points: list[list[float]] = json.loads(contour_points)
    except (json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="contour_points invalide.",
        ) from exc

    # Story 5.1 — génération DXF R2018
    try:
        dxf_bytes = generate_dxf(points, width_mm, height_mm)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Génération DXF échouée : {exc}",
        ) from exc

    # Story 5.2 — PNG contour superposé
    try:
        png_bytes = generate_contour_png(image_bytes, points)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    # Story 5.2 — envoi email Resend (retry intégré dans send_scan_email)
    try:
        send_scan_email(
            dxf_bytes=dxf_bytes,
            png_bytes=png_bytes,
            jpeg_bytes=image_bytes,
            width_mm=width_mm,
            height_mm=height_mm,
            thickness=thickness,
            calibration_warning=calibration_warning,
            operator_name=current_user["username"],
            api_key=settings.resend_api_key,
            from_email=settings.resend_from_email,
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    return {"status": "accepted"}
