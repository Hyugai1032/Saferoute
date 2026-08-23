<template>
  <header class="app-header">
    <div class="brand" @click="goHome">
      <img :src="saferouteLogo" alt="SafeRoute Logo" class="logo-img" />
      <div>
        <h1>SafeRoute</h1>
        <p>Evacuation Monitoring System</p>
      </div>
    </div>
 
    <nav class="nav-links">
      <button @click="goToSection('features')">Features</button>
      <button @click="goToSection('how-it-works')">How it Works</button>
      <button @click="goToSection('roles')">Users</button>
      <button
        @click="goToGISMap"
        :class="{ active: isGISMap }"
      >
        GIS Map
      </button>
      <button @click="goToSection('contact')">Contact</button>
    </nav>
 
    <div class="nav-actions">
      <button class="btn ghost" @click="goToLogin">Login</button>
      <button class="btn primary" @click="goToRegister">Get Started</button>
    </div>
  </header>
</template>
 
<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import saferouteLogo from '@/assets/saferoute-logo.png'
 
const router = useRouter()
const route = useRoute()
 
const isHome = computed(() => route.path === '/')
const isGISMap = computed(() => route.path === '/gis-map')
 
// Section buttons (Features / How it Works / Users / Contact) only exist on
// the landing page. From any other route, navigate home first and pass the
// target section as a hash so LandingPage can scroll to it once mounted.
const goToSection = (id) => {
  if (isHome.value) {
    const el = document.getElementById(id)
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
  } else {
    router.push({ path: '/', hash: `#${id}` })
  }
}
 
const goHome = () => {
  if (isHome.value) {
    goToSection('hero')
  } else {
    router.push('/')
  }
}
 
const goToLogin = () => router.push('/auth/login')
const goToRegister = () => router.push('/auth/register')
const goToGISMap = () => {
  if (!isGISMap.value) router.push('/gis-map')
}
</script>
 
<style scoped>
.app-header {
  position: sticky;
  top: 0;
  z-index: 30;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem 5vw;
  backdrop-filter: blur(18px);
  background: rgba(4, 12, 24, 0.6);
  border-bottom: 1px solid rgba(148, 163, 184, 0.12);
}
 
.brand {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  cursor: pointer;
}
 
.brand h1 {
  margin: 0;
  font-size: 1.05rem;
  color: #f8fbff;
}
 
.brand p {
  margin: 0.1rem 0 0;
  font-size: 0.82rem;
  color: #9bb4d0;
}
 
.logo-img {
  width: 50px;
  height: 50px;
  object-fit: contain;
  display: block;
  border-radius: 8px;
}
 
.nav-links,
.nav-actions {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  flex-wrap: wrap;
}
 
.nav-links button {
  border: none;
  background: transparent;
  color: #c8d8f0;
  font-weight: 600;
  cursor: pointer;
  padding: 0.55rem 0.8rem;
  border-radius: 999px;
  transition: 0.25s ease;
}
 
.nav-links button:hover {
  background: rgba(37, 99, 235, 0.14);
  color: #ffffff;
}
 
.nav-links button.active {
  background: rgba(37, 99, 235, 0.22);
  color: #ffffff;
}
 
.btn {
  border: none;
  border-radius: 999px;
  padding: 0.8rem 1.2rem;
  font-weight: 700;
  cursor: pointer;
  transition: 0.25s ease;
}
 
.btn.primary {
  color: white;
  background: linear-gradient(135deg, #2563eb, #0ea5e9);
  box-shadow: 0 18px 34px rgba(37, 99, 235, 0.34);
}
 
.btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 24px 40px rgba(37, 99, 235, 0.38);
}
 
.btn.ghost {
  background: rgba(10, 20, 38, 0.72);
  color: #e8f1ff;
  border: 1px solid rgba(96, 165, 250, 0.16);
}
 
.btn.ghost:hover {
  transform: translateY(-2px);
}
 
@media (max-width: 1180px) {
  .app-header {
    flex-wrap: wrap;
  }
}
 
@media (max-width: 760px) {
  .app-header {
    flex-direction: column;
    align-items: flex-start;
  }
 
  .nav-links {
    width: 100%;
    overflow-x: auto;
    padding-bottom: 0.2rem;
    flex-wrap: nowrap;
  }
 
  .nav-links::-webkit-scrollbar {
    height: 6px;
  }
 
  .nav-links::-webkit-scrollbar-thumb {
    background: rgba(148, 163, 184, 0.24);
    border-radius: 999px;
  }
 
  .nav-actions {
    width: 100%;
  }
 
  .nav-actions .btn {
    flex: 1;
    justify-content: center;
  }
}
</style>