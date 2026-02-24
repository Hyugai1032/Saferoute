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
      >
        <!-- Card Header -->
        <div class="card-header">
          <div>
            <h3>{{ report.title }}</h3>
            <span class="type">{{ report.hazard_type }}</span>
          </div>

          <span
            class="severity"
            :class="report.severity.toLowerCase()"
          >
            {{ report.severity }}
          </span>
        </div>

        <!-- Description -->
        <p class="description">
          {{ report.description }}
        </p>

        <!-- Meta -->
        <div class="meta">
          <div>
            <span class="label">Location</span>
            <span class="value">{{ report.address }}</span>
          </div>
          <div>
            <span class="label">Municipality</span>
            <span class="value">{{ report.municipality_name || "—" }}</span>
          </div>
        </div>

        <!-- Actions -->
        <div class="actions">
          <button class="btn approve" @click="approve(report.id)">
            Approve
          </button>
          <button class="btn dismiss" @click="dismiss(report.id)">
            Dismiss
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "@/services/api";

const reports = ref([]);
const loading = ref(false);
const errorMsg = ref("");

async function loadReports() {
  loading.value = true;
  errorMsg.value = "";
  try {
    const res = await api.get("hazards/", {
      params: { status: "REPORTED" }
    });
    reports.value = res.data;
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
/* ===== Layout ===== */
.hazard-admin {
  padding: 32px;
  min-height: 100vh;
  background: linear-gradient(135deg, #0b0f1a, #12182b);
  color: #eaeaf0;
  font-family: "Inter", system-ui, sans-serif;
}

/* ===== Header ===== */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
}

.page-header h1 {
  font-size: 28px;
  font-weight: 700;
}

.page-header p {
  margin-top: 4px;
  color: #9aa4bf;
  font-size: 14px;
}

.badge {
  background: rgba(0, 150, 255, 0.15);
  color: #66b7ff;
  padding: 6px 14px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 600;
}

/* ===== States ===== */
.state {
  padding: 16px;
  border-radius: 12px;
  margin-bottom: 20px;
}

.state.muted {
  background: rgba(255,255,255,0.04);
  color: #9aa4bf;
}

.state.error {
  background: rgba(255,0,0,0.12);
  color: #ffb4b4;
}

/* ===== Grid ===== */
.reports-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 22px;
}

/* ===== Card ===== */
.report-card {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 18px;
  padding: 22px;
  backdrop-filter: blur(12px);
  display: flex;
  flex-direction: column;
  transition: transform .2s ease, box-shadow .2s ease;
}

.report-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 40px rgba(0,0,0,0.35);
}

/* ===== Card Header ===== */
.card-header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.card-header h3 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 4px;
}

.type {
  font-size: 12px;
  color: #8ecbff;
}

/* ===== Severity ===== */
.severity {
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  align-self: flex-start;
}

.severity.low { background: rgba(0,200,120,0.2); color:#45e6a1; }
.severity.medium { background: rgba(255,180,0,0.2); color:#ffd166; }
.severity.high { background: rgba(255,80,80,0.25); color:#ff7b7b; }
.severity.critical { background: rgba(255,0,0,0.3); color:#ff4d4d; }

/* ===== Description ===== */
.description {
  margin: 14px 0;
  font-size: 14px;
  line-height: 1.5;
  color: #cfd6e6;
}

/* ===== Meta ===== */
.meta {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 18px;
}

.label {
  font-size: 11px;
  text-transform: uppercase;
  color: #8a94ad;
}

.value {
  font-size: 13px;
}

/* ===== Actions ===== */
.actions {
  display: flex;
  gap: 12px;
  margin-top: auto;
}

.btn {
  flex: 1;
  padding: 12px;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all .2s ease;
}

.btn.approve {
  background: linear-gradient(135deg, #00c896, #00a97a);
  color: #05261b;
}

.btn.approve:hover {
  box-shadow: 0 0 0 3px rgba(0,200,150,0.25);
}

.btn.dismiss {
  background: linear-gradient(135deg, #ff6b6b, #d64545);
  color: #2b0000;
}

.btn.dismiss:hover {
  box-shadow: 0 0 0 3px rgba(255,100,100,0.25);
}
</style>
