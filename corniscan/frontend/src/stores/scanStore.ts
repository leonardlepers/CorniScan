/**
 * scanStore — Store Pinia du pipeline de scan
 *
 * Story 1.1 : squelette avec pattern isLoading + error
 * Story 3.4 : photo (File) capturée + hasPhoto + setPhoto + clearPhoto
 * Story 4.1 : contour (points normalisés), dimensions (mm), calibrationWarning
 *             setResult() + clearResult()
 * Story 4.3 : thickness (mm saisi manuellement) + setThickness()
 *
 * CONVENTION ARCHITECTURE : hasPhoto est le guard utilisé par requirePhoto (Vue Router)
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface ScanDimensions {
  width_mm: number
  height_mm: number
}

export interface ProcessResult {
  contour_points: number[][]
  dimensions: ScanDimensions
  calibration_warning: boolean
}

export const useScanStore = defineStore('scan', () => {
  // Story 3.4: photo capturée depuis l'écran caméra
  const photo = ref<File | null>(null)

  // Story 4.1: résultat d'analyse retourné par /scan/process
  const contour = ref<number[][]>([])
  const dimensions = ref<ScanDimensions | null>(null)
  const calibrationWarning = ref(false)

  // Story 4.3: épaisseur du joint saisie manuellement par l'opérateur (mm)
  const thickness = ref<number | null>(null)

  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Guard utilisé par requirePhoto dans Vue Router (Story 3.4)
  const hasPhoto = computed(() => photo.value !== null)

  function setPhoto(file: File): void {
    photo.value = file
  }

  function clearPhoto(): void {
    photo.value = null
  }

  function setResult(result: ProcessResult): void {
    contour.value = result.contour_points
    dimensions.value = result.dimensions
    calibrationWarning.value = result.calibration_warning
  }

  function setThickness(value: number | null): void {
    thickness.value = value
  }

  function clearResult(): void {
    contour.value = []
    dimensions.value = null
    calibrationWarning.value = false
    thickness.value = null
  }

  return {
    isLoading,
    error,
    photo,
    hasPhoto,
    setPhoto,
    clearPhoto,
    contour,
    dimensions,
    calibrationWarning,
    thickness,
    setResult,
    setThickness,
    clearResult,
  }
})
