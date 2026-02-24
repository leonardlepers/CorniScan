# Routeur auth — Story 1.3 + Story 1.4 + Story 2.3
# POST /api/v1/auth/token             → login → JWT
# POST /api/v1/auth/change-password   → changement mot de passe forcé

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.models.user import users


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Login — vérifie les credentials et retourne un JWT HS256 (8h).

    Retourne le même message HTTP 401 pour username inconnu et mauvais mot de passe
    (pas de fuite d'information sur l'existence du compte — NFR-S1).
    """
    result = await session.execute(
        select(users).where(users.c.username == form_data.username)
    )
    user_row = result.fetchone()

    if not user_row or not verify_password(form_data.password, user_row.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiant ou mot de passe incorrect.",
        )

    # AC#2 Story 2.3 — compte désactivé
    if not user_row.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ce compte a été désactivé. Contactez votre administrateur.",
        )

    await session.execute(
        update(users)
        .where(users.c.username == user_row.username)
        .values(last_login_at=datetime.now(timezone.utc))
    )
    await session.commit()

    token = create_access_token(
        {
            "sub": user_row.username,
            "role": user_row.role,
            "force_password_change": user_row.force_password_change,
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "username": user_row.username,
            "role": user_row.role,
            "force_password_change": user_row.force_password_change,
        },
    }


@router.post("/change-password")
async def change_password(
    body: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Changement de mot de passe forcé (Story 1.4 — FR3).

    Requiert un JWT valide (Authorization: Bearer).
    Vérifie l'ancien mot de passe, refuse si identique au nouveau,
    met à jour la base et retourne un nouveau JWT avec force_password_change=false.
    """
    result = await session.execute(
        select(users).where(users.c.username == current_user["username"])
    )
    user_row = result.fetchone()

    # AC#3 Story 2.3 — compte désactivé (JWT encore valide mais compte inactif)
    if not user_row.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ce compte a été désactivé. Contactez votre administrateur.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Vérifier le mot de passe actuel
    if not verify_password(body.current_password, user_row.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mot de passe actuel incorrect.",
        )

    # Nouveau mot de passe doit être différent de l'ancien (AC#4)
    if verify_password(body.new_password, user_row.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le nouveau mot de passe doit être différent de l'ancien.",
        )

    # Hacher + persister le nouveau mot de passe
    new_hashed = hash_password(body.new_password)
    await session.execute(
        update(users)
        .where(users.c.username == current_user["username"])
        .values(hashed_password=new_hashed, force_password_change=False)
    )
    await session.commit()

    # Retourner un nouveau JWT avec force_password_change=false
    token = create_access_token(
        {
            "sub": user_row.username,
            "role": user_row.role,
            "force_password_change": False,
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "username": user_row.username,
            "role": user_row.role,
            "force_password_change": False,
        },
    }
