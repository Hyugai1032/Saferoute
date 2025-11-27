import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './assets/styles.css'
import 'leaflet/dist/leaflet.css'
import axios from 'axios'
import { logout } from '@/services/authService'

const API_URL = 'http://127.0.0.1:8000/api/'

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
        router.push('/login')
      }
    }

    return Promise.reject(error)
  }
)

app.use(router)
app.mount('#app')

