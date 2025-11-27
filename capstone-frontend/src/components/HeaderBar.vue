<template>
  <header class="header-bar" :style="headerStyle">
    <div class="header-left">
      <button v-if="isMobile" @click="toggleSidebar" class="sidebar-toggle" aria-label="toggle sidebar">
        <div class="toggle-icon" :class="{ 'toggle-icon-collapsed': sidebarCollapsed }">
          <span></span>
          <span></span>
          <span></span>
        </div>
        <span class="toggle-text" v-if="sidebarCollapsed"> Menu</span>
      </button>
      <div class="search-container">
        <div class="search-icon">🔍</div>
        <input 
          v-model="searchQuery" 
          @input="handleSearch" 
          placeholder="Search evacuees, centers, or items..." 
          class="search-input"
        />
      </div>
    </div>
    
    <div class="header-right">
      <div class="header-actions">
        <button class="quick-add-btn" @click="openQuickAdd">
          <span class="add-icon">+</span>
          Quick Add
        </button>
      </div>
      <div class="header-notifications">
        <button class="notification-btn" @click="toggleNotifications">
          <div class="notification-icon">🔔</div>
          <div class="notification-badge">3</div>
        </button>
      </div>
      <div class="user-profile">
        <div class="profile-info">
          <div class="profile-name">{{ user?.first_name }} {{ user?.last_name }}</div>
          <div class="profile-role">{{ user?.role }}</div>
        </div>
        <div class="profile-avatar">
          <div class="avatar">{{ (user?.first_name?.[0] || '') + (user?.last_name?.[0] || '') }}</div>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed } from 'vue';

const user = ref(JSON.parse(localStorage.getItem("userData")));

const searchQuery = ref('');

const emit = defineEmits(['search', 'toggleSidebar']);

const handleSearch = () => {
  emit('search', searchQuery.value);
};

const openQuickAdd = () => {
  alert('Quick add functionality - Add new evacuee, center, or alert');
};

const toggleNotifications = () => {
  alert('Notifications panel would open here');
};

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