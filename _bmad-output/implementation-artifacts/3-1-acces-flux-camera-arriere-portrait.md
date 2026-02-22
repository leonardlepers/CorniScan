# Story 3.1: Accès au flux caméra arrière en mode portrait

Status: review

## Story

As an opérateur,
I want accéder au flux caméra arrière de mon mobile en temps réel depuis le navigateur,
So that je peux cadrer le joint à photographier directement depuis l'application.

## Acceptance Criteria

1. **Given** un opérateur authentifié navigue vers l'écran caméra **When** la page se charge **Then** le flux de la caméra arrière s'affiche via `getUserMedia` avec `facingMode: 'environment'`, plein écran, en orientation portrait (FR9)

2. **Given** le flux caméra est actif et l'opérateur bascule le téléphone en mode paysage **When** le changement d'orientation est détecté **Then** l'interface reste verrouillée en portrait — le flux caméra ne pivote pas (FR13)

3. **Given** le navigateur ne supporte pas `getUserMedia` ou l'opérateur refuse la permission caméra **When** la page tente d'accéder à la caméra **Then** un message d'erreur explicite s'affiche avec une action corrective ("Autorisez l'accès à la caméra dans les paramètres de votre navigateur")

4. **Given** le flux caméra est actif **When** l'opérateur utilise l'application **Then** aucune barre de navigation du navigateur n'est visible (mode plein écran PWA ou scroll masqué)

## Tasks / Subtasks

- [x] Task 1: `useMediaDevices.ts` composable (AC: #1, #2, #3)
  - [x] 1.1 `startCamera()` : `getUserMedia({ video: { facingMode: 'environment' }, audio: false })`
  - [x] 1.2 Portrait lock via `screen.orientation.lock('portrait')` (best-effort, try/catch)
  - [x] 1.3 Gestion erreurs : `NotAllowedError` → message permission, API non supportée → message navigateur
  - [x] 1.4 `stopCamera()` + `onUnmounted` cleanup

- [x] Task 2: `CameraView.vue` — intégration composable + CSS plein écran (AC: #1, #3, #4)
  - [x] 2.1 `<video>` plein écran avec `autoplay playsinline muted`
  - [x] 2.2 Overlay erreur avec message + bouton Réessayer
  - [x] 2.3 CSS `height: 100dvh; overflow: hidden` plein écran (AC#4)

- [x] Task 3: Tests (AC: #1, #3)
  - [x] 3.1 `useMediaDevices.spec.ts` : mock `getUserMedia`, tester startCamera, NotAllowedError, non supporté
  - [x] 3.2 `CameraView.spec.ts` : message erreur visible, forbidden alert conservé

## Dev Notes

### AC#2 — Portrait lock

`screen.orientation.lock('portrait')` est une API expérimentale. Elle lève une exception sur desktop
et dans les navigateurs non supportants. Le try/catch la rend optionnelle (best-effort).

### AC#3 — Erreurs getUserMedia

| Erreur | Message affiché |
|---|---|
| API non supportée (`!navigator.mediaDevices`) | "Votre navigateur ne supporte pas l'accès à la caméra." |
| `NotAllowedError` | "Accès à la caméra refusé. Autorisez l'accès à la caméra dans les paramètres de votre navigateur." |
| `NotFoundError` | "Aucune caméra arrière trouvée sur cet appareil." |
| Autre | "Impossible d'accéder à la caméra." |

### AC#4 — Plein écran

Atteint via `height: 100dvh; overflow: hidden` sur le container. Le manifest PWA
(mode standalone) viendra dans une story dédiée.

### References

- FR9: flux caméra arrière — [Source: epics.md#Story 3.1]
- FR13: verrouillage portrait — [Source: epics.md#Story 3.1]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

(à remplir)

### Completion Notes List

- `useMediaDevices` retourne un `videoRef` lié directement au `<video>` du template via `ref="videoRef"` — le stream est affecté à `srcObject` après `onMounted`.
- Portrait lock (`screen.orientation.lock`) est en try/catch silencieux : lève une exception sur desktop, ignorée.
- `muted` est une propriété DOM (pas un attribut HTML) en JSDOM : le test utilise `element.muted` plutôt que `attributes('muted')`.
- Le mock du composable dans CameraView.spec.ts utilise des vrais `ref()` Vue pour que le template réagisse correctement aux changements de `isLoading` et `error`.
- 54 tests backend GREEN, 51 tests frontend GREEN.

### Change Log

- 2026-02-22 — Story 3.1 démarrée et complétée

### File List

- `corniscan/frontend/src/composables/useMediaDevices.ts` — nouveau composable caméra (getUserMedia + portrait lock + cleanup)
- `corniscan/frontend/src/views/CameraView.vue` — intégration composable, `<video>` plein écran, overlay erreur
- `corniscan/frontend/src/composables/__tests__/useMediaDevices.spec.ts` — 5 tests Story 3.1
- `corniscan/frontend/src/views/__tests__/CameraView.spec.ts` — 8 tests (Story 2.4 conservés + 5 Story 3.1)
