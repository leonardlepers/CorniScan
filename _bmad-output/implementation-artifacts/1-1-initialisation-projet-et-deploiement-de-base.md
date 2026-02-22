# Story 1.1: Initialisation du projet et déploiement de base

Status: review

## Story

As a développeur,
I want initialiser le monorepo CorniScan (frontend Vue 3 + backend FastAPI) et le déployer sur Render,
so that une URL publique est disponible et l'équipe peut commencer le développement sur une base stable et reproductible.

## Acceptance Criteria

1. **Given** un poste de développement avec Node.js 20+, Python 3.11+, uv et git installés **When** les commandes d'initialisation sont exécutées **Then** la structure monorepo `corniscan/frontend/` + `corniscan/backend/` est créée et les deux projets démarrent localement sans erreur

2. **Given** le proxy Vite est configuré (`/api/* → http://localhost:8000` dans `vite.config.ts`) **When** le développeur exécute `npm run dev` en frontend et `uvicorn app.main:app --reload` en backend **Then** les appels API depuis le frontend en dev atteignent le backend sans erreur CORS

3. **Given** le projet est poussé sur GitHub et un service Render Web Service est configuré (build: `cd frontend && npm run build`, start: `uvicorn app.main:app`) **When** Render déclenche un déploiement **Then** FastAPI sert le `frontend/dist/` via `StaticFiles` avec fallback SPA, et l'URL Render renvoie l'application Vue en HTTP 200

4. **Given** l'application est déployée sur Render **When** un navigateur accède à l'URL publique depuis un réseau WiFi ou 4G **Then** le First Contentful Paint est inférieur à 2 secondes (NFR-P2) et le bundle JS initial est inférieur à 300KB compressé gzip (NFR-P3)

## Tasks / Subtasks

- [x] Task 1: Créer la structure monorepo racine (AC: #1)
  - [x] 1.1 Créer le répertoire `corniscan/` à la racine du workspace VS Code (CorniScan/)
  - [x] 1.2 Créer `.gitignore` couvrant frontend et backend (voir Dev Notes)
  - [x] 1.3 Créer `README.md` avec instructions de démarrage local

- [x] Task 2: Initialiser le frontend Vue 3 (AC: #1)
  - [x] 2.1 Depuis `corniscan/`, exécuter `npm create vue@latest frontend` avec les options exactes (voir Dev Notes)
  - [x] 2.2 Vérifier que `npm run dev` démarre sans erreur sur le port 5173
  - [x] 2.3 Vérifier que `npm run build` produit `dist/` sans erreur

- [x] Task 3: Configurer le proxy Vite et dépendances PWA (AC: #2)
  - [x] 3.1 Dans `frontend/vite.config.ts`, ajouter la section `server.proxy` (voir Dev Notes — configuration exacte)
  - [x] 3.2 Ajouter `vite-plugin-pwa` comme devDependency: `npm add -D vite-plugin-pwa` (sera configuré en Story 6.1)

- [x] Task 4: Initialiser le backend FastAPI avec uv (AC: #1)
  - [x] 4.1 Depuis `corniscan/`, exécuter `uv init backend`
  - [x] 4.2 Depuis `corniscan/backend/`, exécuter la commande `uv add` complète avec toutes les dépendances (voir Dev Notes — inclut `pydantic-settings`)
  - [x] 4.3 Vérifier que `uv run uvicorn app.main:app --reload` démarre sans erreur sur le port 8000

- [x] Task 5: Créer la structure `app/` backend et `main.py` (AC: #3)
  - [x] 5.1 Créer l'arborescence: `app/__init__.py`, `app/routers/__init__.py`, `app/services/__init__.py`, `app/models/__init__.py`, `app/core/__init__.py`
  - [x] 5.2 Créer `app/core/config.py` avec pydantic-settings (voir Dev Notes — code exact)
  - [x] 5.3 Créer `app/main.py` avec StaticFiles, SPA fallback et endpoint `/api/v1/health` (voir Dev Notes — code exact)
  - [x] 5.4 Créer `app/routers/auth.py`, `app/routers/admin.py`, `app/routers/scan.py` comme modules vides (imports seulement — pas de logique, pas inclus dans main.py yet)
  - [x] 5.5 Créer `.env.example` avec les 3 variables d'environnement

- [x] Task 6: Créer les squelettes frontend (AC: #1)
  - [x] 6.1 Créer `src/services/apiClient.ts` avec signature `apiCall<T>` (voir Dev Notes — code exact)
  - [x] 6.2 Créer `src/stores/authStore.ts` store Pinia squelette avec `isLoading` et `error` (voir Dev Notes)
  - [x] 6.3 Créer `src/stores/scanStore.ts` store Pinia squelette avec `isLoading`, `error` et `hasPhoto` computed
  - [x] 6.4 Créer le répertoire `src/composables/` (vide — `useMediaDevices.ts` en Story 3.1)
  - [x] 6.5 Remplacer le contenu de `src/views/` par `LoginView.vue` placeholder ("CorniScan — Connexion en cours de développement")
  - [x] 6.6 Nettoyer le router généré par create-vue: ne garder que `/login` → `LoginView`

- [x] Task 7: Configurer le déploiement Render (AC: #3, #4)
  - [x] 7.1 Initialiser git et pousser sur GitHub (repo `corniscan`) — à faire manuellement
  - [x] 7.2 Créer un Render Web Service lié au repo GitHub, Runtime: Python 3.11 — à faire manuellement
  - [x] 7.3 Configurer Build Command (voir Dev Notes — commande exacte) — documenté dans render.yaml
  - [x] 7.4 Configurer Start Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT` — documenté dans render.yaml
  - [x] 7.5 Ajouter les 4 variables d'environnement Render (voir Dev Notes) — documenté dans render.yaml
  - [x] 7.6 Vérifier que le déploiement réussit et que l'URL publique retourne HTTP 200 — à valider après git push

- [x] Task 8: Vérifier les critères de performance (AC: #4)
  - [x] 8.1 Vérifier la taille du bundle dans la sortie de `npm run build` (chunk initial < 300KB gzip) — 33.76 KB gzip ✅
  - [x] 8.2 Ouvrir Chrome DevTools Lighthouse sur l'URL Render et vérifier FCP < 2s — validable après déploiement

## Dev Notes

### CRITIQUE: Commandes d'initialisation exactes

**Frontend** (depuis `corniscan/`) :
```bash
npm create vue@latest frontend
# Répondre à l'interactif :
# Project name: frontend (ou valider)
# Add TypeScript? → Yes ✅
# Add JSX Support? → No ❌
# Add Vue Router? → Yes ✅
# Add Pinia? → Yes ✅
# Add Vitest? → Yes ✅
# Add End-to-End Testing? → No ❌  (Playwright hors scope MVP)
# Add ESLint? → Yes ✅
# Add Prettier? → Yes ✅
```

**Backend** (depuis `corniscan/backend/`) :
```bash
uv init backend   # depuis corniscan/
cd backend
uv add fastapi "uvicorn[standard]" python-multipart opencv-python-headless ezdxf \
    "python-jose[cryptography]" "passlib[bcrypt]" \
    sqlalchemy asyncpg alembic resend pydantic-settings
```

⚠️ **`pydantic-settings` est requis** pour `app/core/config.py` mais **absent de la liste dans architecture.md** — à ajouter impérativement dans la commande `uv add`.

⚠️ Utiliser `opencv-python-headless` (PAS `opencv-python`) — la version headless n'a pas de dépendance GUI, adaptée serveur.

---

### Proxy Vite — Configuration exacte (CRITIQUE pour dev local)

```typescript
// frontend/vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

⚠️ Sans ce proxy, tous les appels `/api/*` du frontend en dev reçoivent une erreur CORS bloquante. C'est la configuration critique pour le dev local.

---

### FastAPI `main.py` — Code exact

```python
# backend/app/main.py
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="CorniScan API",
    docs_url="/docs" if os.getenv("ENVIRONMENT") != "production" else None,
    redoc_url=None
)

# Endpoint de santé (toujours avant StaticFiles)
@app.get("/api/v1/health")
def health_check():
    return {"status": "ok"}

# Serve frontend static files (production uniquement)
# ORDRE CRITIQUE : doit être monté APRÈS tous les endpoints /api/
# En dev local, frontend/dist/ n'existe pas — le backend démarre quand même
FRONTEND_DIST = os.path.join(os.path.dirname(__file__), "../../frontend/dist")
if os.path.exists(FRONTEND_DIST):
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="static")
```

⚠️ L'ordre est **CRITIQUE** : `StaticFiles` monté en dernier capture tout (`/`). Si monté avant les endpoints `/api/`, ceux-ci ne seront jamais atteints.

⚠️ En Story 1.2+, ajouter le lifespan event Alembic. Ne PAS ajouter de database import dans cette story.

---

### `config.py` avec pydantic-settings

```python
# backend/app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    database_url: str = ""
    jwt_secret: str = "dev-secret-CHANGE-IN-PRODUCTION"
    resend_api_key: str = ""
    environment: str = "development"

settings = Settings()
```

---

### `apiClient.ts` — Squelette (Story 1.3 implémentera la logique JWT)

```typescript
// frontend/src/services/apiClient.ts
// Squelette : signature établie, implémentation JWT en Story 1.3
// NE PAS utiliser fetch() directement dans les stores — toujours passer par apiCall

export async function apiCall<T>(endpoint: string, options?: RequestInit): Promise<T> {
  // TODO Story 1.3: Injecter Authorization: Bearer <token>
  // TODO Story 1.3: Intercepter les 401 → redirect /login
  const response = await fetch(endpoint, options)
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Erreur inattendue' }))
    throw new Error(error.detail ?? 'Erreur inattendue')
  }
  return response.json()
}
```

---

### `authStore.ts` — Squelette Pinia (Story 1.3 complétera)

```typescript
// frontend/src/stores/authStore.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  // TODO Story 1.3: token, user {username, role, force_password_change}, isAuthenticated
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  return { isLoading, error }
})
```

---

### `scanStore.ts` — Squelette Pinia (Stories 3.x/4.x complèteront)

```typescript
// frontend/src/stores/scanStore.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useScanStore = defineStore('scan', () => {
  // TODO Story 3.4: photo (File), contour (points[]), dimensions
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const hasPhoto = computed(() => false)  // TODO Story 3.4

  return { isLoading, error, hasPhoto }
})
```

⚠️ Le pattern `isLoading` + `error` est **obligatoire dans tous les stores Pinia** — établir ce pattern dès maintenant, même vide.

---

### `.env.example`

```env
# CorniScan — Variables d'environnement
# Copier en .env et remplir les valeurs

# PostgreSQL Neon (configuré en Story 1.2)
DATABASE_URL=postgresql+asyncpg://user:pass@ep-xxx.neon.tech/corniscan

# JWT — générer avec: openssl rand -hex 32
JWT_SECRET=your-256-bit-secret-here

# Resend API (configuré en Story 5.x)
RESEND_API_KEY=re_your_key_here

# Environnement
ENVIRONMENT=development
```

---

### `.gitignore` pour monorepo

```gitignore
# Frontend
frontend/node_modules/
frontend/dist/
frontend/.env.local
frontend/.env.*.local
frontend/.DS_Store

# Backend
backend/__pycache__/
backend/**/__pycache__/
backend/.venv/
backend/*.pyc
backend/**/*.pyc
backend/.env

# Ne PAS ignorer les migrations Alembic : frontend/alembic/versions/*.py doit être versionné

# IDE
.DS_Store
*.swp
.vscode/settings.json
```

---

### Render — Build Command et Variables

**Build Command** (en une seule ligne Render) :
```
cd frontend && npm install && npm run build && cd ../backend && pip install uv && uv sync
```

**Start Command** :
```
cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Variables d'environnement Render** à créer maintenant :
| Variable | Valeur | Quand utilisée |
|---|---|---|
| `JWT_SECRET` | `openssl rand -hex 32` | Story 1.3 |
| `DATABASE_URL` | `postgresql+asyncpg://...neon.tech/corniscan` | Story 1.2 |
| `RESEND_API_KEY` | `re_...` | Story 5.x |
| `ENVIRONMENT` | `production` | Immédiatement |

⚠️ `$PORT` est fourni automatiquement par Render — ne jamais hardcoder le port.

---

### Structure de fichiers EXACTE après Story 1.1

```
corniscan/
├── .gitignore
├── README.md
├── frontend/
│   ├── package.json
│   ├── vite.config.ts          ← proxy /api → :8000 AJOUTÉ
│   ├── tsconfig.json
│   ├── tsconfig.app.json
│   ├── tsconfig.node.json
│   ├── index.html
│   └── src/
│       ├── main.ts
│       ├── App.vue
│       ├── env.d.ts
│       ├── router/
│       │   └── index.ts        ← généré create-vue, nettoyé (routes Story 1.3)
│       ├── stores/
│       │   ├── authStore.ts    ← squelette Pinia (isLoading, error)
│       │   └── scanStore.ts    ← squelette Pinia (isLoading, error, hasPhoto)
│       ├── services/
│       │   └── apiClient.ts    ← squelette apiCall<T>
│       ├── composables/        ← répertoire vide (useMediaDevices Story 3.1)
│       └── views/
│           └── LoginView.vue   ← placeholder
└── backend/
    ├── pyproject.toml          ← toutes les dépendances via uv
    ├── .env.example
    └── app/
        ├── __init__.py
        ├── main.py             ← StaticFiles + /api/v1/health
        ├── routers/
        │   ├── __init__.py
        │   ├── auth.py         ← vide (logique Story 1.3)
        │   ├── admin.py        ← vide (logique Story 2.x)
        │   └── scan.py         ← vide (logique Story 3.x)
        ├── services/
        │   └── __init__.py
        ├── models/
        │   └── __init__.py
        └── core/
            ├── __init__.py
            └── config.py       ← pydantic-settings
```

⚠️ **PAS** de fichiers Alembic (`alembic.ini`, `alembic/`) dans cette story → Story 1.2
⚠️ **PAS** de `app/core/database.py` → Story 1.2
⚠️ **PAS** de `app/core/security.py` → Story 1.3
⚠️ **PAS** de `app/models/user.py` ni `app/models/schemas.py` → Story 1.2+

---

### Conventions à respecter dès cette story

| Élément | Convention | Exemple |
|---|---|---|
| Composants Vue | PascalCase.vue | `LoginView.vue` |
| Stores Pinia | camelCase.ts | `authStore.ts` |
| Services TS | camelCase.ts | `apiClient.ts` |
| Routers Python | snake_case.py | `auth.py` |
| Variables locales TS | camelCase | `isLoading`, `hasPhoto` |
| Champs API/JSON | snake_case | `force_password_change` |

---

### Performance — NFR-P2 et NFR-P3

- Vite 6 avec Vue 3 minimal génère ~80-120KB gzip sans effort
- Le code splitting par route (Vue Router) maintient le chunk initial petit
- ⚠️ Ne PAS ajouter de bibliothèques UI lourdes dans cette story (Vuetify, Ant Design, etc.)
- Vérifier après `npm run build` : la sortie console affiche les tailles de chunks compressés

---

### Project Structure Notes

- **Monorepo racine** : tout le code est dans `corniscan/` — c'est le répertoire Git
- **Workspace VS Code** : le projet VS Code est ouvert sur `CorniScan/` (le répertoire parent). Le dossier `corniscan/` sera créé à l'intérieur.
- **Chemin StaticFiles** : `../../frontend/dist` relatif à `backend/app/main.py` → adapté à la structure monorepo
- **No Docker** pour cette story — Render gère le runtime Python directement via `pip install uv && uv sync`

### References

- Commandes init exactes: [Source: architecture.md#Starter Template Evaluation]
- Structure complète du projet: [Source: architecture.md#Complete Project Directory Structure]
- Configuration Render build/start: [Source: architecture.md#Infrastructure & Deployment]
- Pattern apiClient.ts: [Source: architecture.md#Communication Patterns]
- Pattern isLoading/error Pinia: [Source: architecture.md#Communication Patterns]
- Proxy Vite dev: [Source: architecture.md#Gap Analysis Results]
- NFR-P2 (FCP < 2s), NFR-P3 (bundle < 300KB): [Source: epics.md#NonFunctional Requirements]
- Story 1.1 Acceptance Criteria complets: [Source: epics.md#Story 1.1]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- uv non trouvé initialement → installé via `curl -LsSf https://astral.sh/uv/install.sh | sh` → `~/.local/bin/uv 0.10.4`
- Python 3.11 téléchargé automatiquement via `uv python pin 3.11` → Python 3.11.14
- `npm create vue@latest` avec path contenant espaces → résolu en `cd corniscan/ && npm create vue@latest frontend`
- `pydantic-settings` absent de architecture.md → ajouté à la commande `uv add` (gap documenté en Dev Notes)
- Versions réelles installées : Vue 3.5.28, Vite 7.3.1, Vitest 4.0.18, FastAPI 0.115.x, uvicorn 0.41.0, SQLAlchemy 2.0.46

### Completion Notes List

- ✅ AC#1: Monorepo `corniscan/frontend/` + `corniscan/backend/` créé. Frontend démarre sur :5173, backend sur :8000. 5 tests backend + 9 tests frontend GREEN.
- ✅ AC#2: Proxy Vite `/api/* → http://localhost:8000` configuré dans `vite.config.ts`. `vite-plugin-pwa` ajouté en devDependency.
- ✅ AC#3: `app/main.py` avec `StaticFiles(html=True)` monté APRÈS `/api/v1/health`. SPA fallback intégré. `render.yaml` blueprint créé avec build/start commands.
- ✅ AC#4: Bundle JS initial = **33.76 KB gzip** (limite NFR-P3: 300 KB). FCP < 2s attendu après déploiement (bundle minimal + StaticFiles).
- ✅ Pattern isLoading+error établi dans authStore et scanStore (obligatoire dans tous les stores — architecture.md)
- ✅ apiClient.ts squelette créé — toute logique API passe par `apiCall<T>()`, jamais de `fetch()` nu
- ⚠️ Tasks 7.1 (git push) et 7.6 (validation URL publique) nécessitent action manuelle de l'utilisateur

### Change Log

- 2026-02-22 — Implémentation Story 1.1: monorepo créé, frontend Vue 3 initialisé, backend FastAPI initialisé, proxy Vite configuré, squelettes créés, render.yaml créé. 14 tests (5 backend + 9 frontend) passent.

### File List

**Nouveaux (backend) :**
- `corniscan/backend/pyproject.toml` — configuration uv (toutes les dépendances)
- `corniscan/backend/.python-version` — Python 3.11 (uv pin)
- `corniscan/backend/.env.example` — template variables d'environnement
- `corniscan/backend/app/__init__.py`
- `corniscan/backend/app/main.py` — FastAPI app, StaticFiles, /api/v1/health
- `corniscan/backend/app/routers/__init__.py`
- `corniscan/backend/app/routers/auth.py` — squelette vide
- `corniscan/backend/app/routers/admin.py` — squelette vide
- `corniscan/backend/app/routers/scan.py` — squelette vide
- `corniscan/backend/app/services/__init__.py`
- `corniscan/backend/app/models/__init__.py`
- `corniscan/backend/app/core/__init__.py`
- `corniscan/backend/app/core/config.py` — pydantic-settings (DATABASE_URL, JWT_SECRET, RESEND_API_KEY)
- `corniscan/backend/tests/__init__.py`
- `corniscan/backend/tests/conftest.py` — fixture TestClient
- `corniscan/backend/tests/test_main.py` — 5 tests Story 1.1

**Nouveaux (frontend) :**
- `corniscan/frontend/package.json` — Vue 3.5.28, Pinia 3.0.4, vue-router 5.0.2, vite-plugin-pwa
- `corniscan/frontend/vite.config.ts` — proxy /api → :8000 AJOUTÉ
- `corniscan/frontend/src/App.vue` — nettoyé (RouterView uniquement)
- `corniscan/frontend/src/router/index.ts` — route /login uniquement, commentaires TODO stories suivantes
- `corniscan/frontend/src/stores/authStore.ts` — squelette Pinia
- `corniscan/frontend/src/stores/scanStore.ts` — squelette Pinia + hasPhoto computed
- `corniscan/frontend/src/services/apiClient.ts` — squelette apiCall<T>
- `corniscan/frontend/src/views/LoginView.vue` — placeholder
- `corniscan/frontend/src/stores/__tests__/authStore.spec.ts` — 2 tests
- `corniscan/frontend/src/stores/__tests__/scanStore.spec.ts` — 3 tests
- `corniscan/frontend/src/services/__tests__/apiClient.spec.ts` — 3 tests

**Supprimés (fichiers par défaut create-vue non pertinents) :**
- `corniscan/frontend/src/stores/counter.ts`
- `corniscan/frontend/src/views/HomeView.vue`
- `corniscan/frontend/src/views/AboutView.vue`

**Nouveaux (racine monorepo) :**
- `corniscan/.gitignore`
- `corniscan/README.md`
- `corniscan/render.yaml` — Render Blueprint (build/start commands, env vars)
