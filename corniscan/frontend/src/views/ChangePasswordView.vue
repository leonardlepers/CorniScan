<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { apiCall } from '@/services/apiClient'
import { useAuthStore, type User } from '@/stores/authStore'

const authStore = useAuthStore()
const router = useRouter()

const currentPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const isLoading = ref(false)
const error = ref<string | null>(null)

async function handleSubmit() {
  error.value = null

  // AC#5 — Validation client : mots de passe identiques (sans appel backend)
  if (newPassword.value !== confirmPassword.value) {
    error.value = 'Les mots de passe ne correspondent pas.'
    return
  }

  isLoading.value = true
  try {
    const data = await apiCall<{ access_token: string; token_type: string; user: User }>(
      '/api/v1/auth/change-password',
      {
        method: 'POST',
        body: JSON.stringify({
          current_password: currentPassword.value,
          new_password: newPassword.value,
        }),
      },
    )
    // Mettre à jour le store avec le nouveau JWT (force_password_change=false)
    authStore.updateAuth(data.access_token, data.user)
    router.push('/camera')
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : 'Erreur inattendue'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <main class="change-password-page">
    <div class="change-password-card">
      <div class="brand-block">
        <p class="brand-kicker">Sécurisation du compte</p>
        <h1>CorniScan</h1>
      </div>
      <p class="subtitle">Veuillez choisir un nouveau mot de passe pour sécuriser votre compte.</p>

      <form class="change-password-form" @submit.prevent="handleSubmit">
        <label for="current-password">Mot de passe actuel</label>
        <input
          id="current-password"
          v-model="currentPassword"
          type="password"
          autocomplete="current-password"
          required
          :disabled="isLoading"
          placeholder="Mot de passe actuel"
        />

        <label for="new-password">Nouveau mot de passe</label>
        <input
          id="new-password"
          v-model="newPassword"
          type="password"
          autocomplete="new-password"
          required
          :disabled="isLoading"
          placeholder="Nouveau mot de passe"
        />

        <label for="confirm-password">Confirmer le nouveau mot de passe</label>
        <input
          id="confirm-password"
          v-model="confirmPassword"
          type="password"
          autocomplete="new-password"
          required
          :disabled="isLoading"
          placeholder="Confirmer le nouveau mot de passe"
        />

        <p v-if="error" class="error-msg" role="alert">{{ error }}</p>

        <button type="submit" :disabled="isLoading">
          {{ isLoading ? 'Enregistrement…' : 'Changer le mot de passe' }}
        </button>
      </form>
    </div>
  </main>
</template>

<style scoped>
.change-password-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100dvh;
  padding: calc(var(--safe-top) + var(--screen-pad)) var(--screen-pad)
    calc(var(--safe-bottom) + var(--screen-pad));
}

.change-password-card {
  width: min(100%, 460px);
  background: var(--color-surface);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
  padding: clamp(24px, 6vw, 36px);
  border: 1px solid var(--color-border);
}

.brand-block {
  margin-bottom: 0.8rem;
}

.brand-kicker {
  text-transform: uppercase;
  letter-spacing: 0.2em;
  font-size: 0.65rem;
  font-weight: 600;
  color: var(--color-text-soft);
  margin-bottom: 0.35rem;
}

h1 {
  margin: 0;
  font-size: 1.6rem;
  font-weight: 700;
}

.subtitle {
  font-size: 0.9rem;
  color: var(--color-text-muted);
  margin: 0 0 1.5rem;
}

.change-password-form {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-text);
}

input {
  padding: 0.8rem 0.9rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-surface-muted);
  font-size: 1rem;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

input:focus {
  outline: none;
  border-color: rgba(201, 123, 99, 0.6);
  box-shadow: 0 0 0 3px rgba(201, 123, 99, 0.2);
}

.error-msg {
  color: var(--color-danger);
  font-size: 0.85rem;
  margin: 0.2rem 0 0;
}

button {
  margin-top: 0.75rem;
  padding: 0.85rem 1rem;
  background: var(--color-accent);
  color: #fff;
  border-radius: 999px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
