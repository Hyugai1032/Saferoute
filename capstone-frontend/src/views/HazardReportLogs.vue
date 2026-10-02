<template>
  <div class="hazard-logs">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1>Hazard Report Logs</h1>
        <p>History of approved, dismissed, reopened and deleted hazard reports</p>
      </div>
      <div class="header-actions">
        <span class="badge">{{ count }} Entr{{ count !== 1 ? "ies" : "y" }}</span>
        <button
          class="export-btn"
          type="button"
          :disabled="exporting || loading || count === 0"
          :title="count === 0 ? 'Nothing to export' : 'Download all entries matching the current filters'"
          @click="exportToExcel"
        >
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor"
               stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M12 3v12" /><path d="M7 11l5 5 5-5" /><path d="M5 21h14" />
          </svg>
          {{ exporting ? "Exporting…" : "Export to Excel" }}
        </button>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters">
      <div class="filter-group grow">
        <label for="logSearch">Search</label>
        <input
          id="logSearch"
          v-model="filters.q"
          type="text"
          placeholder="Report title, ID, address, reporter or staff name"
          @input="onSearchInput"
        />
      </div>

      <div class="filter-group">
        <label for="actionFilter">Action</label>
        <select id="actionFilter" v-model="filters.action" @change="applyFilters">
          <option value="all">All</option>
          <option value="APPROVED">Approved</option>
          <option value="DISMISSED">Dismissed</option>
          <option value="REPORTED">Marked as pending</option>
          <option value="DELETED">Deleted</option>
        </select>
      </div>

      <div class="filter-group">
        <label for="severityFilter">Severity</label>
        <select id="severityFilter" v-model="filters.severity" @change="applyFilters">
          <option value="all">All</option>
          <option value="LOW">Low</option>
          <option value="MEDIUM">Medium</option>
          <option value="HIGH">High</option>
          <option value="CRITICAL">Critical</option>
        </select>
      </div>

      <div class="filter-group">
        <label for="dateFrom">From</label>
        <input id="dateFrom" v-model="filters.date_from" type="date" @change="applyFilters" />
      </div>

      <div class="filter-group">
        <label for="dateTo">To</label>
        <input id="dateTo" v-model="filters.date_to" type="date" @change="applyFilters" />
      </div>

      <button class="reset-btn" type="button" @click="resetFilters">Reset</button>
    </div>

    <!-- States -->
    <div v-if="loading" class="state muted">Loading logs…</div>
    <div v-else-if="errorMsg" class="state error">{{ errorMsg }}</div>
    <div v-else-if="logs.length === 0" class="state muted">
      No log entries found for the selected filters.
    </div>

    <!-- Table -->
    <div v-if="logs.length" class="table-wrap">
      <table class="log-table">
        <thead>
          <tr>
            <th>When</th>
            <th>Report</th>
            <th>Severity</th>
            <th>Action</th>
            <th>Done by</th>
            <th>Municipality</th>
          </tr>
        </thead>

        <tbody>
          <template v-for="log in logs" :key="log.id">
            <tr
              class="row"
              :class="{ open: expandedId === log.id }"
              tabindex="0"
              @click="toggle(log.id)"
              @keyup.enter="toggle(log.id)"
            >
              <td class="nowrap">{{ formatDateTime(log.acted_at) }}</td>

              <td>
                <div class="report-title">{{ log.report_title || "Untitled report" }}</div>
                <div class="report-sub">
                  <span class="mono">#{{ log.report_ref_id }}</span>
                  <span v-if="log.report_hazard_type" class="dot">•</span>
                  <span v-if="log.report_hazard_type" class="type">{{ log.report_hazard_type }}</span>
                </div>
              </td>

              <td>
                <span
                  v-if="log.report_severity"
                  class="severity"
                  :class="log.report_severity.toLowerCase()"
                >
                  {{ log.report_severity }}
                </span>
                <span v-else class="muted-text">—</span>
              </td>

              <td>
                <span class="action-chip" :class="actionClass(log.action)">
                  {{ log.action_label }}
                </span>
              </td>

              <td>
                <div class="who">{{ log.acted_by_name || "Unknown user" }}</div>
                <div class="report-sub">{{ roleLabel(log.acted_by_role) }}</div>
              </td>

              <td>{{ log.municipality_name || "—" }}</td>
            </tr>

            <!-- Details -->
            <tr v-if="expandedId === log.id" class="details-row">
              <td colspan="6">
                <div class="details">
                  <div class="detail-block wide">
                    <span class="label">Description</span>
                    <p>{{ log.report_description || "No description." }}</p>
                  </div>

                  <div class="detail-block">
                    <span class="label">Location</span>
                    <p>{{ log.report_address || "—" }}</p>
                  </div>

                  <div class="detail-block">
                    <span class="label">Reported by</span>
                    <p>{{ log.reporter_name || "—" }}</p>
                  </div>

                  <div class="detail-block">
                    <span class="label">Status change</span>
                    <p>
                      {{ statusLabel(log.previous_status) }}
                      <span class="arrow">→</span>
                      {{ log.action === "DELETED" ? "Deleted" : statusLabel(log.action) }}
                    </p>
                  </div>

                  <div v-if="!log.report_exists && log.action !== 'DELETED'" class="detail-block">
                    <span class="label">Note</span>
                    <p>This report has since been deleted.</p>
                  </div>
                </div>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="pager">
      <button type="button" :disabled="page <= 1 || loading" @click="goTo(page - 1)">← Previous</button>
      <span>Page {{ page }} of {{ totalPages }}</span>
      <button type="button" :disabled="page >= totalPages || loading" @click="goTo(page + 1)">Next →</button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount } from "vue";
import api from "@/services/api";

const logs = ref([]);
const loading = ref(false);
const errorMsg = ref("");

const page = ref(1);
const pageSize = 20;
const count = ref(0);
const totalPages = ref(1);

const expandedId = ref(null);
const exporting = ref(false);

const filters = reactive({
  q: "",
  action: "all",
  severity: "all",
  date_from: "",
  date_to: "",
});

const ROLE_LABELS = {
  PROVINCIAL_ADMIN: "Provincial Admin",
  MUNICIPAL_ADMIN: "Municipal Admin",
  EVAC_CENTER_STAFF: "Evacuation Center Staff",
  RESPONSE_TEAM: "Response Team",
};

const STATUS_LABELS = {
  REPORTED: "Pending",
  APPROVED: "Approved",
  DISMISSED: "Dismissed",
};

function roleLabel(role) {
  return ROLE_LABELS[role] || role || "—";
}

function statusLabel(status) {
  return STATUS_LABELS[status] || status || "—";
}

function actionClass(action) {
  return {
    APPROVED: "approved",
    DISMISSED: "dismissed",
    REPORTED: "reopened",
    DELETED: "deleted",
  }[action] || "";
}

function formatDateTime(iso) {
  if (!iso) return "—";
  return new Date(iso).toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

function toggle(id) {
  expandedId.value = expandedId.value === id ? null : id;
}

// Current filters as query params (shared by the table and the Excel export).
function filterParams() {
  const params = {};
  if (filters.q.trim()) params.q = filters.q.trim();
  if (filters.action !== "all") params.action = filters.action;
  if (filters.severity !== "all") params.severity = filters.severity;
  if (filters.date_from) params.date_from = filters.date_from;
  if (filters.date_to) params.date_to = filters.date_to;
  return params;
}

async function loadLogs() {
  loading.value = true;
  errorMsg.value = "";

  try {
    const params = { page: page.value, page_size: pageSize, ...filterParams() };

    const res = await api.get("hazard-logs/", { params });

    logs.value = res.data.results;
    count.value = res.data.count;
    totalPages.value = res.data.total_pages;
    expandedId.value = null;
  } catch (err) {
    console.error(err);
    logs.value = [];
    count.value = 0;
    totalPages.value = 1;
    errorMsg.value =
      err?.response?.data?.detail ||
      Object.values(err?.response?.data || {})[0] ||
      "Failed to load hazard report logs.";
  } finally {
    loading.value = false;
  }
}

// With responseType "blob", error bodies arrive as a Blob too, so read the message out of it.
async function exportErrorMessage(err) {
  try {
    const data = err?.response?.data;
    if (data instanceof Blob) {
      const body = JSON.parse(await data.text());
      return body.detail || Object.values(body)[0];
    }
  } catch {
    /* fall through */
  }
  return err?.response?.data?.detail || "Failed to export hazard report logs.";
}

async function exportToExcel() {
  if (exporting.value) return;
  exporting.value = true;

  try {
    // Exports every entry matching the filters, not just the page on screen.
    const res = await api.get("hazard-logs/export/", {
      params: filterParams(),
      responseType: "blob",
    });

    const today = new Date().toISOString().slice(0, 10);
    const url = URL.createObjectURL(res.data);
    const link = document.createElement("a");
    link.href = url;
    link.download = `Hazard_Report_Logs_${today}.xlsx`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  } catch (err) {
    console.error(err);
    alert(await exportErrorMessage(err));
  } finally {
    exporting.value = false;
  }
}

function applyFilters() {
  page.value = 1;
  loadLogs();
}

// Wait for the user to stop typing before hitting the API.
let searchTimer = null;
function onSearchInput() {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(applyFilters, 350);
}

function resetFilters() {
  filters.q = "";
  filters.action = "all";
  filters.severity = "all";
  filters.date_from = "";
  filters.date_to = "";
  applyFilters();
}

function goTo(n) {
  if (n < 1 || n > totalPages.value) return;
  page.value = n;
  loadLogs();
}

onMounted(loadLogs);
onBeforeUnmount(() => clearTimeout(searchTimer));
</script>

<style scoped>
.hazard-logs {
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
.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}
.export-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border: 1px solid rgba(86,240,180,0.30);
  background: linear-gradient(135deg, rgba(0,200,120,0.22), rgba(0,200,120,0.10));
  color: #56f0b4;
  border-radius: 999px;
  padding: 8px 16px;
  font-size: 13px;
  font-weight: 800;
  cursor: pointer;
  transition: 0.2s ease;
}
.export-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, rgba(0,200,120,0.34), rgba(0,200,120,0.18));
  box-shadow: 0 0 0 4px rgba(86,240,180,0.14);
  transform: translateY(-1px);
}
.export-btn:disabled { opacity: .5; cursor: not-allowed; }
.badge {
  background: linear-gradient(135deg, rgba(0,140,255,0.18), rgba(0,210,255,0.10));
  border: 1px solid rgba(120,190,255,0.18);
  color: #9fd3ff;
  padding: 8px 14px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 700;
  backdrop-filter: blur(12px);
  white-space: nowrap;
}

/* Filters */
.filters {
  display: flex;
  flex-wrap: wrap;
  align-items: end;
  gap: 14px;
  margin-bottom: 20px;
}
.filter-group { display: flex; flex-direction: column; gap: 6px; }
.filter-group.grow { flex: 1 1 260px; }
.filter-group label {
  font-size: 12px;
  font-weight: 700;
  color: #98a3c7;
  letter-spacing: .02em;
}
.filter-group select,
.filter-group input {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 10px;
  padding: 9px 12px;
  color: #eaeaf0;
  font-size: 14px;
  outline: none;
  color-scheme: dark;
}
.filter-group select:focus,
.filter-group input:focus {
  border-color: rgba(0,140,255,0.45);
  box-shadow: 0 0 0 4px rgba(0,140,255,0.16);
}
.filter-group select option { color: #111; }

.reset-btn {
  border: 1px solid rgba(255,255,255,0.14);
  background: rgba(255,255,255,0.05);
  color: #c8d2f0;
  border-radius: 10px;
  padding: 9px 16px;
  font-weight: 700;
  cursor: pointer;
  transition: 0.2s ease;
}
.reset-btn:hover { background: rgba(255,255,255,0.10); }

/* States */
.state {
  padding: 14px 16px;
  border-radius: 14px;
  margin-bottom: 18px;
  border: 1px solid rgba(255,255,255,0.08);
  backdrop-filter: blur(10px);
}
.state.muted { background: rgba(255,255,255,0.035); color: #9aa4bf; }
.state.error {
  background: rgba(255,0,0,0.10);
  color: #ffb4b4;
  border-color: rgba(255,110,110,0.20);
}

/* Table */
.table-wrap {
  overflow-x: auto;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.09);
  border-radius: 20px;
  backdrop-filter: blur(14px);
}
.log-table {
  width: 100%;
  min-width: 900px;
  border-collapse: collapse;
  font-size: 14px;
}
.log-table th {
  text-align: left;
  padding: 14px 16px;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: .04em;
  text-transform: uppercase;
  color: #98a3c7;
  border-bottom: 1px solid rgba(255,255,255,0.09);
}
.log-table td {
  padding: 14px 16px;
  vertical-align: top;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}
.row { cursor: pointer; outline: none; transition: background .15s ease; }
.row:hover,
.row:focus-visible,
.row.open { background: rgba(0,140,255,0.08); }
.nowrap { white-space: nowrap; color: #c8d2f0; }

.report-title { font-weight: 700; margin-bottom: 3px; }
.report-sub {
  display: flex;
  gap: 8px;
  align-items: center;
  color: #95a3c7;
  font-size: 12.5px;
}
.dot { opacity: .55; }
.type { color: #9fd3ff; }
.mono { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }
.who { font-weight: 600; }
.muted-text { color: #6f7a99; }

/* Severity chips (same palette as the reports page) */
.severity {
  display: inline-block;
  padding: 5px 11px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 800;
  border: 1px solid rgba(255,255,255,0.10);
}
.severity.low { background: rgba(0,200,120,0.18); color:#56f0b4; border-color: rgba(86,240,180,0.18); }
.severity.medium { background: rgba(255,180,0,0.16); color:#ffd166; border-color: rgba(255,209,102,0.18); }
.severity.high { background: rgba(255,80,80,0.18); color:#ff8a8a; border-color: rgba(255,138,138,0.18); }
.severity.critical { background: rgba(190,60,255,0.18); color:#e2a3ff; border-color: rgba(226,163,255,0.20); }

/* Action chips */
.action-chip {
  display: inline-block;
  padding: 5px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 800;
  border: 1px solid rgba(255,255,255,0.10);
}
.action-chip.approved { background: rgba(0,200,120,0.16); color:#56f0b4; border-color: rgba(86,240,180,0.22); }
.action-chip.dismissed { background: rgba(255,180,0,0.14); color:#ffd166; border-color: rgba(255,209,102,0.22); }
.action-chip.reopened { background: rgba(0,140,255,0.16); color:#9fd3ff; border-color: rgba(120,190,255,0.22); }
.action-chip.deleted { background: rgba(255,80,80,0.16); color:#ff8a8a; border-color: rgba(255,138,138,0.22); }

/* Details */
.details-row td {
  background: rgba(255,255,255,0.025);
  padding: 18px 20px 20px;
}
.details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px 24px;
}
.detail-block.wide { grid-column: 1 / -1; }
.detail-block .label {
  display: block;
  margin-bottom: 4px;
  font-size: 12px;
  font-weight: 700;
  color: #98a3c7;
}
.detail-block p { margin: 0; color: #dfe5f7; line-height: 1.5; }
.arrow { color: #6f7a99; margin: 0 4px; }

/* Pagination */
.pager {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 20px;
  color: #98a3c7;
  font-size: 14px;
}
.pager button {
  border: 1px solid rgba(255,255,255,0.14);
  background: rgba(255,255,255,0.05);
  color: #eaeaf0;
  border-radius: 10px;
  padding: 8px 14px;
  font-weight: 700;
  cursor: pointer;
  transition: 0.2s ease;
}
.pager button:hover:not(:disabled) { background: rgba(255,255,255,0.10); }
.pager button:disabled { opacity: .4; cursor: not-allowed; }
</style>