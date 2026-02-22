# Story 6.1: Configuration PWA et mode standalone

Status: done

## Story

As a développeur,
I want configurer l'application comme une PWA avec `vite-plugin-pwa` et Workbox,
So that l'application peut être installée sur l'écran d'accueil et s'exécute en mode standalone sans barre de navigation du navigateur.

## Acceptance Criteria

1. Un Web App Manifest valide est généré avec : `name`, `short_name`, `display: 'standalone'`, `orientation: 'portrait'`, icônes (192px + 512px), `theme_color`, `background_color`
2. L'application s'exécute en mode standalone sans barre de navigation du navigateur (FR35)
3. Les assets statiques (JS, CSS, icônes) sont précachés via Workbox pour l'accès au shell applicatif
4. Le mode portrait est maintenu de façon cohérente avec FR13

## Tasks / Subtasks

- [x] Task 1: `vite.config.ts` — ajouter VitePWA avec manifest + Workbox
- [x] Task 2: `index.html` — titre CorniScan + meta PWA (theme-color, apple-touch-icon, apple-mobile-web-app-capable)
- [x] Task 3: `public/icons/` — icônes PNG 192×192 et 512×512
- [x] Task 4: Tests manifest config

## Dev Notes

### Manifest config
- `name`: "CorniScan"
- `short_name`: "CorniScan"
- `display`: "standalone"
- `orientation`: "portrait"
- `theme_color`: "#111111"
- `background_color`: "#111111"
- `start_url`: "/"
- Icônes : `icons/icon-192.png` + `icons/icon-512.png`

### Workbox
- `globPatterns`: `['**/*.{js,css,html,ico,png,svg}']`
- `registerType`: `'autoUpdate'`

## Dev Agent Record

### Agent Model Used
claude-sonnet-4-6

### Completion Notes List
- vite-plugin-pwa v1.2.0 déjà installé dans package.json
- Icônes générées via OpenCV (backend .venv)

## File List

- `corniscan/frontend/vite.config.ts` (modifié)
- `corniscan/frontend/index.html` (modifié)
- `corniscan/frontend/public/icons/icon-192.png` (nouveau)
- `corniscan/frontend/public/icons/icon-512.png` (nouveau)
- `corniscan/frontend/src/pwa/__tests__/manifest-config.spec.ts` (nouveau)
