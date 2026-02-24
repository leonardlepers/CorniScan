"""Définition SQLAlchemy de la table users — Story 1.2 + Story 2.1."""

from sqlalchemy import Boolean, Column, DateTime, MetaData, String, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import text

metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column(
        "id",
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    ),
    Column("username", String(50), nullable=False, unique=True),
    Column("hashed_password", String(255), nullable=False),
    # Valeurs autorisées : 'operator' | 'admin'
    Column("role", String(10), nullable=False, server_default=text("'operator'")),
    Column(
        "force_password_change",
        Boolean(),
        nullable=False,
        server_default=text("true"),
    ),
    # Story 2.1 — statut actif/inactif (désactivation Story 2.3)
    Column(
        "is_active",
        Boolean(),
        nullable=False,
        server_default=text("true"),
    ),
    Column("created_at", DateTime(timezone=True), server_default=text("NOW()")),
    Column("last_login_at", DateTime(timezone=True), nullable=True),
)
