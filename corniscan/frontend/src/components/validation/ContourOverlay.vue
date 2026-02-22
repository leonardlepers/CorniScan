<script setup lang="ts">
/**
 * ContourOverlay.vue — Story 4.2 (FR19)
 *
 * Affiche la photo capturée avec le contour du joint superposé en SVG.
 * Les contour_points sont normalisés [0,1] → mappés directement sur
 * viewBox="0 0 1 1" / preserveAspectRatio="none".
 */
import { computed } from 'vue'

const props = defineProps<{
  photoUrl: string
  contourPoints: number[][]
}>()

const svgPoints = computed(() =>
  props.contourPoints.map(([x, y]) => `${x},${y}`).join(' '),
)
</script>

<template>
  <div class="contour-overlay-container">
    <img :src="photoUrl" class="photo-img" alt="Photo capturée" />
    <svg
      class="contour-svg"
      viewBox="0 0 1 1"
      preserveAspectRatio="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      <polygon
        v-if="contourPoints.length >= 3"
        :points="svgPoints"
        class="contour-polygon"
      />
    </svg>
  </div>
</template>

<style scoped>
.contour-overlay-container {
  position: relative;
  display: inline-block;
  max-width: 100%;
  line-height: 0; /* évite l'espace sous l'img */
}

.photo-img {
  display: block;
  max-width: 100%;
  max-height: 60dvh;
  object-fit: contain;
}

.contour-svg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.contour-polygon {
  fill: rgba(34, 197, 94, 0.15);
  stroke: #22c55e;
  stroke-width: 0.005;
}
</style>
