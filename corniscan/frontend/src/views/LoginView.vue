<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const authStore = useAuthStore()
const router = useRouter()

const username = ref('')
const password = ref('')

async function handleSubmit() {
  try {
    const user = await authStore.login(username.value, password.value)
    if (user.force_password_change) {
      router.push('/change-password')
    } else {
      router.push('/camera')
    }
  } catch {
    // L'erreur est déjà stockée dans authStore.error
  }
}
</script>

<template>
  <main class="login-page">
    <div class="login-card">
      <h1>CorniScan</h1>

      <form class="login-form" @submit.prevent="handleSubmit">
        <label for="username">Nom d'utilisateur</label>
        <input
          id="username"
          v-model="username"
          type="text"
          autocomplete="username"
          required
          :disabled="authStore.isLoading"
          placeholder="Nom d'utilisateur"
        />

        <label for="password">Mot de passe</label>
        <input
          id="password"
          v-model="password"
          type="password"
          autocomplete="current-password"
          required
          :disabled="authStore.isLoading"
          placeholder="Mot de passe"
        />

        <p v-if="authStore.error" class="error-msg" role="alert">
          {{ authStore.error }}
        </p>

        <button type="submit" :disabled="authStore.isLoading">
          {{ authStore.isLoading ? 'Connexion…' : 'Se connecter' }}
        </button>
      </form>
    </div>
  </main>
</template>

<style scoped>
.login-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: #f5f5f5;
  font-family: sans-serif;
}

.login-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.12);
  padding: 2rem;
  width: 100%;
  max-width: 360px;
}

h1 {
  margin: 0 0 1.5rem;
  font-size: 1.5rem;
  text-align: center;
}

.login-form {
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
