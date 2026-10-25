<template>
  <div class="system-logs">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1>System Logs</h1>
        <p>Every change, sign-in and security event across SafeRoute+</p>
      </div>
      <div class="header-actions">
        <span class="badge">{{ countLabel }}</span>
        <button
          class="export-btn"
          type="button"
          :disabled="exporting || loading || !logs.length"
          :title="!logs.length ? 'Nothing to export' : 'Download all entries matching the current filters'"
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
        <label for="sysSearch">Search</label>
        <input
          id="sysSearch"
          v-model="filters.q"
          type="text"
          placeholder="User name or email, record, path, IP address or #ID"
          @input="onSearchInput"
        />
      </div>

      <div class="filter-group">
        <label for="sysAction">Action</label>
        <select id="sysAction" v-model="filters.action" @change="applyFilters">
          <option value="all">All</option>
          <option v-for="a in meta.actions" :key="a.value" :value="a.value">{{ a.label }}</option>
        </select>
      </div>

      <div class="filter-group">
        <label for="sysType">Record type</label>
        <select id="sysType" v-model="filters.resource_type" @change="onTypeChange">
          <option value="all">All</option>
          <option v-for="t in meta.resource_types" :key="t" :value="t">{{ humanize(t) }}</option>
        </select>
      </div>

      <div class="filter-group">
        <label for="sysFrom">From</label>
        <input id="sysFrom" v-model="filters.date_from" type="date" @change="applyFilters" />
      </div>

      <div class="filter-group">
        <label for="sysTo">To</label>
        <input id="sysTo" v-model="filters.date_to" type="date" @change="applyFilters" />
      </div>

      <button class="reset-btn" type="button" @click="resetFilters">Reset</button>
    </div>

    <!-- Focus chips (record history / single request) -->
    <div v-if="filters.resource_id || filters.request_id" class="focus-chips">
      <span v-if="filters.resource_id" class="focus-chip">
        History of {{ humanize(filters.resource_type) }} #{{ filters.resource_id }}
        <button type="button" aria-label="Clear" @click="clearFocus('resource_id')">×</button>
      </span>
      <span v-if="filters.request_id" class="focus-chip">
        One request · <span class="mono">{{ filters.request_id.slice(0, 8) }}</span>
        <button type="button" aria-label="Clear" @click="clearFocus('request_id')">×</button>
      </span>
    </div>

    <!-- States -->
    <div v-if="loading && !logs.length" class="state muted">Loading logs…</div>
    <div v-else-if="errorMsg" class="state error">{{ errorMsg }}</div>
    <div v-else-if="!loading && !logs.length" class="state muted">
      No log entries found for the selected filters.
    </div>

    <!-- Table -->
    <div v-if="logs.length" class="table-wrap">
      <table class="log-table">
        <thead>
          <tr>
            <th>When</th>
            <th>Action</th>
            <th>User</th>
            <th>Record</th>
            <th>Request</th>
            <th>IP address</th>
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
              <td class="nowrap">{{ formatDateTime(log.timestamp) }}</td>

              <td>
                <span class="action-chip" :class="actionClass(log.action)">{{ log.action_label }}</span>
              </td>

              <td>
                <div class="who">{{ actorName(log) }}</div>
                <div class="sub">
                  {{ log.actor_role ? roleLabel(log.actor_role) : (log.actor_email || "—") }}
                  <template v-if="log.municipality_name"> · {{ log.municipality_name }}</template>
                </div>
              </td>

              <td>
                <template v-if="log.resource_type">
                  <div class="record-label">{{ log.resource_label || "—" }}</div>
                  <div class="sub">
                    <span class="type">{{ humanize(log.resource_type) }}</span>
                    <span class="dot">•</span>
                    <span class="mono">#{{ log.resource_id }}</span>
                  </div>
                </template>
                <span v-else class="muted-text">—</span>
              </td>

              <td>
                <template v-if="log.method">
                  <div class="req">
                    <span class="method" :class="log.method.toLowerCase()">{{ log.method }}</span>
                    <span class="status" :class="statusClass(log.status_code)">{{ log.status_code }}</span>
                  </div>
                  <div class="sub mono path" :title="log.path">{{ log.path }}</div>
                </template>
                <span v-else class="muted-text">System task</span>
              </td>

              <td class="mono nowrap">{{ log.ip_address || "—" }}</td>
            </tr>

            <!-- Details -->
            <tr v-if="expandedId === log.id" class="details-row">
              <td colspan="6">
                <!-- Field changes -->
                <div v-if="detailRows(log).length" class="changes">
                  <div class="changes-title">{{ changesTitle(log) }}</div>
                  <table class="diff">
                    <thead v-if="log.action === 'UPDATE'">
                      <tr><th>Field</th><th>Before</th><th>After</th></tr>
                    </thead>
                    <tbody>
                      <tr v-for="row in detailRows(log)" :key="row.field">
                        <td class="field">{{ row.field }}</td>
                        <template v-if="log.action === 'UPDATE'">
                          <td class="before">{{ row.before }}</td>
                          <td class="after">{{ row.after }}</td>
                        </template>
                        <td v-else class="value">{{ row.value }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                <div class="details">
                  <div class="detail-block">
                    <span class="label">Exact time</span>
                    <p>{{ formatDateTime(log.timestamp, true) }}</p>
                  </div>
                  <div class="detail-block">
                    <span class="label">User email</span>
                    <p>{{ log.actor_email || "—" }}</p>
                  </div>
                  <div class="detail-block wide">
                    <span class="label">Device / browser</span>
                    <p class="ua">{{ log.user_agent || "—" }}</p>
                  </div>
                </div>

                <div class="detail-actions">
                  <button
                    v-if="log.resource_type && log.resource_id"
                    type="button"
                    class="link-btn"
                    @click.stop="showRecordHistory(log)"
                  >
                    Full history of this record
                  </button>
                  <button
                    v-if="log.request_id"
                    type="button"
                    class="link-btn"
                    @click.stop="showRequest(log)"
                  >
                    Everything from this request
                  </button>
                </div>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>

    <!-- Load more (keyset paging) -->
    <div v-if="nextCursor" class="pager">
      <button type="button" :disabled="loading" @click="loadMore">
        {{ loading ? "Loading…" : "Load more" }}
      </button>
      <span>Showing {{ logs.length }}<template v-if="count !== null"> of {{ count }}</template></span>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount } from "vue";
import api from "@/services/api";
import { formatDateTime as fmtDT } from "@/utils/datetime";

const PAGE_SIZE = 25;

const logs = ref([]);
const loading = ref(false);
const errorMsg = ref("");
const count = ref(null);
const nextCursor = ref(null);
const expandedId = ref(null);
const exporting = ref(false);

const meta = reactive({ actions: [], resource_types: [] });

const filters = reactive({
  q: "",
  action: "all",
  resource_type: "all",
  resource_id: "",
  request_id: "",
  date_from: "",
  date_to: "",
});

const ROLE_LABELS = {
  CITIZEN: "Citizen",
  PROVINCIAL_ADMIN: "Provincial Admin",
  MUNICIPAL_ADMIN: "Municipal Admin",
  EVAC_CENTER_STAFF: "Evacuation Center Staff",
  RESPONSE_TEAM: "Response Team",
};

const countLabel = computed(() => {
  const n = count.value ?? logs.value.length;
  return `${n.toLocaleString()} Entr${n === 1 ? "y" : "ies"}`;
});

function roleLabel(role) {
  return ROLE_LABELS[role] || role || "—";
}

function actorName(log) {
  if (log.actor_name) return log.actor_name;
  if (log.actor_email) return log.actor_email;
  return log.method ? "Guest (not signed in)" : "System";
}

// "HazardReport" -> "Hazard Report", "validated_at" -> "Validated at"
function humanize(text) {
  if (!text) return "";
  const spaced = String(text)
    .replace(/_/g, " ")
    .replace(/([a-z])([A-Z])/g, "$1 $2")
    .trim();
  return spaced.charAt(0).toUpperCase() + spaced.slice(1);
}

function actionClass(action) {
  return {
    CREATE: "create",
    UPDATE: "update",
    DELETE: "delete",
    LOGIN: "login",
    LOGIN_FAILED: "danger",
    PERMISSION_DENIED: "danger",
    EXPORT: "export",
  }[action] || "";
}

function statusClass(code) {
  if (!code) return "";
  if (code >= 500) return "s5";
  if (code >= 400) return "s4";
  return "s2";
}

function formatDateTime(iso, withSeconds = false) {
  return fmtDT(iso, { seconds: withSeconds });
}

function show(value) {
  if (value === null || value === undefined || value === "") return "(empty)";
  if (value === true) return "Yes";
  if (value === false) return "No";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

function changesTitle(log) {
  return {
    UPDATE: "What changed",
    CREATE: "Values when created",
    DELETE: "Values at the time of deletion",
  }[log.action] || "Details";
}

function detailRows(log) {
  const d = log.details;
  if (!d || typeof d !== "object") return [];
  return Object.entries(d).map(([key, value]) => {
    if (log.action === "UPDATE" && Array.isArray(value) && value.length === 2) {
      return { field: humanize(key), before: show(value[0]), after: show(value[1]) };
    }
    if (key === "filters" && value && typeof value === "object") {
      const text = Object.entries(value).map(([k, v]) => `${humanize(k)}: ${v}`).join(", ");
      return { field: "Filters used", value: text || "(none)" };
    }
    return { field: humanize(key), value: show(value) };
  });
}

function toggle(id) {
  expandedId.value = expandedId.value === id ? null : id;
}

function filterParams() {
  const params = {};
  if (filters.q.trim()) params.q = filters.q.trim();
  if (filters.action !== "all") params.action = filters.action;
  if (filters.resource_type !== "all") params.resource_type = filters.resource_type;
  if (filters.resource_id) params.resource_id = filters.resource_id;
  if (filters.request_id) params.request_id = filters.request_id;
  if (filters.date_from) params.date_from = filters.date_from;
  if (filters.date_to) params.date_to = filters.date_to;
  return params;
}

function errorText(err, fallback) {
  return (
    err?.response?.data?.detail ||
    Object.values(err?.response?.data || {})[0] ||
    fallback
  );
}

// Ignore responses from older requests if the filters changed while they were loading.
let requestSeq = 0;

async function loadLogs({ append = false } = {}) {
  const seq = ++requestSeq;
  loading.value = true;
  errorMsg.value = "";

  try {
    const params = { page_size: PAGE_SIZE, ...filterParams() };
    if (append && nextCursor.value) params.cursor = nextCursor.value;

    const res = await api.get("audit-logs/", { params });
    if (seq !== requestSeq) return;

    logs.value = append ? [...logs.value, ...res.data.results] : res.data.results;
    nextCursor.value = res.data.next_cursor;
    if (!append) {
      count.value = res.data.count;
      expandedId.value = null;
    }
  } catch (err) {
    if (seq !== requestSeq) return;
    console.error(err);
    if (!append) {
      logs.value = [];
      count.value = null;
      nextCursor.value = null;
    }
    errorMsg.value = errorText(err, "Failed to load system logs.");
  } finally {
    if (seq === requestSeq) loading.value = false;
  }
}

async function loadMeta() {
  try {
    const res = await api.get("audit-logs/meta/");
    meta.actions = res.data.actions || [];
    meta.resource_types = res.data.resource_types || [];
  } catch (err) {
    console.error(err);
  }
}

function loadMore() {
  if (nextCursor.value && !loading.value) loadLogs({ append: true });
}

function applyFilters() {
  loadLogs();
}

function onTypeChange() {
  filters.resource_id = "";
  applyFilters();
}

let searchTimer = null;
function onSearchInput() {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(applyFilters, 350);
}

function resetFilters() {
  Object.assign(filters, {
    q: "",
    action: "all",
    resource_type: "all",
    resource_id: "",
    request_id: "",
    date_from: "",
    date_to: "",
  });
  applyFilters();
}

function clearFocus(key) {
  filters[key] = "";
  applyFilters();
}

function showRecordHistory(log) {
  Object.assign(filters, {
    q: "",
    action: "all",
    request_id: "",
    resource_type: log.resource_type,
    resource_id: log.resource_id,
  });
  applyFilters();
}

function showRequest(log) {
  Object.assign(filters, {
    q: "",
    action: "all",
    resource_type: "all",
    resource_id: "",
    request_id: log.request_id,
  });
  applyFilters();
}

// With responseType "blob", error bodies arrive as a Blob too.
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
  return errorText(err, "Failed to export system logs.");
}

async function exportToExcel() {
  if (exporting.value) return;
  exporting.value = true;
  try {
    const res = await api.get("audit-logs/export/", {
      params: filterParams(),
      responseType: "blob",
    });
    const today = new Date().toISOString().slice(0, 10);
    const url = URL.createObjectURL(res.data);
    const link = document.createElement("a");
    link.href = url;
    link.download = `System_Logs_${today}.xlsx`;
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

onMounted(() => {
  loadMeta();
  loadLogs();
});
onBeforeUnmount(() => clearTimeout(searchTimer));
</script>

<style scoped>
.system-logs {
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
  flex-wrap: wrap;
}
.page-header h1 { font-size: 30px; font-weight: 800; letter-spacing: -0.02em; }
.page-header p { margin-top: 6px; color: #98a3c7; font-size: 14px; }
.header-actions { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
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
.filters { display: flex; flex-wrap: wrap; align-items: end; gap: 14px; margin-bottom: 16px; }
.filter-group { display: flex; flex-direction: column; gap: 6px; }
.filter-group.grow { flex: 1 1 260px; }
.filter-group label { font-size: 12px; font-weight: 700; color: #98a3c7; letter-spacing: .02em; }
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

/* Focus chips */
.focus-chips { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 16px; }
.focus-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px 6px 14px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 700;
  color: #9fd3ff;
  background: rgba(0,140,255,0.14);
  border: 1px solid rgba(120,190,255,0.22);
}
.focus-chip button {
  border: none;
  background: rgba(255,255,255,0.10);
  color: #eaeaf0;
  width: 22px;
  height: 22px;
  border-radius: 999px;
  cursor: pointer;
  font-size: 15px;
  line-height: 1;
}
.focus-chip button:hover { background: rgba(255,255,255,0.20); }

/* States */
.state {
  padding: 14px 16px;
  border-radius: 14px;
  margin-bottom: 18px;
  border: 1px solid rgba(255,255,255,0.08);
  backdrop-filter: blur(10px);
}
.state.muted { background: rgba(255,255,255,0.035); color: #9aa4bf; }
.state.error { background: rgba(255,0,0,0.10); color: #ffb4b4; border-color: rgba(255,110,110,0.20); }

/* Table */
.table-wrap {
  overflow-x: auto;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.09);
  border-radius: 20px;
  backdrop-filter: blur(14px);
}
.log-table { width: 100%; min-width: 980px; border-collapse: collapse; font-size: 14px; }
.log-table > thead th {
  text-align: left;
  padding: 14px 16px;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: .04em;
  text-transform: uppercase;
  color: #98a3c7;
  border-bottom: 1px solid rgba(255,255,255,0.09);
}
.log-table > tbody > tr > td {
  padding: 14px 16px;
  vertical-align: top;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}
.row { cursor: pointer; outline: none; transition: background .15s ease; }
.row:hover, .row:focus-visible, .row.open { background: rgba(0,140,255,0.08); }
.nowrap { white-space: nowrap; color: #c8d2f0; }
.who, .record-label { font-weight: 700; margin-bottom: 3px; }
.record-label { max-width: 260px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.sub { display: flex; gap: 8px; align-items: center; color: #95a3c7; font-size: 12.5px; flex-wrap: wrap; }
.dot { opacity: .55; }
.type { color: #9fd3ff; }
.mono { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }
.muted-text { color: #6f7a99; }
.path { max-width: 240px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; display: block; }

.req { display: flex; gap: 6px; margin-bottom: 4px; }
.method, .status {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 11.5px;
  font-weight: 800;
  padding: 2px 7px;
  border-radius: 6px;
  background: rgba(255,255,255,0.07);
  color: #c8d2f0;
}
.method.post { color: #56f0b4; }
.method.patch, .method.put { color: #ffd166; }
.method.delete { color: #ff8a8a; }
.method.get { color: #9fd3ff; }
.status.s2 { color: #56f0b4; }
.status.s4 { color: #ffd166; }
.status.s5 { color: #ff8a8a; }

/* Action chips */
.action-chip {
  display: inline-block;
  padding: 5px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 800;
  white-space: nowrap;
  border: 1px solid rgba(255,255,255,0.10);
}
.action-chip.create { background: rgba(0,200,120,0.16); color:#56f0b4; border-color: rgba(86,240,180,0.22); }
.action-chip.update { background: rgba(0,140,255,0.16); color:#9fd3ff; border-color: rgba(120,190,255,0.22); }
.action-chip.delete { background: rgba(255,80,80,0.16); color:#ff8a8a; border-color: rgba(255,138,138,0.22); }
.action-chip.login { background: rgba(190,60,255,0.14); color:#e2a3ff; border-color: rgba(226,163,255,0.22); }
.action-chip.export { background: rgba(255,180,0,0.14); color:#ffd166; border-color: rgba(255,209,102,0.22); }
.action-chip.danger { background: rgba(255,60,60,0.24); color:#ffb4b4; border-color: rgba(255,110,110,0.35); }

/* Details */
.details-row > td { background: rgba(255,255,255,0.025); padding: 18px 20px 20px; }
.changes { margin-bottom: 18px; }
.changes-title { font-size: 12px; font-weight: 800; color: #98a3c7; margin-bottom: 8px; letter-spacing: .02em; }
.diff {
  width: 100%;
  border-collapse: collapse;
  font-size: 13.5px;
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 12px;
  overflow: hidden;
}
.diff th {
  text-align: left;
  font-size: 11.5px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: .04em;
  color: #98a3c7;
  padding: 9px 12px;
  background: rgba(255,255,255,0.04);
}
.diff td {
  padding: 9px 12px;
  border-top: 1px solid rgba(255,255,255,0.06);
  vertical-align: top;
  word-break: break-word;
}
.diff .field { width: 22%; font-weight: 700; color: #c8d2f0; }
.diff .before { color: #ff9f9f; text-decoration: line-through; text-decoration-color: rgba(255,138,138,0.45); }
.diff .after { color: #7ef5c4; }
.diff .value { color: #dfe5f7; }

.details { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px 24px; }
.detail-block.wide { grid-column: 1 / -1; }
.detail-block .label { display: block; margin-bottom: 4px; font-size: 12px; font-weight: 700; color: #98a3c7; }
.detail-block p { margin: 0; color: #dfe5f7; line-height: 1.5; }
.ua { font-size: 12.5px; color: #aab5d6 !important; word-break: break-all; }

.detail-actions { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 16px; }
.link-btn {
  border: 1px solid rgba(120,190,255,0.25);
  background: rgba(0,140,255,0.10);
  color: #9fd3ff;
  border-radius: 10px;
  padding: 7px 12px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: 0.2s ease;
}
.link-btn:hover { background: rgba(0,140,255,0.20); }

/* Load more */
.pager {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  margin-top: 20px;
  color: #98a3c7;
  font-size: 13px;
}
.pager button {
  border: 1px solid rgba(255,255,255,0.14);
  background: rgba(255,255,255,0.05);
  color: #eaeaf0;
  border-radius: 10px;
  padding: 9px 22px;
  font-weight: 700;
  cursor: pointer;
  transition: 0.2s ease;
}
.pager button:hover:not(:disabled) { background: rgba(255,255,255,0.10); }
.pager button:disabled { opacity: .4; cursor: not-allowed; }

@media (max-width: 640px) {
  .system-logs { padding: 20px 16px; }
  .page-header h1 { font-size: 24px; }
}
</style>
