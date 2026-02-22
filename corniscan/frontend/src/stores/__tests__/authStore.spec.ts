/**
 * Tests Story 1.3 — authStore (token, user, isAuthenticated, login, logout)
 */
import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '../authStore'

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

describe('authStore — Story 1.3', () => {
  beforeEach(() => {
    localStorageMock.clear()
    setActivePinia(createPinia())
    vi.resetAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  // ── Pattern Story 1.1 (inchangé) ──────────────────────────────────────────

  it('initialise avec isLoading = false', () => {
    const store = useAuthStore()
    expect(store.isLoading).toBe(false)
  })

  it('initialise avec error = null', () => {
    const store = useAuthStore()
    expect(store.error).toBeNull()
  })

  // ── État initial ───────────────────────────────────────────────────────────

  it('initialise avec token = null si localStorage vide', () => {
    const store = useAuthStore()
    expect(store.token).toBeNull()
  })

  it('initialise isAuthenticated = false sans token', () => {
    const store = useAuthStore()
    expect(store.isAuthenticated).toBe(false)
  })

  it('restaure le token depuis localStorage', () => {
    // Créer un JWT valide avec payload minimal
    const payload = btoa(JSON.stringify({ sub: 'alice', role: 'operator', force_password_change: false }))
    const fakeToken = `header.${payload}.signature`
    localStorageMock.setItem('auth_token', fakeToken)

    setActivePinia(createPinia())
    const store = useAuthStore()

    expect(store.token).toBe(fakeToken)
    expect(store.isAuthenticated).toBe(true)
    expect(store.user?.username).toBe('alice')
  })

  // ── login() ────────────────────────────────────────────────────────────────

  it('login() stocke le token et l\'utilisateur en cas de succès', async () => {
    const mockUser = { username: 'alice', role: 'operator', force_password_change: false }
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ access_token: 'mock-token', token_type: 'bearer', user: mockUser }),
    } as Response)

    const store = useAuthStore()
    const user = await store.login('alice', 'password')

    expect(store.token).toBe('mock-token')
    expect(store.user).toEqual(mockUser)
    expect(store.isAuthenticated).toBe(true)
    expect(localStorageMock.getItem('auth_token')).toBe('mock-token')
    expect(user).toEqual(mockUser)
  })

  it('login() met isLoading à true pendant la requête', async () => {
    let resolveLogin!: (value: unknown) => void
    const loginPromise = new Promise((resolve) => { resolveLogin = resolve })

    global.fetch = vi.fn().mockReturnValue(loginPromise)

    const store = useAuthStore()
    const loginCall = store.login('alice', 'password')

    expect(store.isLoading).toBe(true)
    resolveLogin({ ok: true, json: () => Promise.resolve({ access_token: 'tok', token_type: 'bearer', user: {} }) })
    await loginCall.catch(() => {})
  })

  it('login() stocke l\'erreur en cas de réponse 401', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      json: () => Promise.resolve({ detail: 'Identifiant ou mot de passe incorrect.' }),
    } as Response)

    const store = useAuthStore()
    await expect(store.login('alice', 'wrong')).rejects.toThrow('Identifiant ou mot de passe incorrect.')
    expect(store.error).toBe('Identifiant ou mot de passe incorrect.')
    expect(store.token).toBeNull()
  })

  it('login() remet isLoading à false après erreur', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      json: () => Promise.resolve({ detail: 'Erreur' }),
    } as Response)

    const store = useAuthStore()
    await expect(store.login('alice', 'wrong')).rejects.toThrow()
    expect(store.isLoading).toBe(false)
  })

  // ── logout() ───────────────────────────────────────────────────────────────

  it('logout() supprime le token et remet user à null', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({
        access_token: 'tok',
        token_type: 'bearer',
        user: { username: 'alice', role: 'operator', force_password_change: false },
      }),
    } as Response)

    const store = useAuthStore()
    await store.login('alice', 'password')
    expect(store.isAuthenticated).toBe(true)

    store.logout()

    expect(store.token).toBeNull()
    expect(store.user).toBeNull()
    expect(store.isAuthenticated).toBe(false)
    expect(localStorageMock.getItem('auth_token')).toBeNull()
  })
})
