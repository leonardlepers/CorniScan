/**
 * Tests Story 1.3 — apiClient (JWT injection + 401 intercept)
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'

// Mock router (évite les erreurs d'import vue-router dans tests unitaires)
vi.mock('@/router', () => ({
  default: { push: vi.fn() },
}))

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {}
  return {
    getItem: (key: string) => store[key] ?? null,
    setItem: (key: string, value: string) => { store[key] = value },
    removeItem: (key: string) => { delete store[key] },
    clear: () => { store = {} },
  }
})()
Object.defineProperty(globalThis, 'localStorage', { value: localStorageMock, writable: true })

describe('apiClient — Story 1.3', () => {
  beforeEach(() => {
    localStorageMock.clear()
    setActivePinia(createPinia())
    vi.resetAllMocks()
  })

  // ── Comportement de base (Story 1.1) ──────────────────────────────────────

  it('apiCall retourne les données JSON en cas de succès', async () => {
    const mockData = { status: 'ok' }
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: () => Promise.resolve(mockData),
    } as Response)

    const { apiCall } = await import('../apiClient')
    const result = await apiCall<{ status: string }>('/api/v1/health')

    expect(result).toEqual(mockData)
  })

  it('apiCall lève une Error avec le message detail en cas d\'échec HTTP', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
      json: () => Promise.resolve({ detail: 'Erreur de test' }),
    } as Response)

    const { apiCall } = await import('../apiClient')

    await expect(apiCall('/api/v1/protected')).rejects.toThrow('Erreur de test')
  })

  it('apiCall lève une erreur générique si la réponse n\'est pas du JSON', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
      json: () => Promise.reject(new Error('not json')),
    } as Response)

    const { apiCall } = await import('../apiClient')

    await expect(apiCall('/api/v1/broken')).rejects.toThrow('Erreur inattendue')
  })

  // ── Injection du header Authorization ─────────────────────────────────────

  it('apiCall injecte Authorization: Bearer <token> si le store a un token', async () => {
    // Simuler un store authentifié
    const { useAuthStore } = await import('@/stores/authStore')
    const store = useAuthStore()
    store.token = 'my-jwt-token'

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: () => Promise.resolve({ data: 'ok' }),
    } as Response)

    const { apiCall } = await import('../apiClient')
    await apiCall('/api/v1/admin/users')

    const callArgs = (fetch as ReturnType<typeof vi.fn>).mock.calls[0]
    const headers = callArgs[1]?.headers as Record<string, string>
    expect(headers['Authorization']).toBe('Bearer my-jwt-token')
  })

  it('apiCall n\'injecte pas Authorization si le store n\'a pas de token', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: () => Promise.resolve({ data: 'ok' }),
    } as Response)

    const { apiCall } = await import('../apiClient')
    await apiCall('/api/v1/health')

    const callArgs = (fetch as ReturnType<typeof vi.fn>).mock.calls[0]
    const headers = callArgs[1]?.headers as Record<string, string>
    expect(headers['Authorization']).toBeUndefined()
  })

  // ── Intercept 401 ─────────────────────────────────────────────────────────

  it('apiCall appelle logout() et redirige vers /login sur 401', async () => {
    const { useAuthStore } = await import('@/stores/authStore')
    const store = useAuthStore()
    store.token = 'expired-token'
    const logoutSpy = vi.spyOn(store, 'logout')

    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 401,
      json: () => Promise.resolve({ detail: 'Token invalide' }),
    } as Response)

    const { apiCall } = await import('../apiClient')
    const routerModule = await import('@/router')

    await expect(apiCall('/api/v1/scan/process')).rejects.toThrow('Session expirée')
    expect(logoutSpy).toHaveBeenCalledOnce()
    expect(routerModule.default.push).toHaveBeenCalledWith('/login')
  })
})
