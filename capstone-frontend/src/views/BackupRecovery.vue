<template>
  <div class="backup-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1>Backup &amp; Recovery</h1>
        <p>Save a copy of all SafeRoute+ data and restore it if something goes wrong</p>
      </div>
      <div class="header-actions">
        <input ref="fileInput" type="file" accept=".gz,.json" hidden @change="onFilePicked" />
        <button class="btn ghost" type="button" :disabled="busy" @click="$refs.fileInput.click()">
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"
               stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M12 21V9" /><path d="M7 13l5-5 5 5" /><path d="M5 3h14" />
          </svg>
          {{ uploading ? "Uploading…" : "Upload backup" }}
        </button>
        <button class="btn primary" type="button" :disabled="busy" @click="showCreate = true">
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"
               stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M12 5v14" /><path d="M5 12h14" />
          </svg>
          Create backup
        </button>
      </div>
    </div>

    <!-- Message -->
    <div v-if="message.text" class="alert" :class="message.type">
      <span>{{ message.text }}</span>
      <button type="button" class="alert-close" aria-label="Dismiss" @click="message.text = ''">×</button>
    </div>

    <!-- Summary cards -->
    <div class="cards">
      <div class="card">
        <div class="card-label">Latest backup</div>
        <div class="card-value">{{ latest ? timeAgo(latest.created_at) : "None yet" }}</div>
        <div class="card-sub">{{ latest ? formatDateTime(latest.created_at) : "Create your first backup" }}</div>
      </div>
      <div class="card">
        <div class="card-label">Saved backups</div>
        <div class="card-value">{{ backups.length }}</div>
        <div class="card-sub">{{ totalSize }} total</div>
      </div>
      <div class="card">
        <div class="card-label">Records in database now</div>
        <div class="card-value">{{ currentTotal.toLocaleString() }}</div>
        <div class="card-sub">Users, centers, logs, reports and more</div>
      </div>
      <div class="card">
        <div class="card-label">Stored in</div>
        <div class="card-value">{{ storage === "bucket" ? "Cloud bucket" : "Server folder" }}</div>
        <div class="card-sub" :class="{ warn: storage !== 'bucket' }">
          {{ storage === "bucket" ? "Private, kept across deploys" : "Download copies — this folder is lost on redeploy" }}
        </div>
      </div>
    </div>

    <!-- Table -->
    <div class="table-wrap">
      <div v-if="loading" class="empty">Loading backups…</div>
      <div v-else-if="!backups.length" class="empty">
        No backups yet. Click <strong>Create backup</strong> to save a copy of the current data.
      </div>
      <table v-else>
        <thead>
          <tr>
            <th>Backup</th>
            <th>Type</th>
            <th>Created</th>
            <th class="num">Records</th>
            <th class="num">Size</th>
            <th class="actions-col">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="b in backups" :key="b.id">
            <td>
              <div class="file-name">#{{ b.id }} · {{ b.file_name }}</div>
              <div v-if="b.note" class="muted">{{ b.note }}</div>
              <div v-if="b.last_restored_at" class="restored">
                Restored {{ formatDateTime(b.last_restored_at) }} by {{ b.last_restored_by_name || "—" }}
              </div>
            </td>
            <td><span class="kind" :class="b.kind.toLowerCase()">{{ b.kind_label }}</span></td>
            <td>
              <div>{{ formatDateTime(b.created_at) }}</div>
              <div class="muted">{{ b.created_by_name || "—" }}</div>
            </td>
            <td class="num">{{ b.record_count.toLocaleString() }}</td>
            <td class="num">{{ formatSize(b.size_bytes) }}</td>
            <td class="actions-col">
              <button class="icon-btn" type="button" :disabled="busy" title="Download" @click="download(b)">Download</button>
              <button class="icon-btn warn" type="button" :disabled="busy" title="Restore this backup" @click="openRestore(b)">Restore</button>
              <button class="icon-btn danger" type="button" :disabled="busy" title="Delete" @click="toDelete = b">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <p class="footnote">
      Backups include users, municipalities, barangays, evacuation centers, evacuation logs, evacuees,
      hazard reports, donations and analytics. System Logs are never overwritten by a restore.
      Uploaded photos are kept in file storage and are not part of the backup.
    </p>

    <!-- Create modal -->
    <div v-if="showCreate" class="modal-backdrop" @click.self="!creating && (showCreate = false)">
      <div class="modal">
        <h2>Create backup</h2>
        <p class="muted">Saves a copy of all current data. This can take a few seconds.</p>
        <label for="bkNote">Note (optional)</label>
        <input id="bkNote" v-model="note" type="text" maxlength="255" placeholder="e.g. Before typhoon season cleanup" />
        <div class="modal-actions">
          <button class="btn ghost" type="button" :disabled="creating" @click="showCreate = false">Cancel</button>
          <button class="btn primary" type="button" :disabled="creating" @click="createBackup">
            {{ creating ? "Creating…" : "Create backup" }}
          </button>
        </div>
      </div>
    </div>

    <!-- Restore modal -->
    <div v-if="toRestore" class="modal-backdrop" @click.self="!restoring && closeRestore()">
      <div class="modal wide">
        <h2>Restore backup #{{ toRestore.id }}?</h2>
        <div class="danger-box">
          This <strong>replaces all current data</strong> with the data from
          {{ formatDateTime(toRestore.created_at) }}. Anything added or changed after that will be removed.
          A safety copy of the current data is saved first, so you can undo this.
        </div>

        <table class="compare">
          <thead>
            <tr><th>Data</th><th class="num">Now</th><th class="num">After restore</th></tr>
          </thead>
          <tbody>
            <tr v-for="row in compareRows" :key="row.model" :class="{ changed: row.now !== row.backup }">
              <td>{{ row.label }}</td>
              <td class="num">{{ row.now.toLocaleString() }}</td>
              <td class="num">{{ row.backup.toLocaleString() }}</td>
            </tr>
          </tbody>
        </table>

        <label for="bkConfirm">Type <strong>RESTORE</strong> to confirm</label>
        <input id="bkConfirm" v-model="confirmText" type="text" autocomplete="off" placeholder="RESTORE" />
        <div class="modal-actions">
          <button class="btn ghost" type="button" :disabled="restoring" @click="closeRestore">Cancel</button>
          <button class="btn danger" type="button" :disabled="restoring || confirmText.trim().toUpperCase() !== 'RESTORE'"
                  @click="restore">
            {{ restoring ? "Restoring… do not close this page" : "Restore now" }}
          </button>
        </div>
      </div>
    </div>

    <!-- Restore done -->
    <div v-if="restoreDone" class="modal-backdrop">
      <div class="modal">
        <h2>Restore complete</h2>
        <p>
          The data now matches backup #{{ restoreDone.restored.id }}. The previous data was saved as
          backup #{{ restoreDone.safety_backup.id }} in case you need it back.
        </p>
        <p class="muted">Please sign in again so your account details are reloaded.</p>
        <div class="modal-actions">
          <button class="btn primary" type="button" @click="signInAgain">Sign in again</button>
        </div>
      </div>
    </div>

    <!-- Delete modal -->
    <div v-if="toDelete" class="modal-backdrop" @click.self="!deleting && (toDelete = null)">
      <div class="modal">
        <h2>Delete backup #{{ toDelete.id }}?</h2>
        <p class="muted">{{ toDelete.file_name }} will be permanently removed. This cannot be undone.</p>
        <div class="modal-actions">
          <button class="btn ghost" type="button" :disabled="deleting" @click="toDelete = null">Cancel</button>
          <button class="btn danger" type="button" :disabled="deleting" @click="remove">
            {{ deleting ? "Deleting…" : "Delete" }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import api from "@/services/api";
import { formatDateTime, timeAgo } from "@/utils/datetime";

const MODEL_LABELS = {
  "auth.group": "User groups",
  "auth_app.customuser": "User accounts",
  "auth_app.municipality": "Municipalities",
  "auth_app.barangay": "Barangays",
  "auth_app.hazardreport": "Hazard reports",
  "auth_app.hazardphoto": "Hazard photos (links)",
  "auth_app.hazardreportlog": "Hazard report history",
  "auth_app.analyticsevent": "Analytics events",
  "auth_app.gislayer": "GIS layers",
  "auth_app.emailotp": "Email codes",
  "evac_app.evacuationcenter": "Evacuation centers",
  "evac_app.evacuationreason": "Evacuation reasons",
  "evac_app.evacuationlog": "Evacuation logs",
  "evac_app.evacuee": "Evacuees",
  "evac_app.donationneed": "Donation needs",
  "evac_app.donation": "Donations",
  "evac_app.donationdistribution": "Donation distributions",
  "analytics_app.congestionsnapshot": "Congestion snapshots",
};

const backups = ref([]);
const currentCounts = ref({});
const storage = ref("local");
const loading = ref(true);

const showCreate = ref(false);
const note = ref("");
const creating = ref(false);
const uploading = ref(false);
const fileInput = ref(null);

const toRestore = ref(null);
const confirmText = ref("");
const restoring = ref(false);
const restoreDone = ref(null);

const toDelete = ref(null);
const deleting = ref(false);

const message = reactive({ text: "", type: "success" });

const busy = computed(() => creating.value || uploading.value || restoring.value || deleting.value);
const latest = computed(() => backups.value[0] || null);
const currentTotal = computed(() => Object.values(currentCounts.value).reduce((a, b) => a + b, 0));
const totalSize = computed(() => formatSize(backups.value.reduce((a, b) => a + (b.size_bytes || 0), 0)));

const compareRows = computed(() => {
  if (!toRestore.value) return [];
  const backupCounts = toRestore.value.model_counts || {};
  const models = new Set([...Object.keys(currentCounts.value), ...Object.keys(backupCounts)]);
  return [...models]
    .map((m) => ({
      model: m,
      label: MODEL_LABELS[m] || m,
      now: currentCounts.value[m] || 0,
      backup: backupCounts[m] || 0,
    }))
    .filter((r) => r.now || r.backup)
    .sort((a, b) => a.label.localeCompare(b.label));
});

function formatSize(bytes) {
  if (!bytes) return "0 KB";
  const units = ["B", "KB", "MB", "GB"];
  let i = 0;
  let n = bytes;
  while (n >= 1024 && i < units.length - 1) { n /= 1024; i++; }
  return `${n.toFixed(i < 2 ? 0 : 1)} ${units[i]}`;
}

function show(text, type = "success") {
  message.text = text;
  message.type = type;
}

async function errorText(err, fallback) {
  // Blob responses (download) carry the JSON error inside the blob.
  const data = err?.response?.data;
  if (data instanceof Blob) {
    try { return JSON.parse(await data.text()).detail || fallback; } catch { return fallback; }
  }
  return data?.detail || fallback;
}

async function load() {
  loading.value = true;
  try {
    const { data } = await api.get("backups/");
    backups.value = data.results || [];
    currentCounts.value = data.current_counts || {};
    storage.value = data.storage || "local";
  } catch (err) {
    show(await errorText(err, "Could not load backups."), "error");
  } finally {
    loading.value = false;
  }
}

async function createBackup() {
  creating.value = true;
  try {
    const { data } = await api.post("backups/", { note: note.value });
    show(`Backup #${data.id} created (${data.record_count.toLocaleString()} records).`);
    showCreate.value = false;
    note.value = "";
    await load();
  } catch (err) {
    show(await errorText(err, "Backup failed."), "error");
  } finally {
    creating.value = false;
  }
}

async function onFilePicked(e) {
  const file = e.target.files?.[0];
  e.target.value = "";
  if (!file) return;
  uploading.value = true;
  try {
    const form = new FormData();
    form.append("file", file);
    const { data } = await api.post("backups/upload/", form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    show(`Uploaded as backup #${data.id}. Use Restore on it to bring this data back.`);
    await load();
  } catch (err) {
    show(await errorText(err, "Upload failed."), "error");
  } finally {
    uploading.value = false;
  }
}

async function download(b) {
  try {
    const res = await api.get(`backups/${b.id}/download/`, { responseType: "blob" });
    const url = URL.createObjectURL(res.data);
    const a = document.createElement("a");
    a.href = url;
    a.download = b.file_name;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  } catch (err) {
    show(await errorText(err, "Download failed."), "error");
  }
}

function openRestore(b) {
  toRestore.value = b;
  confirmText.value = "";
}

function closeRestore() {
  toRestore.value = null;
  confirmText.value = "";
}

async function restore() {
  restoring.value = true;
  try {
    const { data } = await api.post(
      `backups/${toRestore.value.id}/restore/`,
      { confirm: confirmText.value },
      { timeout: 0 },
    );
    toRestore.value = null;
    restoreDone.value = data;
  } catch (err) {
    show(await errorText(err, "Restore failed. No data was changed."), "error");
    toRestore.value = null;
  } finally {
    restoring.value = false;
  }
}

function signInAgain() {
  localStorage.clear();
  window.location.href = "/auth/login/";
}

async function remove() {
  deleting.value = true;
  try {
    await api.delete(`backups/${toDelete.value.id}/`);
    show(`Backup #${toDelete.value.id} deleted.`);
    toDelete.value = null;
    await load();
  } catch (err) {
    show(await errorText(err, "Delete failed."), "error");
  } finally {
    deleting.value = false;
  }
}

onMounted(load);
</script>

<style scoped>
.backup-page {
  padding: 32px;
  min-height: 100vh;
  background:
    radial-gradient(1200px 600px at 20% 10%, rgba(0,140,255,0.15), transparent 60%),
    radial-gradient(900px 500px at 80% 30%, rgba(0,255,200,0.08), transparent 60%),
    linear-gradient(135deg, #070a12, #0b1022 40%, #070a12);
  color: #eaeaf0;
  font-family: "Inter", system-ui, sans-serif;
}

.page-header {
  display: flex; justify-content: space-between; align-items: end;
  gap: 16px; margin-bottom: 22px; flex-wrap: wrap;
}
.page-header h1 { font-size: 30px; font-weight: 800; letter-spacing: -0.02em; }
.page-header p { margin-top: 6px; color: #98a3c7; font-size: 14px; }
.header-actions { display: flex; gap: 12px; flex-wrap: wrap; }

.btn {
  display: inline-flex; align-items: center; gap: 8px;
  border-radius: 999px; padding: 9px 18px;
  font-size: 13px; font-weight: 800; cursor: pointer; transition: 0.2s ease;
  border: 1px solid rgba(120,190,255,0.22);
  background: rgba(255,255,255,0.04); color: #cfe6ff;
}
.btn:hover:not(:disabled) { transform: translateY(-1px); }
.btn:disabled { opacity: .5; cursor: not-allowed; }
.btn.primary {
  border-color: rgba(86,240,180,0.30);
  background: linear-gradient(135deg, rgba(0,200,120,0.25), rgba(0,200,120,0.10));
  color: #56f0b4;
}
.btn.danger {
  border-color: rgba(255,110,110,0.35);
  background: linear-gradient(135deg, rgba(239,68,68,0.30), rgba(239,68,68,0.12));
  color: #ffb4b4;
}

.alert {
  display: flex; justify-content: space-between; align-items: center; gap: 12px;
  padding: 12px 16px; border-radius: 12px; margin-bottom: 18px; font-size: 14px;
}
.alert.success { background: rgba(16,185,129,0.12); border: 1px solid rgba(16,185,129,0.35); color: #a7f3d0; }
.alert.error { background: rgba(239,68,68,0.12); border: 1px solid rgba(239,68,68,0.35); color: #fecaca; }
.alert-close { background: none; border: 0; color: inherit; font-size: 20px; cursor: pointer; line-height: 1; }

.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 14px; margin-bottom: 20px; }
.card {
  background: rgba(15,23,42,0.72); border: 1px solid rgba(148,163,184,0.16);
  border-radius: 16px; padding: 16px 18px;
}
.card-label { font-size: 12px; font-weight: 700; color: #98a3c7; letter-spacing: .02em; }
.card-value { font-size: 22px; font-weight: 800; margin-top: 6px; }
.card-sub { font-size: 12px; color: #7d89ad; margin-top: 4px; }
.card-sub.warn { color: #fbbf24; }

.table-wrap {
  background: rgba(15,23,42,0.72); border: 1px solid rgba(148,163,184,0.16);
  border-radius: 16px; overflow-x: auto;
}
table { width: 100%; border-collapse: collapse; font-size: 14px; }
th {
  text-align: left; font-size: 12px; font-weight: 700; color: #98a3c7;
  padding: 12px 14px; border-bottom: 1px solid rgba(148,163,184,0.16); white-space: nowrap;
}
td { padding: 12px 14px; border-bottom: 1px solid rgba(148,163,184,0.08); vertical-align: top; }
tbody tr:last-child td { border-bottom: 0; }
.num { text-align: right; white-space: nowrap; }
.file-name { font-weight: 700; word-break: break-all; }
.muted { color: #8a96ba; font-size: 12px; margin-top: 3px; }
.restored { color: #fbbf24; font-size: 12px; margin-top: 3px; }
.empty { padding: 40px; text-align: center; color: #98a3c7; }

.kind {
  display: inline-block; padding: 4px 10px; border-radius: 999px;
  font-size: 11px; font-weight: 800; white-space: nowrap;
  background: rgba(14,165,255,0.14); color: #9fd3ff; border: 1px solid rgba(14,165,255,0.3);
}
.kind.scheduled { background: rgba(20,184,166,0.14); color: #99f6e4; border-color: rgba(20,184,166,0.3); }
.kind.pre_restore { background: rgba(245,158,11,0.14); color: #fde68a; border-color: rgba(245,158,11,0.3); }
.kind.uploaded { background: rgba(168,85,247,0.14); color: #e9d5ff; border-color: rgba(168,85,247,0.3); }

.actions-col { text-align: right; white-space: nowrap; }
.icon-btn {
  border: 1px solid rgba(120,190,255,0.22); background: rgba(255,255,255,0.04);
  color: #cfe6ff; border-radius: 8px; padding: 6px 10px; margin-left: 6px;
  font-size: 12px; font-weight: 700; cursor: pointer;
}
.icon-btn.warn { color: #fde68a; border-color: rgba(245,158,11,0.35); }
.icon-btn.danger { color: #fecaca; border-color: rgba(239,68,68,0.35); }
.icon-btn:disabled { opacity: .5; cursor: not-allowed; }

.footnote { margin-top: 14px; font-size: 12px; color: #7d89ad; max-width: 900px; line-height: 1.5; }

.modal-backdrop {
  position: fixed; inset: 0; background: rgba(2,6,16,0.7); backdrop-filter: blur(4px);
  display: flex; align-items: center; justify-content: center; z-index: 2000; padding: 20px;
}
.modal {
  width: 100%; max-width: 460px; max-height: 90vh; overflow-y: auto;
  background: #0f1d31; border: 1px solid rgba(148,163,184,0.22);
  border-radius: 18px; padding: 24px; box-shadow: 0 18px 50px rgba(0,0,0,0.4);
}
.modal.wide { max-width: 580px; }
.modal h2 { font-size: 20px; font-weight: 800; margin-bottom: 10px; }
.modal p { font-size: 14px; line-height: 1.5; margin-bottom: 10px; }
.modal label { display: block; font-size: 12px; font-weight: 700; color: #98a3c7; margin: 14px 0 6px; }
.modal input {
  width: 100%; padding: 10px 12px; border-radius: 10px; font-size: 14px;
  background: rgba(15,23,42,0.84); border: 1px solid rgba(148,163,184,0.22); color: #f8fafc;
}
.modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; }
.danger-box {
  background: rgba(239,68,68,0.10); border: 1px solid rgba(239,68,68,0.35); color: #fecaca;
  padding: 12px 14px; border-radius: 12px; font-size: 13px; line-height: 1.5; margin-bottom: 14px;
}
.compare { font-size: 13px; }
.compare td, .compare th { padding: 7px 10px; }
.compare tr.changed td { color: #fde68a; }

@media (max-width: 640px) {
  .backup-page { padding: 18px; }
}
</style>
