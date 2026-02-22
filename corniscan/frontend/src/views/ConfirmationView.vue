<script setup lang="ts">
/**
 * ConfirmationView.vue — Story 5.3 (FR28)
 *
 * AC#1 : Message succès + destinataire info@cornille-sa.com.
 * AC#2 : Récapitulatif dimensions + épaisseur depuis scanStore.
 * AC#3 : Bouton "Nouveau scan" → clearPhoto + clearResult + /camera.
 */
import { useRouter } from 'vue-router'
import { useScanStore } from '@/stores/scanStore'

const router = useRouter()
const scanStore = useScanStore()

function handleNewScan(): void {
  scanStore.clearResult()
  scanStore.clearPhoto()
  router.push({ name: 'camera' })
}
</script>

<template>
  <div class="confirmation-page">
    <!-- AC#1 — Message succès + destinataire -->
    <div class="success-header">
      <p class="success-title">Scan envoyé avec succès !</p>
      <p class="success-recipient">Transmis à <strong>info@cornille-sa.com</strong></p>
    </div>

    <!-- AC#2 — Récapitulatif du scan -->
    <div v-if="scanStore.dimensions" class="summary-card">
      <h2 class="summary-title">Récapitulatif</h2>
      <dl class="summary-list">
        <div class="summary-row">
          <dt class="summary-label">Largeur</dt>
          <dd class="summary-value">{{ scanStore.dimensions.width_mm.toFixed(1) }} mm</dd>
        </div>
        <div class="summary-row">
          <dt class="summary-label">Hauteur</dt>
          <dd class="summary-value">{{ scanStore.dimensions.height_mm.toFixed(1) }} mm</dd>
        </div>
        <div class="summary-row">
          <dt class="summary-label">Épaisseur</dt>
          <dd class="summary-value">
            {{ scanStore.thickness !== null ? `${scanStore.thickness} mm` : 'N/A' }}
          </dd>
        </div>
      </dl>
    </div>

    <!-- AC#3 — Bouton nouveau scan -->
    <button class="new-scan-btn" @click="handleNewScan">Nouveau scan</button>
  </div>
</template>

<style scoped>
.confirmation-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100dvh;
  background: #111;
  color: #fff;
  font-family: sans-serif;
  gap: 2rem;
  padding: 1.5rem;
}

.success-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  text-align: center;
}

.success-title {
  font-size: 1.5rem;
  font-weight: 700;
}

.success-recipient {
  font-size: 0.95rem;
  opacity: 0.8;
}

.summary-card {
  background: rgba(255, 255, 255, 0.07);
  border-radius: 12px;
  padding: 1.25rem 2rem;
  width: 100%;
  max-width: 360px;
}

.summary-title {
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  opacity: 0.6;
  margin: 0 0 0.75rem;
}

.summary-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin: 0;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.summary-label {
  font-size: 0.9rem;
  opacity: 0.75;
}

.summary-value {
  font-size: 1rem;
  font-weight: 600;
}

.new-scan-btn {
  padding: 0.875rem 2rem;
  background: #fff;
  color: #111;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  width: 100%;
  max-width: 360px;
}
</style>
