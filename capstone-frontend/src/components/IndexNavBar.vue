```vue
<template>
  <header class="app-header">
    <div class="brand" @click="goHome">
      <img :src="saferouteLogo" alt="SafeRoute Logo" class="logo-img" />
      <div>
        <h1>SafeRoute</h1>
        <p>Evacuation Monitoring System</p>
      </div>
    </div>

    <!-- Desktop Navigation -->
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

    <!-- Desktop Actions -->
    <div class="nav-actions">
      <button class="btn ghost" @click="goToLogin">Login</button>
      <button class="btn primary" @click="goToRegister">Get Started</button>
    </div>

    <!-- Hamburger Button -->
    <button
      class="menu-toggle"
      :class="{ open: isMenuOpen }"
      @click="toggleMenu"
      :aria-expanded="isMenuOpen"
      aria-label="Toggle navigation menu"
    >
      <span></span>
      <span></span>
      <span></span>
    </button>

    <!-- Mobile Menu -->
    <transition name="mobile-menu">
      <div v-if="isMenuOpen" class="mobile-menu">
        <nav class="mobile-nav-links">
          <button @click="goToSection('features')">
            Features
          </button>

          <button @click="goToSection('how-it-works')">
            How it Works
          </button>

          <button @click="goToSection('roles')">
            Users
          </button>

          <button
            @click="goToGISMap"
            :class="{ active: isGISMap }"
          >
            GIS Map
          </button>

          <button @click="goToSection('contact')">
            Contact
          </button>
        </nav>

        <div class="mobile-nav-actions">
          <button class="btn ghost" @click="goToLogin">
            Login
          </button>

          <button class="btn primary" @click="goToRegister">
            Get Started
          </button>
        </div>
      </div>
    </transition>
  </header>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import saferouteLogo from '@/assets/saferoute-logo.png'

const router = useRouter()
const route = useRoute()

const isHome = computed(() => route.path === '/')
const isGISMap = computed(() => route.path === '/gis-map')

const isMenuOpen = ref(false)

const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value
}

const closeMenu = () => {
  isMenuOpen.value = false
}

// Section buttons
const goToSection = (id) => {
  closeMenu()

  if (isHome.value) {
    const el = document.getElementById(id)

    if (el) {
      el.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      })
    }
  } else {
    router.push({
      path: '/',
      hash: `#${id}`
    })
  }
}

const goHome = () => {
  closeMenu()

  if (isHome.value) {
    goToSection('hero')
  } else {
    router.push('/')
  }
}

const goToLogin = () => {
  closeMenu()
  router.push('/auth/login')
}

const goToRegister = () => {
  closeMenu()
  router.push('/auth/register')
}

const goToGISMap = () => {
  closeMenu()

  if (!isGISMap.value) {
    router.push('/gis-map')
  }
}
</script>

<style scoped>
/* =========================
   HEADER
========================= */

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

/* =========================
   BRAND
========================= */

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

/* =========================
   DESKTOP NAVIGATION
========================= */

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

/* =========================
   BUTTONS
========================= */

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

  background: linear-gradient(
    135deg,
    #2563eb,
    #0ea5e9
  );

  box-shadow: 0 18px 34px rgba(37, 99, 235, 0.34);
}

.btn.primary:hover {
  transform: translateY(-2px);

  box-shadow:
    0 24px 40px rgba(37, 99, 235, 0.38);
}

.btn.ghost {
  background: rgba(10, 20, 38, 0.72);

  color: #e8f1ff;

  border: 1px solid rgba(96, 165, 250, 0.16);
}

.btn.ghost:hover {
  transform: translateY(-2px);
}

/* =========================
   HAMBURGER
========================= */

.menu-toggle {
  display: none;

  width: 44px;
  height: 44px;

  padding: 0;

  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: 10px;

  background: rgba(10, 20, 38, 0.72);

  cursor: pointer;

  flex-direction: column;
  align-items: center;
  justify-content: center;

  gap: 5px;

  transition: 0.25s ease;
}

.menu-toggle:hover {
  background: rgba(37, 99, 235, 0.18);
  border-color: rgba(96, 165, 250, 0.35);
}

.menu-toggle span {
  display: block;

  width: 21px;
  height: 2px;

  border-radius: 999px;

  background: #e8f1ff;

  transition: 0.25s ease;
}

/* Animate hamburger into X */

.menu-toggle.open span:nth-child(1) {
  transform: translateY(7px) rotate(45deg);
}

.menu-toggle.open span:nth-child(2) {
  opacity: 0;
}

.menu-toggle.open span:nth-child(3) {
  transform: translateY(-7px) rotate(-45deg);
}

/* =========================
   MOBILE MENU
========================= */

.mobile-menu {
  display: none;
}

/* =========================
   TABLET
========================= */

@media (max-width: 1180px) {
  .app-header {
    gap: 0.7rem;
  }

  .nav-links {
    gap: 0.3rem;
  }

  .nav-links button {
    padding: 0.5rem 0.55rem;
    font-size: 0.9rem;
  }

  .nav-actions {
    gap: 0.4rem;
  }

  .btn {
    padding: 0.7rem 0.9rem;
  }
}

/* =========================
   MOBILE
========================= */

@media (max-width: 760px) {
  .app-header {
    position: sticky;

    display: flex;
    flex-direction: row;

    align-items: center;
    justify-content: space-between;

    padding: 0.8rem 5vw;
  }

  /* Keep brand on the left */
  .brand {
    min-width: 0;
    flex: 1;
  }

  .logo-img {
    width: 44px;
    height: 44px;
  }

  .brand h1 {
    font-size: 1rem;
  }

  .brand p {
    font-size: 0.72rem;

    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  /* Hide desktop navigation */
  .nav-links,
  .nav-actions {
    display: none;
  }

  /* Show hamburger */
  .menu-toggle {
    display: flex;

    flex-shrink: 0;
  }

  /* Mobile dropdown */
  .mobile-menu {
    position: absolute;

    top: 100%;
    left: 0;
    right: 0;

    display: flex;
    flex-direction: column;

    gap: 1rem;

    padding: 1rem 5vw 1.2rem;

    background: rgba(4, 12, 24, 0.97);

    backdrop-filter: blur(18px);

    border-bottom:
      1px solid rgba(148, 163, 184, 0.12);

    box-shadow:
      0 20px 40px rgba(0, 0, 0, 0.25);
  }

  /* Mobile links */
  .mobile-nav-links {
    display: flex;
    flex-direction: column;

    gap: 0.35rem;

    width: 100%;
  }

  .mobile-nav-links button {
    width: 100%;

    padding: 0.85rem 1rem;

    border: none;
    border-radius: 10px;

    background: transparent;

    color: #c8d8f0;

    font-size: 0.95rem;
    font-weight: 600;

    text-align: left;

    cursor: pointer;

    transition: 0.2s ease;
  }

  .mobile-nav-links button:hover {
    background: rgba(37, 99, 235, 0.14);
    color: #ffffff;
  }

  .mobile-nav-links button.active {
    background: rgba(37, 99, 235, 0.22);
    color: #ffffff;
  }

  /* Mobile login/register */
  .mobile-nav-actions {
    display: flex;

    width: 100%;

    gap: 0.6rem;

    padding-top: 0.5rem;

    border-top:
      1px solid rgba(148, 163, 184, 0.12);
  }

  .mobile-nav-actions .btn {
    flex: 1;

    text-align: center;
  }

  /* Menu animation */
  .mobile-menu-enter-active,
  .mobile-menu-leave-active {
    transition:
      opacity 0.2s ease,
      transform 0.2s ease;
  }

  .mobile-menu-enter-from,
  .mobile-menu-leave-to {
    opacity: 0;
    transform: translateY(-10px);
  }
}

/* =========================
   VERY SMALL SCREENS
========================= */

@media (max-width: 400px) {
  .brand {
    gap: 0.6rem;
  }

  .logo-img {
    width: 40px;
    height: 40px;
  }

  .brand h1 {
    font-size: 0.95rem;
  }

  .brand p {
    font-size: 0.68rem;
  }

  .menu-toggle {
    width: 40px;
    height: 40px;
  }
}

</style>