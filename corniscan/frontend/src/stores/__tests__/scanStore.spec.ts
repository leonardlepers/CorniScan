/**
 * Tests Story 1.1 — scanStore squelette
 * L'implémentation complète (photo, contour, dimensions) est en Stories 3.x/4.x
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
