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

// Import fichier (image ou PDF) — alternative à la caméra
const fileInput = ref<HTMLInputElement | null>(null)

function handleFileUpload(event: Event): void {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return
  scanStore.setPhoto(file)
  router.push({ name: 'analyse' })
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
      <button class="dismiss-btn" aria-label="Fermer" @click="dismissAlert">
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
          <path d="M1 1l12 12M13 1L1 13" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
        </svg>
      </button>
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
        <button class="retake-btn" @click="retakePhoto">
          <svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true">
            <path d="M2 9a7 7 0 1 0 1.5-4.33" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
            <path d="M2 4.5V9h4.5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          Recommencer
        </button>
        <button class="confirm-btn" @click="confirmCapture">
          <svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true">
            <path d="M3 9.5l4 4 8-8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          Confirmer
        </button>
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
        <div class="camera-spinner" aria-hidden="true"></div>
        <p>Initialisation de la caméra…</p>
      </div>

      <!-- AC#3 — erreur getUserMedia -->
      <div
        v-else-if="error"
        class="camera-state-overlay camera-error"
        role="alert"
      >
        <div class="error-icon" aria-hidden="true">
          <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
            <circle cx="16" cy="16" r="14" stroke="rgba(255,255,255,0.5)" stroke-width="1.5"/>
            <path d="M16 10v7M16 21h.01" stroke="white" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </div>
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

        <!-- Bouton capture style iOS — cercle -->
        <div class="capture-btn-wrapper">
          <button
            class="capture-btn"
            :class="{ 'capture-btn--ready': allChecked }"
            :disabled="!allChecked"
            :aria-label="allChecked ? 'Capturer la photo' : 'Cochez les deux cases avant de capturer'"
            @click="capture"
          >
            <span class="capture-btn-inner"></span>
          </button>
        </div>

        <!-- Import fichier — alternative à la caméra -->
        <input
          ref="fileInput"
          type="file"
          accept="image/*,application/pdf"
          class="file-input-hidden"
          @change="handleFileUpload"
        />
        <button class="import-btn" @click="fileInput?.click()">
          Importer une image ou un PDF
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.camera-page {
  display: flex;
  flex-direction: column;
  height: 100dvh;
  overflow: hidden;
  background: #0d0f12;
  color: var(--color-on-dark);
}

/* ── Bannière PWA ───────────────────────────────── */
.install-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(201, 123, 99, 0.18);
  color: #fdf7f2;
  padding: 0.65rem calc(1rem + var(--safe-right)) 0.65rem calc(1rem + var(--safe-left));
  font-size: 0.875rem;
  flex-shrink: 0;
  gap: 0.75rem;
  border-bottom: 1px solid rgba(201, 123, 99, 0.35);
}

.install-text {
  flex: 1;
}

.install-btn {
  background: rgba(255, 255, 255, 0.92);
  color: #7a3f2a;
  border-radius: 999px;
  padding: 0.4rem 1rem;
  font-size: 0.8rem;
  font-weight: 700;
  white-space: nowrap;
  transition: transform var(--transition-fast);
}

.install-btn:active {
  transform: scale(0.95);
}

/* ── Alerte accès refusé ─────────────────────────── */
.forbidden-alert {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(209, 73, 91, 0.18);
  color: #ffe7e5;
  padding: 0.65rem calc(1rem + var(--safe-right)) 0.65rem calc(1rem + var(--safe-left));
  font-size: 0.875rem;
  border-bottom: 1px solid rgba(209, 73, 91, 0.4);
  flex-shrink: 0;
  gap: 0.75rem;
}

.dismiss-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.12);
  color: #ffe7e5;
  flex-shrink: 0;
  transition: background var(--transition-fast);
}

.dismiss-btn:active {
  background: rgba(255, 255, 255, 0.22);
}

/* ── Conteneur caméra ────────────────────────────── */
.camera-container {
  flex: 1;
  position: relative;
  overflow: hidden;
}

.camera-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* ── Overlay états ───────────────────────────────── */
.camera-state-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(6, 7, 9, 0.82);
  color: #fff;
  gap: 1.25rem;
  padding: 2rem;
  text-align: center;
}

.camera-spinner {
  width: 44px;
  height: 44px;
  border: 3px solid rgba(255, 255, 255, 0.2);
  border-top-color: rgba(255, 255, 255, 0.85);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-icon {
  opacity: 0.8;
}

.error-text {
  font-size: 0.95rem;
  line-height: 1.55;
  margin: 0;
  max-width: 280px;
  opacity: 0.9;
}

.retry-btn {
  padding: 0 1.6rem;
  height: var(--btn-height-sm);
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 999px;
  font-size: 0.9rem;
  font-weight: 600;
  backdrop-filter: blur(8px);
  transition: background var(--transition-fast), transform var(--transition-fast);
}

.retry-btn:active {
  transform: scale(0.96);
  background: rgba(255, 255, 255, 0.22);
}

/* ── Contrôles caméra ────────────────────────────── */
.camera-controls {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.25rem;
  padding: 1.5rem calc(1.5rem + var(--safe-right)) calc(1.75rem + var(--safe-bottom)) calc(1.5rem + var(--safe-left));
  background: linear-gradient(transparent, rgba(10, 12, 15, 0.95) 40%);
}

/* ── Bouton capture iOS ──────────────────────────── */
.capture-btn-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
}

.capture-btn {
  width: 76px;
  height: 76px;
  border-radius: 50%;
  border: 3px solid rgba(255, 255, 255, 0.85);
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  transition:
    border-color var(--transition-fast),
    transform var(--transition-fast),
    opacity var(--transition-fast);
}

.capture-btn-inner {
  width: 58px;
  height: 58px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.88);
  display: block;
  transition:
    background var(--transition-fast),
    transform var(--transition-fast);
}

/* Prêt à capturer */
.capture-btn--ready {
  border-color: #fff;
}

.capture-btn--ready .capture-btn-inner {
  background: #fff;
}

/* Appui */
.capture-btn--ready:active {
  transform: scale(0.92);
}

.capture-btn--ready:active .capture-btn-inner {
  transform: scale(0.88);
}

/* Désactivé */
.capture-btn:disabled {
  border-color: rgba(255, 255, 255, 0.28);
  cursor: not-allowed;
}

.capture-btn:disabled .capture-btn-inner {
  background: rgba(255, 255, 255, 0.22);
}

/* ── Aperçu capture ──────────────────────────────── */
.capture-preview {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #0d0f12;
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
  justify-content: center;
  gap: 1rem;
  padding: 1.5rem calc(1.5rem + var(--safe-right)) calc(1.75rem + var(--safe-bottom)) calc(1.5rem + var(--safe-left));
  background: linear-gradient(transparent, rgba(10, 12, 15, 0.95) 40%);
}

.retake-btn,
.confirm-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  height: var(--btn-height);
  padding: 0 1.6rem;
  border-radius: 999px;
  font-size: 0.95rem;
  font-weight: 600;
  transition: transform var(--transition-fast), opacity var(--transition-fast);
  flex: 1;
  max-width: 180px;
}

.retake-btn:active,
.confirm-btn:active {
  transform: scale(0.96);
}

.retake-btn {
  background: rgba(255, 255, 255, 0.12);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.28);
  backdrop-filter: blur(8px);
}

.confirm-btn {
  background: var(--color-success);
  color: #fff;
  box-shadow: var(--shadow-success);
}

/* ── Import fichier ──────────────────────────────── */
.file-input-hidden {
  display: none;
}

.import-btn {
  color: rgba(247, 241, 234, 0.6);
  font-size: 0.8rem;
  font-weight: 500;
  text-decoration: underline;
  text-underline-offset: 3px;
  padding: 0.25rem 0;
  transition: color var(--transition-fast);
}

.import-btn:active {
  color: rgba(247, 241, 234, 0.9);
}
</style>
