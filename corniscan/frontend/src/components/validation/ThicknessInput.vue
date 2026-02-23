<script setup lang="ts">
/**
 * ThicknessInput.vue — Story 4.3 (FR21, FR22, FR23)
 *
 * FR21 : champ de saisie numérique pour l'épaisseur du joint (en mm)
 * FR22 : avertissement calibration insuffisante si calibrationWarning = true
 * FR23 : boutons "Recommencer la photo" et "Forcer l'envoi" si avertissement visible
 */
import { ref } from 'vue'

defineProps<{
  calibrationWarning: boolean
}>()

const emit = defineEmits<{
  'update:thickness': [value: number | null]
  retake: []
  'force-send': []
}>()

const rawValue = ref('')

function onInput() {
  const parsed = parseFloat(rawValue.value)
  emit('update:thickness', isNaN(parsed) || parsed < 0 ? null : parsed)
}
</script>

<template>
  <div class="thickness-input-container">
    <!-- Champ épaisseur (FR21) -->
    <div class="thickness-field">
      <label for="thickness-input" class="thickness-label">Épaisseur du joint (mm)</label>
      <div class="thickness-input-wrapper">
        <input
          id="thickness-input"
          v-model="rawValue"
          type="number"
          min="0"
          step="0.1"
          class="thickness-input"
          placeholder="0.0"
          inputmode="decimal"
          @input="onInput"
        />
        <span class="thickness-unit" aria-hidden="true">mm</span>
      </div>
    </div>

    <!-- Avertissement calibration insuffisante (FR22) -->
    <div v-if="calibrationWarning" class="calibration-warning" role="alert">
      <div class="warning-header">
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true">
          <path d="M9 2L16.5 15H1.5L9 2z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
          <path d="M9 7v4M9 13h.01" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
        <p class="warning-title">Calibration insuffisante</p>
      </div>
      <p class="warning-text">
        Moins de 4 coins de la carte détectés. Recommencez avec la carte entièrement visible.
      </p>
      <!-- Deux actions (FR23) -->
      <div class="warning-actions">
        <button class="warn-btn warn-btn--secondary" @click="emit('retake')">
          Recommencer la photo
        </button>
        <button class="warn-btn warn-btn--primary" @click="emit('force-send')">
          Envoyer quand même
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.thickness-input-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
}

/* ── Champ épaisseur ────────────────────────────── */
.thickness-field {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.thickness-label {
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  font-weight: 700;
  color: var(--color-text-soft);
}

.thickness-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.thickness-input {
  height: var(--input-height);
  padding: 0 3.5rem 0 1rem;
  background: var(--color-surface-muted);
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text);
  font-size: 1.2rem;
  font-weight: 600;
  text-align: center;
  width: 100%;
  transition:
    border-color var(--transition-fast),
    box-shadow var(--transition-fast),
    background var(--transition-fast);
}

.thickness-input:focus {
  outline: none;
  border-color: var(--color-accent);
  box-shadow: 0 0 0 4px rgba(201, 123, 99, 0.15);
  background: var(--color-surface);
}

/* Supprime les flèches natives du input number sur iOS/Chrome */
.thickness-input::-webkit-inner-spin-button,
.thickness-input::-webkit-outer-spin-button {
  -webkit-appearance: none;
}

.thickness-unit {
  position: absolute;
  right: 1rem;
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--color-text-soft);
  pointer-events: none;
  user-select: none;
}

/* ── Avertissement calibration ──────────────────── */
.calibration-warning {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 1rem 1.1rem;
  background: rgba(194, 123, 58, 0.08);
  border: 1.5px solid rgba(194, 123, 58, 0.3);
  border-radius: var(--radius-md);
  animation: slideIn 0.25s var(--ease-out) both;
}

@keyframes slideIn {
  from { opacity: 0; transform: translateY(-6px); }
  to { opacity: 1; transform: translateY(0); }
}

.warning-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #9a5c15;
}

.warning-title {
  font-size: 0.9rem;
  font-weight: 700;
  color: #9a5c15;
  margin: 0;
}

.warning-text {
  color: #7a4a10;
  font-size: 0.875rem;
  line-height: 1.5;
  margin: 0;
}

.warning-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.warn-btn {
  height: var(--btn-height-sm);
  padding: 0 1rem;
  border-radius: 999px;
  font-size: 0.875rem;
  font-weight: 700;
  transition: transform var(--transition-fast), opacity var(--transition-fast);
}

.warn-btn:active {
  transform: scale(0.96);
}

.warn-btn--secondary {
  background: var(--color-surface);
  color: var(--color-text);
  border: 1.5px solid var(--color-border-strong);
}

.warn-btn--primary {
  background: var(--color-warning);
  color: #fff;
  border: none;
}
</style>
