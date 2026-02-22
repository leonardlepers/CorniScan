# CorniScan

PWA industrielle : conversion de photos de joints en fichiers DXF via email.

## Prérequis

- Node.js 20+
- uv (Python 3.11+) — [astral.sh/uv](https://astral.sh/uv)
- git

## Démarrage local

### Backend

```bash
cd backend
uv run uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Le frontend est disponible sur [http://localhost:5173](http://localhost:5173).
Les appels `/api/*` sont proxifiés vers le backend (port 8000).

## Variables d'environnement

Copier `backend/.env.example` en `backend/.env` et remplir les valeurs :

```
DATABASE_URL=postgresql+asyncpg://...
JWT_SECRET=<openssl rand -hex 32>
RESEND_API_KEY=re_...
```

## Structure

```
corniscan/
├── frontend/   # Vue 3 + TypeScript + Pinia + Vue Router
└── backend/    # FastAPI + Python 3.11 + uv
```

## Déploiement (Render)

- Build: `cd frontend && npm install && npm run build && cd ../backend && pip install uv && uv sync`
- Start: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
