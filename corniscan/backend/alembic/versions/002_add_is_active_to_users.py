"""Add is_active to users

Revision ID: 002
Revises: 001
Create Date: 2026-02-22

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Ajoute la colonne is_active (Story 2.1 — statut actif/inactif)."""
    op.add_column(
        "users",
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
    )


def downgrade() -> None:
    """Supprime la colonne is_active."""
    op.drop_column("users", "is_active")
