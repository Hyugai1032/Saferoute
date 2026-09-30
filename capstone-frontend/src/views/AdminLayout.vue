<template>
  <div class="app">
    <Sidebar 
      ref="sidebarRef" 
      :isCollapsed="sidebarCollapsed" 
      @toggle="toggleSidebar"
      @mouseenter="handleMouseEnter"
      @mouseleave="handleMouseLeave"
    />   

    <div class="admin-layout">
      <HeaderBar 
        :sidebarCollapsed="sidebarCollapsed" 
        :isMobile="isMobile"
        @toggleSidebar="toggleSidebar"
      />

      <!-- Main content area -->
      <div class="main-content" :style="mainContentStyle">
        <!-- ✅ Child pages (dashboard, analytics, etc.) will render here -->
        <router-view />
      </div>

      <div 
        v-if="isMobile && !sidebarCollapsed" 
        class="backdrop" 
        @click="closeSidebar"
      ></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import Sidebar from '@/components/Sidebar.vue'
import HeaderBar from '@/components/HeaderBar.vue'
import { useRoute } from 'vue-router'

const sidebarCollapsed = ref(true)
const route = useRoute()
const isMobile = ref(window.innerWidth <= 768)

// Handle resize
const handleResize = () => {
  isMobile.value = window.innerWidth <= 768
  if (!isMobile.value && !sidebarCollapsed.value) {
    sidebarCollapsed.value = true
    document.body.style.overflow = ''
  }
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
})

// Watch for route change
watch(route, () => {
  if (isMobile.value) {
    sidebarCollapsed.value = true
    document.body.style.overflow = ''
  }
})

// Handle toggle from logo click or menu button
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
  if (isMobile.value) {
    document.body.style.overflow = sidebarCollapsed.value ? '' : 'hidden'
  }
}

// Close sidebar
const closeSidebar = () => {
  sidebarCollapsed.value = true
  document.body.style.overflow = ''
}

// Handle mouse events for desktop
const handleMouseEnter = () => {
  if (!isMobile.value) {
    sidebarCollapsed.value = false
  }
}

const handleMouseLeave = () => {
  if (!isMobile.value) {
    sidebarCollapsed.value = true
  }
}

const mainContentStyle = computed(() => ({
  // Must match the sidebar widths in Sidebar.vue: 5 units collapsed / 17.5 expanded.
  // (1 unit = --u = 16px up to 1080p, larger on big screens; defined on .app below.)
  marginLeft: isMobile.value ? '0px' : (sidebarCollapsed.value ? 'calc(5 * var(--u))' : 'calc(17.5 * var(--u))'),
  transition: 'margin-left 0.3s ease'
}))

const layoutStyle = computed(() => ({
  '--sidebar-offset': `${sidebarOffsetPx.value}px`
}))
</script>

<style scoped>
/* ===== LARGE-SCREEN / TV SCALING =====
   Same unit as Sidebar.vue, HeaderBar.vue and Dashboard.vue: 16px up to 1080p
   (unchanged look), larger on big screens, following the smaller of
   width/height so any TV ratio fits. First value is a fallback for old TV
   browsers without min()/clamp(). */
.app {
  --u: 16px;
  min-height: 100vh;
}

@supports (font-size: clamp(16px, min(1vw, 1vh), 48px)) {
  .app {
    --u: clamp(16px, min(0.8333vw, 1.4815vh), 48px);
  }
}

.admin-layout {
  margin-left: var(--sidebar-offset, 0px);
  width: calc(100% - var(--sidebar-offset, 0px));
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  transition: margin-left 0.3s ease, width 0.3s ease;
}

.main-content {
  flex: 1;
  min-width: 0; /* prevents weird spacing/overflow in grids */
  /* Column flex so a page (e.g. the dashboard) can fill the height left
     under the header instead of adding its own 100vh on top of it. */
  display: flex;
  flex-direction: column;
}

.backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
  z-index: 1040;
}
</style>