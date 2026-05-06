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
      <button
        v-if="showAdminNotifications"
        class="notification-btn"
        @click="goToHazardReports"
      >
        <div class="notification-icon">🔔</div>
        <div class="notification-badge" v-if="notifCount > 0">
          {{ notifCount }}
        </div>
      </button>
    </div>
  </header>
</template>

<script setup>
import axios from "axios";
import { ref, computed, onMounted, onBeforeUnmount } from "vue";
import { useRouter } from "vue-router";

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
  title: {
    type: String,
    default: "Dashboard",
  },
  subtitle: {
    type: String,
    default: "System overview",
  },
});

const emit = defineEmits(["toggleSidebar"]);

const user = ref(JSON.parse(localStorage.getItem("userData") || "{}"));
const notifCount = ref(0);

const role = computed(() => String(user.value?.role || "").toUpperCase());

const showAdminNotifications = computed(() => {
  return role.value === "ADMIN" || role.value === "PROVINCIAL_ADMIN";
});

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
    console.error("Failed to load notif count:", e);
    notifCount.value = 0;
  }
};

const goToHazardReports = () => {
  router.push({ name: "Hazard Reports" });
};

const toggleSidebar = () => {
  emit("toggleSidebar");
};

const headerStyle = computed(() => ({
  marginLeft: props.sidebarCollapsed ? "80px" : "280px",
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
.header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
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
  max-width: 700px;
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

.search-container {
  display: flex;
  align-items: center;
  flex: 1;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.search-container:focus-within {
  border-color: rgba(14, 165, 255, 0.5);
  box-shadow: 0 0 0 2px rgba(14, 165, 255, 0.1);
}

.search-icon {
  padding: 0 1rem;
  color: var(--muted);
  font-size: 1.1rem;
}

.search-input {
  flex: 1;
  padding: 0.75rem 0;
  background: transparent;
  border: none;
  color: var(--text);
  font-size: 0.9rem;
  outline: none;
}

.search-input::placeholder {
  color: var(--muted);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-actions {
  display: flex;
  align-items: center;
}

.quick-add-btn {
  background: linear-gradient(135deg, #0ea5ff, #0284c7);
  border: none;
  color: white;
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.85rem;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  white-space: nowrap;
}

.quick-add-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 5px 15px rgba(14, 165, 255, 0.4);
}

.add-icon {
  font-size: 1.1rem;
  font-weight: bold;
}

.header-notifications {
  position: relative;
}

.notification-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  width: 40px;
  height: 40px;
  border-radius: 10px;
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
  font-size: 1.2rem;
}

.notification-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
  font-size: 0.7rem;
  font-weight: 700;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid var(--background);
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 10px;
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
  font-size: 0.9rem;
}

.profile-role {
  font-size: 0.75rem;
  color: var(--muted);
}

.profile-avatar .avatar {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #8b5cf6, #a855f7);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: white;
  font-size: 0.9rem;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .header-bar {
    margin-left: 0 !important;
    padding: 1rem;
    flex-direction: column;
    gap: 1rem;
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

  .search-container {
    flex: 1;
  }

  .header-right {
    width: 100%;
    justify-content: space-between;
  }

  .quick-add-btn {
    padding: 0.5rem 1rem;
    font-size: 0.8rem;
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
    padding: 0.5rem;
  }
}
</style>