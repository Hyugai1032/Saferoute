<template>
  <main class="legal-page">
    <div class="legal-card">
      <nav class="legal-nav">
        <button type="button" class="legal-back" @click="goBack">
          <i class="fas fa-arrow-left"></i> Back
        </button>
        <div class="legal-switch">
          <router-link to="/terms" class="legal-tab">Terms of Service</router-link>
          <router-link to="/privacy" class="legal-tab">Privacy Policy</router-link>
        </div>
      </nav>

      <header class="legal-header">
        <p class="legal-kicker">{{ appName }}</p>
        <h1>{{ title }}</h1>
        <p class="legal-date">Effective {{ effectiveDate }}</p>
      </header>

      <article class="legal-body">
        <slot />
      </article>
    </div>
  </main>
</template>

<script setup>
import { useRouter } from "vue-router";
import { LEGAL_INFO } from "@/data/legalInfo";

defineProps({
  title: { type: String, required: true },
  effectiveDate: { type: String, required: true },
});

const appName = LEGAL_INFO.appName;
const router = useRouter();

// Opened in a new tab from the register page there is no history, so fall back.
function goBack() {
  if (window.history.length > 1) router.back();
  else router.push("/auth/register");
}
</script>

<style scoped>
.legal-page {
  min-height: 100vh;
  padding: 2rem 1rem 4rem;
  background: var(--page-bg, var(--background, #0f172a));
  color: var(--text, #e2e8f0);
}

.legal-card {
  max-width: 820px;
  margin: 0 auto;
  padding: 2rem 2.25rem 2.5rem;
  border-radius: 18px;
  background: var(--surface, rgba(15, 23, 42, 0.74));
  border: 1px solid var(--border-light, rgba(148, 163, 184, 0.16));
  box-shadow: var(--shadow-card, 0 20px 60px rgba(0, 0, 0, 0.34));
}

.legal-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 1.75rem;
}

.legal-back {
  background: none;
  border: none;
  color: var(--accent, #0ea5ff);
  font: inherit;
  cursor: pointer;
  padding: 0;
}

.legal-switch {
  display: flex;
  gap: 0.5rem;
}

.legal-tab {
  padding: 0.4rem 0.85rem;
  border-radius: 999px;
  font-size: 0.85rem;
  text-decoration: none;
  color: var(--text-muted, #94a3b8);
  border: 1px solid var(--border-light, rgba(148, 163, 184, 0.16));
}

.legal-tab.router-link-active {
  color: #04111f;
  background: var(--accent, #0ea5ff);
  border-color: transparent;
  font-weight: 600;
}

.legal-header {
  border-bottom: 1px solid var(--border-light, rgba(148, 163, 184, 0.16));
  padding-bottom: 1.25rem;
  margin-bottom: 1.5rem;
}

.legal-kicker {
  margin: 0;
  font-size: 0.8rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--accent, #0ea5ff);
  font-weight: 600;
}

.legal-header h1 {
  margin: 0.35rem 0;
  font-size: 2rem;
}

.legal-date {
  margin: 0;
  color: var(--text-muted, #94a3b8);
  font-size: 0.9rem;
}

.legal-body {
  line-height: 1.7;
}

.legal-body :deep(h2) {
  font-size: 1.2rem;
  margin: 2rem 0 0.6rem;
}

.legal-body :deep(h3) {
  font-size: 1rem;
  margin: 1.25rem 0 0.4rem;
}

.legal-body :deep(p),
.legal-body :deep(li) {
  color: var(--text-secondary, #cbd5e1);
}

.legal-body :deep(ul) {
  padding-left: 1.25rem;
  margin: 0.4rem 0 0.8rem;
}

.legal-body :deep(li) {
  margin-bottom: 0.35rem;
}

.legal-body :deep(a) {
  color: var(--accent, #0ea5ff);
}

.legal-body :deep(.legal-callout) {
  padding: 0.9rem 1rem;
  border-radius: 12px;
  border-left: 4px solid var(--danger, #e53e3e);
  background: rgba(229, 62, 62, 0.08);
  margin: 1rem 0;
}

.legal-body :deep(table) {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.92rem;
  margin: 0.5rem 0 1rem;
}

.legal-body :deep(th),
.legal-body :deep(td) {
  text-align: left;
  padding: 0.55rem 0.6rem;
  border-bottom: 1px solid var(--border-light, rgba(148, 163, 184, 0.16));
  vertical-align: top;
}

.legal-body :deep(th) {
  color: var(--text, #e2e8f0);
}

@media (max-width: 600px) {
  .legal-card {
    padding: 1.5rem 1.1rem 2rem;
  }
  .legal-header h1 {
    font-size: 1.6rem;
  }
  .legal-body :deep(table) {
    display: block;
    overflow-x: auto;
  }
}
</style>