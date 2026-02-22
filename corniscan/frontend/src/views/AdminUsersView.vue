<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { apiCall } from '@/services/apiClient'
import { useAuthStore } from '@/stores/authStore'
import AppHeader from '@/components/AppHeader.vue'

const authStore = useAuthStore()

interface UserRow {
  username: string
  role: string
  is_active: boolean
  created_at: string | null
  force_password_change: boolean
}

// ── Liste ──────────────────────────────────────────────────────────────────
const users = ref<UserRow[]>([])
const isLoading = ref(false)
const error = ref<string | null>(null)

async function loadUsers() {
  isLoading.value = true
  error.value = null
  try {
    users.value = await apiCall<UserRow[]>('/api/v1/admin/users')
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : 'Erreur inattendue'
  } finally {
    isLoading.value = false
  }
}

function formatDate(iso: string | null): string {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })
}

// ── Formulaire de création (Story 2.2) ────────────────────────────────────
const newUsername = ref('')
const newPassword = ref('')
const createError = ref<string | null>(null)
const createSuccess = ref<string | null>(null)
const isCreating = ref(false)

// AC#4 — validation frontend : champs non vides
const formErrors = ref<{ username?: string; password?: string }>({})

function validateForm(): boolean {
  formErrors.value = {}
  if (!newUsername.value.trim()) {
    formErrors.value.username = "Le nom d'utilisateur est requis."
  }
  if (!newPassword.value) {
    formErrors.value.password = 'Le mot de passe est requis.'
  }
  return Object.keys(formErrors.value).length === 0
}

async function handleCreate() {
  createError.value = null
  createSuccess.value = null

  if (!validateForm()) return

  isCreating.value = true
  try {
    const created = await apiCall<UserRow>('/api/v1/admin/users', {
      method: 'POST',
      body: JSON.stringify({ username: newUsername.value.trim(), password: newPassword.value }),
    })
    createSuccess.value = `Compte « ${created.username} » créé avec succès.`
    newUsername.value = ''
    newPassword.value = ''
    formErrors.value = {}
    // Recharger la liste
    await loadUsers()
  } catch (e: unknown) {
    createError.value = e instanceof Error ? e.message : 'Erreur inattendue'
  } finally {
    isCreating.value = false
  }
}

// ── Désactivation (Story 2.3) ─────────────────────────────────────────────
const deactivateError = ref<string | null>(null)
const deactivating = ref<string | null>(null) // username en cours de désactivation

async function handleDeactivate(username: string) {
  deactivateError.value = null
  deactivating.value = username
  try {
    await apiCall(`/api/v1/admin/users/${encodeURIComponent(username)}/deactivate`, {
      method: 'PATCH',
    })
    await loadUsers()
  } catch (e: unknown) {
    deactivateError.value = e instanceof Error ? e.message : 'Erreur inattendue'
  } finally {
    deactivating.value = null
  }
}

onMounted(loadUsers)
</script>

<template>
  <div class="admin-users-page">
    <AppHeader />
    <main class="admin-users-content">
    <div class="admin-users-card">
      <h1>Gestion des comptes</h1>

      <!-- Formulaire de création -->
      <section class="create-section">
        <h2>Créer un compte opérateur</h2>
        <form class="create-form" @submit.prevent="handleCreate">
          <div class="field-group">
            <label for="new-username">Nom d'utilisateur</label>
            <input
              id="new-username"
              v-model="newUsername"
              type="text"
              autocomplete="off"
              :disabled="isCreating"
              placeholder="Nom d'utilisateur"
            />
            <p v-if="formErrors.username" class="field-error">{{ formErrors.username }}</p>
          </div>

          <div class="field-group">
            <label for="new-password">Mot de passe provisoire</label>
            <input
              id="new-password"
              v-model="newPassword"
              type="password"
              autocomplete="new-password"
              :disabled="isCreating"
              placeholder="Mot de passe provisoire"
            />
            <p v-if="formErrors.password" class="field-error">{{ formErrors.password }}</p>
          </div>

          <p v-if="createError" class="error-msg" role="alert">{{ createError }}</p>
          <p v-if="createSuccess" class="success-msg" role="status">{{ createSuccess }}</p>

          <button type="submit" :disabled="isCreating">
            {{ isCreating ? 'Création…' : 'Créer le compte' }}
          </button>
        </form>
      </section>

      <hr class="divider" />

      <!-- Liste des comptes -->
      <section>
        <h2>Comptes existants</h2>
        <p v-if="isLoading" class="loading-msg">Chargement…</p>
        <p v-else-if="error" class="error-msg" role="alert">{{ error }}</p>

        <p v-if="deactivateError" class="error-msg" role="alert">{{ deactivateError }}</p>

        <table v-if="!isLoading && !error" class="users-table" aria-label="Liste des comptes utilisateurs">
          <thead>
            <tr>
              <th>Nom d'utilisateur</th>
              <th>Rôle</th>
              <th>Statut</th>
              <th>Créé le</th>
              <th>MDP à changer</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.username">
              <td>{{ user.username }}</td>
              <td>
                <span :class="['role-badge', user.role]">{{ user.role }}</span>
              </td>
              <td>
                <span :class="['status-badge', user.is_active ? 'active' : 'inactive']">
                  {{ user.is_active ? 'Actif' : 'Inactif' }}
                </span>
              </td>
              <td>{{ formatDate(user.created_at) }}</td>
              <td>{{ user.force_password_change ? 'Oui' : 'Non' }}</td>
              <td>
                <button
                  v-if="user.is_active && user.username !== authStore.user?.username"
                  class="btn-deactivate"
                  :disabled="deactivating === user.username"
                  @click="handleDeactivate(user.username)"
                >
                  {{ deactivating === user.username ? '…' : 'Désactiver' }}
                </button>
              </td>
            </tr>
            <tr v-if="users.length === 0">
              <td colspan="6" class="empty-msg">Aucun compte trouvé.</td>
            </tr>
          </tbody>
        </table>
      </section>
    </div>
    </main>
  </div>
</template>

<style scoped>
.admin-users-page {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: #f5f5f5;
  font-family: sans-serif;
}

.admin-users-content {
  display: flex;
  align-items: flex-start;
  justify-content: center;
  flex: 1;
  padding: 2rem 1rem;
}

.admin-users-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.12);
  padding: 2rem;
  width: 100%;
  max-width: 800px;
}

h1 {
  font-size: 1.25rem;
  margin: 0 0 1.5rem;
}

h2 {
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 1rem;
  color: #333;
}

.divider {
  border: none;
  border-top: 1px solid #e0e0e0;
  margin: 1.5rem 0;
}

/* Formulaire de création */
.create-form {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-width: 400px;
}

.field-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
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
}

input:focus {
  outline: none;
  border-color: #4a6cf7;
  box-shadow: 0 0 0 2px rgba(74, 108, 247, 0.2);
}

.field-error {
  color: #d32f2f;
  font-size: 0.8rem;
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
  align-self: flex-start;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Messages */
.loading-msg,
.empty-msg {
  font-size: 0.9rem;
  color: #555;
}

.error-msg {
  color: #d32f2f;
  font-size: 0.875rem;
  margin: 0;
}

.success-msg {
  color: #2e7d32;
  font-size: 0.875rem;
  margin: 0;
}

/* Tableau */
.users-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.users-table th,
.users-table td {
  text-align: left;
  padding: 0.6rem 0.75rem;
  border-bottom: 1px solid #e0e0e0;
}

.users-table th {
  font-weight: 600;
  color: #333;
  background: #f9f9f9;
}

.role-badge {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
}

.role-badge.admin {
  background: #e3eafd;
  color: #1a3cc8;
}

.role-badge.operator {
  background: #e8f5e9;
  color: #2e7d32;
}

.status-badge {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
}

.status-badge.active {
  background: #e8f5e9;
  color: #2e7d32;
}

.status-badge.inactive {
  background: #fbe9e7;
  color: #bf360c;
}

.btn-deactivate {
  padding: 0.25rem 0.6rem;
  background: #fbe9e7;
  color: #bf360c;
  border: 1px solid #ef9a9a;
  border-radius: 4px;
  font-size: 0.8rem;
  cursor: pointer;
  margin-top: 0;
  align-self: auto;
}

.btn-deactivate:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
