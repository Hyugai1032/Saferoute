import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './assets/styles.css'
import 'leaflet/dist/leaflet.css'
import axios from 'axios'
import { logout } from '@/services/authService'
import './style.css'
import './assets/theme.css'
import { initTheme } from './composables/useTheme'
import { registerSW } from 'virtual:pwa-register'
import { startOutboxAutoSync } from './offline/evacueeOutbox'

const API_URL = import.meta.env.VITE_API_BASE_URL

initTheme()

const app = createApp(App)

// Make axios globally available
app.config.globalProperties.$axios = axios

// Token Refresh Interceptor
axios.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401 && error.config && !error.config.__isRetryRequest) {
      try {
        const refreshToken = localStorage.getItem('refresh_token')

        if (!refreshToken) throw new Error("No refresh token")

        const refreshResponse = await axios.post(API_URL + 'token/refresh/', {
          refresh: refreshToken
        })

        localStorage.setItem('access_token', refreshResponse.data.access)

        // Retry original request
        error.config.headers['Authorization'] = `Bearer ${refreshResponse.data.access}`
        error.config.__isRetryRequest = true

        return axios(error.config)

      } catch (refreshError) {
        logout()
        router.push('/auth/login')
      }
    }

    return Promise.reject(error)
  }
)

app.use(router)

app.mount('#app')

// Hide the splash screen from index.html once the first page has rendered.
// It stays at least ~0.7s so the animation doesn't just flash, but never longer
// than the app actually takes to load.
const hideSplash = () => {
  const splash = document.getElementById('boot-splash')
  if (!splash) return
   const wait = Math.max(0, 1200 - performance.now())
  setTimeout(() => {
    splash.classList.add('hide')
    setTimeout(() => splash.remove(), 600)
  }, wait)
}
router.isReady().finally(hideSplash)

// Offline support: keep the app available with no signal, and upload evacuees that
// were registered offline whenever a connection is available.
registerSW({ immediate: true })
startOutboxAutoSync()