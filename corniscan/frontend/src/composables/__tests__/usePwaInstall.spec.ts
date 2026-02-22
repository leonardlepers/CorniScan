/**
 * Tests Story 6.2 — usePwaInstall composable
 *
 * AC#2 : l'événement `beforeinstallprompt` est capturé + contrôle du prompt
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { defineComponent, nextTick } from 'vue'
import { usePwaInstall } from '@/composables/usePwaInstall'

// Composant minimal pour tester le composable dans un contexte Vue monté
function makeTestComponent() {
  return defineComponent({
    setup() {
      return usePwaInstall()
    },
    template: '<div />',
  })
}

describe('usePwaInstall', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('isInstallable est false par défaut', () => {
    const wrapper = mount(makeTestComponent())
    expect(wrapper.vm.isInstallable).toBe(false)
  })

  it('isInstallable devient true quand beforeinstallprompt est déclenché', async () => {
    const wrapper = mount(makeTestComponent())
    const event = new Event('beforeinstallprompt')
    window.dispatchEvent(event)
    await nextTick()
    expect(wrapper.vm.isInstallable).toBe(true)
  })

  it('preventDefault est appelé sur beforeinstallprompt', () => {
    mount(makeTestComponent())
    const event = new Event('beforeinstallprompt')
    const spy = vi.spyOn(event, 'preventDefault')
    window.dispatchEvent(event)
    expect(spy).toHaveBeenCalled()
  })

  it('isInstallable repasse à false après appinstalled', async () => {
    const wrapper = mount(makeTestComponent())
    window.dispatchEvent(new Event('beforeinstallprompt'))
    await nextTick()
    expect(wrapper.vm.isInstallable).toBe(true)

    window.dispatchEvent(new Event('appinstalled'))
    await nextTick()
    expect(wrapper.vm.isInstallable).toBe(false)
  })

  it('promptInstall ne fait rien si aucun prompt différé', async () => {
    const wrapper = mount(makeTestComponent())
    // Ne doit pas lever d'erreur
    await expect(wrapper.vm.promptInstall()).resolves.toBeUndefined()
  })

  it('promptInstall appelle prompt() et userChoice sur le deferredPrompt', async () => {
    const wrapper = mount(makeTestComponent())

    const mockPrompt = vi.fn().mockResolvedValue(undefined)
    const mockUserChoice = Promise.resolve({ outcome: 'accepted' as const })
    const event = Object.assign(new Event('beforeinstallprompt'), {
      prompt: mockPrompt,
      userChoice: mockUserChoice,
    })
    window.dispatchEvent(event)
    await nextTick()

    await wrapper.vm.promptInstall()

    expect(mockPrompt).toHaveBeenCalledOnce()
  })

  it('isInstallable repasse à false après promptInstall', async () => {
    const wrapper = mount(makeTestComponent())

    const event = Object.assign(new Event('beforeinstallprompt'), {
      prompt: vi.fn().mockResolvedValue(undefined),
      userChoice: Promise.resolve({ outcome: 'accepted' as const }),
    })
    window.dispatchEvent(event)
    await nextTick()

    await wrapper.vm.promptInstall()
    expect(wrapper.vm.isInstallable).toBe(false)
  })

  it('les listeners sont retirés au démontage', async () => {
    const removeSpy = vi.spyOn(window, 'removeEventListener')
    const wrapper = mount(makeTestComponent())
    wrapper.unmount()
    expect(removeSpy).toHaveBeenCalledWith('beforeinstallprompt', expect.any(Function))
    expect(removeSpy).toHaveBeenCalledWith('appinstalled', expect.any(Function))
  })
})
