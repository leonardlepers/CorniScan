/**
 * Tests Story 2.4 + Story 3.1 — CameraView.vue
 * AC#1 Story 2.4 : message d'accès refusé si redirigé depuis une route admin.
 * AC#3 Story 3.1 : message d'erreur caméra affiché si getUserMedia échoue.
 */
import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { ref } from 'vue'
import CameraView from '../CameraView.vue'

vi.mock('@/stores/authStore', () => ({
  useAuthStore: () => ({
    user: { username: 'alice', role: 'operator', force_password_change: false },
    logout: vi.fn(),
  }),
}))

vi.mock('@/components/AppHeader.vue', () => ({
  default: { template: '<div class="mock-header" />' },
}))

vi.mock('vue-router', () => ({
  useRoute: vi.fn(),
  useRouter: () => ({ push: vi.fn() }),
}))

// Mock du composable useMediaDevices pour isoler CameraView des APIs browser
const mockStartCamera = vi.fn()
const mockStopCamera = vi.fn()
const mockVideoRef = ref<HTMLVideoElement | null>(null)
const mockIsLoading = ref(false)
const mockError = ref<string | null>(null)

vi.mock('@/composables/useMediaDevices', () => ({
  useMediaDevices: () => ({
    videoRef: mockVideoRef,
    isLoading: mockIsLoading,
    error: mockError,
    startCamera: mockStartCamera,
    stopCamera: mockStopCamera,
  }),
}))

const { useRoute } = await import('vue-router')
const mockUseRoute = vi.mocked(useRoute)

describe('CameraView — message accès refusé (Story 2.4)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockIsLoading.value = false
    mockError.value = null
  })

  it('AC#1 — affiche le message forbidden si ?forbidden=1 dans la query', () => {
    mockUseRoute.mockReturnValue({ query: { forbidden: '1' } } as ReturnType<typeof useRoute>)

    const wrapper = mount(CameraView)

    expect(wrapper.find('.forbidden-alert').exists()).toBe(true)
    expect(wrapper.find('.forbidden-alert').text()).toContain('Accès refusé')
  })

  it("AC#1 — n'affiche pas le message forbidden si la query est absente", () => {
    mockUseRoute.mockReturnValue({ query: {} } as ReturnType<typeof useRoute>)

    const wrapper = mount(CameraView)

    expect(wrapper.find('.forbidden-alert').exists()).toBe(false)
  })

  it('AC#1 — le message forbidden peut être fermé', async () => {
    mockUseRoute.mockReturnValue({ query: { forbidden: '1' } } as ReturnType<typeof useRoute>)

    const wrapper = mount(CameraView)
    await wrapper.find('.dismiss-btn').trigger('click')

    expect(wrapper.find('.forbidden-alert').exists()).toBe(false)
  })
})

describe('CameraView — flux caméra (Story 3.1)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockUseRoute.mockReturnValue({ query: {} } as ReturnType<typeof useRoute>)
    mockIsLoading.value = false
    mockError.value = null
  })

  it('AC#1 — startCamera est appelé au montage', async () => {
    mount(CameraView)
    await flushPromises()

    expect(mockStartCamera).toHaveBeenCalledOnce()
  })

  it("AC#1 — l'élément <video> est présent dans le DOM", () => {
    const wrapper = mount(CameraView)

    const video = wrapper.find('video')
    expect(video.exists()).toBe(true)
    expect(video.attributes('autoplay')).toBeDefined()
    expect(video.attributes('playsinline')).toBeDefined()
    // muted est une propriété DOM (pas un attribut HTML) en JSDOM
    expect((video.element as HTMLVideoElement).muted).toBe(true)
  })

  it("AC#3 — affiche le message d'erreur caméra si error est défini", () => {
    mockError.value =
      "Accès à la caméra refusé. Autorisez l'accès à la caméra dans les paramètres de votre navigateur."

    const wrapper = mount(CameraView)

    expect(wrapper.find('.camera-error').exists()).toBe(true)
    expect(wrapper.find('.camera-error').text()).toContain('paramètres de votre navigateur')
  })

  it('AC#3 — le bouton Réessayer rappelle startCamera', async () => {
    mockError.value =
      "Accès à la caméra refusé. Autorisez l'accès à la caméra dans les paramètres de votre navigateur."

    const wrapper = mount(CameraView)
    await wrapper.find('.retry-btn').trigger('click')

    // startCamera : 1x au montage + 1x au clic Réessayer
    expect(mockStartCamera).toHaveBeenCalledTimes(2)
  })

  it('affiche le spinner de chargement pendant isLoading', () => {
    mockIsLoading.value = true

    const wrapper = mount(CameraView)

    expect(wrapper.find('[role="status"]').exists()).toBe(true)
    expect(wrapper.find('[role="status"]').text()).toContain('Initialisation')
  })
})
