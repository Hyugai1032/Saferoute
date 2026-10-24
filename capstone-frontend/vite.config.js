import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    vue(),

    // Offline support: a service worker that keeps the app itself (pages, scripts,
    // styles) on the phone, so it opens with no signal. Data entered offline is kept
    // separately in IndexedDB (src/offline/) and uploaded when a connection returns.
    VitePWA({
      registerType: 'autoUpdate',
      injectRegister: false, // registered in src/main.js
      includeAssets: ['favicon.ico', 'favicon_io/apple-touch-icon.png'],
      manifest: {
        name: 'SafeRoute+ — Oriental Mindoro',
        short_name: 'SafeRoute+',
        description: 'Evacuation center monitoring and evacuee registration.',
        // The login route sends signed-in users straight to their own dashboard
        // (see the router guard), so the installed app opens where staff work.
        start_url: '/auth/login/',
        scope: '/',
        display: 'standalone',
        background_color: '#060912',
        theme_color: '#060912',
        icons: [
          { src: '/favicon_io/android-chrome-192x192.png', sizes: '192x192', type: 'image/png' },
          { src: '/favicon_io/android-chrome-512x512.png', sizes: '512x512', type: 'image/png' },
          { src: '/favicon_io/android-chrome-512x512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
        ],
      },
      workbox: {
        // App shell only. Large gallery photos (landing page) are left out on purpose so
        // the first download on a weak connection stays small.
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff,woff2}'],
        globIgnores: ['**/pdrrmo-gallery/**'],
        maximumFileSizeToCacheInBytes: 4 * 1024 * 1024,
        navigateFallback: '/index.html',
        // API calls are never answered from the service worker cache: the app decides
        // what to show offline (see src/offline/), so stale or another user's data
        // can't leak in.
        navigateFallbackDenylist: [/^\/api\//, /^\/admin\//, /^\/media\//],
        cleanupOutdatedCaches: true,
        runtimeCaching: [
          {
            // Font Awesome icons loaded from the CDN in index.html
            urlPattern: ({ url }) => url.origin === 'https://cdnjs.cloudflare.com',
            handler: 'CacheFirst',
            options: {
              cacheName: 'cdn-assets',
              expiration: { maxEntries: 40, maxAgeSeconds: 60 * 60 * 24 * 60 },
              cacheableResponse: { statuses: [0, 200] },
            },
          },
          {
            // Map tiles already viewed stay available with no signal.
            urlPattern: ({ url }) => url.hostname.endsWith('tile.openstreetmap.org'),
            handler: 'StaleWhileRevalidate',
            options: {
              cacheName: 'map-tiles',
              expiration: { maxEntries: 400, maxAgeSeconds: 60 * 60 * 24 * 14 },
              cacheableResponse: { statuses: [0, 200] },
            },
          },
        ],
      },
      devOptions: { enabled: false },
    }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})