<!--
  PublicGISMap.vue

  Wraps the layout-agnostic GISMap.vue with the public NavBar for guests
  arriving from the landing page (e.g. router path "/gis-map").

  Point ONLY the public route at this component. Your authenticated
  dashboard route should keep rendering GISMap.vue directly inside its own
  layout (sidebar/topbar), so logged-in users never see this navbar.

  Example router setup:

    { path: '/gis-map', component: () => import('./PublicGISMap.vue') },       // guests
    {
      path: '/dashboard/gis-map',
      component: () => import('./GISMap.vue'),                                  // inside DashboardLayout
      meta: { requiresAuth: true },
    },
-->
<template>
  <div class="public-map-page">
    <IndexNavBar />
    <GISMap />
  </div>
</template>

<script setup>
import IndexNavBar from '../components/IndexNavBar.vue';
import GISMap from './GISMap.vue'
</script>

<style scoped>
.public-map-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
}
</style>
