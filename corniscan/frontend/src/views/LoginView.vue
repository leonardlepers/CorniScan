<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useIosInstallGuide } from '@/composables/useIosInstallGuide'
import IosInstallGuide from '@/components/IosInstallGuide.vue'

const authStore = useAuthStore()
const router = useRouter()
const { showGuide, checkAndShow, dismissGuide } = useIosInstallGuide()

const username = ref('')
const password = ref('')

async function handleSubmit() {
  try {
    const user = await authStore.login(username.value, password.value)
    // Story 6.3 — guide installation iOS au premier login réussi (FR34)
    checkAndShow()
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
  <!-- Story 6.3 — Guide iOS (affiché après login réussi si conditions remplies) -->
  <IosInstallGuide v-if="showGuide" @dismiss="dismissGuide" />

  <main class="login-page">
    <div class="login-content">
      <!-- Logo / icône -->
      <div class="brand-section">
        <div class="brand-icon" aria-hidden="true">
          <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="4" y="4" width="32" height="32" rx="10" fill="rgba(201,123,99,0.15)"/>
            <rect x="4" y="4" width="32" height="32" rx="10" stroke="rgba(201,123,99,0.4)" stroke-width="1.5"/>
            <!-- Coin haut-gauche -->
            <path d="M10 16 L10 10 L16 10" stroke="#c97b63" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
            <!-- Coin haut-droit -->
            <path d="M24 10 L30 10 L30 16" stroke="#c97b63" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
            <!-- Coin bas-gauche -->
            <path d="M10 24 L10 30 L16 30" stroke="#c97b63" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
            <!-- Coin bas-droit -->
            <path d="M24 30 L30 30 L30 24" stroke="#c97b63" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
            <!-- Cible centrale -->
            <circle cx="20" cy="20" r="3.5" fill="#c97b63"/>
          </svg>
        </div>
        <div class="brand-text">
          <p class="brand-kicker">Plateforme de mesure</p>
          <h1 class="brand-name">CorniScan</h1>
        </div>
      </div>

      <!-- Formulaire de connexion -->
      <div class="login-card">
        <form class="login-form" @submit.prevent="handleSubmit">
          <div class="field-group">
            <div class="field">
              <label for="username">Nom d'utilisateur</label>
              <input
                id="username"
                v-model="username"
                type="text"
                autocomplete="username"
                required
                :disabled="authStore.isLoading"
                placeholder="Entrez votre identifiant"
              />
            </div>

            <div class="field">
              <label for="password">Mot de passe</label>
              <input
                id="password"
                v-model="password"
                type="password"
                autocomplete="current-password"
                required
                :disabled="authStore.isLoading"
                placeholder="••••••••"
              />
            </div>
          </div>

          <p v-if="authStore.error" class="error-msg" role="alert">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
              <circle cx="8" cy="8" r="7" stroke="currentColor" stroke-width="1.5"/>
              <path d="M8 5v3.5M8 11h.01" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
            {{ authStore.error }}
          </p>

          <button type="submit" class="submit-btn" :disabled="authStore.isLoading">
            <span v-if="authStore.isLoading" class="btn-spinner" aria-hidden="true"></span>
            <span>{{ authStore.isLoading ? 'Connexion…' : 'Se connecter' }}</span>
          </button>
        </form>
      </div>
    </div>
  </main>
</template>

<style scoped>
.login-page {
  min-height: 100dvh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding:
    calc(var(--safe-top) + var(--screen-pad))
    calc(var(--safe-right) + var(--screen-pad))
    calc(var(--safe-bottom) + var(--screen-pad))
    calc(var(--safe-left) + var(--screen-pad));
}

.login-content {
  width: min(100%, var(--card-max));
  display: flex;
  flex-direction: column;
  gap: 2rem;
  animation: fadeInUp 0.45s var(--ease-out) both;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ── Marque ─────────────────────────────────────── */
.brand-section {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding-left: 0.25rem;
}

.brand-icon {
  flex-shrink: 0;
}

.brand-text {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.brand-kicker {
  text-transform: uppercase;
  letter-spacing: 0.18em;
  font-size: 0.65rem;
  font-weight: 600;
  color: var(--color-text-soft);
}

.brand-name {
  font-size: 2rem;
  font-weight: 800;
  color: var(--color-text);
  letter-spacing: -0.02em;
  line-height: 1.1;
}

/* ── Carte formulaire ────────────────────────────── */
.login-card {
  position: relative;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-2xl);
  padding: clamp(24px, 6vw, 36px);
  box-shadow: var(--shadow-lg);
  overflow: hidden;
}

.login-card::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(360px 240px at 0% 0%, rgba(201, 123, 99, 0.1), transparent 55%),
    radial-gradient(300px 260px at 100% 0%, rgba(31, 42, 55, 0.05), transparent 55%);
  pointer-events: none;
}

/* ── Formulaire ──────────────────────────────────── */
.login-form {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.field-group {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

label {
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--color-text);
  letter-spacing: 0.02em;
  text-transform: uppercase;
}

input {
  height: var(--input-height);
  padding: 0 1rem;
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface-muted);
  font-size: 1rem;
  transition:
    border-color var(--transition-fast),
    box-shadow var(--transition-fast),
    background var(--transition-fast);
}

input:focus {
  outline: none;
  border-color: var(--color-accent);
  box-shadow: 0 0 0 4px rgba(201, 123, 99, 0.15);
  background: var(--color-surface);
}

input:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

/* ── Message d'erreur ────────────────────────────── */
.error-msg {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--color-danger);
  font-size: 0.875rem;
  font-weight: 500;
  padding: 0.75rem 1rem;
  background: rgba(209, 73, 91, 0.08);
  border: 1px solid rgba(209, 73, 91, 0.2);
  border-radius: var(--radius-sm);
  line-height: 1.4;
}

.error-msg svg {
  flex-shrink: 0;
}

/* ── Bouton principal ────────────────────────────── */
.submit-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.6rem;
  height: var(--btn-height);
  padding: 0 1.5rem;
  background: var(--color-accent);
  color: #fff;
  border-radius: 999px;
  font-size: 1rem;
  font-weight: 700;
  letter-spacing: 0.01em;
  box-shadow: var(--shadow-accent);
  transition:
    transform var(--transition-fast),
    box-shadow var(--transition-fast),
    background var(--transition-fast);
  margin-top: 0.25rem;
}

.submit-btn:not(:disabled):active {
  transform: scale(0.97);
  box-shadow: 0 6px 16px rgba(201, 123, 99, 0.2);
}

.submit-btn:hover:not(:disabled) {
  background: var(--color-accent-strong);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  box-shadow: none;
}

/* Spinner inline dans le bouton */
.btn-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.35);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.75s linear infinite;
  flex-shrink: 0;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (min-width: 700px) {
  .login-content {
    width: min(460px, 100%);
  }
}
</style>
