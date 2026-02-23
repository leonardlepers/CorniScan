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
    <label class="checklist-item" :class="{ 'checklist-item--checked': jointClean }">
      <span class="checklist-box" :class="{ 'checklist-box--checked': jointClean }">
        <svg v-if="jointClean" width="12" height="12" viewBox="0 0 12 12" fill="none" aria-hidden="true">
          <path d="M2 6l3 3 5-5" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </span>
      <input
        v-model="jointClean"
        type="checkbox"
        class="checklist-sr-only"
        aria-label="Joint propre"
      />
      <span class="checklist-label">Joint propre</span>
    </label>

    <label class="checklist-item" :class="{ 'checklist-item--checked': cardVisible }">
      <span class="checklist-box" :class="{ 'checklist-box--checked': cardVisible }">
        <svg v-if="cardVisible" width="12" height="12" viewBox="0 0 12 12" fill="none" aria-hidden="true">
          <path d="M2 6l3 3 5-5" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </span>
      <input
        v-model="cardVisible"
        type="checkbox"
        class="checklist-sr-only"
        aria-label="Carte entièrement visible"
      />
      <span class="checklist-label">Carte entièrement visible</span>
    </label>
  </div>
</template>

<style scoped>
.capture-checklist {
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
  width: 100%;
  max-width: 320px;
}

/* ── Item de checklist ──────────────────────────── */
.checklist-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  user-select: none;
  /* Zone de tap généreuse — iOS HIG */
  min-height: 44px;
  padding: 0.3rem 0;
  transition: opacity var(--transition-fast);
}

.checklist-item:active {
  opacity: 0.7;
}

/* ── Checkbox custom ────────────────────────────── */
.checklist-box {
  width: 24px;
  height: 24px;
  border-radius: 7px;
  border: 2px solid rgba(255, 255, 255, 0.4);
  background: rgba(255, 255, 255, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition:
    background var(--transition-fast),
    border-color var(--transition-fast),
    transform var(--transition-fast);
}

.checklist-box--checked {
  background: var(--color-success);
  border-color: var(--color-success);
  transform: scale(1.05);
}

/* Masquer le vrai checkbox mais le garder accessible */
.checklist-sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
}

/* ── Label texte ────────────────────────────────── */
.checklist-label {
  color: rgba(247, 241, 234, 0.9);
  font-size: 0.9rem;
  font-weight: 500;
  line-height: 1.3;
}

.checklist-item--checked .checklist-label {
  color: rgba(247, 241, 234, 0.65);
}
</style>
