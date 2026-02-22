<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppHeader from '@/components/AppHeader.vue'
import CardDetectionOverlay from '@/components/camera/CardDetectionOverlay.vue'
import CaptureChecklist from '@/components/camera/CaptureChecklist.vue'
import { useCardDetection } from '@/composables/useCardDetection'
import { useMediaDevices } from '@/composables/useMediaDevices'
import { usePwaInstall } from '@/composables/usePwaInstall'
import { useScanStore } from '@/stores/scanStore'

const route = useRoute()
const router = useRouter()
const scanStore = useScanStore()

// AC#1 Story 2.4 — message d'accès refusé si redirigé depuis une route admin
const showForbiddenAlert = ref(route.query.forbidden === '1')

function dismissAlert() {
  showForbiddenAlert.value = false
}

// Story 6.2 — invite installation PWA (Android)
const { isInstallable, promptInstall } = usePwaInstall()

// Story 3.1 — flux caméra
const { videoRef, isLoading, error, startCamera, stopCamera } = useMediaDevices()

// Story 3.2 — détection carte (démarre quand la caméra est active)
const { cardDetected, startDetection, stopDetection } = useCardDetection(videoRef)

// Lance la détection dès que le flux est prêt (srcObject défini), l'arrête en cas d'erreur
watch(error, (newError) => {
  if (newError) {
    stopDetection()
  }
})

onMounted(async () => {
  await startCamera()
  if (!error.value) {
    startDetection()
  }
})

// Story 3.3 — checklist qualité
const allChecked = ref(false)

function onChecklistUpdate(value: boolean) {
  allChecked.value = value
}

// Story 3.4 — capture photo (AC#1 FR12)
const capturedImage = ref<string | null>(null)
let capturedFile: File | null = null

async function capture(): Promise<void> {
  const video = videoRef.value
  if (!video) return

  const canvas = document.createElement('canvas')
  canvas.width = video.videoWidth
  canvas.height = video.videoHeight
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  ctx.drawImage(video, 0, 0)

  // AC#3 — canvas.drawImage capture les pixels affichés (orientation déjà correcte, sans EXIF)
  const blob = await new Promise<Blob | null>((resolve) => {
    canvas.toBlob(resolve, 'image/jpeg', 0.92)
  })

  if (!blob) return

  capturedFile = new File([blob], 'capture.jpg', { type: 'image/jpeg' })
  capturedImage.value = URL.createObjectURL(blob)
  stopCamera()
  stopDetection()
}

// AC#2 — confirmation → stockage dans scanStore + redirection vers /analyse
function confirmCapture(): void {
  if (!capturedFile) return
  scanStore.setPhoto(capturedFile)
  router.push({ name: 'analyse' })
}

// Recommencer — réinitialise et relance la caméra
async function retakePhoto(): Promise<void> {
  if (capturedImage.value) {
    URL.revokeObjectURL(capturedImage.value)
    capturedImage.value = null
    capturedFile = null
  }
  await startCamera()
  if (!error.value) {
    startDetection()
  }
}
</script>

<template>
  <!-- AC#4 — plein écran (overflow masqué, hauteur viewport) -->
  <div class="camera-page">
    <AppHeader />

    <!-- Story 6.2 — bannière installation PWA (Android Chrome) -->
    <div v-if="isInstallable" class="install-banner">
      <span class="install-text">Installez CorniScan sur votre écran d'accueil</span>
      <button class="install-btn" @click="promptInstall">Installer</button>
    </div>

    <!-- Alerte accès refusé (Story 2.4) -->
    <div
      v-if="showForbiddenAlert"
      class="forbidden-alert"
      role="alert"
    >
      <span>Accès refusé. Cette section est réservée aux administrateurs.</span>
      <button class="dismiss-btn" aria-label="Fermer" @click="dismissAlert">✕</button>
    </div>

    <!-- Story 3.4 — aperçu photo capturée (AC#1) -->
    <div
      v-if="capturedImage"
      class="capture-preview"
    >
      <img
        :src="capturedImage"
        class="preview-image"
        alt="Photo capturée"
      />
      <div class="preview-actions">
        <button class="retake-btn" @click="retakePhoto">Recommencer</button>
        <button class="confirm-btn" @click="confirmCapture">Confirmer</button>
      </div>
    </div>

    <!-- Conteneur flux caméra (masqué pendant l'aperçu) -->
    <div v-else class="camera-container">
      <!-- AC#1 — flux caméra arrière (toujours dans le DOM pour que videoRef soit résolu) -->
      <video
        ref="videoRef"
        class="camera-video"
        autoplay
        playsinline
        muted
      />

      <!-- État chargement -->
      <div v-if="isLoading" class="camera-state-overlay" role="status">
        <p>Initialisation de la caméra…</p>
      </div>

      <!-- AC#3 — erreur getUserMedia -->
      <div
        v-else-if="error"
        class="camera-state-overlay camera-error"
        role="alert"
      >
        <p class="error-text">{{ error }}</p>
        <button class="retry-btn" @click="startCamera">Réessayer</button>
      </div>

      <!-- Story 3.2 — indicateur détection carte (AC#2, AC#3) -->
      <CardDetectionOverlay v-if="!isLoading && !error" :card-detected="cardDetected" />

      <!-- Story 3.3 — checklist qualité + bouton capture (AC#1, #2, #3, #4) -->
      <div
        v-if="!isLoading && !error"
        class="camera-controls"
      >
        <CaptureChecklist @update:all-checked="onChecklistUpdate" />
        <button
          class="capture-btn"
          :disabled="!allChecked"
          @click="capture"
        >
          Capturer
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* AC#4 — plein écran, pas de scroll */
.camera-page {
  display: flex;
  flex-direction: column;
  height: 100dvh;
  overflow: hidden;
  background: #000;
  font-family: sans-serif;
}

.install-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #1a237e;
  color: #fff;
  padding: 0.6rem 1rem;
  font-size: 0.875rem;
  flex-shrink: 0;
  gap: 0.75rem;
}

.install-text {
  flex: 1;
}

.install-btn {
  background: #fff;
  color: #1a237e;
  border: none;
  border-radius: 4px;
  padding: 0.35rem 0.875rem;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
}

.forbidden-alert {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fbe9e7;
  color: #bf360c;
  padding: 0.6rem 1rem;
  font-size: 0.875rem;
  border-bottom: 1px solid #ef9a9a;
  flex-shrink: 0;
}

.dismiss-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  color: #bf360c;
  font-size: 1rem;
  line-height: 1;
  padding: 0;
  margin-left: 1rem;
}

/* Conteneur qui occupe tout l'espace restant */
.camera-container {
  flex: 1;
  position: relative;
  overflow: hidden;
}

/* AC#1 — flux caméra plein écran */
.camera-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Overlay partagé (loading + erreur) */
.camera-state-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.75);
  color: #fff;
  gap: 1rem;
  padding: 1.5rem;
  text-align: center;
}

.error-text {
  font-size: 0.95rem;
  line-height: 1.5;
  margin: 0;
}

.retry-btn {
  padding: 0.5rem 1.25rem;
  background: #4a6cf7;
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 0.9rem;
  cursor: pointer;
}

/* Contrôles caméra — checklist + bouton capture (Story 3.3) */
.camera-controls {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem 1.5rem;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.75));
}

.capture-btn {
  padding: 0.75rem 2.5rem;
  background: #4a6cf7;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  min-width: 180px;
}

.capture-btn:disabled {
  background: #444;
  color: #888;
  cursor: not-allowed;
}

/* Aperçu photo capturée (Story 3.4) */
.capture-preview {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #000;
  position: relative;
  overflow: hidden;
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.preview-actions {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-around;
  padding: 1.25rem;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.75));
}

.retake-btn {
  padding: 0.75rem 1.5rem;
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.4);
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
}

.confirm-btn {
  padding: 0.75rem 1.5rem;
  background: #22c55e;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
}
</style>
