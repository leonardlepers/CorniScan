/**
 * Tests Story 4.2 — ContourOverlay.vue
 *
 * AC#1 : la photo est affichée avec la bonne URL
 * AC#1 : le SVG polygon est rendu quand contourPoints.length >= 3
 * AC#1 : le polygon est absent quand contourPoints.length < 3
 * AC#2 : les points SVG sont formatés correctement (x,y x,y ...)
 */
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import ContourOverlay from '../ContourOverlay.vue'

const PHOTO_URL = 'blob:fake-photo-url'

const CONTOUR_4PTS = [
  [0.1, 0.2],
  [0.9, 0.2],
  [0.9, 0.8],
  [0.1, 0.8],
]

describe('ContourOverlay — photo (Story 4.2)', () => {
  it('AC#1 — affiche une image avec la photoUrl fournie', () => {
    const wrapper = mount(ContourOverlay, {
      props: { photoUrl: PHOTO_URL, contourPoints: CONTOUR_4PTS },
    })

    const img = wrapper.find('.photo-img')
    expect(img.exists()).toBe(true)
    expect(img.attributes('src')).toBe(PHOTO_URL)
  })

  it('AC#1 — le conteneur overlay est présent', () => {
    const wrapper = mount(ContourOverlay, {
      props: { photoUrl: PHOTO_URL, contourPoints: CONTOUR_4PTS },
    })

    expect(wrapper.find('.contour-overlay-container').exists()).toBe(true)
  })
})

describe('ContourOverlay — SVG polygon (Story 4.2)', () => {
  it('AC#1 — le polygon SVG est rendu quand contourPoints.length >= 3', () => {
    const wrapper = mount(ContourOverlay, {
      props: { photoUrl: PHOTO_URL, contourPoints: CONTOUR_4PTS },
    })

    expect(wrapper.find('polygon').exists()).toBe(true)
  })

  it('AC#1 — le polygon SVG est absent quand contourPoints est vide', () => {
    const wrapper = mount(ContourOverlay, {
      props: { photoUrl: PHOTO_URL, contourPoints: [] },
    })

    expect(wrapper.find('polygon').exists()).toBe(false)
  })

  it('AC#1 — le polygon SVG est absent quand contourPoints.length < 3', () => {
    const wrapper = mount(ContourOverlay, {
      props: {
        photoUrl: PHOTO_URL,
        contourPoints: [
          [0.1, 0.2],
          [0.9, 0.8],
        ],
      },
    })

    expect(wrapper.find('polygon').exists()).toBe(false)
  })

  it('AC#2 — les points SVG sont formatés en "x,y x,y ..."', () => {
    const wrapper = mount(ContourOverlay, {
      props: { photoUrl: PHOTO_URL, contourPoints: CONTOUR_4PTS },
    })

    const polygon = wrapper.find('polygon')
    const points = polygon.attributes('points')
    expect(points).toBe('0.1,0.2 0.9,0.2 0.9,0.8 0.1,0.8')
  })
})
