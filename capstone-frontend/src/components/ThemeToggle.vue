<!-- src/components/ThemeToggle.vue -->
<template>
  <button
    class="theme-toggle"
    type="button"
    :aria-label="isLight ? 'Switch to dark mode' : 'Switch to light mode'"
    :title="isLight ? 'Switch to dark mode' : 'Switch to light mode'"
    :aria-pressed="isLight"
    @click="toggleTheme"
  >
    <span class="toggle-track">
      <span class="toggle-thumb">
        <span class="toggle-icon">{{ isLight ? '☀️' : '🌙' }}</span>
      </span>
    </span>
    <span class="toggle-label">{{ isLight ? 'Light' : 'Dark' }}</span>
  </button>
</template>

<script setup>
import { useTheme } from '@/composables/useTheme'

const { isLight, toggleTheme } = useTheme()
</script>

<style scoped>
.theme-toggle {
  display: inline-flex;
  align-items: center;
  gap: 0.65rem;
  border: 1px solid var(--border-light);
  border-radius: 999px;
  padding: 0.42rem 0.7rem;
  background: var(--surface-elevated);
  color: var(--text-primary);
  cursor: pointer;
  font-weight: 800;
  font-size: 0.82rem;
  letter-spacing: -0.01em;
  box-shadow: var(--shadow-soft);
  transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
}

.theme-toggle:hover {
  transform: translateY(-1px);
  border-color: var(--accent-primary);
  box-shadow: var(--shadow-glow);
}

.toggle-track {
  width: 46px;
  height: 24px;
  border-radius: 999px;
  background: var(--toggle-track);
  position: relative;
  display: inline-flex;
  align-items: center;
  padding: 3px;
  box-shadow: inset 0 0 0 1px var(--border-light);
}

.toggle-thumb {
  width: 18px;
  height: 18px;
  border-radius: 999px;
  background: var(--toggle-thumb);
  display: grid;
  place-items: center;
  transform: translateX(var(--toggle-x));
  transition: transform 0.24s cubic-bezier(.2,.8,.2,1), background 0.2s ease;
  box-shadow: 0 6px 14px rgba(2, 8, 23, 0.22);
}

.toggle-icon {
  font-size: 0.72rem;
  line-height: 1;
}

.toggle-label {
  white-space: nowrap;
}

@media (max-width: 560px) {
  .toggle-label {
    display: none;
  }

  .theme-toggle {
    padding: 0.42rem;
  }
}
</style>
