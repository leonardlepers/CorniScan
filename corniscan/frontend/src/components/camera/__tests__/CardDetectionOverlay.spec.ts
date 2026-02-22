/**
 * Tests Story 3.2 — CardDetectionOverlay.vue
 * AC#2: indicateur vert "Carte détectée ✓"
 * AC#3: indicateur orange "Carte non détectée"
 */
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import CardDetectionOverlay from '../CardDetectionOverlay.vue'

describe('CardDetectionOverlay — Story 3.2', () => {
  it('AC#2 — affiche "Carte détectée ✓" avec classe .detected quand cardDetected=true', () => {
    const wrapper = mount(CardDetectionOverlay, { props: { cardDetected: true } })

    expect(wrapper.find('.detected').exists()).toBe(true)
    expect(wrapper.text()).toContain('Carte détectée')
    expect(wrapper.find('.not-detected').exists()).toBe(false)
  })

  it('AC#3 — affiche "Carte non détectée" avec classe .not-detected quand cardDetected=false', () => {
    const wrapper = mount(CardDetectionOverlay, { props: { cardDetected: false } })

    expect(wrapper.find('.not-detected').exists()).toBe(true)
    expect(wrapper.text()).toContain('Carte non détectée')
    expect(wrapper.find('.detected').exists()).toBe(false)
  })

  it('a un attribut role="status" pour l\'accessibilité', () => {
    const wrapper = mount(CardDetectionOverlay, { props: { cardDetected: false } })

    expect(wrapper.find('[role="status"]').exists()).toBe(true)
  })
})
