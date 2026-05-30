// src/composables/useTheme.js
import { computed, ref } from 'vue'

const STORAGE_KEY = 'saferoute-theme'
const DEFAULT_THEME = 'dark'
const theme = ref(DEFAULT_THEME)

const canUseDOM = () => typeof window !== 'undefined' && typeof document !== 'undefined'

const getSavedTheme = () => {
  if (!canUseDOM()) return DEFAULT_THEME
  const saved = localStorage.getItem(STORAGE_KEY)
  return saved === 'light' || saved === 'dark' ? saved : DEFAULT_THEME
}

const applyTheme = (value) => {
  if (!canUseDOM()) return

  const safeTheme = value === 'light' ? 'light' : 'dark'
  theme.value = safeTheme

  document.documentElement.setAttribute('data-theme', safeTheme)
  document.body.setAttribute('data-theme', safeTheme)
  document.documentElement.style.colorScheme = safeTheme
  localStorage.setItem(STORAGE_KEY, safeTheme)

  window.dispatchEvent(new CustomEvent('saferoute:theme-change', {
    detail: { theme: safeTheme }
  }))
}

const initTheme = () => {
  applyTheme(getSavedTheme())
}

const setTheme = (value) => applyTheme(value)
const toggleTheme = () => applyTheme(theme.value === 'dark' ? 'light' : 'dark')

export function useTheme() {
  return {
    theme,
    isLight: computed(() => theme.value === 'light'),
    isDark: computed(() => theme.value === 'dark'),
    initTheme,
    setTheme,
    toggleTheme,
  }
}

export { initTheme, setTheme, toggleTheme, theme }
