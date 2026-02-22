/**
 * Tests Story 2.1 — AdminUsersView.vue
 */
import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import AdminUsersView from '../AdminUsersView.vue'

// Mock apiCall
vi.mock('@/services/apiClient', () => ({
  apiCall: vi.fn(),
}))

// Mock authStore — user: admin connecté (Story 2.3: le bouton Désactiver se cache pour le propre compte)
vi.mock('@/stores/authStore', () => ({
  useAuthStore: () => ({ token: 'fake-token', isAuthenticated: true, user: { username: 'admin' } }),
}))

// Mock router
vi.mock('@/router', () => ({ default: { push: vi.fn() } }))

const { apiCall } = await import('@/services/apiClient')
const mockApiCall = vi.mocked(apiCall)

const MOCK_USERS = [
  {
    username: 'admin',
    role: 'admin',
    is_active: true,
    created_at: '2026-02-22T10:00:00+00:00',
    force_password_change: false,
  },
  {
    username: 'alice',
    role: 'operator',
    is_active: true,
    created_at: '2026-02-22T11:00:00+00:00',
    force_password_change: true,
  },
]

describe('AdminUsersView', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('AC#1 — affiche un tableau avec tous les champs requis', async () => {
    mockApiCall.mockResolvedValueOnce(MOCK_USERS)
    const wrapper = mount(AdminUsersView)
    await flushPromises()

    const rows = wrapper.findAll('tbody tr')
    expect(rows).toHaveLength(2)

    const firstRow = rows[0]!.findAll('td')
    expect(firstRow[0]!.text()).toBe('admin')
    expect(firstRow[1]!.text()).toBe('admin')
    expect(firstRow[2]!.text()).toBe('Actif')
  })

  it('AC#2 — le compte admin apparaît avec rôle admin clairement identifié', async () => {
    mockApiCall.mockResolvedValueOnce(MOCK_USERS)
    const wrapper = mount(AdminUsersView)
    await flushPromises()

    const adminBadge = wrapper.find('.role-badge.admin')
    expect(adminBadge.exists()).toBe(true)
    expect(adminBadge.text()).toBe('admin')
  })

  it('AC#1 — les comptes inactifs affichent "Inactif"', async () => {
    const inactiveUsers = [{ ...MOCK_USERS[1], is_active: false }]
    mockApiCall.mockResolvedValueOnce(inactiveUsers)
    const wrapper = mount(AdminUsersView)
    await flushPromises()

    const statusBadge = wrapper.find('.status-badge.inactive')
    expect(statusBadge.exists()).toBe(true)
    expect(statusBadge.text()).toBe('Inactif')
  })

  it('cache le message de chargement une fois les données reçues', async () => {
    mockApiCall.mockResolvedValueOnce(MOCK_USERS)
    const wrapper = mount(AdminUsersView)
    await flushPromises()

    // Après résolution : plus de loading, table visible
    expect(wrapper.find('.loading-msg').exists()).toBe(false)
    expect(wrapper.find('table').exists()).toBe(true)
  })

  it('affiche une erreur si apiCall échoue', async () => {
    mockApiCall.mockRejectedValueOnce(new Error('Accès refusé'))
    const wrapper = mount(AdminUsersView)
    await flushPromises()

    expect(wrapper.find('.error-msg').text()).toBe('Accès refusé')
  })

  it('affiche un message si la liste est vide', async () => {
    mockApiCall.mockResolvedValueOnce([])
    const wrapper = mount(AdminUsersView)
    await flushPromises()

    expect(wrapper.find('.empty-msg').exists()).toBe(true)
  })
})

// ── Tests Story 2.2 — formulaire de création ──────────────────────────────

describe('AdminUsersView — formulaire de création', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('AC#4 — validation frontend : champs vides bloquent la soumission', async () => {
    // loadUsers au montage
    mockApiCall.mockResolvedValueOnce([])
    const wrapper = mount(AdminUsersView)
    await flushPromises()

    // Soumettre sans remplir les champs
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(wrapper.find('.field-error').exists()).toBe(true)
    // apiCall n'a été appelé qu'une fois (loadUsers), pas pour la création
    expect(mockApiCall).toHaveBeenCalledTimes(1)
  })

  it('AC#4 — erreur par champ : username vide', async () => {
    mockApiCall.mockResolvedValueOnce([])
    const wrapper = mount(AdminUsersView)
    await flushPromises()

    // Remplir seulement le password
    await wrapper.find('#new-password').setValue('Pass123!')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    const errors = wrapper.findAll('.field-error')
    expect(errors.some((e) => e.text().includes("utilisateur"))).toBe(true)
  })

  it('AC#1 — création réussie : liste rechargée + formulaire vidé', async () => {
    const newUser = {
      username: 'alice',
      role: 'operator',
      is_active: true,
      created_at: '2026-02-22T10:00:00+00:00',
      force_password_change: true,
    }
    // 1. loadUsers initial, 2. POST création, 3. loadUsers après création
    mockApiCall
      .mockResolvedValueOnce([]) // loadUsers initial
      .mockResolvedValueOnce(newUser) // POST /api/v1/admin/users
      .mockResolvedValueOnce([newUser]) // loadUsers après création

    const wrapper = mount(AdminUsersView)
    await flushPromises()

    await wrapper.find('#new-username').setValue('alice')
    await wrapper.find('#new-password').setValue('ProvPass123!')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    // Message de succès visible
    expect(wrapper.find('.success-msg').exists()).toBe(true)
    expect(wrapper.find('.success-msg').text()).toContain('alice')
    // Champs vidés
    expect((wrapper.find('#new-username').element as HTMLInputElement).value).toBe('')
    // apiCall : loadUsers x2 + POST x1 = 3 appels
    expect(mockApiCall).toHaveBeenCalledTimes(3)
  })

  it("AC#3 — username doublon : message d'erreur du backend affiché", async () => {
    mockApiCall
      .mockResolvedValueOnce([]) // loadUsers
      .mockRejectedValueOnce(new Error('Ce nom d\'utilisateur existe déjà.'))

    const wrapper = mount(AdminUsersView)
    await flushPromises()

    await wrapper.find('#new-username').setValue('alice')
    await wrapper.find('#new-password').setValue('Pass123!')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(wrapper.find('.error-msg').text()).toContain('existe déjà')
  })
})

// ── Tests Story 2.3 — bouton Désactiver ───────────────────────────────────

const MOCK_USERS_WITH_ADMIN: typeof MOCK_USERS = [
  {
    username: 'admin',
    role: 'admin',
    is_active: true,
    created_at: '2026-02-22T10:00:00+00:00',
    force_password_change: false,
  },
  {
    username: 'alice',
    role: 'operator',
    is_active: true,
    created_at: '2026-02-22T11:00:00+00:00',
    force_password_change: false,
  },
]

describe('AdminUsersView — désactivation (Story 2.3)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it("AC#1 — bouton Désactiver visible pour un compte actif qui n'est pas le sien", async () => {
    mockApiCall.mockResolvedValueOnce(MOCK_USERS_WITH_ADMIN)
    const wrapper = mount(AdminUsersView)
    await flushPromises()

    // La ligne de alice (opérateur actif) doit avoir le bouton
    const buttons = wrapper.findAll('.btn-deactivate')
    expect(buttons).toHaveLength(1)
    expect(buttons[0]!.text()).toBe('Désactiver')
  })

  it('AC#4 — bouton Désactiver absent pour le propre compte admin', async () => {
    mockApiCall.mockResolvedValueOnce(MOCK_USERS_WITH_ADMIN)
    const wrapper = mount(AdminUsersView)
    await flushPromises()

    // Trouver la ligne admin et vérifier qu'il n'y a pas de bouton désactiver
    const rows = wrapper.findAll('tbody tr')
    const adminRow = rows.find((r) => r.text().includes('admin'))
    expect(adminRow?.find('.btn-deactivate').exists()).toBe(false)
  })

  it('AC#1 — bouton Désactiver absent pour un compte déjà inactif', async () => {
    const usersWithInactive = [{ ...MOCK_USERS_WITH_ADMIN[1], is_active: false }]
    mockApiCall.mockResolvedValueOnce(usersWithInactive)
    const wrapper = mount(AdminUsersView)
    await flushPromises()

    expect(wrapper.find('.btn-deactivate').exists()).toBe(false)
  })

  it('AC#1 — clic Désactiver → PATCH + rechargement liste', async () => {
    const updatedUsers = [
      MOCK_USERS_WITH_ADMIN[0],
      { ...MOCK_USERS_WITH_ADMIN[1], is_active: false },
    ]
    mockApiCall
      .mockResolvedValueOnce(MOCK_USERS_WITH_ADMIN) // loadUsers initial
      .mockResolvedValueOnce(undefined)              // PATCH deactivate
      .mockResolvedValueOnce(updatedUsers)           // loadUsers après désactivation

    const wrapper = mount(AdminUsersView)
    await flushPromises()

    await wrapper.find('.btn-deactivate').trigger('click')
    await flushPromises()

    // PATCH appelé avec la bonne URL
    expect(mockApiCall).toHaveBeenCalledWith(
      '/api/v1/admin/users/alice/deactivate',
      expect.objectContaining({ method: 'PATCH' }),
    )
    // Liste rechargée : alice maintenant inactive
    const inactiveBadge = wrapper.find('.status-badge.inactive')
    expect(inactiveBadge.exists()).toBe(true)
  })
})
