<template>
  <header class="header-bar" :style="headerStyle">
    <div class="header-left">
      <button
        v-if="isMobile"
        @click="toggleSidebar"
        class="sidebar-toggle"
        aria-label="toggle sidebar"
      >
        <div class="toggle-icon" :class="{ 'toggle-icon-collapsed': sidebarCollapsed }">
          <span></span>
          <span></span>
          <span></span>
        </div>
        <span class="toggle-text" v-if="sidebarCollapsed">Menu</span>
      </button>

      <div class="user-info">
        <h1>Welcome back, {{ user?.first_name }} {{ user?.last_name }}</h1>
      </div>
    </div>

    <div class="header-right">
      <ThemeToggle />

      <div class="header-notifications" v-if="showAdminNotifications">
        <button class="notification-btn" @click="toggleNotifications">
          <div class="notification-icon">🔔</div>
          <div class="notification-badge" v-if="notifCount > 0">
            {{ notifCount }}
          </div>
        </button>
      </div>

      <button class="logout-header-btn" @click="logout">
        Logout
      </button>
    </div>
  </header>
</template>

<script setup>
import axios from "axios";
import { ref, computed, onMounted, onBeforeUnmount } from "vue";
import { useRouter } from "vue-router";
import ThemeToggle from "@/components/ThemeToggle.vue";

const router = useRouter();

const props = defineProps({
  sidebarCollapsed: {
    type: Boolean,
    default: false,
  },
  isMobile: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["toggleSidebar"]);

const user = ref(JSON.parse(localStorage.getItem("userData") || "{}"));

const userType = computed(() => {
  return String(user.value?.userType || "").toLowerCase();
});

const showAdminNotifications = computed(() => {
  return userType.value === "admin";
});

const notifCount = ref(0);

const RAW_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
const API_BASE = RAW_BASE.replace(/\/api\/?$/, "");
const HAZARDS_URL = `${API_BASE}/api/hazards/`;

const fetchNotifCount = async () => {
  if (!showAdminNotifications.value) return;

  try {
    const token = localStorage.getItem("access_token");
    const headers = token ? { Authorization: `Bearer ${token}` } : {};

    const res = await axios.get(`${HAZARDS_URL}?status=REPORTED`, { headers });
    const list = Array.isArray(res.data) ? res.data : res.data.results || [];

    notifCount.value = list.length;
  } catch (e) {
    console.error("Failed to load notification count:", e);
    notifCount.value = 0;
  }
};

const toggleNotifications = () => {
  router.push({ name: "Hazard Reports" });
};

const toggleSidebar = () => {
  emit("toggleSidebar");
};

const logout = () => {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  localStorage.removeItem("isAuthenticated");
  localStorage.removeItem("userData");

  router.replace("/auth/login/");
};

// Must match the sidebar width in Sidebar.vue (5 units collapsed / 17.5 expanded).
// 1 unit = --u = 16px up to 1080p, larger on big screens (defined in .header-bar below).
const headerStyle = computed(() => ({
  marginLeft: props.sidebarCollapsed ? "calc(5 * var(--u))" : "calc(17.5 * var(--u))",
  transition: "margin-left 0.3s ease",
}));

let pollId = null;

onMounted(() => {
  fetchNotifCount();

  if (showAdminNotifications.value) {
    pollId = setInterval(fetchNotifCount, 20000);
    window.addEventListener("alerts:newReport", fetchNotifCount);
  }
});

onBeforeUnmount(() => {
  if (pollId) clearInterval(pollId);
  window.removeEventListener("alerts:newReport", fetchNotifCount);
});
</script>

<style scoped>
.user-profile:hover {
  opacity: 0.85;
}
/* ===== LARGE-SCREEN / TV SCALING =====
   Same unit as Sidebar.vue and Dashboard.vue: 16px up to 1080p (unchanged
   look), larger on bigger screens, following the smaller of width/height so
   any TV ratio fits. First value is a fallback for old TV browsers. */
.header-bar {
  --u: 16px;
  font-size: var(--u);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--u) calc(2 * var(--u));
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(calc(1.25 * var(--u)));
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  position: sticky;
  top: 0;
  z-index: 1030;
  transition: margin-left 0.3s ease;
}

@supports (font-size: clamp(16px, min(1vw, 1vh), 48px)) {
  .header-bar {
    --u: clamp(16px, min(0.8333vw, 1.4815vh), 48px);
  }
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--u);
  flex: 1;
  max-width: calc(43.75 * var(--u));
}

.sidebar-toggle {
  font-size: calc(0.8333 * var(--u));
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: calc(0.75 * var(--u)) var(--u);
  border-radius: calc(0.625 * var(--u));
  display: flex;
  align-items: center;
  gap: calc(0.75 * var(--u));
  cursor: pointer;
  transition: all 0.3s ease;
  color: var(--text);
  text-decoration: none;
}

.sidebar-toggle:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: scale(1.02);
  box-shadow: 0 calc(0.25 * var(--u)) calc(0.75 * var(--u)) rgba(14, 165, 255, 0.2);
}

.toggle-icon {
  display: flex;
  flex-direction: column;
  gap: calc(0.1875 * var(--u));
  width: calc(1.125 * var(--u));
  transition: all 0.3s ease;
}

.toggle-icon span {
  height: calc(0.125 * var(--u));
  background: var(--text);
  border-radius: 1px;
  transition: all 0.3s ease;
}

.toggle-icon span:nth-child(1) { width: 100%; }
.toggle-icon span:nth-child(2) { width: calc(0.875 * var(--u)); }
.toggle-icon span:nth-child(3) { width: calc(0.625 * var(--u)); }

.toggle-icon-collapsed span {
  width: 100% !important;
}

.toggle-text {
  font-weight: 600;
  font-size: calc(0.9 * var(--u));
  white-space: nowrap;
}

.search-container {
  display: flex;
  align-items: center;
  flex: 1;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: calc(0.75 * var(--u));
  overflow: hidden;
  transition: all 0.3s ease;
}

.search-container:focus-within {
  border-color: rgba(14, 165, 255, 0.5);
  box-shadow: 0 0 0 calc(0.125 * var(--u)) rgba(14, 165, 255, 0.1);
}

.search-icon {
  padding: 0 var(--u);
  color: var(--muted);
  font-size: calc(1.1 * var(--u));
}

.search-input {
  flex: 1;
  padding: calc(0.75 * var(--u)) 0;
  background: transparent;
  border: none;
  color: var(--text);
  font-size: calc(0.9 * var(--u));
  outline: none;
}

.search-input::placeholder {
  color: var(--muted);
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--u);
}

.header-actions {
  display: flex;
  align-items: center;
}

.quick-add-btn {
  background: linear-gradient(135deg, #0ea5ff, #0284c7);
  border: none;
  color: white;
  padding: calc(0.6 * var(--u)) calc(1.2 * var(--u));
  border-radius: calc(0.5 * var(--u));
  cursor: pointer;
  font-weight: 600;
  font-size: calc(0.85 * var(--u));
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: calc(0.5 * var(--u));
  white-space: nowrap;
}

.quick-add-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 calc(0.3125 * var(--u)) calc(0.9375 * var(--u)) rgba(14, 165, 255, 0.4);
}

.add-icon {
  font-size: calc(1.1 * var(--u));
  font-weight: bold;
}

.header-notifications {
  position: relative;
}

.notification-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  width: calc(2.5 * var(--u));
  height: calc(2.5 * var(--u));
  border-radius: calc(0.625 * var(--u));
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.notification-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: scale(1.05);
}

.notification-icon {
  font-size: calc(1.2 * var(--u));
}

.notification-badge {
  position: absolute;
  top: calc(-0.3125 * var(--u));
  right: calc(-0.3125 * var(--u));
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
  font-size: calc(0.7 * var(--u));
  font-weight: 700;
  width: calc(1.125 * var(--u));
  height: calc(1.125 * var(--u));
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: calc(0.125 * var(--u)) solid var(--background);
}

.user-profile {
  display: flex;
  align-items: center;
  gap: calc(0.75 * var(--u));
  cursor: pointer;
  padding: calc(0.5 * var(--u));
  border-radius: calc(0.625 * var(--u));
  transition: all 0.3s ease;
}

.user-profile:hover {
  background: rgba(255, 255, 255, 0.05);
}

.profile-info {
  text-align: right;
}

.profile-name {
  font-weight: 700;
  color: var(--text);
  font-size: calc(0.9 * var(--u));
}

.profile-role {
  font-size: calc(0.75 * var(--u));
  color: var(--muted);
}

.profile-avatar .avatar {
  width: calc(2.5 * var(--u));
  height: calc(2.5 * var(--u));
  background: linear-gradient(135deg, #8b5cf6, #a855f7);
  border-radius: calc(0.625 * var(--u));
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: white;
  font-size: calc(0.9 * var(--u));
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .header-bar {
    margin-left: 0 !important;
    padding: var(--u);
    flex-direction: column;
    gap: var(--u);
  }

  .header-left {
    max-width: 100%;
    width: 100%;
  }

  .sidebar-toggle {
    padding: calc(0.5 * var(--u)) calc(0.75 * var(--u));
  }

  .toggle-text {
    font-size: calc(0.8 * var(--u));
  }

  .search-container {
    flex: 1;
  }

  .header-right {
    width: 100%;
    justify-content: space-between;
  }

  .quick-add-btn {
    padding: calc(0.5 * var(--u)) var(--u);
    font-size: calc(0.8 * var(--u));
  }

  .profile-info {
    display: none;
  }
}

@media (max-width: 480px) {
  .toggle-text {
    display: none;
  }
  
  .sidebar-toggle {
    padding: calc(0.5 * var(--u));
  }
}

.logout-header-btn {
  font-size: calc(0.8333 * var(--u));
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
  border: none;
  padding: calc(0.65 * var(--u)) var(--u);
  border-radius: calc(0.625 * var(--u));
  font-weight: 700;
  cursor: pointer;
  transition: all 0.25s ease;
}

.logout-header-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 calc(0.375 * var(--u)) calc(1 * var(--u)) rgba(239, 68, 68, 0.35);
}
</style>