"""Fonctions de sécurité — JWT et hachage bcrypt (Story 1.3)."""

from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.core.config import settings

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 8
_BCRYPT_ROUNDS = 12

_http_bearer = HTTPBearer()


def hash_password(plain_password: str) -> str:
    """Retourne le hash bcrypt (cost=12) d'un mot de passe en clair."""
    salt = bcrypt.gensalt(rounds=_BCRYPT_ROUNDS)
    return bcrypt.hashpw(plain_password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie qu'un mot de passe en clair correspond au hash stocké."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def create_access_token(data: dict) -> str:
    """Crée un JWT HS256 avec expiration à 8h."""
    to_encode = data.copy()
    to_encode["exp"] = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=ALGORITHM)


def verify_token(token: str) -> dict:
    """Décode et valide un JWT. Lève JWTError si invalide ou expiré."""
    return jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_http_bearer),
) -> dict:
    """Dependency FastAPI — extrait et valide le JWT depuis le header Authorization."""
    try:
        payload = verify_token(credentials.credentials)
        return {
            "username": payload["sub"],
            "role": payload["role"],
            "force_password_change": payload.get("force_password_change", False),
        }
    except (JWTError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré.",
            headers={"WWW-Authenticate": "Bearer"},
        )
