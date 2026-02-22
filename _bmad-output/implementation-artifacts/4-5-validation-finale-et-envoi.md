# Story 4.5: Validation finale et déclenchement de l'envoi

Status: done

## Story

As an opérateur,
I want valider et envoyer le scan depuis l'écran de validation,
So that le dossier complet est transmis au pipeline de génération DXF et d'envoi email.

## Acceptance Criteria

1. **Given** l'opérateur est satisfait du résultat **When** il clique sur "Valider et envoyer" **Then** le payload complet (image JPEG + contour_points + dimensions + épaisseur + calibration_warning) est soumis à POST /api/v1/scan/submit (FR24)

2. **Given** `calibration_warning` est `true` et l'opérateur choisit "Forcer l'envoi" **When** il clique **Then** le flag `calibration_warning: true` est inclus dans le payload

3. **Given** la soumission est en cours **When** la requête est envoyée **Then** le bouton est désactivé — aucun double-envoi possible

4. **Given** la soumission aboutit **When** le backend confirme **Then** l'opérateur est redirigé vers `/confirmation` (FR28 — Epic 5 remplira la vue)

## Tasks / Subtasks

- [x] Task 1: `scan.py` — `POST /submit` : File + Form fields, retourne `{"status": "accepted"}` (AC: #1, #2)
- [x] Task 2: `test_scan.py` — tests submit endpoint (AC: #1, #2)
- [x] Task 3: `ConfirmationView.vue` — stub minimal (AC: #4)
- [x] Task 4: `router/index.ts` — route `/confirmation` (AC: #4)
- [x] Task 5: `AnalyseView.vue` — `handleSubmit()`, `isSubmitting`, `submitError`, bouton, `@force-send` (AC: #1–4)
- [x] Task 6: Tests — AnalyseView Story 4.5 (AC: #1–4)

## Dev Notes

### Payload POST /submit (FormData multipart)

| Champ | Type | Obligatoire |
|---|---|---|
| file | File (JPEG) | oui |
| contour_points | str (JSON) | oui |
| width_mm | float | oui |
| height_mm | float | oui |
| thickness | float | non |
| calibration_warning | bool | oui |

### Backend endpoint

`def` synchrone (CPU — lecture fichier). DXF + email = Story 5.x. Story 4.5 retourne juste `{"status": "accepted"}`.

### handleSubmit guard

`if (isSubmitting.value || !scanStore.photo) return` — évite le double-envoi et protège contre un état incohérent.

### force-send wiring

`@force-send="handleSubmit"` sur `<ThicknessInput>` — déclenche la même soumission que le bouton principal. `calibration_warning` est déjà `true` dans le store quand ce bouton est visible.

### ConfirmationView

Stub minimal — Epic 5 l'enrichira avec le résumé du scan et la confirmation email.

### References

- FR24: payload complet soumis
- FR28: redirection écran confirmation
- NFR-P4: bouton désactivé pendant l'envoi (pas d'UI bloquée)

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

(à compléter)

### Completion Notes List

- 23/23 backend GREEN, 126/126 frontend GREEN
- Backend: `def` synchrone + `json.loads()` pour valider contour_points
- Frontend: double-clic protégé par guard `if (isSubmitting.value) return`
- `force-send` de ThicknessInput déclenche `handleSubmit` directement — même code path que le bouton principal

### Change Log

- 2026-02-22 — Story 4.5 démarrée

### File List

- `corniscan/backend/app/routers/scan.py` (modifié — POST /submit)
- `corniscan/backend/tests/test_scan.py` (modifié — tests submit)
- `corniscan/frontend/src/views/ConfirmationView.vue` (nouveau — stub)
- `corniscan/frontend/src/router/index.ts` (modifié — route /confirmation)
- `corniscan/frontend/src/views/AnalyseView.vue` (modifié — handleSubmit + bouton)
- `corniscan/frontend/src/views/__tests__/AnalyseView.spec.ts` (modifié — tests Story 4.5)
