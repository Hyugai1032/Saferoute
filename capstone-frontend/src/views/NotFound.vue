<template>
  <main class="nf">
    <div class="nf-card">
      <p class="nf-code">404</p>
      <h1>Page not found</h1>
      <p class="nf-text">
        The page <code>{{ $route.fullPath }}</code> doesn't exist or may have been moved.
      </p>
      <div class="nf-actions">
        <router-link :to="homePath" class="nf-btn primary">{{ homeLabel }}</router-link>
        <button class="nf-btn" @click="$router.back()">Go back</button>
      </div>
    </div>
  </main>
</template>

<script setup>
import { computed } from 'vue'

const isAuthenticated = localStorage.getItem('isAuthenticated') === 'true'
const userData = JSON.parse(localStorage.getItem('userData') || '{}')

const homePath = computed(() => {
  if (!isAuthenticated) return '/'
  if (userData.userType === 'admin') return '/admin/dashboard'
  if (userData.userType === 'staff') return '/staff/dashboard'
  return '/user/dashboard'
})

const homeLabel = computed(() => (isAuthenticated ? 'Back to dashboard' : 'Back to home'))
</script>

<style scoped>
.nf {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 1.5rem;
  background: var(--page-bg, var(--background));
  color: var(--text);
}
.nf-card {
  max-width: 460px;
  width: 100%;
  text-align: center;
  padding: 2.5rem 2rem;
  border-radius: 18px;
  background: var(--surface, rgba(15, 23, 42, 0.74));
  border: 1px solid var(--border-light, rgba(148, 163, 184, 0.16));
  box-shadow: var(--shadow-card, 0 20px 60px rgba(0, 0, 0, 0.34));
}
.nf-code {
  font-size: 4.5rem;
  font-weight: 800;
  line-height: 1;
  color: var(--accent, #0ea5ff);
}
h1 { margin: 0.75rem 0 0.5rem; font-size: 1.5rem; }
.nf-text { color: var(--text-muted, #94a3b8); word-break: break-word; }
.nf-text code { color: var(--text-secondary, #cbd5e1); }
.nf-actions { display: flex; gap: 0.75rem; justify-content: center; margin-top: 1.75rem; flex-wrap: wrap; }
.nf-btn {
  padding: 0.65rem 1.25rem;
  border-radius: 10px;
  border: 1px solid var(--border-medium, rgba(148, 163, 184, 0.28));
  background: transparent;
  color: var(--text);
  font: inherit;
  cursor: pointer;
  text-decoration: none;
}
.nf-btn.primary { background: var(--accent, #0ea5ff); border-color: transparent; color: #04111f; font-weight: 600; }
</style>