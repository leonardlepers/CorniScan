/**
 * Tests Story 4.1 + Story 4.2 + Story 4.3 — AnalyseView.vue
 *
 * Story 4.1 :
 *   AC#5 : spinner visible pendant le chargement
 *   AC#2 : setResult() appelé avec la réponse API
 *   AC#5 : message d'erreur si API échoue + bouton Recommencer
 *   AC#5 : redirection /camera si scanStore.photo absent
 *
 * Story 4.2 :
 *   AC#1 : ContourOverlay rendu avec photoUrl + contourPoints
 *   AC#3 : dimensions affichées en mm avec 1 décimale
 *   AC#4 : aucun avertissement si calibration_warning = false
 *
 * Story 4.3 :
 *   AC#1 : ThicknessInput rendu dans le résultat
 *   AC#4 : handleRetake appelle clearResult + redirige /camera
 */
import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import AnalyseView from '../AnalyseView.vue'

// ── Mocks modules ──────────────────────────────────────────────────────────────

const mockRouterPush = vi.fn()

vi.mock('vue-router', () => ({
  useRoute: vi.fn(),
  useRouter: () => ({ push: mockRouterPush }),
}))

vi.mock('@/components/validation/ContourOverlay.vue', () => ({
  default: {
    name: 'ContourOverlay',
    props: ['photoUrl', 'contourPoints'],
    template: '<div class="mock-contour-overlay" :data-photo-url="photoUrl" />',
  },
}))

vi.mock('@/components/validation/ThicknessInput.vue', () => ({
  default: {
    name: 'ThicknessInput',
    props: ['calibrationWarning'],
    emits: ['update:thickness', 'retake', 'force-send'],
    template: '<div class="mock-thickness-input" />',
  },
}))

// State mutable du mock scanStore — mis à jour dans beforeEach
const mockSetResult = vi.fn()
const mockClearResult = vi.fn()
const mockSetThickness = vi.fn()
let mockPhoto: File | null = new File(['jpeg'], 'capture.jpg', { type: 'image/jpeg' })
let mockContour: number[][] = []
let mockDimensions: { width_mm: number; height_mm: number } | null = null
let mockCalibrationWarning = false

vi.mock('@/stores/scanStore', () => ({
  useScanStore: () => ({
    get photo() {
      return mockPhoto
    },
    get contour() {
      return mockContour
    },
    get dimensions() {
      return mockDimensions
    },
    get calibrationWarning() {
      return mockCalibrationWarning
    },
    setResult: mockSetResult,
    clearResult: mockClearResult,
    setThickness: mockSetThickness,
  }),
}))

const mockApiCall = vi.fn()

vi.mock('@/services/apiClient', () => ({
  apiCall: (...args: unknown[]) => mockApiCall(...args),
}))

// ── Résultat API simulé ────────────────────────────────────────────────────────

const mockResult = {
  contour_points: [
    [0.1, 0.2],
    [0.9, 0.2],
    [0.9, 0.8],
    [0.1, 0.8],
  ],
  dimensions: { width_mm: 30.5, height_mm: 20.0 },
  calibration_warning: false,
}

// ── Tests Story 4.1 ───────────────────────────────────────────────────────────

describe('AnalyseView — chargement (Story 4.1)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockPhoto = new File(['jpeg'], 'capture.jpg', { type: 'image/jpeg' })
    mockContour = []
    mockDimensions = null
    mockCalibrationWarning = false
    mockApiCall.mockResolvedValue(mockResult)
    vi.stubGlobal('URL', {
      createObjectURL: vi.fn(() => 'blob:fake-url'),
      revokeObjectURL: vi.fn(),
    })
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it("AC#5 — le spinner est visible au montage avant la résolution de l'API", () => {
    const wrapper = mount(AnalyseView)

    expect(wrapper.find('[role="status"]').exists()).toBe(true)
    expect(wrapper.find('[role="status"]').text()).toContain('Analyse en cours')
  })

  it("AC#5 — le spinner disparaît après la résolution de l'API", async () => {
    const wrapper = mount(AnalyseView)
    await flushPromises()

    expect(wrapper.find('[role="status"]').exists()).toBe(false)
  })

  it("AC#2 — apiCall est appelé avec la bonne URL et la photo en FormData", async () => {
    mount(AnalyseView)
    await flushPromises()

    expect(mockApiCall).toHaveBeenCalledOnce()
    const [endpoint, options] = mockApiCall.mock.calls[0] as [string, RequestInit]
    expect(endpoint).toBe('/api/v1/scan/process')
    expect(options.method).toBe('POST')
    expect(options.body).toBeInstanceOf(FormData)
  })

  it("AC#2 — setResult est appelé avec la réponse de l'API", async () => {
    mount(AnalyseView)
    await flushPromises()

    expect(mockSetResult).toHaveBeenCalledOnce()
    expect(mockSetResult).toHaveBeenCalledWith(mockResult)
  })
})

describe("AnalyseView — erreur API (Story 4.1)", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockPhoto = new File(['jpeg'], 'capture.jpg', { type: 'image/jpeg' })
    mockContour = []
    mockDimensions = null
    mockCalibrationWarning = false
    vi.stubGlobal('URL', {
      createObjectURL: vi.fn(() => 'blob:fake-url'),
      revokeObjectURL: vi.fn(),
    })
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it("AC#5 — affiche un message d'erreur si l'API échoue", async () => {
    mockApiCall.mockRejectedValue(new Error('Erreur réseau'))

    const wrapper = mount(AnalyseView)
    await flushPromises()

    expect(wrapper.find('.error-text').exists()).toBe(true)
    expect(wrapper.find('.error-text').text()).toContain('Erreur réseau')
  })

  it("AC#5 — setResult n'est pas appelé en cas d'erreur", async () => {
    mockApiCall.mockRejectedValue(new Error('Erreur réseau'))

    mount(AnalyseView)
    await flushPromises()

    expect(mockSetResult).not.toHaveBeenCalled()
  })

  it('AC#5 — le bouton Recommencer redirige vers /camera', async () => {
    mockApiCall.mockRejectedValue(new Error('Erreur réseau'))

    const wrapper = mount(AnalyseView)
    await flushPromises()

    await wrapper.find('.retry-btn').trigger('click')

    expect(mockRouterPush).toHaveBeenCalledWith({ name: 'camera' })
  })
})

describe('AnalyseView — photo absente (Story 4.1)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockPhoto = null
    mockContour = []
    mockDimensions = null
    mockCalibrationWarning = false
    mockApiCall.mockResolvedValue(mockResult)
    vi.stubGlobal('URL', {
      createObjectURL: vi.fn(() => 'blob:fake-url'),
      revokeObjectURL: vi.fn(),
    })
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('AC#5 — redirige vers /camera si scanStore.photo est null', async () => {
    mount(AnalyseView)
    await flushPromises()

    expect(mockRouterPush).toHaveBeenCalledWith({ name: 'camera' })
    expect(mockApiCall).not.toHaveBeenCalled()
  })
})

// ── Tests Story 4.2 ───────────────────────────────────────────────────────────

describe('AnalyseView — affichage résultat (Story 4.2)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockPhoto = new File(['jpeg'], 'capture.jpg', { type: 'image/jpeg' })
    // Pré-popule le store avec le résultat attendu (simulé par beforeEach)
    mockContour = mockResult.contour_points
    mockDimensions = mockResult.dimensions
    mockCalibrationWarning = false
    mockApiCall.mockResolvedValue(mockResult)
    vi.stubGlobal('URL', {
      createObjectURL: vi.fn(() => 'blob:photo-url'),
      revokeObjectURL: vi.fn(),
    })
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('AC#1 — ContourOverlay est rendu avec photoUrl et contourPoints', async () => {
    const wrapper = mount(AnalyseView)
    await flushPromises()

    const overlay = wrapper.findComponent({ name: 'ContourOverlay' })
    expect(overlay.exists()).toBe(true)
    expect(overlay.props('photoUrl')).toBe('blob:photo-url')
    expect(overlay.props('contourPoints')).toEqual(mockResult.contour_points)
  })

  it('AC#3 — les dimensions sont affichées avec 1 décimale en mm', async () => {
    const wrapper = mount(AnalyseView)
    await flushPromises()

    const dims = wrapper.find('.dimensions-display')
    expect(dims.exists()).toBe(true)
    expect(dims.text()).toContain('30.5 mm')
    expect(dims.text()).toContain('20.0 mm')
  })

  it("AC#4 — aucun avertissement visible si calibration_warning = false", async () => {
    const wrapper = mount(AnalyseView)
    await flushPromises()

    expect(wrapper.find('.calibration-warning').exists()).toBe(false)
  })

  it('AC#1 — URL.createObjectURL est appelé avec scanStore.photo', async () => {
    mount(AnalyseView)
    await flushPromises()

    expect(URL.createObjectURL).toHaveBeenCalledOnce()
    expect(URL.createObjectURL).toHaveBeenCalledWith(mockPhoto)
  })
})

// ── Tests Story 4.3 ───────────────────────────────────────────────────────────

describe('AnalyseView — épaisseur et calibration (Story 4.3)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockPhoto = new File(['jpeg'], 'capture.jpg', { type: 'image/jpeg' })
    mockContour = mockResult.contour_points
    mockDimensions = mockResult.dimensions
    mockCalibrationWarning = false
    mockApiCall.mockResolvedValue(mockResult)
    vi.stubGlobal('URL', {
      createObjectURL: vi.fn(() => 'blob:photo-url'),
      revokeObjectURL: vi.fn(),
    })
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('AC#1 — ThicknessInput est rendu dans la section résultat', async () => {
    const wrapper = mount(AnalyseView)
    await flushPromises()

    expect(wrapper.findComponent({ name: 'ThicknessInput' }).exists()).toBe(true)
  })

  it('AC#1 — ThicknessInput reçoit calibrationWarning = false', async () => {
    const wrapper = mount(AnalyseView)
    await flushPromises()

    const input = wrapper.findComponent({ name: 'ThicknessInput' })
    expect(input.props('calibrationWarning')).toBe(false)
  })

  it('AC#2 — ThicknessInput reçoit calibrationWarning = true quand le store le signale', async () => {
    mockCalibrationWarning = true
    const wrapper = mount(AnalyseView)
    await flushPromises()

    const input = wrapper.findComponent({ name: 'ThicknessInput' })
    expect(input.props('calibrationWarning')).toBe(true)
  })

  it("AC#4 — handleRetake appelle clearResult et redirige vers /camera", async () => {
    const wrapper = mount(AnalyseView)
    await flushPromises()

    const input = wrapper.findComponent({ name: 'ThicknessInput' })
    await input.vm.$emit('retake')

    expect(mockClearResult).toHaveBeenCalledOnce()
    expect(mockRouterPush).toHaveBeenCalledWith({ name: 'camera' })
  })
})
