# Story 2.2: Création d'un compte opérateur avec mot de passe provisoire

Status: review

## Story

As an administrateur,
I want créer un nouveau compte opérateur avec un mot de passe provisoire,
So that je peux donner accès à l'application à un nouvel opérateur sans intervention technique.

## Acceptance Criteria

1. **Given** un administrateur est sur la page de gestion des comptes **When** il remplit le formulaire de création (username + mot de passe provisoire) et soumet **Then** un compte est créé en base avec `role='operator'`, `force_password_change=true`, mot de passe haché bcrypt (≥ 12) **And** le nouveau compte apparaît immédiatement dans la liste des comptes (FR6)

2. **Given** un compte opérateur vient d'être créé avec un mot de passe provisoire **When** le nouvel opérateur se connecte avec ces credentials **Then** l'authentification réussit et il est redirigé vers l'écran de changement de mot de passe forcé (lien avec Story 1.4 — aucun code supplémentaire requis)

3. **Given** un administrateur tente de créer un compte avec un username déjà existant **When** le formulaire est soumis **Then** le backend retourne une erreur explicite ("Ce nom d'utilisateur existe déjà.") et aucun compte n'est créé

4. **Given** un administrateur soumet le formulaire de création avec des champs vides **When** la validation s'exécute **Then** des messages d'erreur s'affichent et la soumission est bloquée côté frontend

## Tasks / Subtasks

- [x] Task 1: Backend `POST /api/v1/admin/users` (AC: #1, #2, #3)
  - [x] 1.1 Ajouter `CreateUserRequest` (Pydantic) : `username`, `password`
  - [x] 1.2 Vérifier unicité username → 409 si doublon
  - [x] 1.3 Hasher `password` (bcrypt ≥ 12) + INSERT `role='operator'`, `force_password_change=true`, `is_active=true`
  - [x] 1.4 Retourner le compte créé (sans hash)

- [x] Task 2: Frontend — formulaire de création dans `AdminUsersView.vue` (AC: #1, #3, #4)
  - [x] 2.1 Ajouter section formulaire (username + password)
  - [x] 2.2 Validation frontend : champs non vides (AC#4)
  - [x] 2.3 Appel `POST /api/v1/admin/users` via `apiCall`
  - [x] 2.4 Sur succès : recharger la liste + vider le formulaire
  - [x] 2.5 Afficher l'erreur du backend (ex. username doublon)

- [x] Task 3: Tests backend (AC: #1, #3)
- [x] Task 4: Tests frontend (AC: #1, #3, #4)

## Dev Notes

### `POST /api/v1/admin/users` — Corps de la requête

```json
{ "username": "alice", "password": "ProvPass123!" }
```

Requiert `Authorization: Bearer <token admin>`. Retourne 409 si username déjà pris.

### Réponse succès (201)

```json
{
  "username": "alice",
  "role": "operator",
  "is_active": true,
  "created_at": "2026-02-22T10:00:00Z",
  "force_password_change": true
}
```

### AC#2 — redirection vers change-password

Géré par le guard Story 1.3/1.4 : `force_password_change=true` dans le JWT → guard redirige automatiquement.

### References

- FR6: création compte opérateur — [Source: epics.md#Story 2.2]
- bcrypt ≥ 12: [Source: architecture.md#Authentication & Security]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

(à remplir)

### Completion Notes List

- AC#2 (redirection vers change-password) couvert sans code supplémentaire : `force_password_change=true` dans le JWT déclenche le guard Story 1.3/1.4.
- Double protection contre les doublons : SELECT avant INSERT + catch `IntegrityError` (race condition).
- `INSERT ... RETURNING` évite un second SELECT pour construire la réponse.
- 48 tests backend GREEN, 30 tests frontend GREEN.

### Change Log

- 2026-02-22 — Story 2.2 démarrée

### File List

- `corniscan/backend/app/routers/admin.py` — ajout `CreateUserRequest` + `POST /api/v1/admin/users`
- `corniscan/backend/tests/test_admin.py` — 4 tests Story 2.2 ajoutés
- `corniscan/frontend/src/views/AdminUsersView.vue` — section formulaire de création
- `corniscan/frontend/src/views/__tests__/AdminUsersView.spec.ts` — 4 tests Story 2.2 ajoutés
