<template>
  <div class="hazard-admin">
    <h1>Hazard Reports – Pending Verification</h1>

    <div class="reports-list">
      <div 
        v-for="report in reports"
        :key="report.id"
        class="report-card"
      >
        <h3>{{ report.title }}</h3>
        <p>{{ report.description }}</p>

        <div class="meta">
          <span>Type: {{ report.hazard_type }}</span>
          <span>Severity: {{ report.severity }}</span>
          <span>Location: {{ report.address }}</span>
        </div>

        <div class="actions">
          <button class="approve" @click="approve(report.id)">Approve</button>
          <button class="dismiss" @click="dismiss(report.id)">Dismiss</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";

const reports = ref([]);

async function loadReports() {
  const res = await fetch("http://127.0.0.1:8000/api/hazards/pending");
  reports.value = await res.json();
}

async function approve(id) {
  await fetch(`http://127.0.0.1:8000/api/hazards/${id}/approve/`, {
    method: "PATCH",
  });
  loadReports();
}

async function dismiss(id) {
  await fetch(`http://127.0.0.1:8000/api/hazards/${id}/dismiss/`, {
    method: "PATCH",
  });
  loadReports();
}

onMounted(loadReports);
</script>
