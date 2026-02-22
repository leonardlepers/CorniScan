/**
 * authStore — Store Pinia d'authentification
 *
 * Story 1.3 : implémentation complète (token, user, isAuthenticated, login, logout)
 *
 * CONVENTION ARCHITECTURE : toujours isLoading + error dans chaque store Pinia
 */
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

export interface User {
  username: string
  role: string
  force_password_change: boolean
}

/** Décode le payload JWT sans vérifier la signature (côté client). */
function decodeTokenPayload(token: string): User | null {
  try {
    // Format JWT : header.payload.signature — payload est en base64url
    const b64 = token.split('.')[1]?.replace(/-/g, '+').replace(/_/g, '/')
    if (!b64) return null
    const payload = JSON.parse(atob(b64))
    return {
      username: payload.sub,
      role: payload.role,
      force_password_change: payload.force_password_change ?? false,
    }
  } catch {
    return null
  }
}

const STORAGE_KEY = 'auth_token'

export const useAuthStore = defineStore('auth', () => {
  const storedToken = localStorage.getItem(STORAGE_KEY)

  const token = ref<string | null>(storedToken)
  const user = ref<User | null>(storedToken ? decodeTokenPayload(storedToken) : null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => !!token.value)

  /**
   * Login — appelle POST /api/v1/auth/token et stocke le JWT.
   * Retourne l'objet user pour que le composant puisse rediriger selon force_password_change.
   */
  async function login(username: string, password: string): Promise<User> {
    isLoading.value = true
    error.value = null
    try {
      const body = new URLSearchParams({ username, password })
      const response = await fetch('/api/v1/auth/token', {
        method: 'POST',
        body,
      })
      if (!response.ok) {
        const err = await response.json().catch(() => ({ detail: 'Erreur inattendue' }))
        throw new Error(err.detail ?? 'Erreur inattendue')
      }
      const data = await response.json()
      token.value = data.access_token
      user.value = data.user
      localStorage.setItem(STORAGE_KEY, data.access_token)
      return data.user as User
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Erreur inattendue'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  /** Logout — supprime le token du localStorage et réinitialise le store. */
  function logout(): void {
    token.value = null
    user.value = null
    error.value = null
    localStorage.removeItem(STORAGE_KEY)
  }

  /**
   * updateAuth — met à jour le token et l'utilisateur après un changement de mot de passe (Story 1.4).
   * Le nouveau JWT a force_password_change=false.
   */
  function updateAuth(newToken: string, newUser: User): void {
    token.value = newToken
    user.value = newUser
    localStorage.setItem(STORAGE_KEY, newToken)
  }

  return { token, user, isLoading, error, isAuthenticated, login, logout, updateAuth }
})
