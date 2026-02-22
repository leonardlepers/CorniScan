<script setup lang="ts">
/**
 * CardDetectionOverlay — Story 3.2 (FR10)
 *
 * Affiche un indicateur visuel sur le flux caméra :
 * - Vert  : carte détectée ("Carte détectée ✓")
 * - Orange : carte absente ("Carte non détectée — repositionnez-la dans le cadre")
 */
defineProps<{
  cardDetected: boolean
}>()
</script>

<template>
  <div
    :class="['detection-overlay', cardDetected ? 'detected' : 'not-detected']"
    role="status"
    :aria-label="cardDetected ? 'Carte détectée' : 'Carte non détectée'"
  >
    <span class="detection-label">
      {{ cardDetected ? 'Carte détectée ✓' : 'Carte non détectée — repositionnez-la dans le cadre' }}
    </span>
  </div>
</template>

<style scoped>
.detection-overlay {
  position: absolute;
  bottom: 6rem; /* au-dessus du futur bouton capture */
  left: 50%;
  transform: translateX(-50%);
  padding: 0.45rem 1rem;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 600;
  white-space: nowrap;
  pointer-events: none;
}

.detected {
  background: rgba(46, 125, 50, 0.85);
  color: #fff;
}

.not-detected {
  background: rgba(230, 81, 0, 0.85);
  color: #fff;
}
</style>
