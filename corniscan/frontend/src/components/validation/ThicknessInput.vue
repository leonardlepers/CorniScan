<script setup lang="ts">
/**
 * ThicknessInput.vue — Story 4.3 (FR21, FR22, FR23)
 *
 * FR21 : champ de saisie numérique pour l'épaisseur du joint (en mm)
 * FR22 : avertissement calibration insuffisante si calibrationWarning = true
 * FR23 : boutons "Recommencer la photo" et "Forcer l'envoi" si avertissement visible
 */
import { ref } from 'vue'

const props = defineProps<{
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
      <input
        id="thickness-input"
        v-model="rawValue"
        type="number"
        min="0"
        step="0.1"
        class="thickness-input"
        placeholder="0.0"
        @input="onInput"
      />
    </div>

    <!-- Avertissement calibration insuffisante (FR22) -->
    <div v-if="calibrationWarning" class="calibration-warning">
      <p class="warning-text">
        Calibration insuffisante — moins de 4 coins de la carte détectés.
        Recommencez avec la carte entièrement visible.
      </p>
      <!-- Deux actions (FR23) -->
      <div class="warning-actions">
        <button class="retake-btn" @click="emit('retake')">Recommencer la photo</button>
        <button class="force-send-btn" @click="emit('force-send')">
          Forcer l'envoi malgré l'avertissement
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
  max-width: 360px;
}

.thickness-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.thickness-label {
  font-size: 0.875rem;
  opacity: 0.8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.thickness-input {
  padding: 0.75rem 1rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.25);
  border-radius: 8px;
  color: #fff;
  font-size: 1.125rem;
  text-align: center;
  width: 100%;
  box-sizing: border-box;
}

.thickness-input:focus {
  outline: none;
  border-color: rgba(255, 255, 255, 0.6);
}

.calibration-warning {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 1rem;
  background: rgba(234, 179, 8, 0.15);
  border: 1px solid rgba(234, 179, 8, 0.5);
  border-radius: 8px;
}

.warning-text {
  color: #fde047;
  font-size: 0.9rem;
  line-height: 1.5;
  margin: 0;
}

.warning-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.retake-btn,
.force-send-btn {
  padding: 0.6rem 1rem;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
}

.retake-btn {
  background: #fff;
  color: #111;
}

.force-send-btn {
  background: rgba(234, 179, 8, 0.3);
  color: #fde047;
  border: 1px solid rgba(234, 179, 8, 0.5);
}
</style>
