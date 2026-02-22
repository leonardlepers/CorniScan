# Story 6.3: Guide d'installation contextuel iOS au premier login

Status: done

## Story

As an opérateur iOS,
I want voir un guide d'installation contextuel lors de ma première connexion réussie sur Safari iOS,
So that je sais comment installer CorniScan sur mon écran d'accueil malgré l'absence d'invite native sur iOS.

## Acceptance Criteria

1. Guide affiché au premier login réussi sur Safari iOS si l'app n'est pas déjà standalone (FR34)
2. Guide présente les instructions iOS : icône Partager → "Sur l'écran d'accueil"
3. Ne s'affiche plus après fermeture (état dans `localStorage`)
4. Non affiché sur non-iOS, non-Safari, ou app déjà standalone

## Tasks / Subtasks

- [x] Task 1: `src/composables/useIosInstallGuide.ts` — détection iOS Safari + standalone + localStorage
- [x] Task 2: `src/components/IosInstallGuide.vue` — modale avec instructions
- [x] Task 3: `src/views/LoginView.vue` — affichage guide après login réussi
- [x] Task 4: Tests composable + composant

## Dev Notes

### Détection iOS Safari
```typescript
const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent)
const isSafari = /WebKit/.test(ua) && !/CriOS|FxiOS|OPiOS|EdgiOS/.test(ua)
```

### Clé localStorage
`'ios_install_guide_shown'` → valeur `'true'`

### Standalone check
`window.matchMedia('(display-mode: standalone)').matches`

## File List

- `corniscan/frontend/src/composables/useIosInstallGuide.ts` (nouveau)
- `corniscan/frontend/src/components/IosInstallGuide.vue` (nouveau)
- `corniscan/frontend/src/views/LoginView.vue` (modifié)
- `corniscan/frontend/src/composables/__tests__/useIosInstallGuide.spec.ts` (nouveau)
- `corniscan/frontend/src/components/__tests__/IosInstallGuide.spec.ts` (nouveau)
