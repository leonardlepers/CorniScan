<script setup lang="ts">
/**
 * AnalyseView.vue — Story 4.1 + Story 4.2 + Story 4.3 + Story 4.4
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
 * Story 4.4 : erreur réseau → message FR32 (navigator.onLine),
 *             erreur traitement → message FR30,
 *             session + photo préservées (NFR-R2, NFR-R3).
 *
 * Story 4.5 : bouton "Valider et envoyer" → POST /scan/submit (FR24),
 *             bouton désactivé pendant l'envoi (NFR-P4),
 *             redirect /confirmation sur succès (FR28).
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
const isSubmitting = ref(false)
const submitError = ref<string | null>(null)

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
  } catch {
    // FR32 : réseau absent → message spécifique
    // FR30 : erreur traitement (serveur, parse, etc.)
    error.value = !navigator.onLine
      ? 'Connexion réseau absente. Vérifiez votre WiFi ou 4G avant de réessayer.'
      : "Une erreur est survenue lors de l'analyse. Recommencez la photo."
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

async function handleSubmit(): Promise<void> {
  if (isSubmitting.value || !scanStore.photo) return
  isSubmitting.value = true
  submitError.value = null

  const formData = new FormData()
  formData.append('file', scanStore.photo)
  formData.append('contour_points', JSON.stringify(scanStore.contour))
  formData.append('width_mm', String(scanStore.dimensions?.width_mm ?? 0))
  formData.append('height_mm', String(scanStore.dimensions?.height_mm ?? 0))
  if (scanStore.thickness !== null) {
    formData.append('thickness', String(scanStore.thickness))
  }
  formData.append('calibration_warning', String(scanStore.calibrationWarning))

  try {
    await apiCall('/api/v1/scan/submit', { method: 'POST', body: formData })
    router.push({ name: 'confirmation' })
  } catch {
    submitError.value = !navigator.onLine
      ? 'Connexion réseau absente. Vérifiez votre WiFi ou 4G avant de réessayer.'
      : "Erreur lors de l'envoi. Veuillez réessayer."
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="analyse-page">
    <!-- Chargement (NFR-P4 : UI non bloquée, spinner visible) -->
    <div v-if="isLoading" class="state-container" role="status">
      <div class="analyse-spinner" aria-hidden="true">
        <svg width="52" height="52" viewBox="0 0 52 52" fill="none">
          <circle cx="26" cy="26" r="22" stroke="var(--color-surface-strong)" stroke-width="3"/>
          <circle
            cx="26" cy="26" r="22"
            stroke="var(--color-accent)"
            stroke-width="3"
            stroke-linecap="round"
            stroke-dasharray="34.5 103.7"
            class="spinner-arc"
          />
        </svg>
      </div>
      <p class="state-title">Analyse en cours…</p>
      <p class="state-subtitle">Détection du joint</p>
    </div>

    <!-- Erreur -->
    <div v-else-if="error" class="state-container">
      <div class="error-icon-wrapper" aria-hidden="true">
        <svg width="44" height="44" viewBox="0 0 44 44" fill="none">
          <circle cx="22" cy="22" r="20" fill="rgba(209,73,91,0.1)" stroke="rgba(209,73,91,0.3)" stroke-width="1.5"/>
          <path d="M22 14v10M22 28h.01" stroke="var(--color-danger)" stroke-width="2.5" stroke-linecap="round"/>
        </svg>
      </div>
      <p class="state-title">Analyse échouée</p>
      <p class="state-subtitle error-subtitle">{{ error }}</p>
      <button class="action-btn action-btn--accent" @click="router.push({ name: 'camera' })">
        Recommencer la photo
      </button>
    </div>

    <!-- Résultat (Story 4.2 + Story 4.3) -->
    <div v-else class="result-scroll">
      <div class="result-container">
        <!-- Photo + overlay contour (FR19) -->
        <ContourOverlay
          v-if="photoUrl"
          :photo-url="photoUrl"
          :contour-points="scanStore.contour"
        />

        <!-- Dimensions numériques (FR20) -->
        <div v-if="scanStore.dimensions" class="dimensions-display">
          <p class="dimensions-label">Dimensions du joint</p>
          <div class="dimensions-values">
            <div class="dim-chip">
              <span class="dim-chip-axis">L</span>
              <span class="dim-chip-value">{{ scanStore.dimensions.width_mm.toFixed(1) }}</span>
              <span class="dim-chip-unit">mm</span>
            </div>
            <span class="dim-separator" aria-hidden="true">×</span>
            <div class="dim-chip">
              <span class="dim-chip-axis">H</span>
              <span class="dim-chip-value">{{ scanStore.dimensions.height_mm.toFixed(1) }}</span>
              <span class="dim-chip-unit">mm</span>
            </div>
          </div>
        </div>

        <!-- Saisie épaisseur + avertissement calibration (Story 4.3) -->
        <ThicknessInput
          :calibration-warning="scanStore.calibrationWarning"
          @update:thickness="scanStore.setThickness($event)"
          @retake="handleRetake"
          @force-send="handleSubmit"
        />

        <!-- Erreur d'envoi (Story 4.5) -->
        <div v-if="submitError" class="submit-error-banner" role="alert">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
            <circle cx="8" cy="8" r="7" stroke="currentColor" stroke-width="1.5"/>
            <path d="M8 5v3.5M8 11h.01" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
          {{ submitError }}
        </div>

        <!-- Bouton validation finale (Story 4.5 — FR24) -->
        <button
          class="action-btn action-btn--accent action-btn--full"
          :disabled="isSubmitting"
          @click="handleSubmit"
        >
          <span v-if="isSubmitting" class="btn-spinner" aria-hidden="true"></span>
          <span>{{ isSubmitting ? 'Envoi en cours…' : 'Valider et envoyer' }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.analyse-page {
  display: flex;
  flex-direction: column;
  min-height: 100dvh;
}

/* ── États loading / erreur ─────────────────────── */
.state-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: calc(var(--safe-top) + 3rem) var(--screen-pad) calc(var(--safe-bottom) + var(--screen-pad));
  text-align: center;
  animation: fadeIn 0.3s var(--ease-out) both;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Spinner SVG animé */
.analyse-spinner {
  margin-bottom: 0.5rem;
}

.spinner-arc {
  animation: rotate 1.1s linear infinite;
  transform-origin: center;
}

@keyframes rotate {
  to { transform: rotate(360deg); }
}

.error-icon-wrapper {
  margin-bottom: 0.25rem;
}

.state-title {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--color-text);
}

.state-subtitle {
  font-size: 0.9rem;
  color: var(--color-text-muted);
  max-width: 300px;
  line-height: 1.5;
}

.error-subtitle {
  color: var(--color-danger);
}

/* ── Zone scrollable résultat ───────────────────── */
.result-scroll {
  flex: 1;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  padding: calc(var(--safe-top) + var(--screen-pad)) var(--screen-pad) calc(var(--safe-bottom) + 1.5rem);
  display: flex;
  justify-content: center;
}

.result-container {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 1.25rem;
  width: min(100%, 520px);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-2xl);
  padding: clamp(20px, 4vw, 28px);
  box-shadow: var(--shadow-lg);
  animation: fadeIn 0.35s var(--ease-out) both;
}

/* ── Affichage dimensions ────────────────────────── */
.dimensions-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.6rem;
}

.dimensions-label {
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  font-weight: 700;
  color: var(--color-text-soft);
}

.dimensions-values {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.dim-chip {
  display: flex;
  align-items: baseline;
  gap: 0.2rem;
  background: var(--color-surface-muted);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 0.5rem 0.85rem;
}

.dim-chip-axis {
  font-size: 0.7rem;
  font-weight: 700;
  color: var(--color-text-soft);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.dim-chip-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text);
  letter-spacing: -0.02em;
  line-height: 1;
}

.dim-chip-unit {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--color-text-muted);
}

.dim-separator {
  font-size: 1.2rem;
  font-weight: 300;
  color: var(--color-text-soft);
}

/* ── Bannière erreur envoi ───────────────────────── */
.submit-error-banner {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--color-danger);
  font-size: 0.875rem;
  font-weight: 500;
  padding: 0.75rem 1rem;
  background: rgba(209, 73, 91, 0.08);
  border: 1px solid rgba(209, 73, 91, 0.2);
  border-radius: var(--radius-sm);
  line-height: 1.4;
}

/* ── Boutons d'action ────────────────────────────── */
.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  height: var(--btn-height);
  padding: 0 1.5rem;
  border-radius: 999px;
  font-size: 1rem;
  font-weight: 700;
  transition:
    transform var(--transition-fast),
    box-shadow var(--transition-fast),
    background var(--transition-fast);
}

.action-btn:active {
  transform: scale(0.97);
}

.action-btn--accent {
  background: var(--color-accent);
  color: #fff;
  box-shadow: var(--shadow-accent);
}

.action-btn--accent:hover:not(:disabled) {
  background: var(--color-accent-strong);
}

.action-btn--accent:disabled {
  opacity: 0.55;
  box-shadow: none;
  cursor: not-allowed;
}

.action-btn--full {
  width: 100%;
}

/* Spinner dans le bouton */
.btn-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.35);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.75s linear infinite;
  flex-shrink: 0;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
