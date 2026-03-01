<template>
  <div class="hazard-admin">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1>Pending Hazard Reports</h1>
        <p>Reports awaiting verification and action</p>
      </div>
      <span class="badge">{{ reports.length }} Pending</span>
    </div>

    <!-- States -->
    <div v-if="loading" class="state muted">Loading reports…</div>
    <div v-else-if="errorMsg" class="state error">{{ errorMsg }}</div>
    <div v-else-if="reports.length === 0" class="state muted">
      No pending reports found.
    </div>

    <!-- Reports Grid -->
    <div class="reports-grid">
      <div
        v-for="report in reports"
        :key="report.id"
        class="report-card"
        tabindex="0"
        role="button"
        @click="openPreview(report)"
        @keyup.enter="openPreview(report)"
      >
        <!-- Subtle glow layer -->
        <div class="glow" />

        <!-- Card Header -->
        <div class="card-header">
          <div class="title-wrap">
            <h3 class="title">{{ report.title }}</h3>
            <div class="sub">
              <span class="type">{{ report.hazard_type }}</span>
              <span class="dot">•</span>
              <span class="meta-mini">{{ report.municipality_name || "—" }}</span>
            </div>
          </div>

          <span class="severity" :class="report.severity.toLowerCase()">
            {{ report.severity }}
          </span>
        </div>

        <!-- Description -->
        <p class="description clamp">
          {{ report.description }}
        </p>

        <!-- Meta -->
        <div class="meta">
          <div>
            <span class="label">Location</span>
            <span class="value">{{ report.address }}</span>
          </div>
          <div>
            <span class="label">Report ID</span>
            <span class="value mono">{{ report.id }}</span>
          </div>
        </div>

        <!-- Hover Reveal (Quick Peek) -->
        <div class="peek">
          <div class="peek-row">
            <div class="peek-item">
              <span class="value mono">{{ report.reporter }}</span>
              <!-- ✅ CHANGE THIS FIELD NAME to whatever your backend returns -->
              <span class="value mono">
                {{ report.reporter_id_number || report.user_id_number || report.id_number || "—" }}
              </span>
            </div>

            <div class="peek-item right">
              <span class="label">Photos</span>
              <span class="value">
                <!-- ✅ CHANGE THIS FIELD NAME if needed -->
                {{ (report.photos?.length || report.images?.length || 0) }} attached
              </span>
            </div>
          </div>

          <!-- Thumbnails -->
          <div class="thumbs" v-if="(report.photos?.length || report.images?.length)">
            <button
              v-for="(p, idx) in (report.photos || report.images)"
              :key="p.id || idx"
              type="button"
              class="thumb"
              @click.stop="openLightbox(p.url || p.image || p.photo || p)"
              :title="'Open photo ' + (idx + 1)"
            >
              <img :src="p.url || p.image || p.photo || p" alt="Hazard photo" />
            </button>
          </div>

          <div class="peek-hint">
            Click card for full preview →
          </div>
        </div>

        <!-- Actions (don’t trigger openPreview) -->
        <div class="actions" @click.stop>
          <button class="btn approve" @click="approve(report.id)">
            Approve
          </button>
          <button class="btn dismiss" @click="dismiss(report.id)">
            Dismiss
          </button>
        </div>
      </div>
    </div>

    <!-- ===== Preview Drawer / Modal ===== -->
    <div v-if="previewOpen" class="overlay" @click="closePreview">
      <div class="drawer" @click.stop>
        <div class="drawer-top">
          <div>
            <div class="drawer-kicker">Hazard Report Preview</div>
            <div class="drawer-title">{{ selected?.title || "—" }}</div>
            <div class="drawer-sub">
              <span class="chip">{{ selected?.hazard_type || "—" }}</span>
              <span class="dot">•</span>
              <span class="muted">{{ selected?.municipality_name || "—" }}</span>
              <span class="dot">•</span>
              <span class="muted">Report #<span class="mono">{{ selected?.id }}</span></span>
            </div>
          </div>

          <button class="icon-btn" @click="closePreview" aria-label="Close">
            ✕
          </button>
        </div>

        <div class="drawer-body">
          <div class="drawer-grid">
            <div class="panel">
              <div class="panel-title">Details</div>
              <div class="kv">
                <div class="k">Severity</div>
                <div class="v">
                  <span class="severity big" :class="(selected?.severity || '').toLowerCase()">
                    {{ selected?.severity || "—" }}
                  </span>
                </div>

                <div class="k">Location</div>
                <div class="v">{{ selected?.address || "—" }}</div>

                <div class="k">User ID</div>
                <div class="v mono">
                  {{ selected?.reporter_id_number || selected?.user_id_number || selected?.id_number || "—" }}
                </div>

                <div class="k">Description</div>
                <div class="v pre">{{ selected?.description || "—" }}</div>
              </div>

              <div class="drawer-actions">
                <button class="btn approve" @click="approve(selected.id); closePreview()">
                  Approve
                </button>
                <button class="btn dismiss" @click="dismiss(selected.id); closePreview()">
                  Dismiss
                </button>
              </div>
            </div>

            <div class="panel">
              <div class="panel-title">Photos</div>

              <div v-if="(selected?.photos?.length || selected?.images?.length)" class="photo-grid">
                <button
                  v-for="(p, idx) in (selected.photos || selected.images)"
                  :key="p.id || idx"
                  class="photo"
                  type="button"
                  @click="openLightbox(p.url || p.image || p.photo || p)"
                >
                  <img :src="p.url || p.image || p.photo || p" alt="Hazard photo large" />
                </button>
              </div>

              <div v-else class="empty-photos">
                No photos attached.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ===== Lightbox ===== -->
    <div v-if="lightboxUrl" class="lightbox" @click="lightboxUrl = ''">
      <img :src="lightboxUrl" alt="Hazard photo preview" @click.stop />
      <button class="icon-btn lb-close" @click.stop="lightboxUrl = ''" aria-label="Close photo">✕</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "@/services/api";

const reports = ref([]);
const loading = ref(false);
const errorMsg = ref(""); 

// Preview modal
const previewOpen = ref(false);
const selected = ref(null);

// Lightbox
const lightboxUrl = ref("");

// MUST exist because template calls it
function openPreview(report) {
  selected.value = report;
  previewOpen.value = true;
}

function closePreview() {
  previewOpen.value = false;
  selected.value = null;
}

function openLightbox(url) {
  lightboxUrl.value = url;
}

function closeLightbox() {
  lightboxUrl.value = "";
}

function onKey(e) {
  if (e.key === "Escape") {
    if (lightboxUrl.value) closeLightbox();
    else if (previewOpen.value) closePreview();
  }
}


async function loadReports() {
  loading.value = true;
  errorMsg.value = "";
  try {
    const res = await api.get("hazards/", {
      params: { status: "REPORTED" }
    });
    reports.value = res.data;
     // ✅ TEMP DEBUG
    console.log("First report:", reports.value?.[0]);
  } catch (err) {
    errorMsg.value = "Failed to load reports.";
  } finally {
    loading.value = false;
  }
}

async function approve(id) {
  await api.patch(`hazards/${id}/`, { status: "APPROVED" });
  await loadReports();
}

async function dismiss(id) {
  await api.patch(`hazards/${id}/`, { status: "DISMISSED" });
  await loadReports();
}

onMounted(loadReports);
</script>

<style scoped>
.hazard-admin {
  padding: 32px;
  min-height: 100vh;
  background:
    radial-gradient(1200px 600px at 20% 10%, rgba(0,140,255,0.15), transparent 60%),
    radial-gradient(900px 500px at 80% 30%, rgba(0,255,200,0.08), transparent 60%),
    linear-gradient(135deg, #070a12, #0b1022 40%, #070a12);
  color: #eaeaf0;
  font-family: "Inter", system-ui, sans-serif;
}

/* Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: end;
  gap: 16px;
  margin-bottom: 22px;
}
.page-header h1 {
  font-size: 30px;
  font-weight: 800;
  letter-spacing: -0.02em;
}
.page-header p {
  margin-top: 6px;
  color: #98a3c7;
  font-size: 14px;
}

.badge {
  background: linear-gradient(135deg, rgba(0,140,255,0.18), rgba(0,210,255,0.10));
  border: 1px solid rgba(120,190,255,0.18);
  color: #9fd3ff;
  padding: 8px 14px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 700;
  backdrop-filter: blur(12px);
}

/* States */
.state {
  padding: 14px 16px;
  border-radius: 14px;
  margin-bottom: 18px;
  border: 1px solid rgba(255,255,255,0.08);
  backdrop-filter: blur(10px);
}
.state.muted {
  background: rgba(255,255,255,0.035);
  color: #9aa4bf;
}
.state.error {
  background: rgba(255,0,0,0.10);
  color: #ffb4b4;
  border-color: rgba(255,110,110,0.20);
}

/* Grid */
.reports-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 18px;
}

/* Card */
.report-card {
  position: relative;
  overflow: hidden;
  background: rgba(255,255,255,0.045);
  border: 1px solid rgba(255,255,255,0.09);
  border-radius: 20px;
  padding: 20px;
  backdrop-filter: blur(14px);
  display: flex;
  flex-direction: column;
  transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
  cursor: pointer;
  outline: none;
}
.report-card:focus-visible {
  box-shadow: 0 0 0 4px rgba(0,140,255,0.22);
  border-color: rgba(0,140,255,0.35);
}
.report-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 24px 60px rgba(0,0,0,0.48);
  border-color: rgba(120,190,255,0.22);
}

.glow {
  position: absolute;
  inset: -2px;
  background: radial-gradient(500px 200px at 25% 0%, rgba(0,140,255,0.22), transparent 55%);
  opacity: 0;
  transition: opacity .2s ease;
  pointer-events: none;
}
.report-card:hover .glow { opacity: 1; }

.card-header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}
.title-wrap { min-width: 0; }
.title {
  font-size: 18px;
  font-weight: 750;
  margin-bottom: 4px;
  letter-spacing: -0.01em;
}
.sub {
  display: flex;
  gap: 8px;
  align-items: center;
  color: #95a3c7;
  font-size: 12.5px;
}
.dot { opacity: .55; }
.type { color: #9fd3ff; }
.meta-mini { opacity: .9; }

/* Severity chips */
.severity {
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 800;
  align-self: flex-start;
  border: 1px solid rgba(255,255,255,0.10);
  backdrop-filter: blur(10px);
}
.severity.big { font-size: 12px; padding: 7px 12px; }

.severity.low { background: rgba(0,200,120,0.18); color:#56f0b4; border-color: rgba(86,240,180,0.18); }
.severity.medium { background: rgba(255,180,0,0.16); color:#ffd166; border-color: rgba(255,209,102,0.18); }
.severity.high { background: rgba(255,80,80,0.18); color:#ff8a8a; border-color: rgba(255,138,138,0.18); }
.severity.critical { background: rgba(255,0,0,0.22); color:#ff5a5a; border-color: rgba(255,90,90,0.22); }

/* Description */
.description {
  margin: 12px 0 14px;
  font-size: 14px;
  line-height: 1.55;
  color: #d3daf0;
}
.clamp {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Meta */
.meta {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 14px;
}
.label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: .08em;
  color: #7f8ab0;
}
.value {
  font-size: 13px;
  color: #e7ecff;
}
.mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; }

/* Hover Peek */
.peek {
  margin-top: 8px;
  padding-top: 12px;
  border-top: 1px dashed rgba(255,255,255,0.10);
  opacity: 0;
  transform: translateY(8px);
  transition: opacity .18s ease, transform .18s ease;
}
.report-card:hover .peek,
.report-card:focus-visible .peek {
  opacity: 1;
  transform: translateY(0);
}

.peek-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: end;
}
.peek-item.right { text-align: right; }

.thumbs {
  display: flex;
  gap: 10px;
  margin-top: 10px;
  overflow-x: auto;
  padding-bottom: 2px;
}
.thumb {
  width: 58px;
  height: 46px;
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.12);
  background: rgba(255,255,255,0.03);
  overflow: hidden;
  flex: 0 0 auto;
  cursor: pointer;
  transition: transform .15s ease, border-color .15s ease;
}
.thumb:hover {
  transform: translateY(-2px) scale(1.02);
  border-color: rgba(120,190,255,0.30);
}
.thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.peek-hint {
  margin-top: 10px;
  font-size: 12px;
  color: rgba(159, 211, 255, 0.85);
}

/* Actions */
.actions {
  display: flex;
  gap: 12px;
  margin-top: 14px;
}
.btn {
  flex: 1;
  padding: 12px;
  border-radius: 14px;
  font-weight: 800;
  cursor: pointer;
  border: none;
  transition: transform .12s ease, box-shadow .18s ease, filter .18s ease;
}
.btn:active { transform: translateY(1px); }

.btn.approve {
  background: linear-gradient(135deg, #00d0ff, #2a6bff);
  color: #041022;
}
.btn.approve:hover { box-shadow: 0 0 0 4px rgba(0,140,255,0.22); filter: brightness(1.05); }

.btn.dismiss {
  background: linear-gradient(135deg, #ff6b6b, #ff3d8d);
  color: #26000c;
}
.btn.dismiss:hover { box-shadow: 0 0 0 4px rgba(255, 90, 140, 0.20); filter: brightness(1.05); }

/* Overlay + Drawer */
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.65);
  backdrop-filter: blur(10px);
  display: grid;
  place-items: center;
  z-index: 80;
  padding: 20px;
}

.drawer {
  width: min(1100px, 96vw);
  max-height: 88vh;
  overflow: auto;
  border-radius: 22px;
  background: linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.035));
  border: 1px solid rgba(255,255,255,0.12);
  box-shadow: 0 30px 90px rgba(0,0,0,0.55);
}

.drawer-top {
  display: flex;
  justify-content: space-between;
  align-items: start;
  gap: 12px;
  padding: 18px 18px 12px;
  border-bottom: 1px solid rgba(255,255,255,0.10);
}

.drawer-kicker {
  font-size: 12px;
  letter-spacing: .12em;
  text-transform: uppercase;
  color: #94a4cf;
}
.drawer-title {
  font-size: 22px;
  font-weight: 850;
  margin-top: 6px;
}
.drawer-sub {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
  margin-top: 8px;
  color: #97a6cc;
  font-size: 13px;
}
.chip {
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(0,140,255,0.14);
  border: 1px solid rgba(120,190,255,0.18);
  color: #9fd3ff;
  font-weight: 800;
}

.icon-btn {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.12);
  background: rgba(255,255,255,0.04);
  color: #eaf1ff;
  cursor: pointer;
  transition: transform .12s ease, border-color .12s ease;
}
.icon-btn:hover { transform: translateY(-1px); border-color: rgba(120,190,255,0.25); }

.drawer-body { padding: 16px 18px 20px; }

.drawer-grid {
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  gap: 14px;
}
@media (max-width: 900px) {
  .drawer-grid { grid-template-columns: 1fr; }
}

.panel {
  border-radius: 18px;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.10);
  padding: 14px;
}
.panel-title {
  font-weight: 850;
  margin-bottom: 10px;
  color: #eaf1ff;
  letter-spacing: -0.01em;
}

.kv {
  display: grid;
  grid-template-columns: 120px 1fr;
  gap: 10px 12px;
  align-items: start;
  font-size: 13px;
  color: #dbe4ff;
}
.k { color: #97a6cc; text-transform: uppercase; letter-spacing: .08em; font-size: 11px; margin-top: 2px; }
.v { color: #eaf1ff; }
.pre { white-space: pre-wrap; line-height: 1.6; color: #dbe4ff; }

.drawer-actions {
  display: flex;
  gap: 12px;
  margin-top: 14px;
}

.photo-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}
.photo {
  border: 1px solid rgba(255,255,255,0.12);
  background: rgba(255,255,255,0.03);
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  padding: 0;
}
.photo img {
  width: 100%;
  height: 210px;
  object-fit: cover;
  display: block;
  transition: transform .18s ease;
}
.photo:hover img { transform: scale(1.03); }

.empty-photos {
  color: #97a6cc;
  padding: 12px;
  border-radius: 14px;
  background: rgba(255,255,255,0.03);
  border: 1px dashed rgba(255,255,255,0.10);
}

/* Lightbox */
.lightbox {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.78);
  display: grid;
  place-items: center;
  z-index: 90;
  padding: 18px;
}
.lightbox img {
  max-width: min(1100px, 96vw);
  max-height: 86vh;
  border-radius: 18px;
  border: 1px solid rgba(255,255,255,0.12);
  box-shadow: 0 40px 120px rgba(0,0,0,0.7);
}
.lb-close {
  position: fixed;
  top: 18px;
  right: 18px;
}
</style>