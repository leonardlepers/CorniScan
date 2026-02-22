/**
 * Tests Story 2.4 — AppHeader.vue
 * AC#4 : aucun lien admin visible pour un opérateur.
 */
import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import AppHeader from '../AppHeader.vue'

vi.mock('@/stores/authStore', () => ({
  useAuthStore: vi.fn(),
}))

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: vi.fn() }),
  RouterLink: { template: '<a><slot /></a>' },
}))

const { useAuthStore } = await import('@/stores/authStore')
const mockUseAuthStore = vi.mocked(useAuthStore)

describe('AppHeader — séparation des rôles (Story 2.4)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('AC#4 — le lien admin est visible pour un administrateur', async () => {
    mockUseAuthStore.mockReturnValue({
      user: { username: 'admin', role: 'admin', force_password_change: false },
      logout: vi.fn(),
    } as ReturnType<typeof useAuthStore>)

    const wrapper = mount(AppHeader)
    await flushPromises()

    expect(wrapper.find('.nav-link').exists()).toBe(true)
    expect(wrapper.find('.nav-link').text()).toContain('Gestion des comptes')
  })

  it('AC#4 — le lien admin est masqué pour un opérateur', async () => {
    mockUseAuthStore.mockReturnValue({
      user: { username: 'alice', role: 'operator', force_password_change: false },
      logout: vi.fn(),
    } as ReturnType<typeof useAuthStore>)

    const wrapper = mount(AppHeader)
    await flushPromises()

    expect(wrapper.find('.nav-link').exists()).toBe(false)
  })

  it('le bouton Déconnexion est toujours visible', async () => {
    mockUseAuthStore.mockReturnValue({
      user: { username: 'alice', role: 'operator', force_password_change: false },
      logout: vi.fn(),
    } as ReturnType<typeof useAuthStore>)

    const wrapper = mount(AppHeader)
    expect(wrapper.find('.btn-logout').exists()).toBe(true)
  })

  it('clic Déconnexion appelle authStore.logout()', async () => {
    const mockLogout = vi.fn()
    mockUseAuthStore.mockReturnValue({
      user: { username: 'alice', role: 'operator', force_password_change: false },
      logout: mockLogout,
    } as ReturnType<typeof useAuthStore>)

    const wrapper = mount(AppHeader)
    await wrapper.find('.btn-logout').trigger('click')

    expect(mockLogout).toHaveBeenCalledOnce()
  })
})
