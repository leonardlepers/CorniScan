/**
 * apiClient — Wrapper fetch centralisé
 *
 * Story 1.1 : signature établie + gestion erreurs de base
 * Story 1.3 : injecte Authorization: Bearer <token>
 *             intercepte les 401 → authStore.logout() + redirect /login
 *
 * RÈGLE ARCHITECTURE : Ne jamais utiliser fetch() directement dans les stores ou composants.
 * Toujours passer par apiCall<T>().
 */

import router from '@/router'
import { useAuthStore } from '@/stores/authStore'

export async function apiCall<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const authStore = useAuthStore()

  // Ne pas forcer Content-Type pour FormData — le navigateur gère le boundary multipart
  const isFormData = options?.body instanceof FormData
  const headers: Record<string, string> = {
    ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
    ...(options?.headers as Record<string, string>),
  }

  if (authStore.token) {
    headers['Authorization'] = `Bearer ${authStore.token}`
  }

  const response = await fetch(endpoint, { ...options, headers })

  // 401 : token expiré ou invalide → logout + redirect /login (NFR-S3)
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
