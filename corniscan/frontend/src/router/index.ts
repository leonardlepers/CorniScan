/**
 * Router Vue — CorniScan
 *
 * Story 1.3 : guards requireAuth + toutes les routes principales
 * Story 2.1 : route /admin/users (requireAdmin)
 *
 * ORDRE DES VÉRIFICATIONS guards (architecture.md) :
 * 1. Route publique (meta.public) → laisser passer
 * 2. Pas de token → redirect /login
 * 3. Route admin + rôle operator → redirect /camera
 * 4. force_password_change + pas sur /change-password → redirect /change-password
 */
import { createRouter, createWebHistory } from 'vue-router'

import { useAuthStore } from '@/stores/authStore'
import AdminUsersView from '../views/AdminUsersView.vue'
import CameraView from '../views/CameraView.vue'
import ChangePasswordView from '../views/ChangePasswordView.vue'
import LoginView from '../views/LoginView.vue'

declare module 'vue-router' {
  interface RouteMeta {
    public?: boolean
    requireAdmin?: boolean
  }
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login',
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { public: true },
    },
    {
      path: '/change-password',
      name: 'change-password',
      component: ChangePasswordView,
    },
    {
      path: '/camera',
      name: 'camera',
      component: CameraView,
      // Logique complète en Story 3.x
    },
    {
      path: '/admin/users',
      name: 'admin-users',
      component: AdminUsersView,
      meta: { requireAdmin: true },
    },
    // TODO Story 3.x: /validation (requireAuth + requirePhoto via scanStore.hasPhoto)
  ],
})

/**
 * Guard global — vérifications dans l'ordre exact défini par l'architecture.
 */
router.beforeEach((to) => {
  const authStore = useAuthStore()

  // 1. Route publique → laisser passer
  if (to.meta.public) {
    // Si déjà authentifié sur /login → rediriger selon état du compte
    if (authStore.isAuthenticated && to.name === 'login') {
      if (authStore.user?.force_password_change) {
        return { name: 'change-password' }
      }
      return { name: 'camera' }
    }
    return true
  }

  // 2. Pas de token → redirect /login
  if (!authStore.isAuthenticated) {
    return { name: 'login' }
  }

  // 3. Route admin + rôle operator → redirect /camera + message accès refusé (AC#1 Story 2.4)
  if (to.meta.requireAdmin && authStore.user?.role !== 'admin') {
    return { name: 'camera', query: { forbidden: '1' } }
  }

  // 4. force_password_change + pas sur /change-password → redirect /change-password
  if (authStore.user?.force_password_change && to.name !== 'change-password') {
    return { name: 'change-password' }
  }

  return true
})

export default router
