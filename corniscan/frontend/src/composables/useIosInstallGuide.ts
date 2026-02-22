/**
 * useIosInstallGuide — Story 6.3 (FR34)
 *
 * Détecte si l'opérateur est sur Safari iOS (hors mode standalone) et n'a
 * jamais vu le guide d'installation. Expose `showGuide` et `dismissGuide()`.
 *
 * Conditions pour afficher :
 *   1. iOS (iPad/iPhone/iPod) + Safari (WebKit sans autre navigateur)
 *   2. Pas en mode standalone (`display-mode: standalone`)
 *   3. Guide jamais montré (localStorage `ios_install_guide_shown` absent)
 */
import { ref } from 'vue'

const IOS_GUIDE_KEY = 'ios_install_guide_shown'

function isIosSafari(): boolean {
  const ua = navigator.userAgent
  const isIOS = /iPad|iPhone|iPod/.test(ua)
  // Safari sur iOS : WebKit présent, sans les identifiants des autres navigateurs
  const isSafari = /WebKit/.test(ua) && !/CriOS|FxiOS|OPiOS|EdgiOS/.test(ua)
  return isIOS && isSafari
}

function isStandalone(): boolean {
  return window.matchMedia('(display-mode: standalone)').matches
}

function hasBeenShown(): boolean {
  return localStorage.getItem(IOS_GUIDE_KEY) === 'true'
}

export function useIosInstallGuide() {
  const showGuide = ref(false)

  /** À appeler après un login réussi. Affiche le guide si les conditions sont remplies. */
  function checkAndShow(): void {
    if (isIosSafari() && !isStandalone() && !hasBeenShown()) {
      showGuide.value = true
    }
  }

  /** Ferme le guide et mémorise qu'il a été vu dans localStorage. */
  function dismissGuide(): void {
    showGuide.value = false
    localStorage.setItem(IOS_GUIDE_KEY, 'true')
  }

  return { showGuide, checkAndShow, dismissGuide }
}
