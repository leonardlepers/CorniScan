# Story 2.4: Protection des routes admin et séparation des rôles

Status: review

## Story

As an administrateur,
I want que les fonctions de gestion des comptes soient exclusivement accessibles aux administrateurs,
So that la séparation des rôles est garantie et les opérateurs ne peuvent pas accéder aux fonctions sensibles.

## Acceptance Criteria

1. **Given** un opérateur authentifié (rôle 'operator') tente d'accéder à une route frontend `/admin/*` **When** le router Vue évalue la navigation **Then** il est redirigé vers sa route principale et un message lui indique l'accès refusé (FR8)

2. **Given** le backend reçoit une requête vers un endpoint d'administration (`/api/v1/admin/*`) avec un JWT de rôle 'operator' **When** le middleware d'autorisation évalue le token **Then** HTTP 403 est retourné, quelle que soit la validité du token JWT

3. **Given** un administrateur est authentifié **When** il accède à la section administration **Then** il voit l'interface complète de gestion des comptes (liste, création, désactivation)

4. **Given** un opérateur est authentifié **When** il consulte la navigation de l'application **Then** aucun lien ou élément d'interface menant aux fonctions admin n'est visible dans son menu

## Tasks / Subtasks

- [x] Task 1: Backend — 403 pour opérateurs sur routes admin (AC: #2) — **déjà couvert par `require_admin` (Stories 2.1–2.3)**

- [x] Task 2: Frontend router — query param `?forbidden=1` quand opérateur redirigé (AC: #1)
  - [x] 2.1 Dans le guard `requireAdmin`, return `{ name: 'camera', query: { forbidden: '1' } }` au lieu de `{ name: 'camera' }`

- [x] Task 3: CameraView — message d'accès refusé (AC: #1)
  - [x] 3.1 Lire `route.query.forbidden` et afficher alerte dismissible
  - [x] 3.2 Inclure AppHeader

- [x] Task 4: AppHeader.vue — navigation avec lien admin conditionnel (AC: #4)
  - [x] 4.1 Afficher nom app + lien `/admin/users` uniquement si `role === 'admin'`
  - [x] 4.2 Bouton logout

- [x] Task 5: AdminUsersView — inclure AppHeader (AC: #3)

- [x] Task 6: Tests frontend (AC: #1, #4)

## Dev Notes

### AC#2 — backend déjà couvert

`require_admin` (admin.py) lève 403 si `role !== 'admin'`. Couvert par les tests existants :
- `test_list_users_operator_gets_403`
- `test_create_user_operator_gets_403`
- `test_deactivate_operator_not_allowed`

### AC#1 — message d'accès refusé

Le router guard ajoute `?forbidden=1` à la redirection. CameraView affiche l'alerte.

### AC#4 — navigation

`AppHeader.vue` : lien `/admin/users` masqué pour les opérateurs (conditionnel sur `role === 'admin'`).

### References

- FR8: séparation des rôles — [Source: epics.md#Story 2.4]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

(à remplir)

### Completion Notes List

- AC#2 (backend 403) entièrement couvert sans code supplémentaire : `require_admin` des Stories 2.1–2.3 couvre les 3 endpoints.
- AC#1 : query param `?forbidden=1` dans le guard router + alerte dismissible dans CameraView (pattern léger, sans store dédié).
- AC#4 : `AppHeader.vue` partagé entre CameraView et AdminUsersView, lien admin conditionnel sur `role === 'admin'`.
- Warn VTU `router-link` non résolue est cosmétique (les tests passent), due au mock `vue-router` en ESM.
- 54 tests backend GREEN, 41 tests frontend GREEN.

### Change Log

- 2026-02-22 — Story 2.4 démarrée et complétée

### File List

- `corniscan/frontend/src/router/index.ts` — guard requireAdmin : query `forbidden=1` à la redirection
- `corniscan/frontend/src/components/AppHeader.vue` — nouveau composant header (lien admin conditionnel + logout)
- `corniscan/frontend/src/views/CameraView.vue` — alerte forbidden + inclusion AppHeader
- `corniscan/frontend/src/views/AdminUsersView.vue` — inclusion AppHeader
- `corniscan/frontend/src/components/__tests__/AppHeader.spec.ts` — 4 tests Story 2.4
- `corniscan/frontend/src/views/__tests__/CameraView.spec.ts` — 3 tests Story 2.4
