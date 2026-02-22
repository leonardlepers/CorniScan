/**
 * Tests Story 6.3 — IosInstallGuide.vue
 *
 * AC#2 : guide présente les instructions iOS (Partager + Sur l'écran d'accueil)
 * AC#3 : émission de l'événement dismiss au clic sur "J'ai compris"
 */
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import IosInstallGuide from '@/components/IosInstallGuide.vue'

describe('IosInstallGuide', () => {
  it('affiche le titre d\'installation', () => {
    const wrapper = mount(IosInstallGuide)
    expect(wrapper.find('.ios-guide-title').text()).toContain('Installer CorniScan')
  })

  it('affiche l\'instruction "Partager"', () => {
    const wrapper = mount(IosInstallGuide)
    expect(wrapper.text()).toContain('Partager')
  })

  it('affiche l\'instruction "Sur l\'écran d\'accueil"', () => {
    const wrapper = mount(IosInstallGuide)
    expect(wrapper.text()).toContain("Sur l'écran d'accueil")
  })

  it('affiche le bouton "J\'ai compris"', () => {
    const wrapper = mount(IosInstallGuide)
    expect(wrapper.find('.ios-guide-close').text()).toBe("J'ai compris")
  })

  it('émet l\'événement dismiss au clic sur "J\'ai compris"', async () => {
    const wrapper = mount(IosInstallGuide)
    await wrapper.find('.ios-guide-close').trigger('click')
    expect(wrapper.emitted('dismiss')).toHaveLength(1)
  })

  it('a le rôle dialog', () => {
    const wrapper = mount(IosInstallGuide)
    expect(wrapper.find('[role="dialog"]').exists()).toBe(true)
  })
})
