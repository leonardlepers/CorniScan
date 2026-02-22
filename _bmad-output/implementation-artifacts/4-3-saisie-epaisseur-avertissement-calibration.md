# Story 4.3: Saisie de l'épaisseur et gestion de l'avertissement de calibration

Status: in-progress

## Story

As an opérateur,
I want saisir manuellement l'épaisseur du joint et être informé clairement en cas de calibration insuffisante,
So that je fournis une information complète et peux décider de la suite si la détection est incomplète.

## Acceptance Criteria

1. **Given** l'écran de validation est affiché **When** l'opérateur le consulte **Then** un champ de saisie numérique pour l'épaisseur du joint (en mm) est visible et éditable (FR21)

2. **Given** `calibration_warning` est `true` **When** l'écran de validation s'affiche **Then** un avertissement explicite s'affiche : "Calibration insuffisante — moins de 4 coins de la carte détectés. Recommencez avec la carte entièrement visible." (FR22)

3. **Given** l'avertissement de calibration est affiché **When** l'opérateur choisit une action **Then** deux options sont proposées : "Recommencer la photo" et "Forcer l'envoi malgré l'avertissement" (FR23)

4. **Given** l'opérateur sélectionne "Recommencer la photo" **When** l'action est déclenchée **Then** il est redirigé vers `/camera` avec le résultat d'analyse réinitialisé

5. **Given** `calibration_warning` est `false` **When** le résultat est affiché **Then** aucun avertissement et aucune option "Forcer l'envoi" ne sont visibles

## Tasks / Subtasks

- [ ] Task 1: `scanStore.ts` — `thickness` + `setThickness()` + `clearResult()` inclut thickness (AC: #1)
- [ ] Task 2: `ThicknessInput.vue` — input numérique + avertissement calibration + boutons (AC: #1, #2, #3, #5)
- [ ] Task 3: `AnalyseView.vue` — `<ThicknessInput>` + `handleRetake()` (AC: #4)
- [ ] Task 4: Tests — scanStore + `ThicknessInput.spec.ts` (nouveau) + AnalyseView Story 4.3 (AC: #1–5)

## Dev Notes

### ThicknessInput events

```
@update:thickness → number | null  (émis à chaque input)
@retake           → []             (clic "Recommencer la photo")
@force-send       → []             (clic "Forcer l'envoi" — wired en Story 4.5)
```

### handleRetake (AnalyseView)

```typescript
function handleRetake(): void {
  scanStore.clearResult()
  router.push({ name: 'camera' })
}
```

`clearPhoto()` n'est pas appelé : la caméra remplacera la photo avec `setPhoto()` lors de la prochaine capture.

### References

- FR21: champ épaisseur éditable
- FR22: message avertissement exact
- FR23: deux actions explicites

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

(à compléter)

### Completion Notes List

(à compléter)

### Change Log

- 2026-02-22 — Story 4.3 démarrée

### File List

- `corniscan/frontend/src/stores/scanStore.ts` (modifié — thickness + setThickness)
- `corniscan/frontend/src/components/validation/ThicknessInput.vue` (nouveau)
- `corniscan/frontend/src/views/AnalyseView.vue` (modifié — ThicknessInput + handleRetake)
- `corniscan/frontend/src/stores/__tests__/scanStore.spec.ts` (modifié — tests thickness)
- `corniscan/frontend/src/components/validation/__tests__/ThicknessInput.spec.ts` (nouveau)
- `corniscan/frontend/src/views/__tests__/AnalyseView.spec.ts` (modifié — tests Story 4.3)
