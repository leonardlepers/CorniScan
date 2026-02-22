/**
 * Tests Story 2.4 + Story 3.1 + Story 3.3 — CameraView.vue
 * AC#1 Story 2.4 : message d'accès refusé si redirigé depuis une route admin.
 * AC#3 Story 3.1 : message d'erreur caméra affiché si getUserMedia échoue.
 * AC#2/3 Story 3.3 : bouton capture désactivé/actif selon état checklist.
 */
import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
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

vi.mock('@/components/camera/CaptureChecklist.vue', () => ({
  default: {
    name: 'CaptureChecklist',
    template: '<div class="mock-checklist" />',
    emits: ['update:allChecked'],
  },
}))

vi.mock('@/components/camera/CardDetectionOverlay.vue', () => ({
  default: { template: '<div class="mock-card-overlay" />' },
}))

const mockRouterPush = vi.fn()

vi.mock('vue-router', () => ({
  useRoute: vi.fn(),
  useRouter: () => ({ push: mockRouterPush }),
}))

const mockSetPhoto = vi.fn()

vi.mock('@/stores/scanStore', () => ({
  useScanStore: () => ({
    setPhoto: mockSetPhoto,
    hasPhoto: false,
    photo: null,
  }),
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

// Mock du composable useCardDetection pour isoler CameraView des APIs caméra + réseau
const mockCardDetected = ref(false)
const mockStartDetection = vi.fn()
const mockStopDetection = vi.fn()

vi.mock('@/composables/useCardDetection', () => ({
  useCardDetection: () => ({
    cardDetected: mockCardDetected,
    startDetection: mockStartDetection,
    stopDetection: mockStopDetection,
  }),
}))

const { useRoute } = await import('vue-router')
const mockUseRoute = vi.mocked(useRoute)

describe('CameraView — message accès refusé (Story 2.4)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockIsLoading.value = false
    mockError.value = null
    mockCardDetected.value = false
  })

  it('AC#1 — affiche le message forbidden si ?forbidden=1 dans la query', () => {
    mockUseRoute.mockReturnValue({ query: { forbidden: '1' } } as unknown as ReturnType<typeof useRoute>)

    const wrapper = mount(CameraView)

    expect(wrapper.find('.forbidden-alert').exists()).toBe(true)
    expect(wrapper.find('.forbidden-alert').text()).toContain('Accès refusé')
  })

  it("AC#1 — n'affiche pas le message forbidden si la query est absente", () => {
    mockUseRoute.mockReturnValue({ query: {} } as unknown as ReturnType<typeof useRoute>)

    const wrapper = mount(CameraView)

    expect(wrapper.find('.forbidden-alert').exists()).toBe(false)
  })

  it('AC#1 — le message forbidden peut être fermé', async () => {
    mockUseRoute.mockReturnValue({ query: { forbidden: '1' } } as unknown as ReturnType<typeof useRoute>)

    const wrapper = mount(CameraView)
    await wrapper.find('.dismiss-btn').trigger('click')

    expect(wrapper.find('.forbidden-alert').exists()).toBe(false)
  })
})

describe('CameraView — flux caméra (Story 3.1)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockUseRoute.mockReturnValue({ query: {} } as unknown as ReturnType<typeof useRoute>)
    mockIsLoading.value = false
    mockError.value = null
    mockCardDetected.value = false
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

describe('CameraView — checklist qualité (Story 3.3)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockUseRoute.mockReturnValue({ query: {} } as unknown as ReturnType<typeof useRoute>)
    mockIsLoading.value = false
    mockError.value = null
    mockCardDetected.value = false
  })

  it('AC#2 — le bouton capture est présent et désactivé par défaut', () => {
    const wrapper = mount(CameraView)

    const btn = wrapper.find('.capture-btn')
    expect(btn.exists()).toBe(true)
    expect(btn.attributes('disabled')).toBeDefined()
  })

  it('AC#3 — le bouton capture devient actif quand la checklist émet allChecked=true', async () => {
    const wrapper = mount(CameraView)

    const checklist = wrapper.findComponent({ name: 'CaptureChecklist' })
    await checklist.vm.$emit('update:allChecked', true)
    await flushPromises()

    expect(wrapper.find('.capture-btn').attributes('disabled')).toBeUndefined()
  })

  it('AC#4 — le bouton capture se désactive à nouveau si allChecked=false est émis', async () => {
    const wrapper = mount(CameraView)

    const checklist = wrapper.findComponent({ name: 'CaptureChecklist' })
    await checklist.vm.$emit('update:allChecked', true)
    await flushPromises()
    await checklist.vm.$emit('update:allChecked', false)
    await flushPromises()

    expect(wrapper.find('.capture-btn').attributes('disabled')).toBeDefined()
  })

  it('AC#1 — checklist et bouton capture absents pendant isLoading', () => {
    mockIsLoading.value = true

    const wrapper = mount(CameraView)

    expect(wrapper.find('.mock-checklist').exists()).toBe(false)
    expect(wrapper.find('.capture-btn').exists()).toBe(false)
  })
})

describe('CameraView — capture photo (Story 3.4)', () => {
  // Capture l'original AVANT toute spy — évite la récursion infinie
  const _origCreateElement = document.createElement.bind(document)

  // Mock canvas pour simuler canvas.toBlob() sans rendering réel
  const mockCtx = { drawImage: vi.fn() }
  const mockCanvas = {
    width: 0,
    height: 0,
    getContext: vi.fn(() => mockCtx),
    toBlob: vi.fn((cb: BlobCallback) => cb(new Blob(['fake-jpeg'], { type: 'image/jpeg' }))),
  }

  beforeEach(() => {
    vi.clearAllMocks()
    mockUseRoute.mockReturnValue({ query: {} } as unknown as ReturnType<typeof useRoute>)
    mockIsLoading.value = false
    mockError.value = null
    mockCardDetected.value = false

    // Video element simulé avec des dimensions
    mockVideoRef.value = { videoWidth: 640, videoHeight: 480 } as HTMLVideoElement

    // Intercept document.createElement pour renvoyer le mock canvas
    // _origCreateElement évite la récursion infinie (spy → mock → spy → ...)
    vi.spyOn(document, 'createElement').mockImplementation((tag: string) => {
      if (tag === 'canvas') return mockCanvas as unknown as HTMLCanvasElement
      return _origCreateElement(tag) as HTMLElement
    })

    vi.stubGlobal('URL', {
      createObjectURL: vi.fn(() => 'blob:fake-url'),
      revokeObjectURL: vi.fn(),
    })
  })

  afterEach(() => {
    vi.restoreAllMocks()
    vi.unstubAllGlobals()
    mockVideoRef.value = null
  })

  it('AC#1 — le clic Capturer appelle canvas.toBlob et arrête la caméra', async () => {
    const wrapper = mount(CameraView)

    const checklist = wrapper.findComponent({ name: 'CaptureChecklist' })
    await checklist.vm.$emit('update:allChecked', true)
    await flushPromises()

    await wrapper.find('.capture-btn').trigger('click')
    await flushPromises()

    expect(mockCanvas.toBlob).toHaveBeenCalled()
    expect(mockStopCamera).toHaveBeenCalled()
    expect(mockStopDetection).toHaveBeenCalled()
  })

  it("AC#1 — l'aperçu s'affiche après la capture", async () => {
    const wrapper = mount(CameraView)

    const checklist = wrapper.findComponent({ name: 'CaptureChecklist' })
    await checklist.vm.$emit('update:allChecked', true)
    await flushPromises()

    await wrapper.find('.capture-btn').trigger('click')
    await flushPromises()

    expect(wrapper.find('.preview-image').exists()).toBe(true)
    expect(wrapper.find('.preview-image').attributes('src')).toBe('blob:fake-url')
    // La section caméra est masquée
    expect(wrapper.find('.camera-container').exists()).toBe(false)
  })

  it('AC#2 — Confirmer stocke la photo dans scanStore et redirige vers /analyse', async () => {
    const wrapper = mount(CameraView)

    const checklist = wrapper.findComponent({ name: 'CaptureChecklist' })
    await checklist.vm.$emit('update:allChecked', true)
    await flushPromises()
    await wrapper.find('.capture-btn').trigger('click')
    await flushPromises()

    await wrapper.find('.confirm-btn').trigger('click')

    expect(mockSetPhoto).toHaveBeenCalledOnce()
    expect(mockSetPhoto.mock.calls[0]?.[0]).toBeInstanceOf(File)
    expect(mockRouterPush).toHaveBeenCalledWith({ name: 'analyse' })
  })

  it("AC#1 — Recommencer masque l'aperçu et relance la caméra", async () => {
    const wrapper = mount(CameraView)

    const checklist = wrapper.findComponent({ name: 'CaptureChecklist' })
    await checklist.vm.$emit('update:allChecked', true)
    await flushPromises()
    await wrapper.find('.capture-btn').trigger('click')
    await flushPromises()

    await wrapper.find('.retake-btn').trigger('click')
    await flushPromises()

    expect(wrapper.find('.preview-image').exists()).toBe(false)
    expect(wrapper.find('.camera-container').exists()).toBe(true)
    // startCamera : 1x au montage + 1x au retake
    expect(mockStartCamera).toHaveBeenCalledTimes(2)
  })
})
