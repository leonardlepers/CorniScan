/**
 * Tests Story 1.1 + Story 3.4 + Story 4.1 + Story 4.3 — scanStore
 */
import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useScanStore } from '../scanStore'

describe('scanStore — Story 1.1 squelette', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('initialise avec isLoading = false', () => {
    const store = useScanStore()
    expect(store.isLoading).toBe(false)
  })

  it('initialise avec error = null', () => {
    const store = useScanStore()
    expect(store.error).toBeNull()
  })

  it('hasPhoto retourne false par défaut', () => {
    const store = useScanStore()
    expect(store.hasPhoto).toBe(false)
  })
})

describe('scanStore — photo (Story 3.4)', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('setPhoto stocke un File et hasPhoto devient true', () => {
    const store = useScanStore()
    const file = new File(['jpeg'], 'capture.jpg', { type: 'image/jpeg' })

    store.setPhoto(file)

    expect(store.photo).toBe(file)
    expect(store.hasPhoto).toBe(true)
  })

  it('clearPhoto remet photo à null et hasPhoto devient false', () => {
    const store = useScanStore()
    const file = new File(['jpeg'], 'capture.jpg', { type: 'image/jpeg' })
    store.setPhoto(file)

    store.clearPhoto()

    expect(store.photo).toBeNull()
    expect(store.hasPhoto).toBe(false)
  })
})

describe('scanStore — résultat analyse (Story 4.1)', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  const mockResult = {
    contour_points: [
      [0.1, 0.2],
      [0.9, 0.2],
      [0.9, 0.8],
      [0.1, 0.8],
    ],
    dimensions: { width_mm: 85.6, height_mm: 53.98 },
    calibration_warning: false,
    holes: [],
  }

  it('initialise avec contour vide, dimensions null, calibrationWarning false', () => {
    const store = useScanStore()
    expect(store.contour).toEqual([])
    expect(store.dimensions).toBeNull()
    expect(store.calibrationWarning).toBe(false)
  })

  it('setResult stocke contour + dimensions + calibrationWarning', () => {
    const store = useScanStore()

    store.setResult(mockResult)

    expect(store.contour).toEqual(mockResult.contour_points)
    expect(store.dimensions).toEqual(mockResult.dimensions)
    expect(store.calibrationWarning).toBe(false)
  })

  it('setResult stocke calibrationWarning = true', () => {
    const store = useScanStore()

    store.setResult({ ...mockResult, calibration_warning: true })

    expect(store.calibrationWarning).toBe(true)
  })

  it('clearResult remet contour, dimensions et calibrationWarning à leur valeur initiale', () => {
    const store = useScanStore()
    store.setResult(mockResult)

    store.clearResult()

    expect(store.contour).toEqual([])
    expect(store.dimensions).toBeNull()
    expect(store.calibrationWarning).toBe(false)
  })
})

describe('scanStore — épaisseur (Story 4.3)', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('initialise avec thickness = null', () => {
    const store = useScanStore()
    expect(store.thickness).toBeNull()
  })

  it('setThickness stocke la valeur en mm', () => {
    const store = useScanStore()

    store.setThickness(2.5)

    expect(store.thickness).toBe(2.5)
  })

  it('setThickness accepte null pour effacer la valeur', () => {
    const store = useScanStore()
    store.setThickness(2.5)

    store.setThickness(null)

    expect(store.thickness).toBeNull()
  })

  it('clearResult remet thickness à null', () => {
    const store = useScanStore()
    store.setThickness(3.0)

    store.clearResult()

    expect(store.thickness).toBeNull()
  })
})
