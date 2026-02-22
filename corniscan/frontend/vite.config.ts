import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import { VitePWA } from 'vite-plugin-pwa'

// VitePWA ne doit pas être actif sous Vitest (son virtual module perturbe localStorage jsdom)
const pwaPlugin = process.env.VITEST
  ? []
  : [
      VitePWA({
        registerType: 'autoUpdate',
        includeAssets: ['favicon.ico', 'icons/*.png'],
        manifest: {
          name: 'CorniScan',
          short_name: 'CorniScan',
          description: 'Scanner de joints de vitrage pour Cornille SA',
          theme_color: '#111111',
          background_color: '#111111',
          display: 'standalone',
          orientation: 'portrait',
          scope: '/',
          start_url: '/',
          icons: [
            {
              src: 'icons/icon-192.png',
              sizes: '192x192',
              type: 'image/png',
            },
            {
              src: 'icons/icon-512.png',
              sizes: '512x512',
              type: 'image/png',
            },
          ],
        },
        workbox: {
          globPatterns: ['**/*.{js,css,html,ico,png,svg}'],
        },
      }),
    ]

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue(), vueDevTools(), ...pwaPlugin],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
