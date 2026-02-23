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
    <!-- Indicateur dot -->
    <span class="detection-dot" aria-hidden="true"></span>
    <span class="detection-label">
      {{ cardDetected ? 'Carte détectée' : 'Carte non détectée — repositionnez' }}
    </span>
  </div>
</template>

<style scoped>
.detection-overlay {
  position: absolute;
  top: 1.25rem;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 600;
  white-space: nowrap;
  pointer-events: none;
  letter-spacing: 0.01em;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  transition:
    background var(--transition-base),
    box-shadow var(--transition-base);
}

.detection-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.detected {
  background: rgba(20, 90, 70, 0.82);
  color: #fff;
  box-shadow: 0 4px 16px rgba(31, 138, 106, 0.3);
}

.detected .detection-dot {
  background: #4ae8b4;
  box-shadow: 0 0 6px rgba(74, 232, 180, 0.7);
  animation: pulse-green 1.8s ease-in-out infinite;
}

.not-detected {
  background: rgba(100, 50, 30, 0.82);
  color: rgba(255, 240, 230, 0.95);
  box-shadow: 0 4px 16px rgba(201, 123, 99, 0.25);
}

.not-detected .detection-dot {
  background: #e8894a;
  box-shadow: 0 0 6px rgba(232, 137, 74, 0.6);
}

@keyframes pulse-green {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(0.85); }
}
</style>
