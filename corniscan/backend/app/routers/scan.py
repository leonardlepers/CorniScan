# Routeur scan — Story 3.2 + Story 4.1
# POST /api/v1/scan/detect-card   → détection carte live (synchrone, thread pool)
# POST /api/v1/scan/process       → pipeline complet (Stories 4.x)
# POST /api/v1/scan/send          → envoi email DXF (Story 5.x)

import asyncio

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.core.security import get_current_user
from app.services.vision_service import detect_card, process_image

router = APIRouter(prefix="/api/v1/scan", tags=["scan"])

_MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 Mo


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
            detail="Image trop volumineuse (max 10 Mo).",
        )

    try:
        result = process_image(image_bytes)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return result
