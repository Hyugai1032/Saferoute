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
import { loadRouteLocation, useRouter } from 'vue-router'

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

onMounted(() => {
  const userData = JSON.parse(localStorage.getItem('userData') || '{}')
  if (userData.name) {
    userName.value = userData.name
  }
})

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
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 1rem 2rem;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
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
}

.user-info h1 {
  font-size: 28px;
  margin-bottom: 5px;
  background: linear-gradient(90deg, #ffffff, #0096ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.user-info p {
  color: #888;
  font-size: 16px;
  margin: 0;
}

.sidebar-toggle {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 0.75rem 1rem;
  border-radius: 10px;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  transition: all 0.3s ease;
  color: var(--text);
  text-decoration: none;
}

.sidebar-toggle:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: scale(1.02);
  box-shadow: 0 4px 12px rgba(14, 165, 255, 0.2);
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
  background: var(--text);
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
  font-size: 0.9rem;
  white-space: nowrap;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.alert-indicator {
  position: relative;
}

.alert-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  background: #ff4444;
  color: white;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.alert-btn {
  background: rgba(255, 68, 68, 0.2);
  border: 1px solid rgba(255, 68, 68, 0.5);
  color: #ff6b6b;
  padding: 10px 20px;
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.alert-btn:hover {
  background: rgba(255, 68, 68, 0.3);
  transform: translateY(-2px);
}

.logout-btn {
  background: rgba(239, 68, 68, 0.2);
  border: 1px solid rgba(239, 68, 68, 0.5);
  color: #ef4444;
  padding: 10px 20px;
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  font-weight: 600;
}

.logout-btn:hover {
  background: rgba(239, 68, 68, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(239, 68, 68, 0.3);
}

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
}

@media (max-width: 480px) {
  .toggle-text {
    display: none;
  }
  
  .sidebar-toggle {
    padding: 0.5rem;
  }
}
</style>