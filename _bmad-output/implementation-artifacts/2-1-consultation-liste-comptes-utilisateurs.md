# Story 2.1: Consultation de la liste des comptes utilisateurs

Status: review

## Story

As an administrateur,
I want consulter la liste de tous les comptes utilisateurs,
So that j'ai une vue d'ensemble des accès à l'application et peux identifier rapidement les comptes à gérer.

## Acceptance Criteria

1. **Given** un administrateur est authentifié et navigue vers la section de gestion des comptes **When** la page se charge **Then** la liste de tous les comptes utilisateurs s'affiche avec pour chaque compte : username, rôle, statut (actif/inactif), date de création, et indicateur de changement de mot de passe en attente (FR5)

2. **Given** la liste est affichée **When** l'administrateur la consulte **Then** son propre compte admin apparaît dans la liste avec le rôle 'admin' clairement identifié

3. **Given** un opérateur (rôle 'operator') est authentifié **When** il tente d'accéder à la page de gestion des comptes **Then** il est redirigé (vers /camera) — guard Vue Router `requireAdmin` déjà en place (Story 1.3)

## Tasks / Subtasks

- [x] Task 1: Migration 002 — colonne `is_active` (AC: #1)
  - [x] 1.1 Ajouter `is_active Boolean NOT NULL DEFAULT true` dans `app/models/user.py`
  - [x] 1.2 Créer `alembic/versions/002_add_is_active_to_users.py`
  - [x] 1.3 Mettre à jour `seed.py` : inclure `is_active=True` à l'INSERT admin

- [x] Task 2: Endpoint `GET /api/v1/admin/users` (AC: #1, #2)
  - [x] 2.1 Créer `app/routers/admin.py` avec dependency `require_admin`
  - [x] 2.2 Implémenter `GET /api/v1/admin/users` → liste triée par `created_at`
  - [x] 2.3 Enregistrer le router admin dans `app/main.py`

- [x] Task 3: Frontend — AdminUsersView + route (AC: #1, #2, #3)
  - [x] 3.1 Créer `src/views/AdminUsersView.vue` (table : username, role, statut, created_at, force_password_change)
  - [x] 3.2 Ajouter route `/admin/users` (`requireAdmin: true`) dans `src/router/index.ts`

- [x] Task 4: Tests backend (AC: #1, #2, #3)
- [x] Task 5: Tests frontend (AC: #1, #3)

## Dev Notes

### `GET /api/v1/admin/users` — Réponse

```json
[
  {
    "username": "admin",
    "role": "admin",
    "is_active": true,
    "created_at": "2026-02-22T10:00:00Z",
    "force_password_change": false
  }
]
```

Triée par `created_at ASC`. Requiert `Authorization: Bearer <token admin>`.
Retourne HTTP 403 si le token est `role=operator`.

### Protection admin

La dependency `require_admin` réutilise `get_current_user` (Story 1.3) et vérifie `role == "admin"`.

```python
def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs.")
    return current_user
```

### Frontend — route et garde

La route `/admin/users` a `meta: { requireAdmin: true }`. Le guard `beforeEach` (Story 1.3, étape 3) redirige les opérateurs vers `/camera` automatiquement.

### References

- FR5: liste comptes admin — [Source: epics.md#Story 2.1]
- Guard requireAdmin: [Source: router/index.ts#beforeEach étape 3]
- Architecture admin: [Source: architecture.md#Cross-Cutting Concerns]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

(aucun)

### Completion Notes List

- `is_active` ajouté via migration 002 (down_revision = 001). Tous les comptes existants reçoivent `true` par défaut.
- `require_admin` dependency réutilise `get_current_user` — pas de duplication JWT.
- Test de timing du loading supprimé (onMounted/Vitest race) ; remplacé par vérification post-flushPromises.
- `test_users_table_columns` (Story 1.2) mis à jour pour inclure `is_active`.
- 44 tests backend GREEN, 26 tests frontend GREEN.

### Change Log

- 2026-02-22 — Story 2.1 implémentée et complète

### File List

- `corniscan/backend/app/models/user.py` — ajout colonne `is_active`
- `corniscan/backend/alembic/versions/002_add_is_active_to_users.py` — migration 002
- `corniscan/backend/app/core/seed.py` — INSERT admin inclut `is_active=True`
- `corniscan/backend/app/routers/admin.py` — nouveau router avec `require_admin` + `GET /api/v1/admin/users`
- `corniscan/backend/app/main.py` — enregistrement admin_router
- `corniscan/backend/tests/test_admin.py` — 9 tests Story 2.1
- `corniscan/backend/tests/test_database.py` — `test_users_table_columns` mis à jour
- `corniscan/frontend/src/views/AdminUsersView.vue` — tableau de liste des comptes
- `corniscan/frontend/src/router/index.ts` — route `/admin/users` (requireAdmin)
- `corniscan/frontend/src/views/__tests__/AdminUsersView.spec.ts` — 6 tests frontend
