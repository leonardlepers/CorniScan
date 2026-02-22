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
      <h1>CorniScan</h1>
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
  min-height: 100vh;
  background: #f5f5f5;
  font-family: sans-serif;
}

.change-password-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.12);
  padding: 2rem;
  width: 100%;
  max-width: 400px;
}

h1 {
  margin: 0 0 0.25rem;
  font-size: 1.5rem;
  text-align: center;
}

.subtitle {
  font-size: 0.875rem;
  color: #555;
  text-align: center;
  margin: 0 0 1.5rem;
}

.change-password-form {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #333;
}

input {
  padding: 0.6rem 0.75rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 1rem;
  margin-bottom: 0.5rem;
}

input:focus {
  outline: none;
  border-color: #4a6cf7;
  box-shadow: 0 0 0 2px rgba(74, 108, 247, 0.2);
}

.error-msg {
  color: #d32f2f;
  font-size: 0.875rem;
  margin: 0;
}

button {
  padding: 0.7rem;
  background: #4a6cf7;
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  margin-top: 0.5rem;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
