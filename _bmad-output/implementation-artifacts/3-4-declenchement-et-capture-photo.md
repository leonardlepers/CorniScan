# Story 3.4: Déclenchement et capture de la photo

Status: review

## Story

As an opérateur,
I want déclencher la capture de la photo depuis l'écran caméra,
So that je peux soumettre l'image du joint au système d'analyse.

## Acceptance Criteria

1. **Given** les 2 cases de la checklist sont cochées et le bouton de capture est actif **When** l'opérateur appuie sur le bouton de capture **Then** une image fixe est capturée depuis le flux caméra via `canvas.toBlob()` au format JPEG (FR12) **And** le flux caméra s'arrête et l'image capturée s'affiche en aperçu

2. **Given** la photo est capturée **When** la capture est confirmée **Then** l'opérateur est automatiquement redirigé vers l'écran d'analyse avec l'image transmise en état de navigation (scanStore)

3. **Given** la photo est capturée en mode portrait **When** l'image est exploitée par le backend **Then** l'orientation est correcte indépendamment des métadonnées EXIF du device

## Tasks / Subtasks

- [x] Task 1: `scanStore.ts` — activer photo + setPhoto + clearPhoto + hasPhoto (AC: #2)
- [x] Task 2: `router/index.ts` — route `/analyse` + guard `requirePhoto` (AC: #2)
- [x] Task 3: `AnalyseView.vue` — placeholder minimal (AC: #2)
- [x] Task 4: `CameraView.vue` — capture() + aperçu + confirm/retake (AC: #1, #2, #3)
- [x] Task 5: Tests (AC: #1, #2)

## Dev Notes

### Capture via canvas

```typescript
const canvas = document.createElement('canvas')
canvas.width = video.videoWidth
canvas.height = video.videoHeight
ctx.drawImage(video, 0, 0)
const blob = await new Promise<Blob | null>(resolve => canvas.toBlob(resolve, 'image/jpeg', 0.92))
```

**AC#3 — Orientation EXIF :** `canvas.drawImage(videoElement)` capture les pixels tels qu'affichés par le navigateur (déjà orientés correctement). Aucun EXIF n'est inscrit dans le JPEG résultant → orientation toujours correcte. Aucun code spécifique nécessaire.

### Passage de la photo à l'écran d'analyse

Stockage dans `scanStore.photo` (ref<File | null>) puis `router.push({ name: 'analyse' })`.
Le guard `requirePhoto` redirige vers `/camera` si `!scanStore.hasPhoto`.

### References

- FR12: capture JPEG via canvas — [Source: epics.md#Story 3.4]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- `vi.spyOn(document, 'createElement').mockImplementation(tag => document.createElement.call(document, tag))` → stack overflow : la spy appelle la spy en récursion infinie. Fix : capturer `const _origCreateElement = document.createElement.bind(document)` AVANT l'installation de la spy, puis appeler `_origCreateElement(tag)` dans le mock.
- BMAD hook a activé le mode plan après un Edit — résolu en écrivant un plan minimal et appelant ExitPlanMode.

### Completion Notes List

- `scanStore.ts` : `photo = ref<File | null>(null)`, `hasPhoto = computed(() => photo.value !== null)`, `setPhoto(file)`, `clearPhoto()`.
- `router/index.ts` : route `/analyse` (requirePhoto) + guard step 5 (`!scanStore.hasPhoto → redirect /camera`). `AnalyseView.vue` placeholder minimal.
- `CameraView.vue` : `capture()` promisifie `canvas.toBlob`, stop caméra + détection, affiche `<img class="preview-image">`. `confirmCapture()` → `scanStore.setPhoto` + `router.push('analyse')`. `retakePhoto()` → révoque blob URL, relance caméra + détection.
- AC#3 : la capture via canvas est intrinsèquement correcte en orientation (pixels affichés = pixels orientés par le browser, sans EXIF).
- 61/61 backend GREEN, 74/74 frontend GREEN.

### Change Log

- 2026-02-22 — Story 3.4 démarrée et complétée

### File List

- `corniscan/frontend/src/stores/scanStore.ts` (modifié — photo + setPhoto + clearPhoto + hasPhoto)
- `corniscan/frontend/src/router/index.ts` (modifié — route /analyse + requirePhoto guard)
- `corniscan/frontend/src/views/AnalyseView.vue` (nouveau — placeholder)
- `corniscan/frontend/src/views/CameraView.vue` (modifié — capture + aperçu + confirm/retake)
- `corniscan/frontend/src/stores/__tests__/scanStore.spec.ts` (modifié — tests Story 3.4)
- `corniscan/frontend/src/views/__tests__/CameraView.spec.ts` (modifié — mock scanStore/router + 4 tests Story 3.4)
