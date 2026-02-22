"""Seed de bootstrap — crée le compte admin par défaut si absent (Story 1.2).

Story 1.3 : hash_password et verify_password déplacés dans security.py (source unique).
Ils sont re-exportés ici pour compatibilité avec les tests Story 1.2.
"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from app.core.security import hash_password, verify_password

# Re-exportés pour compatibilité avec les tests Story 1.2
__all__ = ["hash_password", "verify_password", "seed_admin", "ADMIN_DEFAULT_PASSWORD"]

# Mot de passe provisoire admin — l'admin est forcé de le changer au premier login (Story 1.4)
ADMIN_DEFAULT_PASSWORD = "Admin123!"


async def seed_admin(conn: AsyncConnection) -> None:
    """Insère le compte admin par défaut si inexistant.

    Idempotent : ne réinsère pas si 'admin' existe déjà.
    """
    result = await conn.execute(
        text("SELECT COUNT(*) FROM users WHERE username = 'admin'")
    )
    count = result.scalar()
    if count == 0:
        hashed = hash_password(ADMIN_DEFAULT_PASSWORD)
        await conn.execute(
            text(
                "INSERT INTO users (username, hashed_password, role, force_password_change, is_active) "
                "VALUES ('admin', :hashed, 'admin', true, true)"
            ),
            {"hashed": hashed},
        )
        await conn.commit()
