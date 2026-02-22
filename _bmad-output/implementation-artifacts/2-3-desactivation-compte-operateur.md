# Story 2.3: Désactivation d'un compte opérateur

Status: review

## Story

As an administrateur,
I want désactiver un compte opérateur,
So that je peux révoquer immédiatement l'accès d'un opérateur sans supprimer son historique.

## Acceptance Criteria

1. **Given** un administrateur clique sur "Désactiver" sur un compte opérateur actif **When** l'action est soumise **Then** le compte est marqué `is_active=false` en base et son statut est mis à jour dans la liste (FR7)

2. **Given** un compte opérateur vient d'être désactivé **When** cet opérateur tente de se connecter **Then** le backend retourne HTTP 401 avec "Ce compte a été désactivé. Contactez votre administrateur."

3. **Given** un opérateur possède une session JWT active et son compte est désactivé **When** il effectue la prochaine requête API (ex: change-password) **Then** le backend retourne HTTP 401 et le frontend redirige vers `/login`

4. **Given** un administrateur tente de désactiver son propre compte **When** l'action est soumise **Then** le backend retourne 400 "Impossible de désactiver votre propre compte." et le compte reste actif

## Tasks / Subtasks

- [x] Task 1: Backend — is_active check dans login (AC: #2)
  - [x] 1.1 Dans `POST /api/v1/auth/token` : si `is_active=false` → 401 avec message dédié

- [x] Task 2: Backend — is_active check dans change-password (AC: #3)
  - [x] 2.1 Dans `POST /api/v1/auth/change-password` : si `is_active=false` → 401 avec message dédié

- [x] Task 3: Backend — `PATCH /api/v1/admin/users/{username}/deactivate` (AC: #1, #4)
  - [x] 3.1 404 si user introuvable
  - [x] 3.2 400 si l'admin tente de désactiver son propre compte (AC#4)
  - [x] 3.3 UPDATE users SET is_active=false
  - [x] 3.4 Retourner le compte mis à jour

- [x] Task 4: Frontend — bouton "Désactiver" dans `AdminUsersView.vue` (AC: #1)
  - [x] 4.1 Afficher le bouton pour les comptes actifs (sauf propre compte admin)
  - [x] 4.2 Appeler `PATCH /api/v1/admin/users/{username}/deactivate` via `apiCall`
  - [x] 4.3 Recharger la liste après désactivation

- [x] Task 5: Tests backend (AC: #1, #2, #3, #4)
- [x] Task 6: Tests frontend (AC: #1, #4)

## Dev Notes

### Endpoint

```
PATCH /api/v1/admin/users/{username}/deactivate
Authorization: Bearer <token admin>
```

Réponse 200 :
```json
{"username": "alice", "role": "operator", "is_active": false, "created_at": "...", "force_password_change": false}
```

### Message désactivation (AC#2 + AC#3)

`"Ce compte a été désactivé. Contactez votre administrateur."`

### AC#3 — implémentation minimale

Le check `is_active` est ajouté inline dans `change_password` (déjà DB-aware). Les endpoints admin ne nécessitent pas ce check car seuls les admins y accèdent et les admins ne peuvent pas être désactivés (AC#4).

### AC#4 — protection propre compte

Comparer `current_user["username"] == username` (path param) → 400 si égal.

### References

- FR7: désactivation compte — [Source: epics.md#Story 2.3]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

(à remplir)

### Completion Notes List

- AC#2 et AC#3 : le check `is_active` est ajouté inline dans `auth.py` (login + change_password), sans modifier `require_admin` (qui reste JWT-only car les admins ne peuvent pas être désactivés via AC#4).
- AC#4 : comparaison `current_admin["username"] == username` avant tout accès DB → 400 immédiat.
- Test `test_deactivate_own_account_returns_400` nécessite `get_db` overridé malgré le 400 anticipé, car FastAPI résout toutes les dépendances avant l'exécution de la fonction.
- 54 tests backend GREEN, 34 tests frontend GREEN.

### Change Log

- 2026-02-22 — Story 2.3 démarrée et complétée

### File List

- `corniscan/backend/app/routers/auth.py` — checks `is_active` dans login + change_password
- `corniscan/backend/app/routers/admin.py` — `PATCH /api/v1/admin/users/{username}/deactivate`
- `corniscan/backend/tests/test_auth.py` — 2 tests Story 2.3 ajoutés
- `corniscan/backend/tests/test_admin.py` — 4 tests Story 2.3 ajoutés
- `corniscan/frontend/src/views/AdminUsersView.vue` — bouton Désactiver + handler
- `corniscan/frontend/src/views/__tests__/AdminUsersView.spec.ts` — 4 tests Story 2.3 ajoutés
