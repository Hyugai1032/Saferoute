// stores/auth.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token'))

  const isAuthenticated = computed(() => !!token.value)
  const userRole = computed(() => user.value?.role || 'user') // Default to 'user'

  function login(userData, authToken) {
    user.value = userData
    token.value = authToken
    localStorage.setItem('token', authToken)
    localStorage.setItem('user', JSON.stringify(userData))
  }

  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  function initialize() {
    const savedToken = localStorage.getItem('token')
    const savedUser = localStorage.getItem('user')
    
    if (savedToken && savedUser) {
      token.value = savedToken
      try {
        user.value = JSON.parse(savedUser)
      } catch (e) {
        console.error('Error parsing saved user data:', e)
        user.value = null
      }
    }
  }

  // Mock function for demo purposes
  function mockLogin(role = 'user') {
    const userData = {
      id: 1,
      name: role === 'admin' ? 'Admin User' : 'Regular User',
      email: role === 'admin' ? 'admin@example.com' : 'user@example.com',
      role: role
    }
    login(userData, 'mock-token-' + Date.now())
  }

  return {
    user,
    token,
    isAuthenticated,
    userRole,
    login,
    logout,
    initialize,
    mockLogin
  }
})