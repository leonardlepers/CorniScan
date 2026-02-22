# Story 4.1: Soumission de la photo et pipeline d'analyse backend

Status: review

## Story

As an opérateur,
I want soumettre la photo capturée pour analyse,
So that le système détecte automatiquement la carte bancaire, corrige la perspective, détecte le contour du joint et calcule ses dimensions en millimètres.

## Acceptance Criteria

1. **Given** une photo JPEG est soumise à `POST /scan/process` **When** le backend reçoit la requête **Then** il exécute séquentiellement : détection de la carte + homographie pixel/mm (FR14), correction de la distorsion de perspective (FR15), détection du contour extérieur du joint (FR16), calcul des dimensions largeur × hauteur en mm (FR17)

2. **Given** le backend complète l'analyse avec succès **When** la réponse est retournée au frontend **Then** elle contient : les coordonnées du contour du joint (normalisées), les dimensions (largeur × hauteur en mm), et le statut de calibration

3. **Given** la détection de la carte identifie moins de 4 coins **When** l'analyse s'exécute **Then** la réponse inclut `calibration_warning: true` et l'analyse se poursuit dans la mesure du possible (FR18)

4. **Given** l'endpoint `/scan/process` exécute le traitement OpenCV **Then** l'endpoint est déclaré `def` (synchrone) — aucune photo ni métadonnée n'est persistée (NFR-S4)

5. **Given** la soumission est en cours côté frontend **When** l'utilisateur attend la réponse **Then** un indicateur de chargement est visible et l'interface reste interactive (NFR-P4)

## Tasks / Subtasks

- [x] Task 1: `vision_service.py` — `_find_card_corners()` + `_detect_joint_contour()` + `process_image()` (AC: #1, #2, #3)
- [x] Task 2: `scan.py` — endpoint `def process_image_endpoint()` (AC: #4)
- [x] Task 3: Tests backend — `process_image` + `POST /scan/process` (AC: #1, #2, #3, #4)
- [x] Task 4: `scanStore.ts` — `contour` + `dimensions` + `calibrationWarning` + `setResult()` + `clearResult()` (AC: #2, #5)
- [x] Task 5: `AnalyseView.vue` — soumission FormData + loading + error (AC: #5)
- [x] Task 6: Tests frontend — `scanStore` Story 4.1 + `AnalyseView.spec.ts` (AC: #2, #5)

## Dev Notes

### Pipeline vision_service.process_image

```
image_bytes → decode JPEG
→ _find_card_corners() → (corners_4x2 | None, calibration_warning)
→ si corners: getPerspectiveTransform → warpPerspective (856×540px = 10px/mm)
→ sinon: resize (dégradé)
→ _detect_joint_contour(warped) → (points_px, (w_px, h_px))
→ dimensions mm = px / SCALE
→ perspectiveTransform(H_inv) → contour en coordonnées image originale
→ normalize ([0,1]) → contour_points
→ return {contour_points, dimensions, calibration_warning}
```

**Constantes :**
- `_SCALE = 10.0` (px/mm) → warped = 856×540px
- Contour retourné en coordonnées **normalisées** [0,1] relatives à l'image originale

### Endpoint scan.py

```python
@router.post("/process")
def process_image_endpoint(
    file: UploadFile = File(...),
    _: dict = Depends(get_current_user),
) -> dict:
```

⚠️ `def` synchrone (pas `async def`) — Uvicorn thread pool pour CPU-bound OpenCV.

### scanStore.ts — état ajouté

```typescript
contour = ref<number[][]>([])
dimensions = ref<{ width_mm: number; height_mm: number } | null>(null)
calibrationWarning = ref(false)
setResult(result: ProcessResult): void
clearResult(): void
```

### AnalyseView.vue — soumission

```
onMounted → FormData(scanStore.photo) → apiCall('/api/v1/scan/process', POST)
→ success: scanStore.setResult(result) → affiche résultat (Story 4.2)
→ erreur: affiche message (Story 4.4)
→ toujours: isLoading = false
```

### References

- FR14-FR18: pipeline backend (homographie + perspective + contour + dimensions + calibration_warning)
- NFR-P1: < 5s pour 90% des requêtes
- NFR-P4: UI non bloquée pendant le traitement
- NFR-S4: aucune donnée persistée

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- Apostrophes françaises dans les strings de test (`l'API`) → parse error esbuild. Fix : guillemets doubles `"AC — ... l'API"`.

### Completion Notes List

- `vision_service.py` : `_order_points(pts)` ordonne TL/TR/BR/BL ; `_find_card_corners(img)` retourne `(corners_4x2 | None, calibration_warning)` (réutilise algo Canny+approxPolyDP) ; `_detect_joint_contour(img)` retourne `(points, (w_px, h_px))` — contour le plus grand ou fallback image entière ; `process_image(bytes)` : warpPerspective (856×540px = 10px/mm) si 4 coins, sinon resize ; remappage contour via `perspectiveTransform(H_inv)` → normalisé [0,1].
- `scan.py` : `def process_image_endpoint()` synchrone (thread pool Uvicorn) ; lit `file.file.read()` ; lève HTTP 422 si ValueError (JPEG invalide).
- `scanStore.ts` : exports `ScanDimensions`, `ProcessResult` ; `contour = ref<number[][]>([])`, `dimensions = ref<ScanDimensions | null>(null)`, `calibrationWarning = ref(false)` ; `setResult()` + `clearResult()`.
- `AnalyseView.vue` : `onMounted` → FormData + `apiCall<ProcessResult>('/api/v1/scan/process', {method:'POST', body:formData})` → `scanStore.setResult(result)` ; spinner `role="status"` pendant isLoading ; `.error-text` + `.retry-btn` si erreur ; redirection `/camera` si `!scanStore.photo`.
- 72/72 backend GREEN, 86/86 frontend GREEN.

### Change Log

- 2026-02-22 — Story 4.1 démarrée et complétée

### File List

- `corniscan/backend/app/services/vision_service.py` (modifié — process_image + helpers)
- `corniscan/backend/app/routers/scan.py` (modifié — POST /scan/process)
- `corniscan/backend/tests/test_scan.py` (modifié — tests Story 4.1)
- `corniscan/frontend/src/stores/scanStore.ts` (modifié — contour + dimensions + setResult)
- `corniscan/frontend/src/views/AnalyseView.vue` (modifié — implémentation complète Story 4.1)
- `corniscan/frontend/src/stores/__tests__/scanStore.spec.ts` (modifié — tests Story 4.1)
- `corniscan/frontend/src/views/__tests__/AnalyseView.spec.ts` (nouveau — tests Story 4.1)
