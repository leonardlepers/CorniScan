<script setup lang="ts">
/**
 * IosInstallGuide.vue — Story 6.3 (FR34)
 *
 * Modale contextuelle affichant les instructions d'installation sur iOS Safari :
 *   1. Appuyer sur l'icône Partager (⬆)
 *   2. Sélectionner "Sur l'écran d'accueil" (+)
 *
 * Émis :
 *   - dismiss : l'opérateur ferme le guide
 */
defineEmits<{ dismiss: [] }>()
</script>

<template>
  <div class="ios-guide-overlay" role="dialog" aria-modal="true" aria-label="Guide d'installation">
    <!-- Backdrop tap pour fermer -->
    <div class="ios-guide-backdrop" aria-hidden="true" @click="$emit('dismiss')"></div>

    <div class="ios-guide-sheet">
      <!-- Poignée iOS -->
      <div class="sheet-handle" aria-hidden="true"></div>

      <div class="sheet-content">
        <!-- En-tête -->
        <div class="sheet-header">
          <div class="sheet-app-icon" aria-hidden="true">
            <svg width="36" height="36" viewBox="0 0 36 36" fill="none">
              <rect x="3" y="3" width="30" height="30" rx="9" fill="rgba(201,123,99,0.15)"/>
              <rect x="3" y="3" width="30" height="30" rx="9" stroke="rgba(201,123,99,0.4)" stroke-width="1.2"/>
              <path d="M9 15 L9 9 L15 9" stroke="#c97b63" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M21 9 L27 9 L27 15" stroke="#c97b63" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M9 21 L9 27 L15 27" stroke="#c97b63" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M21 27 L27 27 L27 21" stroke="#c97b63" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
              <circle cx="18" cy="18" r="3" fill="#c97b63"/>
            </svg>
          </div>
          <div>
            <h2 class="sheet-title">Installer CorniScan</h2>
            <p class="sheet-subtitle">Ajoutez l'app à votre écran d'accueil</p>
          </div>
        </div>

        <!-- Étapes -->
        <ol class="ios-guide-steps">
          <li class="ios-guide-step">
            <span class="step-number" aria-hidden="true">1</span>
            <div class="step-body">
              <p class="step-text">
                Appuyez sur
                <span class="step-icon-inline" aria-label="l'icône Partager">⬆</span>
                <strong>Partager</strong> en bas de Safari
              </p>
            </div>
          </li>
          <li class="ios-guide-step">
            <span class="step-number" aria-hidden="true">2</span>
            <div class="step-body">
              <p class="step-text">
                Faites défiler et sélectionnez<br>
                <strong>« Sur l'écran d'accueil »</strong>
              </p>
            </div>
          </li>
        </ol>

        <!-- Bouton -->
        <button class="sheet-close-btn" @click="$emit('dismiss')">
          J'ai compris
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.ios-guide-overlay {
  position: fixed;
  inset: 0;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  z-index: 1000;
  /* Anime l'entrée du backdrop */
  animation: fadeBackdrop 0.25s var(--ease-out) both;
}

@keyframes fadeBackdrop {
  from { background: rgba(16, 12, 9, 0); }
  to { background: rgba(16, 12, 9, 0.55); }
}

.ios-guide-backdrop {
  position: absolute;
  inset: 0;
  background: transparent;
}

/* ── Sheet iOS (slide-up) ───────────────────────── */
.ios-guide-sheet {
  position: relative;
  background: var(--color-surface);
  border-radius: var(--radius-2xl) var(--radius-2xl) 0 0;
  width: 100%;
  max-width: 480px;
  padding-bottom: calc(1.5rem + var(--safe-bottom));
  box-shadow: 0 -12px 48px rgba(16, 12, 9, 0.2);
  border: 1px solid var(--color-border);
  border-bottom: none;
  animation: slideUp 0.35s var(--ease-spring) both;
}

@keyframes slideUp {
  from { transform: translateY(100%); opacity: 0.8; }
  to { transform: translateY(0); opacity: 1; }
}

/* Poignée style iOS */
.sheet-handle {
  width: 36px;
  height: 5px;
  border-radius: 3px;
  background: var(--color-border-strong);
  margin: 0.75rem auto 0;
}

.sheet-content {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  padding: 1.25rem 1.5rem 0;
}

/* ── En-tête ────────────────────────────────────── */
.sheet-header {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.sheet-app-icon {
  flex-shrink: 0;
}

.sheet-title {
  font-size: 1.15rem;
  font-weight: 800;
  color: var(--color-text);
  margin: 0;
  letter-spacing: -0.01em;
  line-height: 1.2;
}

.sheet-subtitle {
  font-size: 0.85rem;
  color: var(--color-text-muted);
  margin: 0.15rem 0 0;
}

/* ── Étapes ─────────────────────────────────────── */
.ios-guide-steps {
  display: flex;
  flex-direction: column;
  gap: 0;
  padding: 0;
  list-style: none;
  margin: 0;
  background: var(--color-surface-muted);
  border-radius: var(--radius-lg);
  overflow: hidden;
  border: 1px solid var(--color-border);
}

.ios-guide-step {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  padding: 1rem 1.1rem;
}

.ios-guide-step + .ios-guide-step {
  border-top: 1px solid var(--color-border);
}

.step-number {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--color-accent-soft);
  color: var(--color-accent-strong);
  font-size: 0.8rem;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.step-body {
  flex: 1;
}

.step-text {
  font-size: 0.9rem;
  color: var(--color-text);
  line-height: 1.5;
  margin: 0;
}

.step-icon-inline {
  display: inline-block;
  margin: 0 0.1em;
  font-size: 0.95em;
}

/* ── Bouton fermeture ───────────────────────────── */
.sheet-close-btn {
  height: var(--btn-height);
  background: var(--color-accent);
  color: #fff;
  border-radius: 999px;
  font-size: 1rem;
  font-weight: 700;
  width: 100%;
  box-shadow: var(--shadow-accent);
  transition: transform var(--transition-fast), background var(--transition-fast);
}

.sheet-close-btn:active {
  transform: scale(0.97);
  background: var(--color-accent-strong);
}
</style>
