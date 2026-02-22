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
        Gestion des comptes
      </router-link>

      <button class="btn-logout" @click="logout">Déconnexion</button>
    </nav>
  </header>
</template>

<style scoped>
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.6rem 1rem;
  background: #fff;
  border-bottom: 1px solid #e0e0e0;
  font-family: sans-serif;
}

.app-title {
  font-weight: 700;
  font-size: 1rem;
  color: #1a1a1a;
}

.app-nav {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.nav-link {
  font-size: 0.875rem;
  color: #4a6cf7;
  text-decoration: none;
}

.nav-link:hover {
  text-decoration: underline;
}

.btn-logout {
  padding: 0.35rem 0.75rem;
  background: transparent;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 0.875rem;
  cursor: pointer;
  color: #555;
}

.btn-logout:hover {
  background: #f5f5f5;
}
</style>
