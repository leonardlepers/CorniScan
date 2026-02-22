# Story 1.2: Base de données et table utilisateurs

Status: review

## Story

As a développeur,
I want provisionner la base de données PostgreSQL Neon et créer la table `users` via Alembic,
So that le système peut persister les comptes utilisateurs de façon sécurisée dès le premier démarrage.

## Acceptance Criteria

1. **Given** un compte Neon free tier est créé et la `DATABASE_URL` est configurée dans les variables d'environnement Render **When** l'application FastAPI démarre (via lifespan event) **Then** Alembic exécute automatiquement les migrations en attente sans erreur, sans intervention manuelle

2. **Given** la migration initiale est appliquée **When** on inspecte la base de données **Then** la table `users` existe avec les colonnes : `id` (UUID), `username` (VARCHAR unique), `hashed_password` (VARCHAR), `role` (VARCHAR : 'operator'/'admin'), `force_password_change` (BOOLEAN, défaut TRUE), `created_at` (TIMESTAMP) **And** aucune autre table ni colonne n'est créée (NFR-S4 — données minimales)

3. **Given** un mot de passe en clair est fourni lors de la création ou mise à jour d'un compte **When** le système le persiste en base **Then** seul le hash bcrypt (salt cost ≥ 12) est stocké — jamais le mot de passe en clair (NFR-S1)

4. **Given** les migrations sont appliquées et la base est vide **When** un seed de bootstrap est exécuté **Then** un compte admin par défaut existe (`admin` / mot de passe provisoire documenté) avec `role='admin'` et `force_password_change=true`

## Tasks / Subtasks

- [x] Task 1: Créer `app/core/database.py` (AC: #1)
  - [x] 1.1 Créer `create_async_engine` avec `pool_size=2` (contrainte Neon free tier)
  - [x] 1.2 Créer `async_sessionmaker` et `get_db` dependency FastAPI
  - [x] 1.3 Gérer le cas `DATABASE_URL=""` (dev sans base) — engine=None, pas d'erreur au démarrage

- [x] Task 2: Créer `app/models/user.py` (AC: #2)
  - [x] 2.1 Définir `Table("users", metadata, ...)` avec toutes les colonnes exactes
  - [x] 2.2 Colonnes : id (UUID gen_random_uuid()), username (VARCHAR 50 UNIQUE), hashed_password (VARCHAR 255), role (VARCHAR 10, défaut 'operator'), force_password_change (BOOLEAN, défaut true), created_at (TIMESTAMP NOW())

- [x] Task 3: Configurer Alembic (AC: #1, #2)
  - [x] 3.1 Créer `alembic.ini` à la racine de `backend/`
  - [x] 3.2 Créer `alembic/env.py` avec support async (asyncio + async_engine_from_config)
  - [x] 3.3 Créer `alembic/script.py.mako` (template standard)
  - [x] 3.4 Créer la migration initiale `alembic/versions/001_create_users_table.py`

- [x] Task 4: Créer `app/core/seed.py` (AC: #3, #4)
  - [x] 4.1 Hachage bcrypt cost=12 via passlib (`CryptContext(bcrypt__rounds=12)`)
  - [x] 4.2 Fonction `seed_admin(conn)` — insère admin si absent, ne pas re-insérer si déjà présent
  - [x] 4.3 Mot de passe provisoire documenté : `Admin123!` (à changer au premier login)

- [x] Task 5: Mettre à jour `app/main.py` avec lifespan event (AC: #1, #4)
  - [x] 5.1 Ajouter `@asynccontextmanager lifespan(app)` avec `alembic upgrade head`
  - [x] 5.2 Appeler `seed_admin` via l'engine après les migrations (si DATABASE_URL configuré)
  - [x] 5.3 Passer `lifespan=lifespan` à `FastAPI(...)`

- [x] Task 6: Écrire les tests Story 1.2 (AC: #3)
  - [x] 6.1 Test hachage bcrypt — vérifier que hash généré est valide et jamais le plain text
  - [x] 6.2 Test bcrypt cost ≥ 12 — vérifier les rounds
  - [x] 6.3 Test seed_admin — mock connexion, vérifier INSERT conditionnel
  - [x] 6.4 Test migration file importable et révision correcte

## Dev Notes

### `app/core/database.py` — Code exact

```python
# backend/app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text
from app.core.config import settings

# pool_size=2 : contrainte Neon free tier (max 5 connexions)
engine = (
    create_async_engine(settings.database_url, pool_size=2, max_overflow=0)
    if settings.database_url
    else None
)

AsyncSessionLocal = (
    async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    if engine
    else None
)

async def get_db():
    """Dependency FastAPI — fournit une session SQLAlchemy async."""
    if AsyncSessionLocal is None:
        raise RuntimeError("DATABASE_URL non configurée")
    async with AsyncSessionLocal() as session:
        yield session
```

### `app/models/user.py` — Code exact

```python
# backend/app/models/user.py
from sqlalchemy import Table, Column, String, Boolean, DateTime, MetaData
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import text

metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")),
    Column("username", String(50), nullable=False, unique=True),
    Column("hashed_password", String(255), nullable=False),
    Column("role", String(10), nullable=False, server_default="operator"),
    Column("force_password_change", Boolean(), nullable=False, server_default=text("true")),
    Column("created_at", DateTime(timezone=True), server_default=text("NOW()")),
)
```

### `app/core/seed.py` — Code exact

```python
# backend/app/core/seed.py
"""Seed de bootstrap — crée le compte admin par défaut si absent."""
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy import text

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

# Mot de passe provisoire — l'admin est forcé de le changer au premier login
ADMIN_DEFAULT_PASSWORD = "Admin123!"

async def seed_admin(conn: AsyncConnection) -> None:
    """Insère le compte admin par défaut si la table users est vide."""
    result = await conn.execute(text("SELECT COUNT(*) FROM users WHERE username = 'admin'"))
    count = result.scalar()
    if count == 0:
        hashed = _pwd_context.hash(ADMIN_DEFAULT_PASSWORD)
        await conn.execute(
            text(
                "INSERT INTO users (username, hashed_password, role, force_password_change) "
                "VALUES ('admin', :hashed, 'admin', true)"
            ),
            {"hashed": hashed},
        )
        await conn.commit()
```

### `app/main.py` — Lifespan event (ajout Story 1.2)

```python
# backend/app/main.py — version Story 1.2
import os
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from alembic.config import Config as AlembicConfig
from alembic import command as alembic_command
from app.core.config import settings

def run_migrations() -> None:
    """Exécute alembic upgrade head via l'API Python Alembic."""
    alembic_cfg = AlembicConfig(str(Path(__file__).parent.parent / "alembic.ini"))
    alembic_command.upgrade(alembic_cfg, "head")

@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.database_url:
        run_migrations()
        from app.core.database import engine
        from app.core.seed import seed_admin
        async with engine.connect() as conn:
            await seed_admin(conn)
    yield

app = FastAPI(
    title="CorniScan API",
    version="0.1.0",
    docs_url="/docs" if settings.environment != "production" else None,
    redoc_url=None,
    lifespan=lifespan,
)
...
```

### `alembic.ini` — Configuration

```ini
[alembic]
script_location = alembic
# sqlalchemy.url sera surchargé par env.py (lit DATABASE_URL)
sqlalchemy.url = driver://user:pass@localhost/dbname
```

### Mot de passe admin par défaut

**Mot de passe provisoire : `Admin123!`**

⚠️ L'admin a `force_password_change=true` — le mot de passe provisoire doit être changé au premier login (Story 1.4). Ne jamais utiliser ce mot de passe en production sans l'avoir changé.

### Contrainte Neon free tier

`pool_size=2, max_overflow=0` : Neon free tier limite à 5 connexions simultanées max. Avec 1 seul worker uvicorn en production, 2 connexions dans le pool sont suffisantes et laissent de la marge pour les migrations Alembic.

### Structure de fichiers EXACTE après Story 1.2

```
corniscan/backend/
├── alembic.ini
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 001_create_users_table.py
├── app/
│   ├── core/
│   │   ├── config.py         ← inchangé
│   │   ├── database.py       ← NOUVEAU
│   │   └── seed.py           ← NOUVEAU
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py           ← NOUVEAU
│   └── main.py               ← MODIFIÉ (lifespan event)
└── tests/
    └── test_database.py      ← NOUVEAU
```

### References

- Schéma table users: [Source: epics.md#Story 1.2 AC]
- pool_size=2 Neon constraint: [Source: architecture.md#Data Architecture]
- bcrypt cost ≥ 12: [Source: architecture.md#Authentication & Security]
- lifespan alembic upgrade head: [Source: architecture.md#Infrastructure & Deployment]
- Alembic async setup: [Source: architecture.md#Data Architecture]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- `passlib` 1.7.4 + `bcrypt` 5.x incompatibles (`detect_wrap_bug` crash) → utilisation de `bcrypt` directement dans `seed.py` à la place de `passlib.CryptContext`. `passlib` reste dans `pyproject.toml` pour Story 1.3 (à réévaluer si même incompatibilité).
- `pytest-asyncio` manquant → ajouté en dev dependency + `asyncio_mode = "auto"` dans `pyproject.toml`
- Import migration `001_create_users_table.py` impossible via `import` standard (nom commence par chiffre) → import via `importlib.util.spec_from_file_location`

### Completion Notes List

- ✅ AC#1 : Lifespan event ajouté dans `main.py` — `alembic upgrade head` s'exécute au démarrage si `DATABASE_URL` configurée
- ✅ AC#2 : Table `users` définie dans `app/models/user.py` avec colonnes exactes : id (UUID gen_random_uuid), username (VARCHAR 50 UNIQUE), hashed_password (VARCHAR 255), role (VARCHAR 10, défaut 'operator'), force_password_change (BOOLEAN, défaut true), created_at (TIMESTAMP NOW())
- ✅ AC#3 : `hash_password()` et `verify_password()` dans `seed.py` utilisent `bcrypt` directement (cost=12 — NFR-S1). Jamais le mot de passe en clair n'est stocké.
- ✅ AC#4 : `seed_admin()` insère le compte admin (`Admin123!`, role='admin', force_password_change=true) si absent. Idempotent.
- ✅ 16 tests Story 1.2 passent. 21 tests totaux backend (5 Story 1.1 + 16 Story 1.2) GREEN.
- ⚠️ `DATABASE_URL` Neon à configurer manuellement dans les variables Render avant déploiement
- ⚠️ La migration s'exécutera au premier démarrage sur Render une fois `DATABASE_URL` configurée

### Change Log

- 2026-02-22 — Implémentation Story 1.2 : `database.py`, `user.py`, Alembic (ini + env.py + migration 001), `seed.py`, lifespan event `main.py`. 16 tests Story 1.2 GREEN.

### File List

**Nouveaux (backend) :**
- `corniscan/backend/app/core/database.py` — SQLAlchemy async engine + get_db dependency
- `corniscan/backend/app/core/seed.py` — hash_password, verify_password, seed_admin
- `corniscan/backend/app/models/user.py` — Table SQLAlchemy "users"
- `corniscan/backend/alembic.ini` — Configuration Alembic
- `corniscan/backend/alembic/env.py` — Env Alembic async (asyncio + async_engine_from_config)
- `corniscan/backend/alembic/script.py.mako` — Template migrations
- `corniscan/backend/alembic/versions/001_create_users_table.py` — Migration initiale
- `corniscan/backend/tests/test_database.py` — 16 tests Story 1.2

**Modifiés :**
- `corniscan/backend/app/main.py` — Ajout lifespan event (alembic upgrade head + seed_admin)
- `corniscan/backend/pyproject.toml` — Ajout pytest-asyncio dev dep + asyncio_mode=auto
