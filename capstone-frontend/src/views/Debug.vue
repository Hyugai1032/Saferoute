<!-- views/Debug.vue -->
<template>
  <div class="debug-page">
    <h1>Debug Information</h1>
    
    <div class="debug-section">
      <h3>Route Information</h3>
      <p>Current Path: {{ $route.path }}</p>
      <p>Full Path: {{ $route.fullPath }}</p>
      <p>Route Name: {{ $route.name }}</p>
    </div>

    <div class="debug-section">
      <h3>Auth Information</h3>
      <p>Is Authenticated: {{ isAuthenticated }}</p>
      <p>User Role: {{ userRole }}</p>
      <p>User Data: {{ user }}</p>
    </div>

    <div class="debug-section">
      <h3>Layout Information</h3>
      <p>Is Admin Route: {{ isAdminRoute }}</p>
      <p>Is User Route: {{ isUserRoute }}</p>
    </div>

    <div class="debug-actions">
      <button @click="testAdminRoute">Test Admin Route</button>
      <button @click="testUserRoute">Test User Route</button>
      <button @click="clearStorage">Clear Storage</button>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

export default {
  name: 'DebugPage',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()

    const testAdminRoute = () => {
      router.push('/admin/dashboard')
    }

    const testUserRoute = () => {
      router.push('/user/dashboard')
    }

    const clearStorage = () => {
      localStorage.clear()
      location.reload()
    }

    return {
      isAuthenticated: computed(() => authStore.isAuthenticated),
      userRole: computed(() => authStore.userRole),
      user: computed(() => authStore.user),
      isAdminRoute: computed(() => router.currentRoute.value.path.startsWith('/admin')),
      isUserRoute: computed(() => router.currentRoute.value.path.startsWith('/user')),
      testAdminRoute,
      testUserRoute,
      clearStorage
    }
  }
}
</script>

<style scoped>
.debug-page {
  padding: 20px;
  color: white;
  background: #1a1a1a;
  min-height: 100vh;
}

.debug-section {
  background: #2a2a2a;
  padding: 20px;
  margin: 10px 0;
  border-radius: 8px;
}

.debug-actions {
  margin-top: 20px;
}

.debug-actions button {
  background: #0096ff;
  color: white;
  border: none;
  padding: 10px 20px;
  margin: 5px;
  border-radius: 5px;
  cursor: pointer;
}
</style>