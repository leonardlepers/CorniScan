/**
 * useMediaDevices — Story 3.1
 *
 * Gère l'accès au flux caméra arrière (facingMode: 'environment') et le
 * verrouillage portrait. Retourne une ref à lier à l'élément <video> du template.
 *
 * Usage :
 *   const { videoRef, isLoading, error, startCamera, stopCamera } = useMediaDevices()
 *   onMounted(startCamera)
 */
import { onUnmounted, ref } from 'vue'

export function useMediaDevices() {
  const videoRef = ref<HTMLVideoElement | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  /**
   * Démarre le flux caméra arrière et tente le verrouillage portrait (AC#1, AC#2).
   * Gère les erreurs de permission et de compatibilité navigateur (AC#3).
   */
  async function startCamera(): Promise<void> {
    isLoading.value = true
    error.value = null

    // AC#3 — navigateur sans support getUserMedia
    if (!navigator.mediaDevices?.getUserMedia) {
      error.value = "Votre navigateur ne supporte pas l'accès à la caméra."
      isLoading.value = false
      return
    }

    try {
      // AC#1 — caméra arrière, portrait
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment', width: { ideal: 4096 }, height: { ideal: 4096 } },
        audio: false,
      })

      if (videoRef.value) {
        videoRef.value.srcObject = stream
        localStorage.setItem('camera_granted', 'true')
      }

      // AC#2 — portrait lock (best-effort : ignore si non supporté)
      try {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        await (screen.orientation as any).lock('portrait')
      } catch {
        // desktop et navigateurs non supportants : silencieux
      }
    } catch (err) {
      if (err instanceof DOMException) {
        if (err.name === 'NotAllowedError') {
          error.value =
            "Accès à la caméra refusé. Autorisez l'accès à la caméra dans les paramètres de votre navigateur."
        } else if (err.name === 'NotFoundError') {
          error.value = "Aucune caméra arrière trouvée sur cet appareil."
        } else {
          error.value = "Impossible d'accéder à la caméra."
        }
      } else {
        error.value = "Impossible d'accéder à la caméra."
      }
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Arrête tous les tracks du flux actif.
   */
  function stopCamera(): void {
    if (videoRef.value?.srcObject) {
      const stream = videoRef.value.srcObject as MediaStream
      stream.getTracks().forEach((track) => track.stop())
      videoRef.value.srcObject = null
    }
  }

  // Nettoyage automatique quand le composant est démonté
  onUnmounted(stopCamera)

  return { videoRef, isLoading, error, startCamera, stopCamera }
}
