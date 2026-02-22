# Routeur scan — implémenté en Stories 3.x / 4.x / 5.x
# POST /api/v1/scan/detect-card   → détection carte live (def synchrone — thread pool)
# POST /api/v1/scan/process       → pipeline complet (def synchrone — thread pool)
# POST /api/v1/scan/send          → envoi email DXF

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/scan", tags=["scan"])
