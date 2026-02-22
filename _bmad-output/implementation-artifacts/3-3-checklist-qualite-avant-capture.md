# Story 3.3: Checklist qualité avant capture

Status: review

## Story

As an opérateur,
I want cocher une checklist de qualité avant de déclencher la capture,
So that je m'assure consciemment que les conditions sont optimales avant de soumettre la photo au traitement.

## Acceptance Criteria

1. **Given** l'écran caméra est affiché **When** l'opérateur le consulte **Then** une checklist avec 2 cases à cocher est visible : "Joint propre" et "Carte entièrement visible" (FR11)

2. **Given** au moins une case de la checklist est non cochée **When** l'opérateur tente de déclencher la capture **Then** le bouton de capture est désactivé (visuellement grisé) et ne répond pas au tap

3. **Given** l'opérateur coche les 2 cases de la checklist **When** toutes les cases sont cochées **Then** le bouton de capture devient actif et cliquable

4. **Given** l'opérateur décoche une case précédemment cochée **When** ce changement d'état se produit **Then** le bouton de capture redevient immédiatement désactivé

## Tasks / Subtasks

- [x] Task 1: `CaptureChecklist.vue` — composant checklist (AC: #1, #2, #3, #4)
  - [x] 1.1 2 cases à cocher : "Joint propre" et "Carte entièrement visible"
  - [x] 1.2 Émet `update:allChecked: boolean` à chaque changement (+ immédiat au montage)

- [x] Task 2: Intégration `CameraView.vue` (AC: #1, #2, #3, #4)
  - [x] 2.1 Affiche `CaptureChecklist` quand caméra active (`!isLoading && !error`)
  - [x] 2.2 Bouton "Capturer" désactivé si `allChecked === false`

- [x] Task 3: Tests (AC: #1, #2, #3, #4)

## Dev Notes

### CaptureChecklist

Composant purement frontend, sans appel réseau.
- Gère son propre état interne (2 `ref<boolean>`)
- Computed `allChecked = jointClean && cardVisible`
- Émet `'update:allChecked'` via `watch(allChecked, ..., { immediate: true })`

### CameraView — bouton capture

Le bouton `:disabled="!allChecked"` est introduit ici (Story 3.3).
La logique de capture (`canvas.toBlob()`, envoi, redirection) sera ajoutée en Story 3.4.

### References

- FR11: checklist qualité — [Source: epics.md#Story 3.3]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- `nextTick` importé par erreur depuis `vitest` — n'existe pas dans ce module. Fix : supprimé et remplacé par `flushPromises` (déjà importé depuis `@vue/test-utils`).

### Completion Notes List

- `CaptureChecklist.vue` : état interne 2 refs, computed `allChecked`, watch immédiat → emit `update:allChecked`.
- CameraView écoute `@update:all-checked` et stocke dans `allChecked` local. Bouton `:disabled="!allChecked"`.
- Checklist + bouton conditionnés à `!isLoading && !error` — absents si caméra non active.
- CaptureChecklist mocké dans CameraView.spec.ts (`name: 'CaptureChecklist'`) pour tester les émissions via `findComponent({ name })`.
- 61/61 backend GREEN, 68/68 frontend GREEN.

### Change Log

- 2026-02-22 — Story 3.3 démarrée et complétée

### File List

- `corniscan/frontend/src/components/camera/CaptureChecklist.vue` (nouveau)
- `corniscan/frontend/src/views/CameraView.vue` (modifié — ajout checklist + bouton capture)
- `corniscan/frontend/src/components/camera/__tests__/CaptureChecklist.spec.ts` (nouveau)
- `corniscan/frontend/src/views/__tests__/CameraView.spec.ts` (modifié — mock CaptureChecklist + 4 tests Story 3.3)
