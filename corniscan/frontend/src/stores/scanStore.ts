/**
 * scanStore — Store Pinia du pipeline de scan
 *
 * Story 1.1 : squelette avec pattern isLoading + error + hasPhoto
 * Story 3.4 : photo (File) capturée
 * Story 4.x : contour (points[]), dimensions ({width, height, thickness})
 *
 * CONVENTION ARCHITECTURE : hasPhoto est le guard utilisé par requirePhoto (Vue Router)
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useScanStore = defineStore('scan', () => {
  // TODO Story 3.4: photo = ref<File | null>(null)
  // TODO Story 4.x: contour = ref<number[][]>([]), dimensions = ref<{width: number, height: number} | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Guard utilisé par requirePhoto dans Vue Router — Story 3.4 remplacera par: photo.value !== null
  const hasPhoto = computed(() => false)

  return { isLoading, error, hasPhoto }
})
