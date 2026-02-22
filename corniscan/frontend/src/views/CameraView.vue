<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import AppHeader from '@/components/AppHeader.vue'
import { useMediaDevices } from '@/composables/useMediaDevices'

const route = useRoute()

// AC#1 Story 2.4 — message d'accès refusé si redirigé depuis une route admin
const showForbiddenAlert = ref(route.query.forbidden === '1')

function dismissAlert() {
  showForbiddenAlert.value = false
}

// Story 3.1 — flux caméra
const { videoRef, isLoading, error, startCamera } = useMediaDevices()

onMounted(startCamera)
</script>

<template>
  <!-- AC#4 — plein écran (overflow masqué, hauteur viewport) -->
  <div class="camera-page">
    <AppHeader />

    <!-- Alerte accès refusé (Story 2.4) -->
    <div
      v-if="showForbiddenAlert"
      class="forbidden-alert"
      role="alert"
    >
      <span>Accès refusé. Cette section est réservée aux administrateurs.</span>
      <button class="dismiss-btn" aria-label="Fermer" @click="dismissAlert">✕</button>
    </div>

    <!-- Conteneur flux caméra -->
    <div class="camera-container">
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
</style>
