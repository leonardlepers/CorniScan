/**
 * Tests Story 3.3 — CaptureChecklist.vue
 * AC#1 : 2 cases à cocher visibles dès le montage
 * AC#2 : allChecked=false tant que les 2 cases ne sont pas cochées
 * AC#3 : allChecked=true quand les 2 cases sont cochées
 * AC#4 : allChecked=false si une case est décochée après avoir été cochée
 */
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import CaptureChecklist from '../CaptureChecklist.vue'

describe('CaptureChecklist (Story 3.3)', () => {
  it('AC#1 — affiche les 2 cases non cochées initialement avec les bons libellés', () => {
    const wrapper = mount(CaptureChecklist)

    const checkboxes = wrapper.findAll('input[type="checkbox"]')
    expect(checkboxes).toHaveLength(2)
    expect((checkboxes[0].element as HTMLInputElement).checked).toBe(false)
    expect((checkboxes[1].element as HTMLInputElement).checked).toBe(false)

    expect(wrapper.text()).toContain('Joint propre')
    expect(wrapper.text()).toContain('Carte entièrement visible')
  })

  it('AC#2 — émet allChecked=false immédiatement au montage', () => {
    const wrapper = mount(CaptureChecklist)

    const emissions = wrapper.emitted('update:allChecked') as boolean[][]
    expect(emissions).toBeDefined()
    expect(emissions[0]).toEqual([false])
  })

  it('AC#2 — émet allChecked=false si seulement une case est cochée', async () => {
    const wrapper = mount(CaptureChecklist)
    const checkboxes = wrapper.findAll('input[type="checkbox"]')

    await checkboxes[0].setValue(true)

    const emissions = wrapper.emitted('update:allChecked') as boolean[][]
    expect(emissions[emissions.length - 1]).toEqual([false])
  })

  it('AC#3 — émet allChecked=true quand les 2 cases sont cochées', async () => {
    const wrapper = mount(CaptureChecklist)
    const checkboxes = wrapper.findAll('input[type="checkbox"]')

    await checkboxes[0].setValue(true)
    await checkboxes[1].setValue(true)

    const emissions = wrapper.emitted('update:allChecked') as boolean[][]
    expect(emissions[emissions.length - 1]).toEqual([true])
  })

  it('AC#4 — émet allChecked=false si une case est décochée après avoir été cochée', async () => {
    const wrapper = mount(CaptureChecklist)
    const checkboxes = wrapper.findAll('input[type="checkbox"]')

    await checkboxes[0].setValue(true)
    await checkboxes[1].setValue(true)
    // Décocher une case
    await checkboxes[0].setValue(false)

    const emissions = wrapper.emitted('update:allChecked') as boolean[][]
    expect(emissions[emissions.length - 1]).toEqual([false])
  })
})
