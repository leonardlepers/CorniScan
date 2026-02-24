<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { apiCall, deleteUser, toggleAdminRole } from '@/services/apiClient'
import { useAuthStore } from '@/stores/authStore'
import AppHeader from '@/components/AppHeader.vue'

const authStore = useAuthStore()

interface UserRow {
  username: string
  role: string
  is_active: boolean
  created_at: string | null
  force_password_change: boolean
  last_login_at: string | null
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

function formatDateTime(iso: string | null): string {
  if (!iso) return '—'
  return new Date(iso).toLocaleString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
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

// ── Suppression ──────────────────────────────────────────────────────────
const actionError = ref<string | null>(null)
const actioning = ref<string | null>(null)

async function handleDelete(username: string) {
  if (!confirm(`Supprimer définitivement le compte « ${username} » ?`)) return
  actionError.value = null
  actioning.value = username
  try {
    await deleteUser(username)
    await loadUsers()
  } catch (e: unknown) {
    actionError.value = e instanceof Error ? e.message : 'Erreur inattendue'
  } finally {
    actioning.value = null
  }
}

// ── Toggle rôle admin ────────────────────────────────────────────────────
async function handleToggleAdmin(username: string) {
  actionError.value = null
  actioning.value = username
  try {
    await toggleAdminRole(username)
    await loadUsers()
  } catch (e: unknown) {
    actionError.value = e instanceof Error ? e.message : 'Erreur inattendue'
  } finally {
    actioning.value = null
  }
}

onMounted(loadUsers)
</script>

<template>
  <div class="admin-users-page">
    <AppHeader />
    <main class="admin-users-content">
      <div class="admin-users-card">
        <div class="card-header">
          <div>
            <p class="eyebrow">Administration</p>
            <h1>Gestion des comptes</h1>
          </div>
          <div class="header-chip">Accès réservé</div>
        </div>

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
          <p v-if="actionError" class="error-msg" role="alert">{{ actionError }}</p>

          <div class="table-wrapper" v-if="!isLoading && !error">
            <table class="users-table" aria-label="Liste des comptes utilisateurs">
              <thead>
                <tr>
                  <th>Nom d'utilisateur</th>
                  <th>Rôle</th>
                  <th>Statut</th>
                  <th>Créé le</th>
                  <th>Dernier login</th>
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
                  <td>{{ formatDateTime(user.last_login_at) }}</td>
                  <td>{{ user.force_password_change ? 'Oui' : 'Non' }}</td>
                  <td class="actions-cell">
                    <button
                      v-if="user.is_active && user.username !== authStore.user?.username"
                      class="btn-deactivate"
                      :disabled="deactivating === user.username"
                      @click="handleDeactivate(user.username)"
                    >
                      {{ deactivating === user.username ? '…' : 'Désactiver' }}
                    </button>
                    <button
                      v-if="user.username !== authStore.user?.username"
                      class="btn-toggle-admin"
                      :disabled="actioning === user.username"
                      @click="handleToggleAdmin(user.username)"
                    >
                      {{ user.role === 'admin' ? '→ Opérateur' : '→ Admin' }}
                    </button>
                    <button
                      v-if="user.username !== authStore.user?.username"
                      class="btn-delete"
                      :disabled="actioning === user.username"
                      @click="handleDelete(user.username)"
                    >
                      Supprimer
                    </button>
                  </td>
                </tr>
                <tr v-if="users.length === 0">
                  <td colspan="7" class="empty-msg">Aucun compte trouvé.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </main>
  </div>
</template>

<style scoped>
.admin-users-page {
  display: flex;
  flex-direction: column;
  min-height: 100dvh;
}

.admin-users-content {
  display: flex;
  align-items: flex-start;
  justify-content: center;
  flex: 1;
  padding: var(--screen-pad);
}

.admin-users-card {
  background: var(--color-surface);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
  padding: clamp(24px, 4vw, 36px);
  width: min(100%, 980px);
  border: 1px solid var(--color-border);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.3em;
  font-size: 0.65rem;
  font-weight: 700;
  color: var(--color-text-soft);
  margin-bottom: 0.35rem;
}

.header-chip {
  padding: 0.35rem 0.9rem;
  border-radius: 999px;
  background: var(--color-accent-soft);
  color: var(--color-accent-strong);
  font-weight: 600;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
}

h1 {
  font-size: 1.35rem;
  margin: 0;
}

h2 {
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 1rem;
  color: var(--color-text);
}

.divider {
  border: none;
  border-top: 1px solid var(--color-border);
  margin: 1.5rem 0;
}

.create-form {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  max-width: 420px;
}

.field-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-text);
}

input {
  padding: 0.75rem 0.9rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: 1rem;
  background: var(--color-surface-muted);
}

input:focus {
  outline: none;
  border-color: rgba(201, 123, 99, 0.6);
  box-shadow: 0 0 0 3px rgba(201, 123, 99, 0.2);
}

.field-error {
  color: var(--color-danger);
  font-size: 0.8rem;
  margin: 0;
}

button {
  padding: 0.65rem 1.2rem;
  background: var(--color-accent);
  color: #fff;
  border-radius: 999px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  margin-top: 0.3rem;
  align-self: flex-start;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-msg,
.empty-msg {
  font-size: 0.9rem;
  color: var(--color-text-muted);
}

.error-msg {
  color: var(--color-danger);
  font-size: 0.875rem;
  margin: 0;
}

.success-msg {
  color: var(--color-success);
  font-size: 0.875rem;
  margin: 0;
}

.table-wrapper {
  overflow-x: auto;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
}

.users-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
  min-width: 640px;
  background: var(--color-surface);
}

.users-table th,
.users-table td {
  text-align: left;
  padding: 0.75rem 0.9rem;
  border-bottom: 1px solid var(--color-border);
}

.users-table th {
  font-weight: 600;
  color: var(--color-text);
  background: var(--color-surface-strong);
}

.role-badge,
.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.role-badge.admin {
  background: rgba(31, 138, 106, 0.12);
  color: var(--color-success);
}

.role-badge.operator {
  background: var(--color-accent-soft);
  color: var(--color-accent-strong);
}

.status-badge.active {
  background: rgba(31, 138, 106, 0.12);
  color: var(--color-success);
}

.status-badge.inactive {
  background: rgba(209, 73, 91, 0.12);
  color: var(--color-danger);
}

.actions-cell {
  display: flex;
  gap: 0.4rem;
  flex-wrap: wrap;
  align-items: center;
}

.btn-deactivate {
  padding: 0.35rem 0.75rem;
  background: rgba(209, 73, 91, 0.12);
  color: var(--color-danger);
  border: 1px solid rgba(209, 73, 91, 0.35);
  border-radius: 999px;
  font-size: 0.8rem;
  cursor: pointer;
  margin-top: 0;
  align-self: auto;
}

.btn-deactivate:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-toggle-admin {
  padding: 0.35rem 0.75rem;
  background: var(--color-accent-soft);
  color: var(--color-accent-strong);
  border: 1px solid rgba(201, 123, 99, 0.35);
  border-radius: 999px;
  font-size: 0.8rem;
  cursor: pointer;
  margin-top: 0;
}

.btn-toggle-admin:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-delete {
  padding: 0.35rem 0.75rem;
  background: transparent;
  color: var(--color-danger);
  border: 1px solid rgba(209, 73, 91, 0.35);
  border-radius: 999px;
  font-size: 0.8rem;
  cursor: pointer;
  margin-top: 0;
}

.btn-delete:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
