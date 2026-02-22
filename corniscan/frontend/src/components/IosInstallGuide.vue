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
    <div class="ios-guide-card">
      <h2 class="ios-guide-title">Installer CorniScan</h2>
      <p class="ios-guide-intro">
        Pour ajouter CorniScan à votre écran d'accueil depuis Safari :
      </p>
      <ol class="ios-guide-steps">
        <li class="ios-guide-step">
          <span class="ios-guide-icon" aria-hidden="true">⬆</span>
          Appuyez sur l'icône <strong>Partager</strong> en bas de l'écran
        </li>
        <li class="ios-guide-step">
          <span class="ios-guide-icon" aria-hidden="true">＋</span>
          Sélectionnez <strong>« Sur l'écran d'accueil »</strong>
        </li>
      </ol>
      <button class="ios-guide-close" @click="$emit('dismiss')">J'ai compris</button>
    </div>
  </div>
</template>

<style scoped>
.ios-guide-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.65);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.ios-guide-card {
  background: #1c1c1e;
  color: #fff;
  border-radius: 16px;
  padding: 1.5rem;
  width: 100%;
  max-width: 400px;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.ios-guide-title {
  font-size: 1.125rem;
  font-weight: 700;
  margin: 0;
}

.ios-guide-intro {
  font-size: 0.9rem;
  opacity: 0.8;
  margin: 0;
}

.ios-guide-steps {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding-left: 0;
  list-style: none;
  margin: 0;
}

.ios-guide-step {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.95rem;
  line-height: 1.4;
}

.ios-guide-icon {
  font-size: 1.25rem;
  width: 2rem;
  text-align: center;
  flex-shrink: 0;
}

.ios-guide-close {
  background: #fff;
  color: #111;
  border: none;
  border-radius: 10px;
  padding: 0.75rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  width: 100%;
}
</style>
