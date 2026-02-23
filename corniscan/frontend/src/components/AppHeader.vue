<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const authStore = useAuthStore()
const router = useRouter()

function logout() {
  authStore.logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <header class="app-header">
    <span class="app-title">CorniScan</span>

    <nav class="app-nav">
      <!-- Lien admin — uniquement visible pour le rôle 'admin' (AC#4 Story 2.4) -->
      <router-link
        v-if="authStore.user?.role === 'admin'"
        to="/admin/users"
        class="nav-link"
      >
        Comptes
      </router-link>

      <button class="btn-logout" @click="logout" aria-label="Se déconnecter">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
          <path d="M6 2H3a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          <path d="M10 5l3 3-3 3M13 8H6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <span class="logout-label">Déconnexion</span>
      </button>
    </nav>
  </header>
</template>

<style scoped>
.app-header {
  position: sticky;
  top: 0;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: space-between;
  /* Hauteur fixe + clearance Dynamic Island */
  min-height: calc(var(--header-height) + var(--safe-top));
  padding:
    calc(0.5rem + var(--safe-top))
    calc(1.1rem + var(--safe-right))
    0.5rem
    calc(1.1rem + var(--safe-left));
  background: rgba(250, 247, 242, 0.88);
  border-bottom: 1px solid var(--color-border);
  backdrop-filter: blur(16px) saturate(1.4);
  -webkit-backdrop-filter: blur(16px) saturate(1.4);
}

.app-title {
  font-weight: 800;
  font-size: 1.05rem;
  color: var(--color-text);
  letter-spacing: -0.01em;
}

.app-nav {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.nav-link {
  display: flex;
  align-items: center;
  height: var(--btn-height-sm);
  padding: 0 0.85rem;
  font-size: 0.875rem;
  color: var(--color-accent);
  font-weight: 700;
  white-space: nowrap;
  border-radius: 999px;
  transition: background var(--transition-fast);
}

.nav-link:active {
  background: var(--color-accent-soft);
}

.btn-logout {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  height: var(--btn-height-sm);
  padding: 0 0.85rem;
  border: 1.5px solid var(--color-border-strong);
  border-radius: 999px;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text);
  background: var(--color-surface);
  transition:
    background var(--transition-fast),
    transform var(--transition-fast);
}

.btn-logout:active {
  transform: scale(0.95);
  background: var(--color-surface-muted);
}

/* Sur les très petits écrans, masquer le texte "Déconnexion" */
@media (max-width: 360px) {
  .logout-label {
    display: none;
  }
}
</style>
