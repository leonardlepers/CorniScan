# Story 1.4: Changement de mot de passe au premier login

Status: review

## Story

As an opérateur,
I want être contraint de changer mon mot de passe provisoire lors de ma première connexion,
So that mon accès est immédiatement sécurisé avec un mot de passe que je suis le seul à connaître.

## Acceptance Criteria

1. **Given** un opérateur se connecte avec succès et que `force_password_change = true` sur son compte **When** le JWT est émis et le frontend reçoit la réponse **Then** il est automatiquement redirigé vers l'écran de changement de mot de passe — aucune autre route n'est accessible (FR3)

2. **Given** un opérateur est sur l'écran de changement de mot de passe forcé et tente de naviguer vers une autre route **When** le router Vue évalue la navigation **Then** il est redirigé de force vers l'écran de changement de mot de passe

3. **Given** un opérateur saisit un nouveau mot de passe et sa confirmation, et les deux correspondent **When** il soumet le formulaire **Then** le nouveau mot de passe est haché (bcrypt ≥ 12) et persisté en base, `force_password_change` est mis à `false`, et il est redirigé vers la route principale

4. **Given** un opérateur soumet un nouveau mot de passe identique au mot de passe provisoire actuel **When** le backend reçoit la requête **Then** une erreur explicite est retournée ("Le nouveau mot de passe doit être différent de l'ancien.") et le changement est refusé

5. **Given** un opérateur saisit un nouveau mot de passe et une confirmation qui ne correspondent pas **When** le formulaire est soumis **Then** une erreur de validation s'affiche côté frontend ("Les mots de passe ne correspondent pas.") sans appel au backend

## Tasks / Subtasks

- [x] Task 1: Implémenter `POST /api/v1/auth/change-password` (AC: #3, #4)
  - [x] 1.1 Accepter `{current_password, new_password}` — JSON body (Pydantic)
  - [x] 1.2 Vérifier current_password contre le hash DB
  - [x] 1.3 Vérifier new_password != current_password (AC#4)
  - [x] 1.4 Hacher new_password (bcrypt ≥ 12) + UPDATE users SET hashed_password, force_password_change=false
  - [x] 1.5 Retourner nouveau JWT (force_password_change=false) + user info

- [x] Task 2: Ajouter `updateAuth()` à authStore.ts (AC: #3)
  - [x] 2.1 `updateAuth(token, user)` — met à jour token + user + localStorage

- [x] Task 3: Implémenter `ChangePasswordView.vue` (AC: #1, #2, #3, #5)
  - [x] 3.1 Champs : current_password, new_password, confirm_password
  - [x] 3.2 Validation client : new_password == confirm_password (AC#5 — sans appel backend)
  - [x] 3.3 Appel POST /api/v1/auth/change-password via apiCall
  - [x] 3.4 Sur succès : authStore.updateAuth(token, user) → router.push('/camera')

- [x] Task 4: Tests backend (AC: #3, #4)
- [x] Task 5: Tests frontend (AC: #3, #5)

## Dev Notes

### `POST /api/v1/auth/change-password` — Corps de la requête

```json
{"current_password": "Admin123!", "new_password": "MonNouveauMDP!"}
```

⚠️ Requiert `Authorization: Bearer <token>` — le token JWT obtenu au login est valide même avec `force_password_change=true`.

### Réponse succès (200)

```json
{
  "access_token": "<nouveau JWT avec force_password_change=false>",
  "token_type": "bearer",
  "user": {"username": "admin", "role": "admin", "force_password_change": false}
}
```

⚠️ Le nouveau JWT doit être stocké — l'ancien (avec force_password_change=true) reste valide 8h mais le guard frontend ne le bloque plus une fois le store mis à jour.

### Guard AC#1 et AC#2

Le guard `beforeEach` implémenté en Story 1.3 gère déjà AC#1 et AC#2 :
- AC#1 : Après login avec force_password_change=true → redirect /change-password (déjà en place)
- AC#2 : Toute navigation depuis /change-password → redirigée vers /change-password (déjà en place)

Aucune modification du router nécessaire pour Story 1.4.

### `authStore.updateAuth()` — Code exact

```typescript
function updateAuth(newToken: string, newUser: User): void {
  token.value = newToken
  user.value = newUser
  localStorage.setItem(STORAGE_KEY, newToken)
}
```

### References

- FR3 (changement forcé): [Source: epics.md#Story 1.4]
- Endpoint architecture: [Source: architecture.md#API & Communication]
- bcrypt ≥ 12: [Source: architecture.md#Authentication & Security]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

(à remplir)

### Completion Notes List

- AC#1/AC#2 couverts sans modification du router : le guard `beforeEach` (Story 1.3) gère déjà la redirection forcée vers `/change-password`.
- `HTTPBearer` FastAPI ≥ 0.114 retourne 401 (et non 403) quand aucun header Authorization n'est fourni — test corrigé en conséquence.
- 35 tests backend GREEN, 20 tests frontend GREEN.

### Change Log

- 2026-02-22 — Story 1.4 démarrée

### File List

- `corniscan/backend/app/routers/auth.py` — ajout `ChangePasswordRequest` + `POST /api/v1/auth/change-password`
- `corniscan/backend/tests/test_auth.py` — 4 tests Story 1.4 ajoutés (test_change_password_*)
- `corniscan/frontend/src/stores/authStore.ts` — ajout `updateAuth()`
- `corniscan/frontend/src/views/ChangePasswordView.vue` — implémentation complète (form 3 champs + validation client + apiCall)
