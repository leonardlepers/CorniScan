/**
 * Tests Story 3.1 — useMediaDevices composable
 * AC#1: startCamera → getUserMedia avec facingMode: 'environment'
 * AC#3: gestion erreurs (NotAllowedError, API non supportée)
 */
import { mount, flushPromises } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { defineComponent, onMounted } from 'vue'
import { useMediaDevices } from '../useMediaDevices'

// Composant minimal pour tester le composable dans un contexte Vue
function makeWrapper() {
  const TestComponent = defineComponent({
    setup() {
      const composable = useMediaDevices()
      onMounted(composable.startCamera)
      return composable
    },
    template: '<video ref="videoRef" />',
  })
  return mount(TestComponent)
}

describe('useMediaDevices — Story 3.1', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
    // Reset screen.orientation mock
    Object.defineProperty(screen, 'orientation', {
      writable: true,
      value: { lock: vi.fn().mockResolvedValue(undefined) },
    })
  })

  it('AC#1 — startCamera appelle getUserMedia avec facingMode: environment', async () => {
    const mockStream = { getTracks: () => [] } as unknown as MediaStream
    const mockGetUserMedia = vi.fn().mockResolvedValue(mockStream)

    Object.defineProperty(navigator, 'mediaDevices', {
      writable: true,
      value: { getUserMedia: mockGetUserMedia },
    })

    const wrapper = makeWrapper()
    await flushPromises()

    expect(mockGetUserMedia).toHaveBeenCalledWith({
      video: { facingMode: 'environment' },
      audio: false,
    })
    expect(wrapper.vm.error).toBeNull()
    expect(wrapper.vm.isLoading).toBe(false)
  })

  it('AC#3 — NotAllowedError → message de permission', async () => {
    const error = new DOMException('Permission denied', 'NotAllowedError')
    Object.defineProperty(navigator, 'mediaDevices', {
      writable: true,
      value: { getUserMedia: vi.fn().mockRejectedValue(error) },
    })

    const wrapper = makeWrapper()
    await flushPromises()

    expect(wrapper.vm.error).toContain('paramètres de votre navigateur')
    expect(wrapper.vm.isLoading).toBe(false)
  })

  it('AC#3 — NotFoundError → message caméra introuvable', async () => {
    const error = new DOMException('Device not found', 'NotFoundError')
    Object.defineProperty(navigator, 'mediaDevices', {
      writable: true,
      value: { getUserMedia: vi.fn().mockRejectedValue(error) },
    })

    const wrapper = makeWrapper()
    await flushPromises()

    expect(wrapper.vm.error).toContain('Aucune caméra arrière')
  })

  it('AC#3 — navigator.mediaDevices absent → message navigateur non supporté', async () => {
    Object.defineProperty(navigator, 'mediaDevices', {
      writable: true,
      value: undefined,
    })

    const wrapper = makeWrapper()
    await flushPromises()

    expect(wrapper.vm.error).toContain('ne supporte pas')
  })

  it('isLoading passe à true pendant startCamera puis revient à false', async () => {
    let resolveStream!: (v: MediaStream) => void
    const streamPromise = new Promise<MediaStream>((res) => {
      resolveStream = res
    })
    Object.defineProperty(navigator, 'mediaDevices', {
      writable: true,
      value: { getUserMedia: vi.fn().mockReturnValue(streamPromise) },
    })

    const wrapper = makeWrapper()
    // Immédiatement après onMounted : isLoading devrait être true
    expect(wrapper.vm.isLoading).toBe(true)

    resolveStream({ getTracks: () => [] } as unknown as MediaStream)
    await flushPromises()
    expect(wrapper.vm.isLoading).toBe(false)
  })
})
