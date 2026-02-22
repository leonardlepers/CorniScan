/**
 * Tests Story 4.3 — ThicknessInput.vue
 *
 * AC#1 : champ épaisseur visible et éditable
 * AC#2 : avertissement calibration affiché si calibrationWarning = true (texte exact FR22)
 * AC#3 : deux boutons d'action si avertissement visible (FR23)
 * AC#5 : aucun avertissement si calibrationWarning = false
 * Emit : update:thickness, retake, force-send
 */
import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import ThicknessInput from '../ThicknessInput.vue'

describe('ThicknessInput — champ épaisseur (AC#1)', () => {
  it("affiche un champ de saisie numérique visible", () => {
    const wrapper = mount(ThicknessInput, {
      props: { calibrationWarning: false },
    })

    const input = wrapper.find('#thickness-input')
    expect(input.exists()).toBe(true)
    expect(input.attributes('type')).toBe('number')
  })

  it('affiche le label pour le champ épaisseur', () => {
    const wrapper = mount(ThicknessInput, {
      props: { calibrationWarning: false },
    })

    const label = wrapper.find('label[for="thickness-input"]')
    expect(label.exists()).toBe(true)
    expect(label.text()).toContain('mm')
  })

  it("émet update:thickness avec la valeur parsée quand l'utilisateur saisit", async () => {
    const wrapper = mount(ThicknessInput, {
      props: { calibrationWarning: false },
    })

    const input = wrapper.find('#thickness-input')
    await input.setValue('2.5')
    await input.trigger('input')

    expect(wrapper.emitted('update:thickness')).toBeTruthy()
    expect(wrapper.emitted('update:thickness')![0]).toEqual([2.5])
  })

  it("émet update:thickness avec null si la valeur est vide", async () => {
    const wrapper = mount(ThicknessInput, {
      props: { calibrationWarning: false },
    })

    const input = wrapper.find('#thickness-input')
    await input.setValue('')
    await input.trigger('input')

    expect(wrapper.emitted('update:thickness')![0]).toEqual([null])
  })

  it("émet update:thickness avec null si la valeur est négative", async () => {
    const wrapper = mount(ThicknessInput, {
      props: { calibrationWarning: false },
    })

    const input = wrapper.find('#thickness-input')
    await input.setValue('-1')
    await input.trigger('input')

    expect(wrapper.emitted('update:thickness')![0]).toEqual([null])
  })
})

describe("ThicknessInput — avertissement calibration (AC#2, AC#3, AC#5)", () => {
  it("n'affiche pas l'avertissement si calibrationWarning = false (AC#5)", () => {
    const wrapper = mount(ThicknessInput, {
      props: { calibrationWarning: false },
    })

    expect(wrapper.find('.calibration-warning').exists()).toBe(false)
  })

  it("affiche l'avertissement si calibrationWarning = true (AC#2)", () => {
    const wrapper = mount(ThicknessInput, {
      props: { calibrationWarning: true },
    })

    expect(wrapper.find('.calibration-warning').exists()).toBe(true)
  })

  it("affiche le texte d'avertissement exact (AC#2)", () => {
    const wrapper = mount(ThicknessInput, {
      props: { calibrationWarning: true },
    })

    const warning = wrapper.find('.warning-text')
    expect(warning.text()).toContain('Calibration insuffisante')
    expect(warning.text()).toContain('moins de 4 coins de la carte')
  })

  it("affiche le bouton Recommencer la photo si avertissement visible (AC#3)", () => {
    const wrapper = mount(ThicknessInput, {
      props: { calibrationWarning: true },
    })

    const btn = wrapper.find('.retake-btn')
    expect(btn.exists()).toBe(true)
    expect(btn.text()).toContain('Recommencer la photo')
  })

  it("affiche le bouton Forcer l'envoi si avertissement visible (AC#3)", () => {
    const wrapper = mount(ThicknessInput, {
      props: { calibrationWarning: true },
    })

    const btn = wrapper.find('.force-send-btn')
    expect(btn.exists()).toBe(true)
    expect(btn.text()).toContain("Forcer l'envoi")
  })

  it("le bouton Recommencer émet retake au clic", async () => {
    const wrapper = mount(ThicknessInput, {
      props: { calibrationWarning: true },
    })

    await wrapper.find('.retake-btn').trigger('click')

    expect(wrapper.emitted('retake')).toBeTruthy()
  })

  it("le bouton Forcer l'envoi émet force-send au clic", async () => {
    const wrapper = mount(ThicknessInput, {
      props: { calibrationWarning: true },
    })

    await wrapper.find('.force-send-btn').trigger('click')

    expect(wrapper.emitted('force-send')).toBeTruthy()
  })
})
