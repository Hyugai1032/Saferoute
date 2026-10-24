<!-- Shows connection state and evacuee records waiting to upload. Hidden when online with nothing pending. -->
<template>
  <div v-if="visible" class="sync-stack" role="status" aria-live="polite">
    <div class="sync-banner" :class="tone">
      <span class="sync-dot" :class="{ spin: s.syncing }"></span>

      <div class="sync-text">
        <strong>{{ title }}</strong>
        <span>{{ detail }}</span>
      </div>

      <div class="sync-actions">
        <button
          v-if="s.pendingCount > 0 && !s.authRequired"
          type="button"
          class="sync-btn"
          :disabled="s.syncing"
          @click="syncNow"
        >
          {{ s.syncing ? 'Uploading…' : 'Sync now' }}
        </button>
        <button
          v-if="s.authRequired"
          type="button"
          class="sync-btn"
          @click="goSignIn"
        >
          Sign in again
        </button>
        <router-link
          v-if="(s.pendingCount || s.failedCount) && $route.path !== '/staff/evacuees'"
          to="/staff/evacuees"
          class="sync-link"
        >
          View
        </router-link>
      </div>
    </div>

    <div v-for="(notice, i) in s.notices" :key="notice" class="sync-banner notice">
      <span class="sync-dot"></span>
      <div class="sync-text"><span>{{ notice }}</span></div>
      <div class="sync-actions">
        <button type="button" class="sync-btn ghost" @click="dismissNotice(i)">Dismiss</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { outboxState as s, syncNow, refreshOutbox, dismissNotice } from '@/offline/evacueeOutbox'

const router = useRouter()

onMounted(() => refreshOutbox())

const visible = computed(() =>
  !s.online || s.pendingCount > 0 || s.failedCount > 0 || s.authRequired || s.notices.length > 0
)

const tone = computed(() => {
  if (s.authRequired || s.failedCount > 0) return 'danger'
  if (!s.online || s.pendingCount > 0) return 'warn'
  return 'ok'
})

const plural = (n, word) => `${n} ${word}${n === 1 ? '' : 's'}`

const title = computed(() => {
  if (s.authRequired) return 'Sign-in expired'
  if (!s.online && s.pendingCount === 0) return 'You are offline'
  if (s.pendingCount > 0) return `${plural(s.pendingCount, 'record')} waiting to upload`
  if (s.failedCount > 0) return `${plural(s.failedCount, 'record')} need attention`
  return 'All records uploaded'
})

const detail = computed(() => {
  if (s.authRequired) return 'Saved records are safe on this phone. Sign in again to upload them.'
  if (s.failedCount > 0 && s.pendingCount === 0) return 'The server could not accept them. Open Evacuees to fix or discard.'
  if (!s.online) return 'You can keep registering evacuees. They are saved on this phone and upload when signal returns.'
  if (s.syncing) return 'Uploading now…'
  return s.lastError || 'Uploading automatically when the connection allows.'
})

function goSignIn() {
  // Logging out keeps the saved records (they live in IndexedDB, not localStorage).
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('isAuthenticated')
  router.push('/auth/login/')
}
</script>

<style scoped>
.sync-stack {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px clamp(12px, 3vw, 32px) 0;
}

.sync-banner {
  --tone: #38bdf8;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 14px;
  border: 1px solid color-mix(in srgb, var(--tone) 45%, transparent);
  background: color-mix(in srgb, var(--tone) 12%, rgba(6, 9, 18, 0.9));
  color: #e5e7eb;
}

html[data-theme="light"] .sync-banner {
  background: color-mix(in srgb, var(--tone) 12%, #ffffff);
  color: #0f172a;
}

.sync-banner.warn { --tone: #fbbf24; }
.sync-banner.danger { --tone: #fb7185; }
.sync-banner.ok { --tone: #34d399; }
.sync-banner.notice { --tone: #a78bfa; }

.sync-dot {
  flex: 0 0 auto;
  width: 12px;
  height: 12px;
  border-radius: 999px;
  background: var(--tone);
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--tone) 22%, transparent);
}

.sync-dot.spin {
  background: transparent;
  border: 2px solid var(--tone);
  border-top-color: transparent;
  animation: sync-spin 0.9s linear infinite;
}

@keyframes sync-spin { to { transform: rotate(360deg); } }

.sync-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
  flex: 1;
  font-size: 13px;
  line-height: 1.4;
}

.sync-text strong { font-size: 14px; }
.sync-text span { opacity: 0.82; }

.sync-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.sync-btn,
.sync-link {
  min-height: 40px; /* comfortable tap target on phones */
  padding: 8px 14px;
  border-radius: 10px;
  border: 1px solid color-mix(in srgb, var(--tone) 55%, transparent);
  background: color-mix(in srgb, var(--tone) 22%, transparent);
  color: inherit;
  font-weight: 800;
  font-size: 13px;
  cursor: pointer;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
}

.sync-btn.ghost { background: transparent; }
.sync-btn:disabled { opacity: 0.6; cursor: wait; }

@media (max-width: 560px) {
  .sync-banner { flex-wrap: wrap; }
  .sync-actions { width: 100%; }
  .sync-btn, .sync-link { flex: 1; justify-content: center; }
}

@media (prefers-reduced-motion: reduce) {
  .sync-dot.spin { animation: none; }
}
</style>