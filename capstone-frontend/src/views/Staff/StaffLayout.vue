<!-- src/views/Staff/StaffLayout.vue -->
<template>
  <div class="app">
    <StaffSidebar
      ref="sidebarRef"
      :isCollapsed="sidebarCollapsed"
      @toggle="toggleSidebar"
      @mouseenter="handleMouseEnter"
      @mouseleave="handleMouseLeave"
    />

    <div class="staff-layout">
      <HeaderBar
        :sidebarCollapsed="sidebarCollapsed"
        :isMobile="isMobile"
        @toggleSidebar="toggleSidebar"
      />

      <div class="main-content" :style="mainContentStyle">
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
import { ref, computed, onMounted, onBeforeUnmount, watch } from "vue";
import { useRoute } from "vue-router";
import HeaderBar from "@/components/HeaderBar.vue";
import StaffSidebar from "@/components/Staff/StaffSidebar.vue";

const sidebarCollapsed = ref(true);
const route = useRoute();
const isMobile = ref(window.innerWidth <= 768);

const handleResize = () => {
  isMobile.value = window.innerWidth <= 768;
  if (!isMobile.value && !sidebarCollapsed.value) {
    sidebarCollapsed.value = true;
    document.body.style.overflow = "";
  }
};

onMounted(() => window.addEventListener("resize", handleResize));
onBeforeUnmount(() => window.removeEventListener("resize", handleResize));

watch(route, () => {
  if (isMobile.value) {
    sidebarCollapsed.value = true;
    document.body.style.overflow = "";
  }
});

const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value;
  if (isMobile.value) {
    document.body.style.overflow = sidebarCollapsed.value ? "" : "hidden";
  }
};

const closeSidebar = () => {
  sidebarCollapsed.value = true;
  document.body.style.overflow = "";
};

const handleMouseEnter = () => {
  if (!isMobile.value) sidebarCollapsed.value = false;
};

const handleMouseLeave = () => {
  if (!isMobile.value) sidebarCollapsed.value = true;
};

const mainContentStyle = computed(() => ({
  marginLeft: isMobile.value ? "0px" : sidebarCollapsed.value ? "80px" : "280px",
  transition: "margin-left 0.3s ease",
}));
</script>

<style scoped>
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
