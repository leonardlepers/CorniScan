/**
 * Tests Story 5.3 — ConfirmationView.vue
 *
 * AC#1 : message succès + destinataire info@cornille-sa.com
 * AC#2 : récapitulatif dimensions + épaisseur depuis scanStore
 * AC#3 : bouton "Nouveau scan" → clearPhoto + clearResult + /camera
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { flushPromises } from '@vue/test-utils'
import ConfirmationView from '@/views/ConfirmationView.vue'
import { useScanStore } from '@/stores/scanStore'

// ── Mock vue-router ──────────────────────────────────────────────────────────

const mockPush = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({ push: mockPush }),
}))

// ── Setup ────────────────────────────────────────────────────────────────────

function mountView() {
  return mount(ConfirmationView, { global: { plugins: [] } })
}

function withDimensions(store: ReturnType<typeof useScanStore>) {
  store.setResult({
    contour_points: [[0, 0], [1, 0], [1, 1], [0, 1]],
    dimensions: { width_mm: 30.5, height_mm: 20.0 },
    calibration_warning: false,
    holes: [],
  })
}

describe('ConfirmationView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    mockPush.mockReset()
  })

  // AC#1 — Message succès + destinataire
  it('affiche le message de succès', () => {
    const wrapper = mountView()
    expect(wrapper.find('.success-title').text()).toContain('Scan envoyé avec succès')
  })

  it('affiche le destinataire info@cornille-sa.com', () => {
    const wrapper = mountView()
    expect(wrapper.find('.success-recipient').text()).toContain('info@cornille-sa.com')
  })

  // AC#2 — Récapitulatif dimensions
  it('affiche la largeur en mm depuis le store', () => {
    const store = useScanStore()
    withDimensions(store)
    const wrapper = mountView()
    expect(wrapper.text()).toContain('30.5 mm')
  })

  it('affiche la hauteur en mm depuis le store', () => {
    const store = useScanStore()
    withDimensions(store)
    const wrapper = mountView()
    expect(wrapper.text()).toContain('20.0 mm')
  })

  it('affiche l\'épaisseur en mm si définie', () => {
    const store = useScanStore()
    withDimensions(store)
    store.setThickness(2.5)
    const wrapper = mountView()
    expect(wrapper.text()).toContain('2.5 mm')
  })

  it('affiche N/A si épaisseur est null', () => {
    const store = useScanStore()
    withDimensions(store)
    store.setThickness(null)
    const wrapper = mountView()
    expect(wrapper.text()).toContain('N/A')
  })

  it('n\'affiche pas la carte récap si dimensions absentes', () => {
    const wrapper = mountView()
    expect(wrapper.find('.summary-card').exists()).toBe(false)
  })

  // AC#3 — Bouton nouveau scan
  it('affiche le bouton "Nouveau scan"', () => {
    const wrapper = mountView()
    expect(wrapper.find('.new-scan-btn').text()).toBe('Nouveau scan')
  })

  it('appelle clearResult et clearPhoto au clic sur "Nouveau scan"', async () => {
    const store = useScanStore()
    withDimensions(store)
    store.setPhoto(new File([new Uint8Array(10)], 'photo.jpg', { type: 'image/jpeg' }))
    const wrapper = mountView()

    await wrapper.find('.new-scan-btn').trigger('click')
    await flushPromises()

    expect(store.dimensions).toBeNull()
    expect(store.photo).toBeNull()
  })

  it('navigue vers /camera au clic sur "Nouveau scan"', async () => {
    const wrapper = mountView()
    await wrapper.find('.new-scan-btn').trigger('click')
    await flushPromises()
    expect(mockPush).toHaveBeenCalledWith({ name: 'camera' })
  })
})
