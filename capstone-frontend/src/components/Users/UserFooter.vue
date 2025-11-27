<!-- components/Users/UserFooter.vue -->
<template>
  <footer class="user-footer">
    <div class="footer-content">
      <p>&copy; 2024 Emergency Response System. All rights reserved.</p>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'UserFooter'
}
</script>

<style scoped>
.user-footer {
  background: rgba(15, 15, 20, 0.9);
  backdrop-filter: blur(10px);
  padding: 1rem 2rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  text-align: center;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
}

.user-footer p {
  color: #888;
  margin: 0;
}
</style>