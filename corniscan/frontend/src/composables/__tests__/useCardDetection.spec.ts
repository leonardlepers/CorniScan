/**
 * Tests Story 3.2 — useCardDetection composable
 * AC#1: setInterval 500ms → POST /scan/detect-card
 * AC#4: erreurs réseau silencieuses
 */
import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { defineComponent, onMounted, ref } from 'vue'
import { useCardDetection } from '../useCardDetection'

vi.mock('@/services/apiClient', () => ({
  apiCall: vi.fn(),
}))

vi.mock('@/stores/authStore', () => ({
  useAuthStore: () => ({ token: 'fake-token' }),
}))

vi.mock('@/router', () => ({ default: { push: vi.fn() } }))

const { apiCall } = await import('@/services/apiClient')
const mockApiCall = vi.mocked(apiCall)

// Composant minimal pour tester le composable dans un contexte Vue
function makeWrapper(videoMock: HTMLVideoElement | null = null) {
  const TestComponent = defineComponent({
    setup() {
      const videoRef = ref<HTMLVideoElement | null>(videoMock)
      const composable = useCardDetection(videoRef)
      onMounted(composable.startDetection)
      return composable
    },
    template: '<div />',
  })
  return mount(TestComponent)
}

function makeMockVideo(): HTMLVideoElement {
  const video = document.createElement('video')
  Object.defineProperty(video, 'srcObject', { value: {}, writable: true })
  Object.defineProperty(video, 'videoWidth', { value: 640 })
  Object.defineProperty(video, 'videoHeight', { value: 480 })
  return video
}

describe('useCardDetection — Story 3.2', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('AC#1 — appelle apiCall après 500ms avec FormData', async () => {
    mockApiCall.mockResolvedValue({ card_detected: true })

    // Mock canvas.toBlob
    const mockBlob = new Blob(['fake'], { type: 'image/jpeg' })
    vi.spyOn(HTMLCanvasElement.prototype, 'getContext').mockReturnValue({
      drawImage: vi.fn(),
    } as unknown as CanvasRenderingContext2D)
    vi.spyOn(HTMLCanvasElement.prototype, 'toBlob').mockImplementation((cb) => cb(mockBlob))

    makeWrapper(makeMockVideo())

    // Avancer de 500ms pour déclencher l'intervalle
    vi.advanceTimersByTime(500)
    await flushPromises()

    expect(mockApiCall).toHaveBeenCalledWith(
      '/api/v1/scan/detect-card',
      expect.objectContaining({ method: 'POST', body: expect.any(FormData) }),
    )
  })

  it('AC#1 — cardDetected passe à true si backend détecte la carte', async () => {
    mockApiCall.mockResolvedValue({ card_detected: true })

    vi.spyOn(HTMLCanvasElement.prototype, 'getContext').mockReturnValue({
      drawImage: vi.fn(),
    } as unknown as CanvasRenderingContext2D)
    const mockBlob = new Blob(['fake'], { type: 'image/jpeg' })
    vi.spyOn(HTMLCanvasElement.prototype, 'toBlob').mockImplementation((cb) => cb(mockBlob))

    const wrapper = makeWrapper(makeMockVideo())

    vi.advanceTimersByTime(500)
    await flushPromises()

    expect(wrapper.vm.cardDetected).toBe(true)
  })

  it('AC#3 — cardDetected passe à false si backend ne détecte pas la carte', async () => {
    mockApiCall.mockResolvedValue({ card_detected: false })

    vi.spyOn(HTMLCanvasElement.prototype, 'getContext').mockReturnValue({
      drawImage: vi.fn(),
    } as unknown as CanvasRenderingContext2D)
    const mockBlob = new Blob(['fake'], { type: 'image/jpeg' })
    vi.spyOn(HTMLCanvasElement.prototype, 'toBlob').mockImplementation((cb) => cb(mockBlob))

    const wrapper = makeWrapper(makeMockVideo())

    vi.advanceTimersByTime(500)
    await flushPromises()

    expect(wrapper.vm.cardDetected).toBe(false)
  })

  it('AC#4 — erreur réseau silencieuse (pas de throw)', async () => {
    mockApiCall.mockRejectedValue(new Error('Network error'))

    vi.spyOn(HTMLCanvasElement.prototype, 'getContext').mockReturnValue({
      drawImage: vi.fn(),
    } as unknown as CanvasRenderingContext2D)
    const mockBlob = new Blob(['fake'], { type: 'image/jpeg' })
    vi.spyOn(HTMLCanvasElement.prototype, 'toBlob').mockImplementation((cb) => cb(mockBlob))

    const wrapper = makeWrapper(makeMockVideo())

    // Ne doit pas lever d'exception
    await expect(async () => {
      vi.advanceTimersByTime(500)
      await flushPromises()
    }).not.toThrow()

    // cardDetected reste false (valeur initiale)
    expect(wrapper.vm.cardDetected).toBe(false)
  })

  it("ne lance pas de détection si la vidéo n'est pas prête (srcObject null)", async () => {
    makeWrapper(null) // videoRef.value = null

    vi.advanceTimersByTime(500)
    await flushPromises()

    expect(mockApiCall).not.toHaveBeenCalled()
  })
})
