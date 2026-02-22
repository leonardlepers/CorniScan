/**
 * useCardDetection — Story 3.2
 *
 * Détection périodique de la carte bancaire dans le flux caméra.
 * Toutes les 500ms : capture une frame via canvas.toBlob() → POST /scan/detect-card.
 * Les erreurs réseau sont silencieuses (non-bloquantes — NFR-P4).
 *
 * Usage :
 *   const { cardDetected, startDetection, stopDetection } = useCardDetection(videoRef)
 */
import { onUnmounted, ref } from 'vue'
import type { Ref } from 'vue'
import { apiCall } from '@/services/apiClient'

const DETECTION_INTERVAL_MS = 500

export function useCardDetection(videoRef: Ref<HTMLVideoElement | null>) {
  const cardDetected = ref(false)
  let intervalId: ReturnType<typeof setInterval> | null = null
  let detecting = false // garde contre les appels concurrents

  async function captureAndDetect(): Promise<void> {
    const video = videoRef.value
    if (!video || !video.srcObject || video.videoWidth === 0 || detecting) return

    detecting = true
    try {
      // Capture une frame dans un canvas offscreen
      const canvas = document.createElement('canvas')
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      const ctx = canvas.getContext('2d')
      if (!ctx) return
      ctx.drawImage(video, 0, 0)

      // AC#1 — canvas.toBlob() → JPEG 60%
      const blob = await new Promise<Blob | null>((resolve) =>
        canvas.toBlob(resolve, 'image/jpeg', 0.6),
      )
      if (!blob) return

      const formData = new FormData()
      formData.append('file', blob, 'frame.jpg')

      // AC#4 — appel non-bloquant : les erreurs réseau sont ignorées
      const result = await apiCall<{ card_detected: boolean }>('/api/v1/scan/detect-card', {
        method: 'POST',
        body: formData,
      })
      cardDetected.value = result.card_detected
    } catch {
      // Silencieux — ne pas bloquer l'UI ni afficher d'erreur (NFR-P4)
    } finally {
      detecting = false
    }
  }

  /** Démarre l'intervalle de détection (500ms). */
  function startDetection(): void {
    if (intervalId !== null) return
    intervalId = setInterval(captureAndDetect, DETECTION_INTERVAL_MS)
  }

  /** Arrête l'intervalle. */
  function stopDetection(): void {
    if (intervalId !== null) {
      clearInterval(intervalId)
      intervalId = null
    }
  }

  onUnmounted(stopDetection)

  return { cardDetected, startDetection, stopDetection }
}
