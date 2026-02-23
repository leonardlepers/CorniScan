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
    <div class="confirmation-content">
      <!-- Icône succès animée -->
      <div class="success-icon-wrapper" aria-hidden="true">
        <svg class="success-circle" width="80" height="80" viewBox="0 0 80 80" fill="none">
          <!-- Cercle de fond -->
          <circle cx="40" cy="40" r="36" fill="rgba(31,138,106,0.1)"/>
          <!-- Cercle animé -->
          <circle
            cx="40" cy="40" r="36"
            stroke="var(--color-success)"
            stroke-width="2.5"
            stroke-linecap="round"
            stroke-dasharray="226"
            stroke-dashoffset="226"
            class="circle-draw"
          />
          <!-- Checkmark animé -->
          <path
            d="M24 40l11 11 21-22"
            stroke="var(--color-success)"
            stroke-width="3.5"
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-dasharray="50"
            stroke-dashoffset="50"
            class="check-draw"
          />
        </svg>
      </div>

      <!-- AC#1 — Message succès + destinataire -->
      <div class="success-header">
        <h1 class="success-title">Scan envoyé !</h1>
        <p class="success-recipient">
          Transmis à <strong>info@cornille-sa.com</strong>
        </p>
      </div>

      <!-- AC#2 — Récapitulatif du scan -->
      <div v-if="scanStore.dimensions" class="summary-card">
        <p class="summary-heading">Récapitulatif</p>
        <dl class="summary-list">
          <div class="summary-row">
            <dt class="summary-label">Largeur</dt>
            <dd class="summary-value">{{ scanStore.dimensions.width_mm.toFixed(1) }} mm</dd>
          </div>
          <div class="summary-divider" aria-hidden="true"></div>
          <div class="summary-row">
            <dt class="summary-label">Hauteur</dt>
            <dd class="summary-value">{{ scanStore.dimensions.height_mm.toFixed(1) }} mm</dd>
          </div>
          <div class="summary-divider" aria-hidden="true"></div>
          <div class="summary-row">
            <dt class="summary-label">Épaisseur</dt>
            <dd class="summary-value">
              {{ scanStore.thickness !== null ? `${scanStore.thickness} mm` : 'N/A' }}
            </dd>
          </div>
        </dl>
      </div>

      <!-- AC#3 — Bouton nouveau scan -->
      <button class="new-scan-btn" @click="handleNewScan">
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true">
          <path d="M4 4h3.5M4 4v3.5M14 14h-3.5M14 14v-3.5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <path d="M4 14h3.5M4 14v-3.5M14 4h-3.5M14 4v3.5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
        Nouveau scan
      </button>
    </div>
  </div>
</template>

<style scoped>
.confirmation-page {
  min-height: 100dvh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding:
    calc(var(--safe-top) + var(--screen-pad))
    calc(var(--safe-right) + var(--screen-pad))
    calc(var(--safe-bottom) + var(--screen-pad))
    calc(var(--safe-left) + var(--screen-pad));
}

.confirmation-content {
  width: min(100%, var(--card-max));
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.75rem;
  animation: fadeInUp 0.45s var(--ease-out) both;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ── Icône succès ────────────────────────────────── */
.success-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Cercle qui se dessine */
.circle-draw {
  animation: drawCircle 0.6s var(--ease-out) 0.1s both;
}

@keyframes drawCircle {
  to { stroke-dashoffset: 0; }
}

/* Checkmark qui se dessine après le cercle */
.check-draw {
  animation: drawCheck 0.4s var(--ease-out) 0.65s both;
}

@keyframes drawCheck {
  to { stroke-dashoffset: 0; }
}

/* ── Header succès ───────────────────────────────── */
.success-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.35rem;
  text-align: center;
}

.success-title {
  font-size: 2rem;
  font-weight: 800;
  color: var(--color-text);
  letter-spacing: -0.025em;
  line-height: 1.1;
}

.success-recipient {
  font-size: 0.9rem;
  color: var(--color-text-muted);
  line-height: 1.5;
}

/* ── Carte récapitulatif ─────────────────────────── */
.summary-card {
  background: var(--color-surface);
  border-radius: var(--radius-2xl);
  padding: 1.4rem 1.6rem;
  width: 100%;
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-md);
  animation: fadeInUp 0.45s var(--ease-out) 0.15s both;
}

.summary-heading {
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  font-weight: 700;
  color: var(--color-text-soft);
  margin-bottom: 0.85rem;
}

.summary-list {
  display: flex;
  flex-direction: column;
  margin: 0;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.7rem 0;
}

.summary-divider {
  height: 1px;
  background: var(--color-border);
}

.summary-label {
  font-size: 0.9rem;
  color: var(--color-text-muted);
  font-weight: 500;
}

.summary-value {
  font-size: 1rem;
  font-weight: 700;
  color: var(--color-text);
  letter-spacing: -0.01em;
}

/* ── Bouton nouveau scan ─────────────────────────── */
.new-scan-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.6rem;
  height: var(--btn-height);
  padding: 0 2rem;
  background: var(--color-accent);
  color: #fff;
  border-radius: 999px;
  font-size: 1rem;
  font-weight: 700;
  width: 100%;
  box-shadow: var(--shadow-accent);
  transition:
    transform var(--transition-fast),
    box-shadow var(--transition-fast),
    background var(--transition-fast);
  animation: fadeInUp 0.45s var(--ease-out) 0.25s both;
}

.new-scan-btn:active {
  transform: scale(0.97);
  box-shadow: 0 6px 16px rgba(201, 123, 99, 0.2);
}

.new-scan-btn:hover {
  background: var(--color-accent-strong);
}
</style>
