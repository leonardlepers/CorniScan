/**
 * usePwaInstall — Story 6.2 (FR33)
 *
 * Capture l'événement `beforeinstallprompt` pour contrôler le moment
 * d'affichage de l'invite native "Ajouter à l'écran d'accueil" (Android/Chrome).
 *
 * Usage :
 *   const { isInstallable, promptInstall } = usePwaInstall()
 */
import { ref, onMounted, onUnmounted } from 'vue'

// Le type BeforeInstallPromptEvent n'est pas dans lib.dom.d.ts standard
interface BeforeInstallPromptEvent extends Event {
  prompt(): Promise<void>
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>
}

export function usePwaInstall() {
  const isInstallable = ref(false)
  let deferredPrompt: BeforeInstallPromptEvent | null = null

  function handleBeforeInstallPrompt(event: Event): void {
    event.preventDefault()
    deferredPrompt = event as BeforeInstallPromptEvent
    isInstallable.value = true
  }

  function handleAppInstalled(): void {
    deferredPrompt = null
    isInstallable.value = false
  }

  async function promptInstall(): Promise<void> {
    if (!deferredPrompt) return
    await deferredPrompt.prompt()
    await deferredPrompt.userChoice
    deferredPrompt = null
    isInstallable.value = false
  }

  onMounted(() => {
    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt)
    window.addEventListener('appinstalled', handleAppInstalled)
  })

  onUnmounted(() => {
    window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt)
    window.removeEventListener('appinstalled', handleAppInstalled)
  })

  return { isInstallable, promptInstall }
}
