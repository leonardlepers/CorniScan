---
stepsCompleted: ['step-01-init', 'step-02-context', 'step-03-starter', 'step-04-decisions', 'step-05-patterns', 'step-06-structure', 'step-07-validation', 'step-08-complete']
inputDocuments: ['_bmad-output/planning-artifacts/prd.md', '_bmad-output/planning-artifacts/research/technical-CorniScan-stack-research-2026-02-21.md']
workflowType: 'architecture'
lastStep: 8
status: 'complete'
completedAt: '2026-02-21'
project_name: 'CorniScan'
user_name: 'Léo'
date: '2026-02-21'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Functional Requirements — 35 FRs en 7 domaines :**

| Domaine | FRs | Implication architecturale |
|---|---|---|
| Authentification & Sessions | FR1–4 | Module auth JWT, route guards |
| Administration comptes | FR5–8 | CRUD utilisateurs, gestion rôles admin/user |
| Capture Scan | FR9–13 | MediaDevices API, portrait lock, feedback temps réel carte |
| Traitement Image & Calibration | FR14–18 | Homographie + contours OpenCV, pipeline backend synchrone |
| Validation Scan | FR19–24 | Overlay contour, saisie épaisseur, gestion avertissement calibration |
| Génération & Livraison | FR25–29 | DXF R2018 ezdxf, email triple pièce jointe, retry SMTP |
| Erreurs & PWA | FR30–35 | Gestion d'erreurs uniforme, PWA manifest + service worker |

**Non-Functional Requirements structurants :**

- **Performance** : traitement < 5s → pipeline synchrone en RAM ; FCP < 2s → bundle JS < 300KB
- **Sécurité** : bcrypt ≥ 12 + HTTPS + session expiry + zéro stockage fichier serveur
- **Fiabilité** : > 99% uptime heures ouvrées ; validation DXF avant envoi ; retry SMTP transitoire
- **Intégration** : DXF AutoCAD 2018+ compatible ; format email stable et structuré

**Scale & Complexity :**

- Niveau : **Medium** — risque concentré sur la précision algo (Phase 0) et la détection carte live
- Domaine primaire : full-stack (Vue 3 SPA + FastAPI backend + module vision Python)
- Utilisateurs simultanés max : 5–10
- Composants architecturaux estimés : 4 (Frontend SPA, Backend API, Module Vision, Module Email/Output)

### Technical Constraints & Dependencies

- **Stateless strict** : aucun fichier persisté côté serveur — photos et DXF transitent uniquement en mémoire RAM (FastAPI `UploadFile` in-memory)
- **Stack contraint** : Python 3.11 + FastAPI + OpenCV + ezdxf (backend) / Vue 3 + Vite + Pinia (frontend) — défini dans la recherche technique
- **Déploiement** : Render Starter — un seul service web, HTTPS automatique, coût ≤ 10€/mois
- **Base de données** : 5–10 utilisateurs, données minimales (username + hash) — décision à prendre entre SQLite + persistent disk vs PostgreSQL hébergé
- **Connectivité** : WiFi/4G atelier, latence 1–3s tolérée, pas de mode offline

### Cross-Cutting Concerns Identifiés

- **Auth/Authorization** : JWT requis sur toutes les routes protégées (`/camera`, `/validation`, admin endpoints)
- **Gestion d'erreurs** : messages explicites avec action corrective sur toutes les couches (FR30–32, NFR-R2)
- **Traitement stateless** : aucune persistance fichier — contrainte transversale à tous les modules backend
- **Retry SMTP** : fiabilité de l'envoi email sans intervention utilisateur (NFR-I3)
- **Validation DXF** : vérification conformité avant envoi email (NFR-I2) — intégrée au pipeline, pas optionnelle

## Starter Template Evaluation

### Primary Technology Domain

Full-stack à deux runtimes : Vue 3 SPA (frontend) + FastAPI (backend Python). Initialisations indépendantes, déployées en tant que service unique sur Render (backend sert les assets frontend en production).

### Frontend — `create-vue` (officiel Vue)

**Commande d'initialisation :**

```bash
npm create vue@latest corniscan-frontend
# Options sélectionnées :
# ✅ TypeScript
# ✅ Vue Router
# ✅ Pinia
# ✅ ESLint + Prettier
# ✅ Vitest (unit tests)
# ❌ Playwright (E2E — hors scope MVP)
```

**Décisions architecturales fournies par le starter :**

- Language : TypeScript strict
- Build : Vite (HMR, bundle optimisé, < 300KB gzip atteignable)
- Routing : Vue Router 4 en mode `history`
- State : Pinia (stores photo/contour/auth)
- Linting : ESLint + Prettier
- Tests unitaires : Vitest
- Structure : `src/views/`, `src/components/`, `src/stores/`, `src/router/`
- PWA : ajout post-init via `vite-plugin-pwa` (Workbox)

### Backend — FastAPI avec `uv`

**Commande d'initialisation :**

```bash
uv init corniscan-backend
uv add fastapi uvicorn[standard] python-multipart \
        opencv-python-headless ezdxf \
        python-jose[cryptography] passlib[bcrypt] \
        sqlalchemy asyncpg alembic resend
```

**Décisions architecturales fournies :**

- Runtime : Python 3.11+, gestionnaire `uv` (lockfile déterministe)
- Serveur ASGI : Uvicorn
- Auth : `python-jose` (JWT) + `passlib` (bcrypt ≥ 12)
- ORM : SQLAlchemy Core (1 table users — pas d'ORM full)
- Vision : `opencv-python-headless` (sans GUI — adapté serveur)
- DXF : `ezdxf`
- Email : `resend` (Resend API — remplace aiosmtplib)
- Structure : `app/routers/`, `app/services/`, `app/models/`, `app/core/`

### Structure du Projet

```
corniscan/
├── frontend/          # Vue 3 SPA (create-vue)
│   ├── src/
│   │   ├── views/     # Login, Camera, Validation
│   │   ├── stores/    # auth, scan
│   │   └── router/
│   └── dist/          # Build statique servi par le backend
└── backend/           # FastAPI (uv init)
    ├── app/
    │   ├── routers/   # auth, admin, scan
    │   ├── services/  # vision, dxf, email
    │   └── core/      # config, security
    └── pyproject.toml
```

**Note :** En production, FastAPI sert les assets statiques du build Vue via `StaticFiles`. Un seul service Render.

## Core Architectural Decisions

### Decision Priority Analysis

**Critical Decisions (Bloquantes pour l'implémentation) :**

- Base de données : PostgreSQL Neon free tier (remplace SQLite+persistent disk)
- Détection carte live : capture périodique frontend → backend (remplace OpenCV.js WebAssembly)
- Email : Resend API (remplace aiosmtplib direct SMTP)

**Important Decisions (Structurent l'architecture) :**

- JWT stocké localStorage, session 8h, pas de refresh token MVP
- Pipeline traitement image : synchrone (pas d'async worker — latence < 5s acceptable)
- Frontend serving : FastAPI `StaticFiles` sert `frontend/dist/` en production

**Deferred Decisions (Post-MVP) :**

- Refresh token / rotation JWT
- Rate limiting par IP sur `/scan/*`
- Monitoring APM (Sentry, Datadog)

### Data Architecture

**Base de données :** PostgreSQL via Neon free tier

- Driver : `asyncpg` via SQLAlchemy async Core (pas d'ORM full — 1 seule table)
- Pool : `pool_size=2` (contrainte Neon free tier — max 5 connexions)
- URL : variable d'environnement `DATABASE_URL` (format `postgresql+asyncpg://...`)

**Schéma — table `users` :**

```sql
id                  SERIAL PRIMARY KEY
username            VARCHAR(50) UNIQUE NOT NULL
hashed_password     VARCHAR(255) NOT NULL
role                VARCHAR(10) NOT NULL DEFAULT 'user'  -- 'admin' | 'user'
force_password_change BOOLEAN NOT NULL DEFAULT false
created_at          TIMESTAMP DEFAULT NOW()
```

**Migrations :** Alembic (versionné, appliqué au démarrage du service Render)

**Validation données :** Pydantic v2 (intégré FastAPI) — schémas stricts sur tous les endpoints

**Caching :** Aucun — volume utilisateurs < 10, latence Neon acceptable

### Authentication & Security

- **JWT** : `python-jose` HS256, payload `{sub: username, role, exp}`
- **Session** : 8h, stocké `localStorage` côté frontend (`authStore`)
- **Pas de refresh token** pour le MVP (reconnexion explicite après expiry)
- **Hachage** : `passlib` bcrypt, salt cost 12
- **Route guards** : Vue Router `beforeEach` — redirige `/login` si pas de token valide
- **HTTPS** : automatique Render (TLS Let's Encrypt)
- **Headers sécurité** : `X-Content-Type-Options`, `X-Frame-Options` via FastAPI middleware

### API & Communication

**Design :** REST JSON, préfixe `/api/v1/`

**Endpoints :**

| Méthode | Route | Auth | Description |
|---|---|---|---|
| POST | `/api/v1/auth/token` | Non | Login → JWT |
| POST | `/api/v1/auth/change-password` | User | Changement mot de passe forcé |
| GET | `/api/v1/admin/users` | Admin | Liste utilisateurs |
| POST | `/api/v1/admin/users` | Admin | Créer utilisateur |
| PATCH | `/api/v1/admin/users/{id}` | Admin | Modifier / reset mdp |
| DELETE | `/api/v1/admin/users/{id}` | Admin | Supprimer utilisateur |
| POST | `/api/v1/scan/detect-card` | User | Détection carte live (frame JPEG) |
| POST | `/api/v1/scan/process` | User | Pipeline complet (photo → contour DXF) |
| POST | `/api/v1/scan/send` | User | Envoi email (DXF + aperçu) |

**Détection carte live (FR10) :**

- Frontend : `setInterval(500ms)` → `canvas.toBlob('image/jpeg', 0.6)` → `POST /api/v1/scan/detect-card`
- Backend : OpenCV détection rectangle → réponse `{"card_detected": bool, "confidence": float}`
- UX : overlay couleur sur le viewfinder (vert = carte détectée, rouge = absent)

**Format erreur uniforme :**

```json
{"detail": "Message explicite en français avec action corrective"}
```

**Documentation API :** Swagger UI intégré FastAPI (`/docs`) — désactivé en production

### Frontend Architecture

**State Management (Pinia) :**

```
authStore   → token, user {username, role, force_password_change}, isAuthenticated
scanStore   → photo (File), contour (points[]), dimensions {thickness}, hasPhoto
```

**Routing (Vue Router 4) :**

| Route | Guard | Composant |
|---|---|---|
| `/login` | Public (redirect si auth) | `LoginView` |
| `/camera` | `requireAuth` | `CameraView` |
| `/validation` | `requireAuth` + `requirePhoto` | `ValidationView` |
| `/admin` | `requireAdmin` | `AdminView` |

**Guard `requirePhoto`** : vérifie `scanStore.hasPhoto` avant accès `/validation` — redirige `/camera` si absent

**Bundle :** Vite code splitting par route — target < 300KB gzip initial chunk

**PWA :** `vite-plugin-pwa` + Workbox, manifest Android + guide install iOS affiché au premier login

### Infrastructure & Deployment

**Hébergement :** Render Starter (1 service web Python)

- FastAPI sert `frontend/dist/` via `StaticFiles(directory="frontend/dist")`
- Route fallback `GET /{path}` → `index.html` (SPA routing)

**Variables d'environnement Render :**

```
DATABASE_URL      postgresql+asyncpg://...neon.tech/corniscan
JWT_SECRET        <secret 256-bit généré>
RESEND_API_KEY    re_...
```

**Email (Resend API) :**

- SDK Python `resend`
- 3 000 emails/mois gratuits — largement suffisant
- Pièces jointes : DXF + aperçu PNG + image originale
- Retry : 2 tentatives avec délai 2s avant erreur surfacée au client

**CI/CD :** Render déploie automatiquement sur push `main` — pas de pipeline CI MVP

**Build script Render :**

```bash
cd frontend && npm install && npm run build
cd ../backend && pip install uv && uv sync
```

**Start command :** `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Decision Impact Analysis

**Séquence d'implémentation recommandée :**

1. Init projet (frontend create-vue + backend uv init)
2. Base de données : Neon + Alembic + table users
3. Auth : JWT endpoints + Vue Router guards
4. Admin : CRUD utilisateurs
5. Camera : MediaDevices + détection carte live
6. Pipeline vision : OpenCV homographie + contours
7. Validation : overlay contour + saisie épaisseur
8. Génération : DXF ezdxf + email Resend
9. PWA : vite-plugin-pwa + manifest

**Cross-Component Dependencies :**

- `authStore` → alimenté par `/auth/token` → requis par tous les guards router
- `scanStore.photo` → prérequis `/scan/process` → prérequis `/scan/send`
- Alembic migrations → doivent s'exécuter avant le premier démarrage
- `frontend/dist/` → doit être buildé avant que FastAPI `StaticFiles` puisse servir

## Implementation Patterns & Consistency Rules

### Points de Conflit Identifiés

7 zones où des agents IA pourraient faire des choix incompatibles entre eux.

### Naming Patterns

**JSON & API — snake_case partout :**

- FastAPI renvoie du snake_case (défaut Python/Pydantic) — pas d'`alias_generator`
- Stores Pinia utilisent snake_case pour les champs issus de l'API
- Exception : variables locales TypeScript en camelCase (`isLoading`, `hasPhoto`)

```python
# ✅ Backend Pydantic
class UserOut(BaseModel):
    id: int
    username: str
    role: str
    force_password_change: bool

# ✅ Frontend store — garde snake_case pour les données API
const user = ref<{username: string, role: string, force_password_change: boolean} | null>(null)
```

**Base de données — snake_case, tables au pluriel :**

```sql
-- ✅
users, force_password_change, created_at
-- ❌
Users, forcePasswordChange, createdAt
```

**Fichiers Frontend :**

- Composants Vue : `PascalCase.vue` (`LoginView.vue`, `ScanOverlay.vue`)
- Stores Pinia : `camelCase.ts` (`authStore.ts`, `scanStore.ts`)
- Services : `camelCase.ts` (`apiClient.ts`, `cameraService.ts`)
- Tests : `NomDuFichier.spec.ts` co-localisé avec le fichier testé

**Fichiers Backend :**

- Routers : `snake_case.py` (`auth.py`, `admin.py`, `scan.py`)
- Services : `snake_case.py` (`vision_service.py`, `dxf_service.py`, `email_service.py`)
- Modèles Pydantic : `PascalCase` dans le fichier (`UserCreate`, `UserOut`, `ScanResult`)

**Code Python :** snake_case fonctions/variables, PascalCase classes — PEP 8 strict

**Code TypeScript :** camelCase variables/fonctions, PascalCase classes/interfaces/composants

### Structure Patterns

**Backend — dossier `tests/` séparé :**

```
backend/
└── tests/
    ├── test_auth.py
    ├── test_admin.py
    ├── test_scan.py
    └── conftest.py   # fixtures Pytest partagées
```

**Frontend — logique dans les stores, composables pour l'UI :**

```
src/
├── stores/
│   ├── authStore.ts        # token, user, isAuthenticated — logique auth
│   └── scanStore.ts        # photo, contour, dimensions — logique scan
├── composables/
│   └── useMediaDevices.ts  # accès caméra — logique UI pure
└── services/
    └── apiClient.ts        # wrapper fetch centralisé
```

### Format Patterns

**Réponses API — JSON direct (pas de wrapper d'enveloppe) :**

```json
// ✅ Succès
{"id": 1, "username": "leo", "role": "admin", "force_password_change": false}

// ✅ Erreur (FastAPI HTTPException)
{"detail": "Identifiants incorrects. Vérifiez votre nom d'utilisateur et mot de passe."}

// ❌ Pas de wrapper
{"success": true, "data": {...}, "error": null}
```

**HTTP Status Codes :**

| Code | Usage |
|---|---|
| `200` | Succès GET / réponse standard |
| `201` | Création réussie (POST /admin/users) |
| `400` | Validation input |
| `401` | Non authentifié |
| `403` | Accès refusé (rôle insuffisant) |
| `404` | Ressource introuvable |
| `422` | Erreur Pydantic (validation automatique FastAPI) |
| `500` | Erreur serveur inattendue |

### Communication Patterns

**Appels API Frontend — wrapper centralisé `apiClient.ts` :**

```typescript
// src/services/apiClient.ts
// Injecte automatiquement le header Authorization + gère les 401 (redirect /login)
export async function apiCall<T>(endpoint: string, options?: RequestInit): Promise<T>

// ✅ Usage dans les stores
const user = await apiCall<UserOut>('/api/v1/admin/users/1')

// ❌ fetch() nu dans un composant ou store
const res = await fetch('/api/v1/admin/users', {headers: {'Authorization': `Bearer ${token}`}})
```

**États de chargement — convention `isLoading` + `error` dans chaque store :**

```typescript
// Pattern standard dans tous les stores Pinia
const isLoading = ref(false)
const error = ref<string | null>(null)

async function doAction() {
  isLoading.value = true
  error.value = null
  try {
    // appel API via apiClient
  } catch (e: any) {
    error.value = e.message ?? 'Erreur inattendue'
  } finally {
    isLoading.value = false
  }
}
```

### Process Patterns

**Gestion d'erreurs :**

- Backend : `HTTPException(status_code=..., detail="Message en français")` — toujours
- Frontend : `apiClient.ts` intercepte, extrait `detail`, propage comme `Error(detail)`
- UI : afficher `store.error` dans un composant `<ErrorBanner>` au niveau de la vue
- Logger backend : `logging.error(...)` pour les 500 — jamais exposé au client

**Retry — uniquement pour l'email Resend :**

```python
for attempt in range(3):
    try:
        await send_email(...)
        break
    except Exception:
        if attempt == 2:
            raise
        await asyncio.sleep(2)
```

**Auth guard Vue Router — ordre des vérifications :**

```typescript
// router/index.ts — beforeEach
// 1. Route publique → laisser passer
// 2. Pas de token → redirect /login
// 3. Route admin + rôle user → redirect /camera
// 4. force_password_change + pas sur /change-password → redirect /change-password
```

### Enforcement Guidelines

**Tous les agents DOIVENT :**

- Utiliser `apiClient.ts` pour tout appel HTTP côté frontend (jamais de `fetch()` nu)
- Lever `HTTPException` avec `detail` en français sur toutes les erreurs backend
- Nommer les champs JSON en snake_case (données API) et camelCase (variables locales TS)
- Placer la logique métier dans les stores Pinia, pas dans les composants
- Suivre `isLoading` + `error` dans chaque store pour les états async
- Co-localiser les tests frontend (`.spec.ts`) et séparer les tests backend dans `tests/`

**Anti-patterns interdits :**

```python
# ❌ Return dict brut non typé
return {"status": "ok", "user": user_dict}

# ✅ Pydantic model validé
return UserOut.model_validate(user)
```

## Project Structure & Boundaries

### Complete Project Directory Structure

```
corniscan/
├── .gitignore
├── README.md
│
├── frontend/                           # Vue 3 SPA (create-vue + TypeScript)
│   ├── package.json
│   ├── vite.config.ts                  # Vite + vite-plugin-pwa (Workbox)
│   ├── tsconfig.json
│   ├── tsconfig.app.json
│   ├── tsconfig.node.json
│   ├── .eslintrc.js
│   ├── index.html
│   ├── public/
│   │   ├── pwa-192x192.png
│   │   └── pwa-512x512.png
│   ├── dist/                           # Build statique (servi par FastAPI)
│   └── src/
│       ├── main.ts
│       ├── App.vue
│       ├── env.d.ts
│       ├── router/
│       │   └── index.ts                # Routes + guards (requireAuth, requireAdmin, requirePhoto)
│       ├── stores/
│       │   ├── authStore.ts            # token, user, isAuthenticated — FR1–4, FR5–8
│       │   └── scanStore.ts            # photo, contour, dimensions, hasPhoto — FR9–24
│       ├── services/
│       │   └── apiClient.ts            # Wrapper fetch centralisé + injection JWT header
│       ├── composables/
│       │   └── useMediaDevices.ts      # MediaDevices API, portrait lock — FR9, FR11
│       ├── views/
│       │   ├── LoginView.vue           # FR1–4 (auth + change-password forcé)
│       │   ├── CameraView.vue          # FR9–13 (flux caméra + détection carte live)
│       │   ├── ValidationView.vue      # FR19–24 (overlay contour + saisie épaisseur)
│       │   └── AdminView.vue           # FR5–8 (CRUD utilisateurs)
│       └── components/
│           ├── common/
│           │   ├── ErrorBanner.vue     # FR30–32 (affichage erreurs uniformes)
│           │   └── LoadingSpinner.vue  # états isLoading
│           ├── camera/
│           │   ├── CardOverlay.vue     # FR10 (overlay vert/rouge détection carte)
│           │   └── CaptureButton.vue   # FR12 (déclencheur capture)
│           └── validation/
│               ├── ContourOverlay.vue  # FR20 (overlay SVG contour joint)
│               └── ThicknessInput.vue  # FR21–22 (saisie + avertissement épaisseur)
│
└── backend/                            # FastAPI (Python 3.11, uv)
    ├── pyproject.toml                  # uv deps : fastapi, uvicorn, opencv, ezdxf, jose, passlib, sqlalchemy, asyncpg, alembic, resend
    ├── .env.example                    # DATABASE_URL, JWT_SECRET, RESEND_API_KEY
    ├── alembic.ini
    ├── alembic/
    │   ├── env.py
    │   └── versions/
    │       └── 001_create_users_table.py
    ├── app/
    │   ├── main.py                     # FastAPI app, StaticFiles("frontend/dist"), routers, startup migrations
    │   ├── routers/
    │   │   ├── auth.py                 # POST /api/v1/auth/token, POST /api/v1/auth/change-password
    │   │   ├── admin.py                # GET/POST/PATCH/DELETE /api/v1/admin/users
    │   │   └── scan.py                 # POST /api/v1/scan/detect-card, /process, /send
    │   ├── services/
    │   │   ├── vision_service.py       # FR14–18 : homographie carte → contour joint (OpenCV)
    │   │   ├── dxf_service.py          # FR25–26 : génération DXF R2018 (ezdxf) + validation
    │   │   └── email_service.py        # FR27–29 : envoi Resend + retry 2× (3 pièces jointes)
    │   ├── models/
    │   │   ├── user.py                 # SQLAlchemy Table "users" (AsyncEngine)
    │   │   └── schemas.py              # Pydantic v2 : UserCreate, UserOut, TokenResponse, ScanResult, CardDetectionResult
    │   └── core/
    │       ├── config.py               # pydantic-settings : DATABASE_URL, JWT_SECRET, RESEND_API_KEY
    │       ├── database.py             # create_async_engine, AsyncSession, get_db dependency
    │       └── security.py             # create_access_token, verify_token, hash_password, verify_password
    └── tests/
        ├── conftest.py                 # fixtures : test DB, FastAPI TestClient
        ├── test_auth.py                # FR1–4
        ├── test_admin.py               # FR5–8
        └── test_scan.py                # FR9–29 (pipeline + email mock)
```

### Architectural Boundaries

**API Boundaries :**

- Frontière unique : `/api/v1/*` — tout ce qui passe cette frontière est JSON validé Pydantic
- Routes publiques : `POST /api/v1/auth/token` uniquement
- Routes user : `/api/v1/auth/change-password`, `/api/v1/scan/*`
- Routes admin : `/api/v1/admin/*` — middleware vérifie `role == 'admin'`
- Assets statiques : `GET /*` → `frontend/dist/index.html` (SPA fallback) — pas d'auth

**Component Boundaries :**

- `CameraView` ne connaît pas `ValidationView` — communique uniquement via `scanStore`
- `scanStore.hasPhoto` → frontière de navigation (guard `requirePhoto`)
- `authStore` → source unique de vérité pour le token JWT (lu par `apiClient.ts`)

**Service Boundaries (Backend) :**

- `vision_service.py` : reçoit `bytes` (image JPEG), retourne `ContourResult(points, calibration_ok)`
- `dxf_service.py` : reçoit `ContourResult + thickness`, retourne `bytes` (fichier DXF)
- `email_service.py` : reçoit `bytes DXF + bytes PNG + bytes JPEG + recipient`, retourne `bool`
- Chaque service est indépendant — pas d'import croisé entre services

**Data Boundaries :**

- PostgreSQL Neon : accessible uniquement via `app/core/database.py` (dependency injection FastAPI)
- Fichiers (photos, DXF, PNG) : jamais persistés — transitent en `bytes` RAM uniquement
- Variables d'environnement : lues uniquement dans `app/core/config.py` (settings singleton)

### Requirements to Structure Mapping

| Domaine | FRs | Backend | Frontend |
|---|---|---|---|
| Auth & Sessions | FR1–4 | `routers/auth.py`, `core/security.py` | `views/LoginView.vue`, `stores/authStore.ts`, `router/index.ts` |
| Admin comptes | FR5–8 | `routers/admin.py` | `views/AdminView.vue` |
| Capture Scan | FR9–13 | `routers/scan.py` (detect-card) | `views/CameraView.vue`, `composables/useMediaDevices.ts`, `components/camera/` |
| Traitement Image | FR14–18 | `services/vision_service.py`, `routers/scan.py` (process) | `stores/scanStore.ts` (contour reçu) |
| Validation Scan | FR19–24 | — | `views/ValidationView.vue`, `components/validation/` |
| Génération & Livraison | FR25–29 | `services/dxf_service.py`, `services/email_service.py`, `routers/scan.py` (send) | `views/ValidationView.vue` (déclencheur) |
| Erreurs & PWA | FR30–35 | `app/main.py` (exception handlers) | `components/common/ErrorBanner.vue`, `vite.config.ts` |

**Cross-Cutting Concerns :**

| Concern | Fichier(s) |
|---|---|
| Auth JWT | `backend/app/core/security.py` + `frontend/src/services/apiClient.ts` |
| Gestion erreurs uniforme | `backend/app/main.py` (handler global) + `frontend/src/components/common/ErrorBanner.vue` |
| Traitement stateless | Règle : aucun `open()` / `write()` dans les services — uniquement `bytes` |
| Retry email | `backend/app/services/email_service.py` |
| Validation DXF | `backend/app/services/dxf_service.py` (ezdxf validate avant retour) |

### Integration Points

**Flux de données principal (scan complet) :**

```
[CameraView] → canvas.toBlob() → apiClient.ts
  → POST /api/v1/scan/process (multipart JPEG)
  → [scan.py] → vision_service.py → ContourResult
  → JSON {contour, calibration_ok} → scanStore.contour

[ValidationView] → ThicknessInput → apiClient.ts
  → POST /api/v1/scan/send {thickness, email}
  → [scan.py] → dxf_service.py → bytes DXF
  → [scan.py] → email_service.py → Resend API
  → JSON {success: true}
```

**Intégrations externes :**

| Service | Intégration | Fichier |
|---|---|---|
| Neon PostgreSQL | asyncpg via SQLAlchemy | `app/core/database.py` |
| Resend API | SDK Python `resend` | `app/services/email_service.py` |
| Render (hébergement) | Uvicorn ASGI + env vars | `app/main.py` + `pyproject.toml` |

### Development Workflow

**Dev local :**

```bash
# Terminal 1 — Backend
cd backend && uv run uvicorn app.main:app --reload --port 8000

# Terminal 2 — Frontend (Vite proxy /api/* → localhost:8000)
cd frontend && npm run dev
```

**Build production (Render) :**

```bash
cd frontend && npm install && npm run build   # → frontend/dist/
cd ../backend && uv sync
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Migrations au démarrage :**

```python
# app/main.py — lifespan event
# alembic upgrade head → exécuté avant de servir les requêtes
```

## Architecture Validation Results

### Coherence Validation ✅

**Decision Compatibility :** Toutes les technologies choisies sont mutuellement compatibles.
Vue 3/TypeScript/Pinia/Vue Router 4 forment l'ecosystem officiel Vue. FastAPI + asyncpg +
SQLAlchemy async Core forment un stack async cohérent. python-jose + passlib sont le standard
FastAPI auth. Resend SDK et ezdxf sont indépendants, sans conflit.

**Issue résolue — OpenCV sync dans FastAPI async :**
Les endpoints `/scan/process` et `/scan/detect-card` sont déclarés `def` (synchrones) plutôt
qu'`async def`. FastAPI/Uvicorn les exécute dans un thread pool automatiquement — adapté au
code CPU-bound OpenCV sans bloquer l'event loop, sans complexité pour une charge < 10 users.

```python
# Pattern : endpoints CPU-bound → def synchrone
@router.post("/process")
def process_scan(file: UploadFile, current_user: User = Depends(get_current_user)):
    return vision_service.process(file.file.read())
```

**Pattern Consistency :** snake_case uniforme JSON/BD/Python. apiClient.ts centralise tous les
appels HTTP. isLoading + error standardisés dans tous les stores Pinia. ✅

**Structure Alignment :** Structure complète et spécifique. Frontière `/api/v1/*` bien définie.
Boundaries services (bytes in → bytes out) respectent la contrainte stateless. ✅

### Requirements Coverage Validation ✅

**Functional Requirements (35 FRs) :** Couverture complète confirmée.

| Domaine | FRs | Status |
|---|---|---|
| Auth & Sessions | FR1–4 | ✅ auth.py + security.py + authStore + router guards |
| Admin comptes | FR5–8 | ✅ admin.py + AdminView.vue |
| Capture Scan | FR9–13 | ✅ CameraView + useMediaDevices + /scan/detect-card |
| Traitement Image | FR14–18 | ✅ vision_service.py + /scan/process |
| Validation Scan | FR19–24 | ✅ ValidationView + ContourOverlay + ThicknessInput |
| Génération & Livraison | FR25–29 | ✅ dxf_service.py + email_service.py + Resend |
| Erreurs & PWA | FR30–35 | ✅ ErrorBanner + exception handlers + vite-plugin-pwa |

**Non-Functional Requirements (14 NFRs) :** Couverture complète confirmée.

- Performance (< 5s / FCP < 2s / bundle < 300KB) : pipeline RAM sync + Vite splitting + StaticFiles ✅
- Sécurité (bcrypt 12 / HTTPS / stateless) : passlib + Render TLS + règle bytes RAM ✅
- Fiabilité (DXF valid / retry email) : ezdxf validate + 2 retries × 2s ✅
- Intégration (DXF R2018 / email stable) : ezdxf R2018 + Resend API ✅

### Implementation Readiness Validation ✅

**Decision Completeness :**
- 3 décisions critiques documentées avec rationale ✅
- 9 endpoints listés avec méthode, route, auth, description ✅
- Versions et commandes init complètes ✅

**Structure Completeness :**
- Arbre complet avec tous les fichiers et leur responsabilité ✅
- Boundaries services (signature in/out) documentées ✅
- Mapping FR → fichiers exhaustif ✅
- Flux de données principal documenté ✅

**Pattern Completeness :**
- 7 zones de conflit identifiées et résolues ✅
- Exemples ✅/❌ fournis pour chaque pattern ✅
- Guard order documenté ✅
- Retry pattern documenté ✅

### Gap Analysis Results

**Critical Gaps :** Aucun

**Important Gaps résolus :**
- OpenCV sync dans FastAPI async → endpoints `/scan/process` et `/scan/detect-card` déclarés `def`

**Minor Gaps documentés :**
- `vite.config.ts` doit configurer un proxy dev :

```typescript
// vite.config.ts — server.proxy pour dev local
server: {
  proxy: {
    '/api': 'http://localhost:8000'
  }
}
```

### Architecture Completeness Checklist

**✅ Requirements Analysis**
- [x] Contexte projet analysé (35 FRs, 14 NFRs, 4 composants)
- [x] Scale et complexité évalués (Medium, 5–10 users)
- [x] Contraintes techniques identifiées (stateless, Render Starter, Neon free tier)
- [x] Cross-cutting concerns mappés (auth, erreurs, retry, validation DXF)

**✅ Architectural Decisions**
- [x] Décisions critiques documentées (PostgreSQL Neon, détection carte, Resend)
- [x] Stack complet spécifié (versions et commandes init)
- [x] Patterns d'intégration définis (REST JSON, apiClient, StaticFiles)
- [x] Performance et sécurité adressés (synchrone RAM, bcrypt 12, HTTPS)

**✅ Implementation Patterns**
- [x] Naming conventions établies (snake_case/camelCase règles)
- [x] Structure patterns définis (stores vs composables, tests séparés)
- [x] Communication patterns spécifiés (apiClient, isLoading/error)
- [x] Process patterns documentés (error handling, retry, guard order)
- [x] Anti-patterns interdits documentés

**✅ Project Structure**
- [x] Structure complète avec tous les fichiers
- [x] Boundaries composants et services établies
- [x] Integration points mappés (flux scan, Neon, Resend)
- [x] Mapping FR → structure exhaustif

### Architecture Readiness Assessment

**Overall Status : PRÊT POUR L'IMPLÉMENTATION** ✅

**Confidence Level : Élevé**

**Key Strengths :**
- Stack homogène et sans conflit — ecosystem Vue officiel + FastAPI standard
- Contrainte stateless stricte bien supportée (bytes RAM uniquement)
- Boundaries services claires (vision, dxf, email indépendants)
- Patterns précis pour guider des agents IA sans ambiguïté

**Areas for Future Enhancement (post-MVP) :**
- Refresh token / rotation JWT
- Rate limiting `/scan/*`
- Monitoring APM (Sentry)
- Tests E2E (Playwright)

### Implementation Handoff

**First Implementation Step :**

```bash
# Frontend
npm create vue@latest corniscan-frontend
# ✅ TypeScript / Vue Router / Pinia / ESLint+Prettier / Vitest

# Backend
uv init corniscan-backend
uv add fastapi uvicorn[standard] python-multipart \
        opencv-python-headless ezdxf \
        python-jose[cryptography] passlib[bcrypt] \
        sqlalchemy asyncpg alembic resend
```

**AI Agent Guidelines :**
- Suivre les décisions architecturales exactement telles que documentées
- Utiliser les patterns d'implémentation de façon cohérente entre tous les composants
- Respecter la structure et les boundaries du projet
- Déclarer `def` (pas `async def`) les endpoints qui appellent `vision_service.py`
- Se référer à ce document pour toute question architecturale
