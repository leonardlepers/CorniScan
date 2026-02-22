# Story 6.2: Invite d'installation native Android

Status: done

## Story

As an opérateur Android,
I want recevoir une invite native pour installer l'application sur mon écran d'accueil,
So that j'accède à CorniScan directement depuis mon écran d'accueil sans passer par le navigateur.

## Acceptance Criteria

1. L'invite native "Ajouter à l'écran d'accueil" apparaît automatiquement quand les critères PWA sont remplis (FR33)
2. L'événement `beforeinstallprompt` est capturé par le frontend pour contrôler le moment d'affichage
3. L'application reste installable via le menu Chrome si l'invite est ignorée
4. Démarre en mode standalone depuis l'écran d'accueil Android (FR35 confirmé)

## Tasks / Subtasks

- [x] Task 1: `src/composables/usePwaInstall.ts` — capture `beforeinstallprompt` + `promptInstall()`
- [x] Task 2: `src/views/CameraView.vue` — bannière d'installation discrète si `isInstallable`
- [x] Task 3: Tests composable `usePwaInstall`

## Dev Notes

### usePwaInstall composable
- Écoute `beforeinstallprompt` → stocke `deferredPrompt`, `isInstallable = true`
- Écoute `appinstalled` → remet `isInstallable = false`
- `promptInstall()` → appelle `deferredPrompt.prompt()` + attend `userChoice`
- Nettoyage des listeners dans `onUnmounted`

### CameraView bannière
- Affichée discrètement en haut si `isInstallable`
- Bouton "Installer l'application" → appelle `promptInstall()`

## File List

- `corniscan/frontend/src/composables/usePwaInstall.ts` (nouveau)
- `corniscan/frontend/src/views/CameraView.vue` (modifié — bannière install)
- `corniscan/frontend/src/composables/__tests__/usePwaInstall.spec.ts` (nouveau)
