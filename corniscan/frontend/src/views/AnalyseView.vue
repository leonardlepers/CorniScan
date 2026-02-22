<script setup lang="ts">
/**
 * AnalyseView.vue — Story 4.1 + Story 4.2
 *
 * Story 4.1 : soumet la photo à POST /api/v1/scan/process au montage,
 *             affiche spinner pendant le traitement (NFR-P4),
 *             stocke le résultat dans scanStore.
 *
 * Story 4.2 : affiche la photo avec ContourOverlay (FR19) et les
 *             dimensions numériques en mm à 1 décimale (FR20).
 *
 * Story 4.3 : saisie épaisseur via ThicknessInput (FR21),
 *             avertissement calibration + retake (FR22, FR23).
 *
 * Stories suivantes :
 *   4.4 — gestion erreurs complète
 *   4.5 — validation et envoi
 */
import { onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { apiCall } from '@/services/apiClient'
import { useScanStore, type ProcessResult } from '@/stores/scanStore'
import ContourOverlay from '@/components/validation/ContourOverlay.vue'
import ThicknessInput from '@/components/validation/ThicknessInput.vue'

const router = useRouter()
const scanStore = useScanStore()

const isLoading = ref(true)
const error = ref<string | null>(null)
const photoUrl = ref<string | null>(null)

onMounted(async () => {
  if (!scanStore.photo) {
    router.push({ name: 'camera' })
    return
  }

  // Blob URL pour afficher la photo (révoqué dans onUnmounted)
  photoUrl.value = URL.createObjectURL(scanStore.photo)

  const formData = new FormData()
  formData.append('file', scanStore.photo)

  try {
    const result = await apiCall<ProcessResult>('/api/v1/scan/process', {
      method: 'POST',
      body: formData,
    })
    scanStore.setResult(result)
  } catch (e) {
    error.value =
      e instanceof Error ? e.message : "Erreur lors de l'analyse. Veuillez recommencer."
  } finally {
    isLoading.value = false
  }
})

onUnmounted(() => {
  if (photoUrl.value) {
    URL.revokeObjectURL(photoUrl.value)
  }
})

function handleRetake(): void {
  scanStore.clearResult()
  router.push({ name: 'camera' })
}
</script>

<template>
  <div class="analyse-page">
    <!-- Chargement (NFR-P4 : UI non bloquée, spinner visible) -->
    <div v-if="isLoading" class="loading-container" role="status">
      <div class="spinner" aria-hidden="true"></div>
      <p class="loading-text">Analyse en cours…</p>
    </div>

    <!-- Erreur -->
    <div v-else-if="error" class="error-container">
      <p class="error-text">{{ error }}</p>
      <button class="retry-btn" @click="router.push({ name: 'camera' })">
        Recommencer la photo
      </button>
    </div>

    <!-- Résultat (Story 4.2 + Story 4.3) -->
    <div v-else class="result-container">
      <!-- Photo + overlay contour (FR19) -->
      <ContourOverlay
        v-if="photoUrl"
        :photo-url="photoUrl"
        :contour-points="scanStore.contour"
      />

      <!-- Dimensions numériques (FR20) -->
      <div v-if="scanStore.dimensions" class="dimensions-display">
        <span class="dimensions-label">Dimensions du joint :</span>
        <span class="dimensions-value">
          {{ scanStore.dimensions.width_mm.toFixed(1) }} mm
          ×
          {{ scanStore.dimensions.height_mm.toFixed(1) }} mm
        </span>
      </div>

      <!-- Saisie épaisseur + avertissement calibration (Story 4.3) -->
      <ThicknessInput
        :calibration-warning="scanStore.calibrationWarning"
        @update:thickness="scanStore.setThickness($event)"
        @retake="handleRetake"
      />
    </div>
  </div>
</template>

<style scoped>
.analyse-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100dvh;
  background: #111;
  color: #fff;
  font-family: sans-serif;
  gap: 1.5rem;
  padding: 1rem;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid rgba(255, 255, 255, 0.2);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-text {
  font-size: 1rem;
  opacity: 0.8;
}

.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 2rem;
  text-align: center;
}

.error-text {
  color: #f87171;
  font-size: 1rem;
}

.retry-btn {
  padding: 0.75rem 1.5rem;
  background: #fff;
  color: #111;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
}

.result-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.25rem;
  width: 100%;
}

.dimensions-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
}

.dimensions-label {
  font-size: 0.875rem;
  opacity: 0.7;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.dimensions-value {
  font-size: 1.5rem;
  font-weight: 600;
  letter-spacing: 0.02em;
}
</style>
