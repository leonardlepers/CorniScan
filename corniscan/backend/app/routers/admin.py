# Routeur admin — Story 2.1 + Story 2.2 + Story 2.3
# GET   /api/v1/admin/users                        → liste de tous les comptes
# POST  /api/v1/admin/users                        → création d'un compte opérateur
# PATCH /api/v1/admin/users/{username}/deactivate  → désactivation d'un compte

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, hash_password
from app.models.user import users


class CreateUserRequest(BaseModel):
    username: str
    password: str

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Dependency — lève 403 si le token n'est pas de rôle 'admin'."""
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux administrateurs.",
        )
    return current_user


@router.get("/users")
async def list_users(
    _: dict = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> list[dict]:
    """Retourne la liste de tous les comptes triée par date de création (Story 2.1 — FR5).

    Champs retournés : username, role, is_active, created_at, force_password_change.
    Le mot de passe haché n'est jamais exposé.
    """
    result = await session.execute(
        select(
            users.c.username,
            users.c.role,
            users.c.is_active,
            users.c.created_at,
            users.c.force_password_change,
        ).order_by(users.c.created_at.asc())
    )
    rows = result.fetchall()
    return [
        {
            "username": row.username,
            "role": row.role,
            "is_active": row.is_active,
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "force_password_change": row.force_password_change,
        }
        for row in rows
    ]


@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(
    body: CreateUserRequest,
    _: dict = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Crée un compte opérateur avec mot de passe provisoire (Story 2.2 — FR6).

    Retourne 409 si le username est déjà pris.
    Le compte est créé avec role='operator', force_password_change=true, is_active=true.
    """
    # Vérifier l'unicité du username avant l'INSERT
    result = await session.execute(
        select(users.c.username).where(users.c.username == body.username)
    )
    if result.fetchone() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ce nom d'utilisateur existe déjà.",
        )

    hashed = hash_password(body.password)
    stmt = (
        insert(users)
        .values(
            username=body.username,
            hashed_password=hashed,
            role="operator",
            force_password_change=True,
            is_active=True,
        )
        .returning(
            users.c.username,
            users.c.role,
            users.c.is_active,
            users.c.created_at,
            users.c.force_password_change,
        )
    )
    try:
        result = await session.execute(stmt)
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ce nom d'utilisateur existe déjà.",
        )

    row = result.fetchone()
    return {
        "username": row.username,
        "role": row.role,
        "is_active": row.is_active,
        "created_at": row.created_at.isoformat() if row.created_at else None,
        "force_password_change": row.force_password_change,
    }


@router.patch("/users/{username}/deactivate")
async def deactivate_user(
    username: str,
    current_admin: dict = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Désactive un compte utilisateur (Story 2.3 — FR7).

    Retourne 400 si l'admin tente de désactiver son propre compte.
    Retourne 404 si l'utilisateur est introuvable.
    """
    # AC#4 — protection propre compte
    if current_admin["username"] == username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible de désactiver votre propre compte.",
        )

    # Vérifier que l'utilisateur existe
    result = await session.execute(
        select(
            users.c.username,
            users.c.role,
            users.c.is_active,
            users.c.created_at,
            users.c.force_password_change,
        ).where(users.c.username == username)
    )
    user_row = result.fetchone()
    if user_row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Utilisateur '{username}' introuvable.",
        )

    # Désactiver le compte
    await session.execute(
        update(users).where(users.c.username == username).values(is_active=False)
    )
    await session.commit()

    return {
        "username": user_row.username,
        "role": user_row.role,
        "is_active": False,
        "created_at": user_row.created_at.isoformat() if user_row.created_at else None,
        "force_password_change": user_row.force_password_change,
    }
