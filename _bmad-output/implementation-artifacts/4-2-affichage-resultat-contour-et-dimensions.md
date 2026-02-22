# Story 4.2: Affichage du résultat — contour superposé et dimensions

Status: review

## Story

As an opérateur,
I want voir le contour détecté du joint superposé sur la photo originale ainsi que les dimensions calculées numériquement,
So that je peux valider visuellement que l'analyse correspond bien au joint photographié.

## Acceptance Criteria

1. **Given** le backend retourne un résultat d'analyse réussi **When** l'écran de validation s'affiche **Then** le contour détecté du joint est dessiné en surimpression sur la photo originale (FR19)

2. **Given** le contour est affiché en superposition **When** l'opérateur le compare visuellement à la photo **Then** il trace fidèlement le contour extérieur du joint visible dans l'image

3. **Given** les dimensions sont calculées **When** l'écran de validation s'affiche **Then** la largeur et la hauteur du joint sont affichées numériquement en millimètres avec 1 décimale de précision (FR20)

4. **Given** `calibration_warning` est `false` **When** le résultat est affiché **Then** aucun avertissement n'est visible

## Tasks / Subtasks

- [x] Task 1: `ContourOverlay.vue` — img + SVG polygon (coordonnées normalisées [0,1]) (AC: #1, #2)
- [x] Task 2: `AnalyseView.vue` — intégration ContourOverlay + affichage dimensions.toFixed(1) mm (AC: #1, #2, #3, #4)
- [x] Task 3: Tests — `ContourOverlay.spec.ts` (nouveau) + extension `AnalyseView.spec.ts` (AC: #1, #3, #4)

## Dev Notes

### ContourOverlay

Overlay SVG absolu sur l'image — viewBox="0 0 1 1" + preserveAspectRatio="none" pour que les coordonnées normalisées [0,1] des contour_points se mappent directement sur les pixels de l'image.

```vue
<div class="contour-overlay-container">
  <img :src="photoUrl" class="photo-img" />
  <svg viewBox="0 0 1 1" preserveAspectRatio="none" ...>
    <polygon :points="svgPoints" />  <!-- x,y x,y ... -->
  </svg>
</div>
```

### AnalyseView — URL blob

```typescript
// onMounted — avant l'appel API
photoUrl.value = URL.createObjectURL(scanStore.photo)
// onUnmounted
URL.revokeObjectURL(photoUrl.value)
```

### AnalyseView — dimensions

```html
{{ scanStore.dimensions.width_mm.toFixed(1) }} mm × {{ scanStore.dimensions.height_mm.toFixed(1) }} mm
```

### References

- FR19: contour dessiné en surimpression — [Source: epics.md#Story 4.2]
- FR20: dimensions numériques en mm, 1 décimale — [Source: epics.md#Story 4.2]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

Aucun.

### Completion Notes List

- `ContourOverlay.vue` : `viewBox="0 0 1 1" preserveAspectRatio="none"` → les coordonnées normalisées [0,1] se mappent directement. `polygon` affiché seulement si `contourPoints.length >= 3`. `svgPoints` computed = `"x,y x,y ..."`. Polygon : `fill rgba(34,197,94,0.15)` + `stroke #22c55e` + `stroke-width 0.005`.
- `AnalyseView.vue` : `photoUrl = URL.createObjectURL(scanStore.photo)` dans `onMounted` ; `URL.revokeObjectURL` dans `onUnmounted`. Résultat : `<ContourOverlay>` + `.dimensions-display` avec `.toFixed(1) mm × .toFixed(1) mm`.
- `AnalyseView.spec.ts` : mock `ContourOverlay` + mock `URL` global (`stubGlobal`/`unstubAllGlobals`) ; state mutable scanStore via getters → mis à jour en `beforeEach`.
- 72/72 backend GREEN, 96/96 frontend GREEN.

### Change Log

- 2026-02-22 — Story 4.2 démarrée et complétée

### File List

- `corniscan/frontend/src/components/validation/ContourOverlay.vue` (nouveau)
- `corniscan/frontend/src/views/AnalyseView.vue` (modifié — photo + overlay + dimensions)
- `corniscan/frontend/src/components/validation/__tests__/ContourOverlay.spec.ts` (nouveau)
- `corniscan/frontend/src/views/__tests__/AnalyseView.spec.ts` (modifié — tests Story 4.2)
