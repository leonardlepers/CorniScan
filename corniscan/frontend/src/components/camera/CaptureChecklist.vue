<script setup lang="ts">
/**
 * CaptureChecklist — Story 3.3
 *
 * Checklist qualité 2 items avant capture.
 * Émet `update:allChecked: boolean` à chaque changement d'état (+ immédiatement au montage).
 */
import { computed, ref, watch } from 'vue'

const emit = defineEmits<{
  'update:allChecked': [value: boolean]
}>()

const jointClean = ref(false)
const cardVisible = ref(false)

const allChecked = computed(() => jointClean.value && cardVisible.value)

watch(
  allChecked,
  (value) => {
    emit('update:allChecked', value)
  },
  { immediate: true },
)
</script>

<template>
  <div class="capture-checklist">
    <label class="checklist-item">
      <input
        v-model="jointClean"
        type="checkbox"
        class="checklist-checkbox"
      />
      <span>Joint propre</span>
    </label>
    <label class="checklist-item">
      <input
        v-model="cardVisible"
        type="checkbox"
        class="checklist-checkbox"
      />
      <span>Carte entièrement visible</span>
    </label>
  </div>
</template>

<style scoped>
.capture-checklist {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  width: 100%;
}

.checklist-item {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  color: #fff;
  font-size: 0.9rem;
  cursor: pointer;
  user-select: none;
}

.checklist-checkbox {
  width: 1.1rem;
  height: 1.1rem;
  cursor: pointer;
  accent-color: #4a6cf7;
}
</style>
