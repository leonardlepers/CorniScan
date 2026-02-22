# Story 1.3: Authentification — login, session JWT et logout

Status: review

## Story

As an opérateur,
I want me connecter avec mon nom d'utilisateur et mon mot de passe et me déconnecter,
So that j'accède à l'application de façon sécurisée et peux terminer ma session proprement.

## Acceptance Criteria

1. **Given** un opérateur non authentifié tente d'accéder à n'importe quelle route protégée **When** le router Vue évalue la navigation **Then** il est redirigé vers `/login` avant d'atteindre la page demandée (FR2)

2. **Given** un opérateur est sur l'écran de connexion **When** il saisit un username et un mot de passe valides et soumet le formulaire **Then** le backend vérifie les credentials via bcrypt, génère un JWT HS256 (durée 8h), le frontend stocke le token dans `localStorage`, et l'opérateur est redirigé vers la route principale (FR1)

3. **Given** un opérateur soumet des credentials invalides (username inconnu ou mot de passe erroné) **When** le backend retourne HTTP 401 **Then** un message d'erreur explicite s'affiche dans l'interface ("Identifiant ou mot de passe incorrect.") sans révéler lequel des deux est erroné

4. **Given** un opérateur est authentifié et effectue des appels API via `apiClient.ts` **When** le frontend envoie une requête HTTP **Then** le header `Authorization: Bearer <token>` est automatiquement injecté dans chaque requête

5. **Given** un opérateur est authentifié depuis plus de 8 heures **When** il tente une action nécessitant le backend **Then** le token JWT est expiré, le backend retourne HTTP 401, et le frontend redirige vers `/login` (NFR-S3)

6. **Given** un opérateur authentifié clique sur "Se déconnecter" **When** l'action de logout est déclenchée **Then** le token JWT est supprimé du `localStorage`, le store Pinia est réinitialisé, et l'opérateur est redirigé vers `/login` (FR4)

## Tasks / Subtasks

- [x] Task 1: Créer `app/core/security.py` (AC: #2, #4, #5)
  - [x] 1.1 `create_access_token(data: dict) -> str` — JWT HS256, exp=8h
  - [x] 1.2 `verify_token(token: str) -> dict` — décode et valide
  - [x] 1.3 `get_current_user(credentials: HTTPAuthorizationCredentials) -> dict` — dependency FastAPI
  - [x] 1.4 Refactoriser `seed.py` pour importer `hash_password`/`verify_password` depuis `security.py`

- [x] Task 2: Implémenter `app/routers/auth.py` (AC: #2, #3)
  - [x] 2.1 POST `/api/v1/auth/token` : OAuth2PasswordRequestForm → vérif bcrypt → JWT + user info
  - [x] 2.2 HTTP 401 avec message identique pour username inconnu ET mauvais mot de passe (pas de fuite)

- [x] Task 3: Inclure le router auth dans `app/main.py` (AC: #2)

- [x] Task 4: Tests backend `tests/test_auth.py` (AC: #2, #3, #5)
  - [x] 4.1 create_access_token + verify_token — unit tests
  - [x] 4.2 POST /token credentials valides → 200 + token
  - [x] 4.3 POST /token credentials invalides → 401 (même message)
  - [x] 4.4 Token expiré → verify_token lève JWTError

- [x] Task 5: Implémenter `src/stores/authStore.ts` (AC: #2, #6)
  - [x] 5.1 `token` (ref, initialisé depuis localStorage)
  - [x] 5.2 `user` (ref, décodé depuis JWT au chargement)
  - [x] 5.3 `isAuthenticated` (computed)
  - [x] 5.4 `login(username, password)` — fetch /api/v1/auth/token + stocke token + navigue
  - [x] 5.5 `logout()` — supprime localStorage + reset store

- [x] Task 6: Implémenter `src/services/apiClient.ts` (AC: #4, #5)
  - [x] 6.1 Injecter `Authorization: Bearer <token>` depuis authStore
  - [x] 6.2 Intercepter HTTP 401 → appeler authStore.logout() + rediriger vers /login

- [x] Task 7: Implémenter `src/router/index.ts` (AC: #1)
  - [x] 7.1 Routes : /login (public), /change-password (requireAuth), /camera (requireAuth), /validation (requireAuth + requirePhoto)
  - [x] 7.2 `beforeEach` guard — ordre : public → no token → admin check → force_password_change

- [x] Task 8: Implémenter `src/views/LoginView.vue` (AC: #2, #3)
  - [x] 8.1 Formulaire username + password + bouton Connexion
  - [x] 8.2 Afficher erreur (store.error) + état chargement
  - [x] 8.3 Redirection post-login : /change-password si force_password_change, sinon /camera

- [x] Task 9: Créer vues placeholder (AC: #1)
  - [x] 9.1 `src/views/ChangePasswordView.vue` — placeholder (logique Story 1.4)
  - [x] 9.2 `src/views/CameraView.vue` — placeholder (logique Story 3.x)

- [x] Task 10: Mettre à jour les tests frontend (AC: #1, #2, #4, #6)

## Dev Notes

### `app/core/security.py` — Code exact

```python
# backend/app/core/security.py
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
import bcrypt
from app.core.config import settings

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 8
_BCRYPT_ROUNDS = 12
_security = HTTPBearer()

def hash_password(plain_password: str) -> str:
    salt = bcrypt.gensalt(rounds=_BCRYPT_ROUNDS)
    return bcrypt.hashpw(plain_password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode["exp"] = expire
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=ALGORITHM)

def verify_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_security),
) -> dict:
    try:
        payload = verify_token(credentials.credentials)
        return {
            "username": payload["sub"],
            "role": payload["role"],
            "force_password_change": payload.get("force_password_change", False),
        }
    except (JWTError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré.",
            headers={"WWW-Authenticate": "Bearer"},
        )
```

### `app/routers/auth.py` — Code exact

```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import create_access_token, verify_password
from app.models.user import users

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_db),
):
    result = await session.execute(
        select(users).where(users.c.username == form_data.username)
    )
    user_row = result.fetchone()
    if not user_row or not verify_password(form_data.password, user_row.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiant ou mot de passe incorrect.",
        )
    token = create_access_token({
        "sub": user_row.username,
        "role": user_row.role,
        "force_password_change": user_row.force_password_change,
    })
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "username": user_row.username,
            "role": user_row.role,
            "force_password_change": user_row.force_password_change,
        },
    }
```

### `authStore.ts` — Code exact

```typescript
// src/stores/authStore.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

interface User {
  username: string
  role: string
  force_password_change: boolean
}

function decodeTokenPayload(token: string): User | null {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    return { username: payload.sub, role: payload.role, force_password_change: payload.force_password_change ?? false }
  } catch { return null }
}

export const useAuthStore = defineStore('auth', () => {
  const storedToken = localStorage.getItem('auth_token')
  const token = ref<string | null>(storedToken)
  const user = ref<User | null>(storedToken ? decodeTokenPayload(storedToken) : null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const isAuthenticated = computed(() => !!token.value)

  async function login(username: string, password: string): Promise<User> {
    isLoading.value = true
    error.value = null
    try {
      const body = new URLSearchParams({ username, password })
      const response = await fetch('/api/v1/auth/token', { method: 'POST', body })
      if (!response.ok) {
        const err = await response.json().catch(() => ({ detail: 'Erreur inattendue' }))
        throw new Error(err.detail ?? 'Erreur inattendue')
      }
      const data = await response.json()
      token.value = data.access_token
      user.value = data.user
      localStorage.setItem('auth_token', data.access_token)
      return data.user
    } catch (e: any) {
      error.value = e.message ?? 'Erreur inattendue'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  function logout(): void {
    token.value = null
    user.value = null
    localStorage.removeItem('auth_token')
  }

  return { token, user, isLoading, error, isAuthenticated, login, logout }
})
```

### `apiClient.ts` — Code exact (Story 1.3)

```typescript
import router from '@/router'
import { useAuthStore } from '@/stores/authStore'

export async function apiCall<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const authStore = useAuthStore()
  const headers: Record<string, string> = { 'Content-Type': 'application/json', ...(options?.headers as Record<string, string>) }
  if (authStore.token) headers['Authorization'] = `Bearer ${authStore.token}`

  const response = await fetch(endpoint, { ...options, headers })

  if (response.status === 401) {
    authStore.logout()
    router.push('/login')
    throw new Error('Session expirée. Veuillez vous reconnecter.')
  }
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Erreur inattendue' }))
    throw new Error(error.detail ?? 'Erreur inattendue')
  }
  return response.json()
}
```

### Guard router `beforeEach` — ordre exact

```typescript
// 1. Route publique → laisser passer
// 2. Pas de token → redirect /login
// 3. Route admin + rôle operator → redirect /camera
// 4. force_password_change + pas sur /change-password → redirect /change-password
```

### Clé localStorage

**`auth_token`** (pas `token` — évite collision avec d'autres apps sur le même domaine dev)

### References

- JWT payload: [Source: architecture.md#Authentication & Security]
- Guard order: [Source: architecture.md#Process Patterns]
- apiCall pattern: [Source: architecture.md#Communication Patterns]
- FR1 (login), FR2 (guard), FR4 (logout): [Source: epics.md]
- NFR-S3 (session expiry 8h): [Source: epics.md]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- `passlib` 1.7.4 incompatible avec `bcrypt` 5.x — `security.py` utilise `bcrypt` directement (même décision que Story 1.2)
- `seed.py` refactorisé pour importer depuis `security.py` — source unique de vérité pour hachage
- Import circulaire potentiel `apiClient → router → authStore` : pas de cycle car `authStore` n'importe ni router ni apiClient

### Completion Notes List

- ✅ AC#1 : Guard `router.beforeEach()` en place — redirect /login si non authentifié
- ✅ AC#2 : POST `/api/v1/auth/token` → JWT HS256 8h, token en localStorage (`auth_token`), user info retourné
- ✅ AC#3 : HTTP 401 avec message identique pour username inconnu ET mauvais mot de passe (NFR-S1)
- ✅ AC#4 : `apiClient.ts` injecte `Authorization: Bearer <token>` automatiquement
- ✅ AC#5 : Sur 401 reçu, `authStore.logout()` appelé + redirect `/login` (NFR-S3)
- ✅ AC#6 : `authStore.logout()` supprime `auth_token` de localStorage + reset store
- ✅ 31 tests backend GREEN (10 Story 1.3 + 16 Story 1.2 + 5 Story 1.1)
- ✅ 20 tests frontend GREEN (10 authStore + 6 apiClient + 3 scanStore + 1 HelloWorld)

### Change Log

- 2026-02-22 — Implémentation Story 1.3 : security.py, auth.py (POST /token), router guard beforeEach, authStore complet, apiClient JWT, LoginView, vues placeholder. 51 tests totaux GREEN.

### File List

**Nouveaux (backend) :**
- `corniscan/backend/app/core/security.py` — hash_password, verify_password, create_access_token, verify_token, get_current_user
- `corniscan/backend/tests/test_auth.py` — 10 tests Story 1.3

**Modifiés (backend) :**
- `corniscan/backend/app/core/seed.py` — importe depuis security.py (refactorisé)
- `corniscan/backend/app/routers/auth.py` — POST /api/v1/auth/token implémenté
- `corniscan/backend/app/main.py` — include_router(auth_router)

**Nouveaux (frontend) :**
- `corniscan/frontend/src/views/ChangePasswordView.vue` — placeholder (Story 1.4)
- `corniscan/frontend/src/views/CameraView.vue` — placeholder (Story 3.x)

**Modifiés (frontend) :**
- `corniscan/frontend/src/stores/authStore.ts` — implémentation complète
- `corniscan/frontend/src/services/apiClient.ts` — JWT injection + 401 intercept
- `corniscan/frontend/src/router/index.ts` — routes complètes + beforeEach guard
- `corniscan/frontend/src/views/LoginView.vue` — formulaire connexion complet
- `corniscan/frontend/src/stores/__tests__/authStore.spec.ts` — 10 tests Story 1.3
- `corniscan/frontend/src/services/__tests__/apiClient.spec.ts` — 6 tests Story 1.3
