<template>
<div :class="['sidebar', { collapsed: isCollapsed }]">
  <aside class="sidebar" :class="{ 'sidebar-collapsed': isCollapsed }">
    <!-- Background Glow Effect -->
    <div class="sidebar-glow"></div>
    
    <div class="sidebar-content">
      <!-- Logo Section -->
      <div class="logo-section" @click="$emit('toggle')">
        <div class="logo">
          <div class="logo-mark">
            <div class="logo-inner">
              <img :src="saferouteLogo" alt="SafeRoute Logo" class="logo-img" />
            </div>
            <div class="logo-pulse"></div>
          </div>

          <div class="logo-text" :class="{ 'logo-text-hidden': isCollapsed }">
            <div class="app-name">SafeRoute+</div>
            <div class="app-tagline">Emergency Response System</div>
          </div>
        </div>
      </div>

      <!-- Navigation -->
      <nav class="sidebar-nav">
        <router-link 
          v-for="item in navItems" 
          :key="item.to"
          :to="item.to" 
          class="nav-item"
          :class="{ 'nav-item-active': $route.path === item.to }"
        >
          <div class="nav-item-background"></div>
          <div class="nav-icon-wrapper">
            <div class="nav-icon">{{ item.icon }}</div>
            <div class="nav-active-indicator"></div>
          </div>
          <span class="nav-text" :class="{ 'nav-text-hidden': isCollapsed }">
            {{ item.name }}
          </span>
          <div class="nav-highlight"></div>
        </router-link>
      </nav>

      <!-- User Info -->
      <div class="user-section" :class="{ 'user-section-collapsed': isCollapsed }">
        <div class="user-avatar">
          <div class="avatar-initials">{{ (user?.first_name?.[0] || '') + (user?.last_name?.[0] || '') }}</div>
          <div class="avatar-status"></div>
        </div>
        <div class="user-info" :class="{ 'user-info-hidden': isCollapsed }">
          <div class="user-name">{{ user?.first_name }} {{ user?.last_name }}</div>
          <div class="user-role">{{ user?.role }}</div>
          <div class="user-status">Online</div>
        </div>
      </div>
    </div>
  </aside>
</div>
</template>

<script setup>
import { useRoute } from 'vue-router';
import { ref } from 'vue';

import saferouteLogo from '@/assets/saferoute-logo.png'
import { icon } from 'leaflet';

defineProps({ isCollapsed: Boolean })
defineEmits(['toggle'])

const user = ref(JSON.parse(localStorage.getItem("userData")));

const userData = JSON.parse(localStorage.getItem("userData") || "{}");
const isProvincialAdmin =
  userData.userType === "admin" &&
  (
    userData.role === "PROVINCIAL_ADMIN" ||
    userData.isProvincialAdmin === true ||
    userData.municipality_id == null
  );

const route = useRoute();

const navItems = [
  { to: '/admin/dashboard', name: 'Dashboard', icon: '📊' },
  { to: '/admin/centers', name: 'Evacuation Centers', icon: '🏢' },
  { to: '/admin/hazard_report', name: 'Hazard Reports', icon: '📝' },
  { to: '/admin/hazard_logs', name: 'Hazard Report Logs', icon: '🧾' },
  { to: '/admin/map', name: 'GIS Map', icon: '🗺️' },
  { to: '/admin/analytics', name: 'Analytics', icon: '📈' },
  ...(isProvincialAdmin ? [
    { to: '/admin/reports/affected-population', name: 'Affected Population Report', icon: '📄' }
  ] : []),
  { to: '/admin/donation-drive', name: 'Donation Drive', icon: '📦'},
  { to: '/admin/edit_forms', name: 'Edit Forms', icon: '✏️' },
  { to: '/admin/users', name: 'User Management', icon: '👥' },
  { to: '/admin/profile', name: 'Profile', icon: '👤' },
];
</script>

<style scoped>
/* ===== LARGE-SCREEN / TV SCALING =====
   Same unit as Dashboard.vue: --u is 16px up to 1080p (unchanged look) and
   grows on bigger screens, following the smaller of width/height so it fits
   any TV ratio. First value is a fallback for old TV browsers. */
.sidebar {
  --u: 16px;
  font-size: var(--u);
  width: calc(17.5 * var(--u));
  height: 100vh;
  background: linear-gradient(180deg, 
    rgba(26, 54, 93, 0.95) 0%, 
    rgba(26, 26, 46, 0.98) 100%);
  backdrop-filter: blur(calc(1.25 * var(--u)));
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  position: fixed;
  left: 0;
  top: 0;
  z-index: 1050;
  transition: width 0.3s ease;
  overflow: hidden;
}

@supports (font-size: clamp(16px, min(1vw, 1vh), 48px)) {
  .sidebar {
    --u: clamp(16px, min(0.8333vw, 1.4815vh), 48px);
  }
}

.sidebar.collapsed {
  width: calc(5 * var(--u));
}

.sidebar-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 100%;
  background: linear-gradient(45deg, 
    rgba(14, 165, 255, 0.1) 0%, 
    transparent 50%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.sidebar:hover .sidebar-glow {
  opacity: 1;
}

.sidebar-content {
  padding: calc(1.5 * var(--u)) var(--u);
  height: 100%;
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: 2;
}

/* Logo Section */
.logo-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: calc(2 * var(--u));
  padding-bottom: calc(1.5 * var(--u));
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  cursor: pointer;
}

.logo {
  display: flex;
  align-items: center;
  gap: calc(0.75 * var(--u));
  flex: 1;
}

.logo-mark {
  position: relative;
  width: calc(3.25 * var(--u));
  height: calc(3.25 * var(--u));
  min-width: calc(3.25 * var(--u));
  flex-shrink: 0;
}

.logo-inner {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #9fcef6 0%, #95eff4 100%);
  border-radius: calc(0.875 * var(--u));
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 2;
  overflow: hidden;
  box-shadow: 0 0 calc(1.125 * var(--u)) rgba(34, 211, 238, 0.35);
}

.logo-img {
  width: calc(3.125 * var(--u));
  height:  calc(3.125 * var(--u));
  object-fit: contain;
  display: block;
  border-radius: calc(0.5 * var(--u));
}

.logo-pulse {
  position: absolute;
  top: calc(-0.125 * var(--u));
  left: calc(-0.125 * var(--u));
  right: calc(-0.125 * var(--u));
  bottom: calc(-0.125 * var(--u));
  background: linear-gradient(135deg, #4facfe, #00f2fe);
  border-radius: calc(1 * var(--u));
  opacity: 0.6;
  animation: pulse 2s infinite;
  z-index: 1;
}

.logo-text {
  flex: 1;
  transition: all 0.3s ease;
  overflow: hidden;
}

.logo-text-hidden {
  opacity: 0;
  transform: translateX(calc(-0.625 * var(--u)));
}




.app-name {
  font-weight: 900;
  color: var(--text);
  font-size: calc(1.1 * var(--u));
  background: linear-gradient(135deg, #f1f5f9, #cbd5e1);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: calc(0.25 * var(--u));
}

.app-tagline {
  font-size: calc(0.7 * var(--u));
  color: var(--muted);
  line-height: 1.2;
}

.collapse-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: var(--text);
  width: calc(2 * var(--u));
  height: calc(2 * var(--u));
  border-radius: calc(0.5 * var(--u));
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.collapse-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: scale(1.05);
  box-shadow: 0 calc(0.25 * var(--u)) calc(0.75 * var(--u)) rgba(14, 165, 255, 0.2);
}

.collapse-icon {
  transition: transform 0.3s ease;
}

.collapse-icon.rotated {
  transform: rotate(180deg);
}

/* Navigation */
.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: calc(0.5 * var(--u));
  flex: 1;
}

.nav-item {
  color: var(--muted);
  padding: calc(0.75 * var(--u));
  border-radius: calc(0.75 * var(--u));
  text-decoration: none;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: calc(0.75 * var(--u));
  position: relative;
  overflow: hidden;
}

.nav-item-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(14, 165, 255, 0.1), transparent);
  opacity: 0;
  transition: opacity 0.3s ease;
  border-radius: calc(0.75 * var(--u));
}

.nav-item:hover {
  color: var(--text);
  transform: translateX(calc(0.25 * var(--u)));
}

.nav-item:hover .nav-item-background {
  opacity: 1;
}

.nav-item-active {
  color: #0ea5ff !important;
  background: rgba(14, 165, 255, 0.15) !important;
  border-left: calc(0.1875 * var(--u)) solid #0ea5ff;
  transform: translateX(0);
}

.nav-item-active .nav-item-background {
  opacity: 1;
}

.nav-icon-wrapper {
  position: relative;
  width: calc(1.5 * var(--u));
  height: calc(1.5 * var(--u));
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.nav-icon {
  font-size: calc(1.2 * var(--u));
  transition: transform 0.3s ease;
}

.nav-item:hover .nav-icon {
  transform: scale(1.1);
}

.nav-active-indicator {
  position: absolute;
  top: calc(-0.125 * var(--u));
  right: calc(-0.125 * var(--u));
  width: calc(0.375 * var(--u));
  height: calc(0.375 * var(--u));
  background: #0ea5ff;
  border-radius: 50%;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.nav-item-active .nav-active-indicator {
  opacity: 1;
  animation: glow 2s infinite;
}

.nav-text {
  font-weight: 500;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.nav-text-hidden {
  opacity: 0;
  transform: translateX(calc(-0.625 * var(--u)));
  width: 0;
}

.nav-highlight {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: calc(0.1875 * var(--u));
  height: 0;
  background: linear-gradient(180deg, #0ea5ff, #4facfe);
  border-radius: 0 calc(0.125 * var(--u)) calc(0.125 * var(--u)) 0;
  transition: height 0.3s ease;
}

.nav-item-active .nav-highlight {
  height: 70%;
}

/* User Section */
.user-section {
  margin-top: auto;
  padding-top: calc(1.5 * var(--u));
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  gap: calc(0.75 * var(--u));
  transition: all 0.3s ease;
}

.user-section-collapsed {
  justify-content: center;
  padding: var(--u) 0;
}

.user-avatar {
  position: relative;
  width: calc(2.5 * var(--u));
  height: calc(2.5 * var(--u));
  flex-shrink: 0;
}

.avatar-initials {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #8b5cf6, #a855f7);
  border-radius: calc(0.625 * var(--u));
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: white;
  font-size: calc(0.9 * var(--u));
}

.avatar-status {
  position: absolute;
  bottom: calc(-0.125 * var(--u));
  right: calc(-0.125 * var(--u));
  width: calc(0.75 * var(--u));
  height: calc(0.75 * var(--u));
  background: #10b981;
  border: calc(0.125 * var(--u)) solid var(--background);
  border-radius: 50%;
}

.user-info {
  flex: 1;
  transition: all 0.3s ease;
  overflow: hidden;
}

.user-info-hidden {
  opacity: 0;
  width: 0;
  height: 0;
}

.user-name {
  font-weight: 700;
  color: var(--text);
  font-size: calc(0.9 * var(--u));
  margin-bottom: calc(0.1 * var(--u));
}

.user-role {
  font-size: calc(0.75 * var(--u));
  color: var(--muted);
  margin-bottom: calc(0.1 * var(--u));
}

.user-status {
  font-size: calc(0.7 * var(--u));
  color: #10b981;
  font-weight: 600;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .sidebar {
    width: calc(17.5 * var(--u));
    transition: transform 0.3s ease, width 0.3s ease;
    transform: translateX(0);
  }

  .sidebar.collapsed {
    transform: translateX(-100%);
    width: calc(17.5 * var(--u));
  }

  .logo-text-hidden,
  .nav-text-hidden,
  .user-info-hidden {
    opacity: 1;
    transform: none;
    width: auto;
  }
}

/* Animations */
@keyframes pulse {
  0%, 100% { 
    transform: scale(1);
    opacity: 0.6;
  }
  50% { 
    transform: scale(1.1);
    opacity: 0.8;
  }
}
</style>