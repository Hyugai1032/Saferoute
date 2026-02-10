<template>
  <div style="padding: 20px;">
    <div class="header-actions">
      <button class="logout-btn" @click="logout">
        <i class="icon-logout"></i>
        Logout
      </button>
    </div>

    <h1>Staff Dashboard</h1>
    <p>Quick access for evacuation staff (centers + logs).</p>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";

const router = useRouter();

const logout = () => {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  localStorage.removeItem("isAuthenticated");
  localStorage.removeItem("userData");

  router.push("/auth/login");
  // or: router.replace("/auth/login"); // prevents going back
};
</script>
