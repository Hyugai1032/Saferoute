<!-- src/App.vue - CLEAN VERSION -->
<template>
  
    <!-- Main Router View -->
    <router-view />
  
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

:root {
  --primary: #1a365d;
  --secondary: #2d3748;
  --accent: #3182ce;
  --danger: #e53e3e;
  --success: #38a169;
  --warning: #dd6b20;
  --light: #f7fafc;
  --dark: #2d3748;
  --text: #f1f5f9;
  --text-light: #718096;
  --muted: #94a3b8;
  --background: #1a1a2e;
  --sidebar-width: 280px;
  --sidebar-collapsed-width: 80px;
}

body {
  background: linear-gradient(135deg, #1a365d 0%, #1a1a2e 100%);
  color: var(--text);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  min-height: 100vh;
  overflow-x: hidden;
}

#app {
  min-height: 100vh;
}

/* Global animations */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}

@keyframes slideIn {
  from { transform: translateX(-100%); }
  to { transform: translateX(0); }
}

@keyframes glow {
  0%, 100% { box-shadow: 0 0 5px rgba(14, 165, 255, 0.3); }
  50% { box-shadow: 0 0 20px rgba(14, 165, 255, 0.6); }
}
</style>