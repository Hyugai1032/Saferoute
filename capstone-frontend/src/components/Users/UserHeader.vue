<template>
  <header class="user-header" :style="headerStyle">
    <div class="header-left">
      <button v-if="isMobile" @click="toggleSidebar" class="sidebar-toggle" aria-label="toggle sidebar">
        <div class="toggle-icon" :class="{ 'toggle-icon-collapsed': sidebarCollapsed }">
          <span></span>
          <span></span>
          <span></span>
        </div>
        <span class="toggle-text" v-if="sidebarCollapsed"> Menu</span>
      </button>  
      <div class="user-info">
        <h1>Welcome back, {{ user?.first_name }} {{ user?.last_name }}</h1>
        <p>Here's what's happening in your area</p>
      </div>
    </div>
    <div class="header-right">
      <div class="header-actions">
        <ThemeToggle />
        <div class="alert-indicator">
          <div class="alert-badge" v-if="activeAlerts > 0">{{ activeAlerts }}</div>
              <router-link :to="{ name: 'UserAlerts' }" class="forgot-password">
                <button class="alert-btn">
                  <i class="icon-alert"></i>
                  Alerts
                </button>
              </router-link>
            
        </div>
        <button class="logout-btn" @click="logout">
          <i class="icon-logout"></i>
          Logout
        </button>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted, computed, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import ThemeToggle from '@/components/ThemeToggle.vue'

const handleNewReport = () => {
  // instant badge bump (optimistic)
  activeAlerts.value = Number(activeAlerts.value || 0) + 1
  localStorage.setItem("unread_alerts_count", String(activeAlerts.value))
}

const unreadAlerts = ref(Number(localStorage.getItem("unread_alerts_count") || 0))

const handleUnreadEvent = (e) => {
  unreadAlerts.value = Number(e?.detail?.count || 0)
}

const handleStorage = (e) => {
  if (e.key === "unread_alerts_count") {
    unreadAlerts.value = Number(e.newValue || 0)
  }
}

onMounted(() => {
  window.addEventListener("alerts:unread", handleUnreadEvent)
  window.addEventListener("storage", handleStorage)
  window.addEventListener("alerts:newReport", handleNewReport)
})

onBeforeUnmount(() => {
  window.removeEventListener("alerts:unread", handleUnreadEvent)
  window.removeEventListener("storage", handleStorage)
  window.removeEventListener("alerts:newReport", handleNewReport)
})


const emit = defineEmits(['toggleSidebar']);

const user = ref(JSON.parse(localStorage.getItem("userData")));

const router = useRouter()
const activeAlerts = ref(Number(localStorage.getItem("unread_alerts_count") || 0))
const logout = () => {
  localStorage.removeItem('isAuthenticated')
  localStorage.removeItem('userData')
  router.push('/auth/login')
}


const toggleSidebar = () => {
  emit('toggleSidebar');
};

// Accept sidebarCollapsed as a prop
const { sidebarCollapsed, isMobile } = defineProps({
  sidebarCollapsed: {
    type: Boolean,
    default: false
  },
  isMobile: {
    type: Boolean,
    default: false
  }
});

const headerStyle = computed(() => ({
  marginLeft: sidebarCollapsed ? '80px' : '280px',
  transition: 'margin-left 0.3s ease'
}));
</script>

<style scoped>
.user-header {
  --sr-accent: var(--accent-primary, #0096ff);
  --sr-accent-2: #4dc4ff;

  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-bottom: 24px;
  padding: 1rem 2rem;
  background: rgba(255, 255, 255, 0.045);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  position: sticky;
  top: 0;
  z-index: 1030;
  transition: margin-left 0.3s ease;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
  min-width: 0;
}

.user-info {
  min-width: 0;
}

.user-info h1 {
  font-size: 26px;
  line-height: 1.25;
  font-weight: 700;
  margin: 0 0 4px;
  background: linear-gradient(90deg, #ffffff, var(--sr-accent));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-info p {
  color: var(--text-secondary, #9a9ea8);
  font-size: 14px;
  margin: 0;
}

.sidebar-toggle {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 0.65rem 0.9rem;
  border-radius: 10px;
  display: flex;
  align-items: center;
  gap: 0.7rem;
  cursor: pointer;
  transition: background 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
  color: var(--text, #fff);
  text-decoration: none;
  flex-shrink: 0;
}

.sidebar-toggle:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: scale(1.02);
  box-shadow: 0 4px 12px rgba(14, 165, 255, 0.2);
}

.sidebar-toggle:focus-visible {
  outline: 2px solid var(--sr-accent);
  outline-offset: 2px;
}

.toggle-icon {
  display: flex;
  flex-direction: column;
  gap: 3px;
  width: 18px;
  transition: all 0.3s ease;
}

.toggle-icon span {
  height: 2px;
  background: var(--text, #fff);
  border-radius: 1px;
  transition: all 0.3s ease;
}

.toggle-icon span:nth-child(1) { width: 100%; }
.toggle-icon span:nth-child(2) { width: 14px; }
.toggle-icon span:nth-child(3) { width: 10px; }

.toggle-icon-collapsed span {
  width: 100% !important;
}

.toggle-text {
  font-weight: 600;
  font-size: 0.85rem;
  white-space: nowrap;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-shrink: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.alert-indicator {
  position: relative;
}

.alert-badge {
  position: absolute;
  top: -6px;
  right: -6px;
  background: #ef4444;
  color: white;
  border-radius: 50%;
  min-width: 18px;
  height: 18px;
  padding: 0 4px;
  font-size: 11px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 0 2px rgba(15, 15, 20, 0.9);
  animation: badge-pulse 2s infinite;
  pointer-events: none;
  z-index: 2;
}

@keyframes badge-pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.14); }
}

/* ===== Alerts button =====
   A navigation action, not a danger state — stays in the accent palette so
   it never competes with genuine hazard warnings elsewhere on the page. */
.alert-btn {
  --glow: rgba(0, 150, 255, 0.35);
  position: relative;
  isolation: isolate;
  overflow: hidden;
  background: linear-gradient(135deg, rgba(0, 150, 255, 0.22), rgba(0, 150, 255, 0.08));
  border: 1px solid rgba(0, 150, 255, 0.4);
  color: #8fd0ff;
  font-size: 0.9rem;
  font-weight: 600;
  padding: 0.6rem 1.15rem;
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: transform 0.25s cubic-bezier(.2,.8,.2,1), box-shadow 0.25s ease, border-color 0.25s ease, color 0.25s ease;
}

.alert-btn::after {
  content: '';
  position: absolute;
  top: 0;
  left: -60%;
  width: 45%;
  height: 100%;
  background: linear-gradient(115deg, transparent, rgba(255, 255, 255, 0.45), transparent);
  transform: skewX(-20deg);
  transition: left 0.65s ease;
  pointer-events: none;
  z-index: -1;
}

.alert-btn i {
  font-size: 14px;
  display: inline-block;
  transform-origin: top center;
}

.alert-btn:hover {
  transform: translateY(-2px) scale(1.045);
  border-color: var(--sr-accent-2);
  color: #d4ecff;
  box-shadow: 0 10px 24px var(--glow);
}

.alert-btn:hover::after {
  left: 130%;
}

.alert-btn:active {
  transform: translateY(0) scale(0.96);
}

.alert-btn:focus-visible {
  outline: 2px solid var(--sr-accent);
  outline-offset: 2px;
}

/* When there's an unread count, gently draw the eye — pure CSS reacting to
   the badge that's already conditionally rendered, no logic added. */
.alert-indicator:has(.alert-badge) .alert-btn {
  animation: alert-ambient-glow 2.4s ease-in-out infinite;
}

@keyframes alert-ambient-glow {
  0%, 100% { box-shadow: 0 0 0 0 rgba(0, 150, 255, 0); }
  50% { box-shadow: 0 0 0 5px rgba(0, 150, 255, 0.16); }
}

.alert-indicator:has(.alert-badge) .alert-btn i {
  animation: bell-ring 2.6s ease-in-out infinite;
}

@keyframes bell-ring {
  0%, 60%, 100% { transform: rotate(0deg); }
  63% { transform: rotate(-14deg); }
  67% { transform: rotate(11deg); }
  71% { transform: rotate(-8deg); }
  75% { transform: rotate(5deg); }
  79% { transform: rotate(0deg); }
}

/* ===== Logout button =====
   Quiet by default so it isn't mistaken for a warning at rest; the red
   only shows intent once the person actually reaches for it. */
.logout-btn {
  position: relative;
  isolation: isolate;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.14);
  color: #b7bac2;
  font-size: 0.9rem;
  font-weight: 600;
  padding: 0.6rem 1.15rem;
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: transform 0.25s cubic-bezier(.2,.8,.2,1), box-shadow 0.25s ease, border-color 0.25s ease, color 0.25s ease, background 0.25s ease;
}

.logout-btn::after {
  content: '';
  position: absolute;
  top: 0;
  left: -60%;
  width: 45%;
  height: 100%;
  background: linear-gradient(115deg, transparent, rgba(255, 255, 255, 0.35), transparent);
  transform: skewX(-20deg);
  transition: left 0.65s ease;
  pointer-events: none;
  z-index: -1;
}

.logout-btn i {
  font-size: 14px;
  transition: transform 0.25s ease;
}

.logout-btn:hover {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.22), rgba(239, 68, 68, 0.08));
  border-color: rgba(239, 68, 68, 0.55);
  color: #ffb3b3;
  transform: translateY(-2px) scale(1.045);
  box-shadow: 0 10px 24px rgba(239, 68, 68, 0.28);
}

.logout-btn:hover::after {
  left: 130%;
}

.logout-btn:hover i {
  transform: translateX(4px);
}

.logout-btn:active {
  transform: translateY(0) scale(0.96);
}

.logout-btn:focus-visible {
  outline: 2px solid #ef4444;
  outline-offset: 2px;
}

.icon-alert::before { content: "\1F514"; }
.icon-logout::before { content: "\2192"; }

/* Mobile Responsive */
@media (max-width: 768px) {
  .user-header {
    margin-left: 0 !important;
    padding: 1rem;
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }

  .header-left {
    max-width: 100%;
    width: 100%;
  }

  .sidebar-toggle {
    padding: 0.5rem 0.75rem;
  }

  .toggle-text {
    font-size: 0.8rem;
  }

  .header-right {
    width: 100%;
    justify-content: space-between;
  }

  .alert-btn,
  .logout-btn {
    padding: 0.55rem 0.85rem;
    font-size: 0.85rem;
  }
}

@media (max-width: 480px) {
  .toggle-text {
    display: none;
  }

  .sidebar-toggle {
    padding: 0.5rem;
  }

  .user-info h1 {
    font-size: 21px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .alert-btn,
  .logout-btn,
  .alert-btn i,
  .logout-btn i,
  .alert-badge {
    animation: none;
    transition: none;
  }
}
</style>