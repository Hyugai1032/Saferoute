<template>
<div :class="['sidebar', { collapsed: isCollapsed }]">
  <aside class="sidebar" :class="{ 'sidebar-collapsed': isCollapsed, 'sidebar-mobile-open': mobileOpen }">
    <!-- Background Glow Effect -->
    <div class="sidebar-glow"></div>
    
    <div class="sidebar-content">
      <!-- Logo Section -->
      <div class="logo-section">
        <div class="logo">
          <div class="logo-mark">
            <div class="logo-inner">SR+</div>
            <div class="logo-pulse"></div>
          </div>
          <div class="logo-text" :class="{ 'logo-text-hidden': isCollapsed }">
            <div class="app-name">SafeRoute+</div>
            <div class="app-tagline">Emergency Response System</div>
          </div>
        </div>
        <!-- <button 
          class="collapse-btn" 
          @click="toggleCollapse" 
          :title="isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'"
        >
          <div class="collapse-icon" :class="{ rotated: isCollapsed }">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
              <path d="M15 18L9 12L15 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
        </button>-->
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
          <div class="user-role">{{ user?.role}}</div>
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

defineProps({ isCollapsed: Boolean })
defineEmits(['toggle'])

const user = ref(JSON.parse(localStorage.getItem("userData")));

const route = useRoute();

const navItems = [
  { to: '/user/dashboard', name: 'Dashboard', icon: '📊' },
  { to: '/user/report', name: 'Report Hazard', icon: '📝' },
  { to: '/user/map', name: 'View Map', icon: '🗺️' },
  { to: '/user/alerts', name: 'Alerts', icon: '🔔' },
  { to: '/user/profile', name: 'Profile', icon: '👤' },
];

</script>

<style scoped>
.sidebar {
  width: 280px;
  height: 100vh;
  background: linear-gradient(180deg, 
    rgba(26, 54, 93, 0.95) 0%, 
    rgba(26, 26, 46, 0.98) 100%);
  backdrop-filter: blur(20px);
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  position: fixed;
  left: 0;
  top: 0;
  z-index: 1050;
  transition: width 0.3s ease;
  overflow: hidden;
}

.sidebar.collapsed {
  width: 80px;
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
  padding: 1.5rem 1rem;
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
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  cursor: pointer;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
}

.logo-mark {
  position: relative;
  width: 45px;
  height: 45px;
  flex-shrink: 0;
}

.logo-inner {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 900;
  color: white;
  font-size: 14px;
  position: relative;
  z-index: 2;
}

.logo-pulse {
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: linear-gradient(135deg, #4facfe, #00f2fe);
  border-radius: 14px;
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
  transform: translateX(-10px);
}

.app-name {
  font-weight: 900;
  color: var(--text);
  font-size: 1.1rem;
  background: linear-gradient(135deg, #f1f5f9, #cbd5e1);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 0.25rem;
}

.app-tagline {
  font-size: 0.7rem;
  color: var(--muted);
  line-height: 1.2;
}

.collapse-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: var(--text);
  width: 32px;
  height: 32px;
  border-radius: 8px;
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
  box-shadow: 0 4px 12px rgba(14, 165, 255, 0.2);
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
  gap: 0.5rem;
  flex: 1;
}

.nav-item {
  color: var(--muted);
  padding: 0.75rem;
  border-radius: 12px;
  text-decoration: none;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.75rem;
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
  border-radius: 12px;
}

.nav-item:hover {
  color: var(--text);
  transform: translateX(4px);
}

.nav-item:hover .nav-item-background {
  opacity: 1;
}

.nav-item-active {
  color: #0ea5ff !important;
  background: rgba(14, 165, 255, 0.15) !important;
  border-left: 3px solid #0ea5ff;
  transform: translateX(0);
}

.nav-item-active .nav-item-background {
  opacity: 1;
}

.nav-icon-wrapper {
  position: relative;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.nav-icon {
  font-size: 1.2rem;
  transition: transform 0.3s ease;
}

.nav-item:hover .nav-icon {
  transform: scale(1.1);
}

.nav-active-indicator {
  position: absolute;
  top: -2px;
  right: -2px;
  width: 6px;
  height: 6px;
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
  transform: translateX(-10px);
  width: 0;
}

.nav-highlight {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 0;
  background: linear-gradient(180deg, #0ea5ff, #4facfe);
  border-radius: 0 2px 2px 0;
  transition: height 0.3s ease;
}

.nav-item-active .nav-highlight {
  height: 70%;
}

/* User Section */
.user-section {
  margin-top: auto;
  padding-top: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  gap: 0.75rem;
  transition: all 0.3s ease;
}

.user-section-collapsed {
  justify-content: center;
  padding: 1rem 0;
}

.user-avatar {
  position: relative;
  width: 40px;
  height: 40px;
  flex-shrink: 0;
}

.avatar-initials {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #8b5cf6, #a855f7);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: white;
  font-size: 0.9rem;
}

.avatar-status {
  position: absolute;
  bottom: -2px;
  right: -2px;
  width: 12px;
  height: 12px;
  background: #10b981;
  border: 2px solid var(--background);
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
  font-size: 0.9rem;
  margin-bottom: 0.1rem;
}

.user-role {
  font-size: 0.75rem;
  color: var(--muted);
  margin-bottom: 0.1rem;
}

.user-status {
  font-size: 0.7rem;
  color: #10b981;
  font-weight: 600;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .sidebar {
    width: 280px;
    transition: transform 0.3s ease, width 0.3s ease;
    transform: translateX(0);
  }

  .sidebar.collapsed {
    transform: translateX(-100%);
    width: 280px;
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