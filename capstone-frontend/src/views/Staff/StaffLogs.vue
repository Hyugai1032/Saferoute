<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h1>Evacuation Logs</h1>
        <p class="muted">Record and review incoming/outgoing evacuees</p>
      </div>

      <div class="actions">
          <button class="btn primary" @click="openCreate" :disabled="!canCreate" :title="!canCreate ? 'Ask admin to assign you a center first' : ''">
            + Add Log
          </button>
      </div>
    </div>

    <div v-if="isStaff && !me.assigned_center_id" class="warn-banner">
      <span class="warn-icon">!</span>
      <div>
        <b>Unassigned center</b>
        <div class="muted small">You can’t add logs until an admin assigns you to an evacuation center.</div>
      </div>
    </div>

    <!-- FILTER / CONTROLS -->
    <div class="card">
      <div class="row" style="align-items: center;">
        <div class="info-block">
          <div class="label">Logged in as</div>
          <div>
            <b>{{ me.email || "-" }}</b>
            <span class="muted">({{ me.role || "-" }})</span>
          </div>
        </div>

        <div v-if="isStaff" class="info-block">
          <div class="label">Assigned center</div>
          <div><b>{{ me.assigned_center_name || "Unassigned" }}</b></div>
        </div>

        <div class="info-block accent">
          <div class="label">Current Total Evacuees</div>
          <div class="value">{{ currentEvacuees }}</div>
          <div class="muted">Computed from all logs</div>
        </div>

        <div v-if="isAdminOrMunicipalOrResponse" class="info-block" style="min-width: 320px;">
          <div class="label">Filter by center</div>
          <select v-model.number="filters.center" @change="fetchLogs(1)" class="control">
            <option :value="null">All centers</option>
            <option v-for="c in centers" :key="c.id" :value="c.id">
              {{ c.name }} ({{ c.municipality_name }})
            </option>
          </select>
        </div>

        <div style="margin-left:auto; display:flex; gap:10px;">
          <button class="btn ghost amber" @click="fetchLogs(1)" :disabled="loading">
            ⟳ Refresh logs
          </button>
          <button
            v-if="isAdminOrMunicipalOrResponse"
            class="btn ghost amber"
            @click="fetchCenters()"
          >
            ⟳ Refresh centers
          </button>
        </div>
      </div>
    </div>

    <!-- TABLE -->
    <div class="table-card">
      <div class="pad table-card-head">
        <div>
          <b>Logs</b>
          <div class="muted" style="font-size: 12px;">
            {{ pagination.count || logs.length || 0 }} total
          </div>
        </div>

        <div class="muted" v-if="loading">Loading...</div>
      </div>

      <div class="table-scroll" v-if="!loading">
        <table class="table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Center</th>
              <th>Reason for Evacuation</th>
              <th class="num">In (Ind)</th>
              <th class="num">Out (Ind)</th>
              <th class="num">Vulnerable</th>
              <th class="num">Vulnerable Out</th>
              <th class="num">Total Current</th>
              <th class="remarks">Remarks</th>
              <th style="width: 190px;">Actions</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="log in logs" :key="log.id">
              <td class="date-cell">{{ formatDate(log.date_recorded) }}</td>
              <td>
                <span class="center-dot"></span>{{ log.center_name || log.center }}
              </td>
              <td>
                <span v-if="log.reason_for_evacuation_display" class="reason-chip">
                  {{ log.reason_for_evacuation_display }}
                </span>
                <span v-else class="muted">-</span>
              </td>
              <td class="num"><span class="badge green">{{ log.individuals_in }}</span></td>
              <td class="num"><span class="badge red">{{ log.individuals_out }}</span></td>
              <td class="num"><span class="badge amber">{{ log.vulnerable_individuals }}</span></td>
              <td class="num"><span class="badge pink">{{ logVulnerableOut(log) }}</span></td>
              <td class="num">
                <span class="total-pill">{{ log.total_current }}</span>
              </td>
              <td class="remarks">
                {{ log.remarks || "-" }}
              </td>
              <td class="action-cell">
                <button class="btn ghost teal sm" @click="openEdit(log)">Edit</button>
                <button class="btn danger sm" @click="deleteLog(log)">Delete</button>
              </td>
            </tr>

            <tr v-if="logs.length === 0">
              <td colspan="10" class="empty">No logs found.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div class="pager" v-if="pagination.count > 0">
        <button class="btn ghost teal sm" :disabled="!pagination.previous" @click="fetchLogs(pagination.page - 1)">
          ← Prev
        </button>

        <div class="muted page-indicator">
          Page {{ pagination.page }} of {{ Math.ceil(pagination.count / pagination.page_size) }}
        </div>

        <button class="btn ghost teal sm" :disabled="!pagination.next" @click="fetchLogs(pagination.page + 1)">
          Next →
        </button>
      </div>
    </div>

    <!-- MODAL (uses your .backdrop/.modal/.grid CSS) -->
    <div v-if="modal.open" class="backdrop" @click.self="closeModal">
      <div class="modal">
        <div style="display:flex; align-items:center; justify-content:space-between;">
          <h3 style="margin:0;">
            {{ modal.mode === 'create' ? 'Add Log' : 'Edit Log' }}
          </h3>
          <button class="btn ghost close-btn" @click="closeModal" :disabled="saving">&times;</button>
        </div>

        <div class="grid">
          <!-- Center selector -->
          <label v-if="isAdminOrMunicipalOrResponse" class="wide">
            Evacuation Center
            <select v-model.number="modal.form.center">
              <option :value="null">Select center</option>
              <option v-for="c in centers" :key="c.id" :value="c.id">
                {{ c.name }} ({{ c.municipality_name }})
              </option>
            </select>
          </label>

          <div class="checkbox-section">
            <p class="section-title">Classification / Reason for Evacuation</p>

            <label class="full">
              Reason for Evacuation
              <select v-model="modal.form.reason_for_evacuation" required>
                <option :value="null" disabled>-- Select reason --</option>
                <option
                  v-for="reason in availableReasonOptions"
                  :key="reason.id"
                  :value="reason.id"
                >
                  {{ reason.name }}
                </option>
              </select>
              <small v-if="reasonsError" class="field-error">{{ reasonsError }}</small>
            </label>
          </div>

          <label>
            Families In
            <input v-model.number="modal.form.families_in" type="number" min="0" />
          </label>

          <label>
            Individuals In
            <input v-model.number="modal.form.individuals_in" type="number" min="0" />
          </label>

          <label>
            Families Out
            <input v-model.number="modal.form.families_out" type="number" min="0" />
          </label>

          <label>
            Individuals Out
            <input v-model.number="modal.form.individuals_out" type="number" min="0" />
          </label>

          <div class="wide">
            <div style="display:flex; align-items:center; justify-content:space-between; gap:10px;">
              <b style="">Vulnerable Arriving</b>
              <span style="font-size:12px; opacity:.7;">
                Total: {{ vulnerableInTotal }}
              </span>
            </div>

            <div class="vgrid">
              <label>
                Children
                <input v-model.number="modal.form.children_count" type="number" min="0" />
              </label>

              <label>
                Seniors
              <input v-model.number="modal.form.senior_count" type="number" min="0" />
              </label>

              <label>
                PWD
              <input v-model.number="modal.form.pwd_count" type="number" min="0" /> 
              </label>

              <label>
                Pregnant
                <input v-model.number="modal.form.pregnant_count" type="number" min="0" />
              </label>

              <label>
                Lactating
                <input v-model.number="modal.form.lactating_count" type="number" min="0" />
              </label>
            </div>
          </div>

          <div class="wide">
            <div style="display:flex; align-items:center; justify-content:space-between; gap:10px;">
              <b style="">Vulnerable Leaving</b>
              <span style="font-size:12px; opacity:.7;">
                Total: {{ vulnerableOutTotal }}
              </span>
            </div>

            <div class="vgrid">
              <label>
                Children
                <input v-model.number="modal.form.children_out" type="number" min="0" />
              </label>

              <label>
                Seniors
              <input v-model.number="modal.form.senior_out" type="number" min="0" />
              </label>

              <label>
                PWD
              <input v-model.number="modal.form.pwd_out" type="number" min="0" /> 
              </label>

              <label>
                Pregnant
                <input v-model.number="modal.form.pregnant_out" type="number" min="0" />
              </label>

              <label>
                Lactating
                <input v-model.number="modal.form.lactating_out" type="number" min="0" />
              </label>
            </div>
          </div>

          <label class="wide">
            Remarks
            <textarea v-model="modal.form.remarks" rows="3" placeholder="Optional notes..."></textarea>
          </label>
        </div>
<form @submit.prevent="saveLog">
  <div class="error" v-if="modalError">
    {{ modalError }}
  </div>

  <div class="modal-actions">
    <button class="btn primary" type="submit" :disabled="saving">
      {{ saving ? "Saving..." : "Save" }}
    </button>
    <button class="btn ghost" type="button" @click="closeModal" :disabled="saving">
      Cancel
    </button>
  </div>
</form>
      </div>
      
    </div>

  </div>
</template>

<script>
import api from "../../services/api";

export default {
  name: "StaffLogs",
  data() {
    return {
      me: {},
      centers: [],
      logs: [],
      summary: null,
      loading: false,
      saving: false,
      modalError: "",

      filters: {
        center: null,
      },

      reasonOptions: [],
      reasonsLoading: false,
      reasonsError: "",

      pagination: {
        page: 1,
        page_size: 10,
        count: 0,
        next: null,
        previous: null,
      },

      modal: {
        open: false,
        mode: "create",
        id: null,
        form: {
          center: null,
          reason_for_evacuation: null,
          reason_for_evacuation_name: "",
          disaster_cause: "OTHER",
          families_in: 0,
          individuals_in: 0,
          families_out: 0,
          individuals_out: 0,
          remarks: "",
          children_count: 0,
          senior_count: 0,
          pwd_count: 0,
          pregnant_count: 0,
          lactating_count: 0,
          children_out: 0,
          senior_out: 0,
          pwd_out: 0,
          pregnant_out: 0,
          lactating_out: 0,
        },
      },
    };
  },

  computed: {
    isStaff() {
      return this.me.role === "EVAC_CENTER_STAFF";
    },
    isAdminOrMunicipalOrResponse() {
      return ["PROVINCIAL_ADMIN", "MUNICIPAL_ADMIN", "RESPONSE_TEAM"].includes(this.me.role);
    },
    canCreate() {
      if (this.isStaff) return !!this.me.assigned_center_id;
      return this.isAdminOrMunicipalOrResponse;
    },
    latestLog() {
      if (!this.logs?.length) return null;
      return this.logs.reduce((latest, cur) => {
        const a = new Date(latest?.date_recorded || 0).getTime();
        const b = new Date(cur?.date_recorded || 0).getTime();
        if (b > a) return cur;
        if (b === a) return (cur.id ?? 0) > (latest.id ?? 0) ? cur : latest;
        return latest;
      }, this.logs[0]);
    },
    availableReasonOptions() {
      const options = [...this.reasonOptions];
      const currentId = this.modal.form.reason_for_evacuation;
      const alreadyListed = options.some((reason) => reason.id === currentId);
      if (currentId && !alreadyListed && this.modal.form.reason_for_evacuation_name) {
        options.push({
          id: currentId,
          name: `${this.modal.form.reason_for_evacuation_name} (inactive)`,
        });
      }
      return options;
    },
    currentEvacuees() {
      return this.summary?.total_current ?? 0;
    },
    lastUpdatedText() {
      if (!this.latestLog?.date_recorded) return "-";
      const d = new Date(this.latestLog.date_recorded);
      return isNaN(d.getTime()) ? this.latestLog.date_recorded : d.toLocaleString();
    },
    vulnerableInTotal() {
      const f = this.modal.form || {};
      return (
        (f.children_count || 0) +
        (f.senior_count || 0) +
        (f.pwd_count || 0) +
        (f.pregnant_count || 0) +
        (f.lactating_count || 0)
      );
    },
    vulnerableOutTotal() {
      const f = this.modal.form || {};
      return (
        (f.children_out || 0) +
        (f.senior_out || 0) +
        (f.pwd_out || 0) +
        (f.pregnant_out || 0) +
        (f.lactating_out || 0)
      );
    },
    activeCenterLabel() {
      if (this.isStaff) return this.me.assigned_center_name || "Unassigned";
      if (this.filters.center) {
        const c = this.centers.find(x => x.id === this.filters.center);
        return c ? `${c.name}${c.municipality_name ? ` (${c.municipality_name})` : ""}` : `Center #${this.filters.center}`;
      }
      return "All Centers";
    },
  },

  async mounted() {
    await this.fetchMe();
    if (this.isAdminOrMunicipalOrResponse) {
      await this.fetchCenters();
    }
    await this.fetchLogs(1);
    await this.fetchReasonOptions();
  },

methods: {
    formatDate(dt) {
      if (!dt) return "-";
      const d = new Date(dt);
      return isNaN(d.getTime()) ? dt : d.toLocaleString();
    },

    logVulnerableOut(log) {
      return (
        (log.children_out || 0) +
        (log.senior_out || 0) +
        (log.pwd_out || 0) +
        (log.pregnant_out || 0) +
        (log.lactating_out || 0)
      );
    },

    async fetchReasonOptions() {
      this.reasonsLoading = true;
      this.reasonsError = "";
      try {
        const res = await api.get("evac_centers/evacuation-reasons/");
        const data = res.data;
        const reasons = data.results || (Array.isArray(data) ? data : []);
        this.reasonOptions = reasons.filter((reason) => reason.is_active !== false);
        console.log("[fetchReasonOptions] loaded", this.reasonOptions);
      } catch (e) {
        console.error("[fetchReasonOptions] error:", e);
        this.reasonOptions = [];
        this.reasonsError = e?.response?.data?.detail || "Unable to load evacuation reasons.";
      } finally {
        this.reasonsLoading = false;
      }
    },

    async fetchMe() {
      const res = await api.get("user/profile/");
      this.me = res.data;
      if (this.me.role === "EVAC_CENTER_STAFF") {
        this.filters.center = null;
      }
    },

    async fetchCenters() {
      const res = await api.get("evac_centers/evacuation-centers/");
      const data = res.data;
      this.centers = Array.isArray(data) ? data : (data.results || []);
    },

    async fetchLogs(page = 1) {
      this.loading = true;
      try {
        const pageNum = Number(page) || 1;
        const params = new URLSearchParams();
        params.append("page", pageNum);
        params.append("page_size", this.pagination.page_size);

        if (this.isStaff && this.me.assigned_center_id) {
          params.append("center", this.me.assigned_center_id);
        } else if (this.filters.center) {
          params.append("center", this.filters.center);
        }

        const res = await api.get(`evac_centers/evacuation-logs/?${params.toString()}`);
        const data = res.data;

        this.logs = data.results || (Array.isArray(data) ? data : []);
        this.pagination.count = data.count || this.logs.length || 0;
        this.pagination.next = data.next || null;
        this.pagination.previous = data.previous || null;
        this.pagination.page = pageNum;
        await this.fetchSummary();
      } finally {
        this.loading = false;
      }
    },

    async fetchSummary() {
      try {
        let url = "evac_centers/evacuation-logs/staff_summary/";
        if (!this.isStaff && this.filters.center) {
          url += `?center=${this.filters.center}`;
        }
        const res = await api.get(url);
        this.summary = res.data;
      } catch (e) {
        console.error("fetchSummary error:", e);
      }
    },

    openCreate() {
      this.modalError = "";
      this.modal.open = true;
      this.modal.mode = "create";
      this.modal.id = null;

      this.modal.form = {
        center: this.isStaff ? (this.me.assigned_center_id || null) : null,
        reason_for_evacuation: null,
        reason_for_evacuation_name: "",
        disaster_cause: "OTHER",
        families_in: 0,
        individuals_in: 0,
        families_out: 0,
        individuals_out: 0,
        children_count: 0,
        senior_count: 0,
        pwd_count: 0,
        pregnant_count: 0,
        lactating_count: 0,
        children_out: 0,
        senior_out: 0,
        pwd_out: 0,
        pregnant_out: 0,
        lactating_out: 0,
        remarks: "",
      };
    },

    openEdit(log) {
      this.modalError = "";
      this.modal.open = true;
      this.modal.mode = "edit";
      this.modal.id = log.id;

      this.modal.form = {
        center: log.center || null,
        reason_for_evacuation: log.reason_for_evacuation || null,
        reason_for_evacuation_name: log.reason_for_evacuation_display || "",
        disaster_cause: log.disaster_cause || "OTHER",
        families_in: log.families_in ?? 0,
        individuals_in: log.individuals_in ?? 0,
        families_out: log.families_out ?? 0,
        individuals_out: log.individuals_out ?? 0,
        children_count: log.children_count ?? 0,
        senior_count: log.senior_count ?? 0,
        pwd_count: log.pwd_count ?? 0,
        pregnant_count: log.pregnant_count ?? 0,
        lactating_count: log.lactating_count ?? 0,
        children_out: log.children_out ?? 0,
        senior_out: log.senior_out ?? 0,
        pwd_out: log.pwd_out ?? 0,
        pregnant_out: log.pregnant_out ?? 0,
        lactating_out: log.lactating_out ?? 0,
        remarks: log.remarks || "",
      };
    },

    closeModal() {
      this.modal.open = false;
      this.modal.id = null;
      this.modalError = "";
    },

    async saveLog() {
      console.log("[saveLog] clicked", {
        role: this.me.role,
        assigned_center_id: this.me.assigned_center_id,
        isStaff: this.isStaff,
        mode: this.modal.mode,
        form_center: this.modal.form.center,
      });

      this.saving = true;
      this.modalError = "";
      try {
        if (this.isStaff) {
          if (!this.me.assigned_center_id) {
            this.modalError = "You have no assigned evacuation center.";
            return;
          }
          if (!this.modal?.form) {
            this.modalError = "Form not initialized. Please reopen the modal.";
            return;
          }
          this.modal.form.center = this.me.assigned_center_id;
        } else {
          if (!this.modal.form.center) {
            this.modalError = "Please select an evacuation center.";
            return;
          }
        }

        const payload = {
          center: this.modal.form.center,
          reason_for_evacuation: this.modal.form.reason_for_evacuation,
          families_in: this.modal.form.families_in ?? 0,
          individuals_in: this.modal.form.individuals_in ?? 0,
          families_out: this.modal.form.families_out ?? 0,
          individuals_out: this.modal.form.individuals_out ?? 0,

          children_count: this.modal.form.children_count ?? 0,
          senior_count: this.modal.form.senior_count ?? 0,
          pwd_count: this.modal.form.pwd_count ?? 0,
          pregnant_count: this.modal.form.pregnant_count ?? 0,
          lactating_count: this.modal.form.lactating_count ?? 0,

          children_out: this.modal.form.children_out ?? 0,
          senior_out: this.modal.form.senior_out ?? 0,
          pwd_out: this.modal.form.pwd_out ?? 0,
          pregnant_out: this.modal.form.pregnant_out ?? 0,
          lactating_out: this.modal.form.lactating_out ?? 0,

          remarks: this.modal.form.remarks || "",
        };

        console.log("[saveLog] payload", payload);
        if (!this.modal?.form) {
          this.modalError = "Form not initialized. Please reopen the modal.";
          return;
        }

        if (this.modal.mode === "create") {
          const res = await api.post("evac_centers/evacuation-logs/", payload);
          this.logs.unshift(res.data);
        } else {
          await api.patch(`evac_centers/evacuation-logs/${this.modal.id}/`, payload);
        }

        this.closeModal();
        await this.fetchLogs(1);
      } catch (e) {
        this.modalError =
          e?.response?.data?.detail ||
          (typeof e?.response?.data === "string" ? e.response.data : "") ||
          "Save failed.";
        console.error("saveLog error:", e);
      } finally {
        this.saving = false;
      }
    },

    async deleteLog(log) {
      const ok = confirm("Delete this log? This cannot be undone.");
      if (!ok) return;
      await api.delete(`evac_centers/evacuation-logs/${log.id}/`);
      await this.fetchLogs(1);
    },
  },
};
</script>

<style scoped>
.page {
  --bg: #060912;
  --panel: rgba(10,14,28,.65);
  --panel2: rgba(8,12,24,.82);
  --border2: rgba(255,255,255,.08);
  --text: #e5e7eb;
  --muted: rgba(229,231,235,.62);

  --blue: #38bdf8;
  --blue2: #6366f1;
  --violet: #a78bfa;
  --pink: #f472b6;
  --green: #34d399;
  --red: #fb7185;
  --amber: #fbbf24;
  --teal: #2dd4bf;

  --field-bg: rgba(2,6,23,.55);
  --field-border: rgba(56,189,248,.18);
  --modal-a: rgba(10,14,28,.96);
  --modal-b: rgba(6,9,18,.98);

  padding: 20px;
  color: var(--text);
  background:
    radial-gradient(900px 400px at 8% -10%, rgba(99,102,241,.10), transparent 60%),
    radial-gradient(700px 380px at 100% 0%, rgba(244,114,182,.08), transparent 55%);
}

[data-theme="light"] .page {
  --bg: #f0f4fa;
  --panel: rgba(255,255,255,.92);
  --panel2: rgba(255,255,255,.96);
  --border2: rgba(15,23,42,.18);
  --text: #0f172a;
  --muted: rgba(15,23,42,.55);
  --field-bg: rgba(255,255,255,.95);
  --field-border: rgba(15,23,42,.14);
  --modal-a: rgba(255,255,255,.98);
  --modal-b: rgba(244,246,251,.98);
}

.page-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}
.page-header h1 {
  margin: 0;
  font-size: 1.7rem;
  font-weight: 900;
  background: linear-gradient(90deg, #f8fafc, var(--blue) 65%, var(--violet));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}
.page-header p { margin: 6px 0 0; color: var(--muted); font-size: 13px; }

.actions { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }

.warn-banner {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-top: 12px;
  padding: 12px 14px;
  border-radius: 14px;
  border: 1px solid rgba(251,191,36,.4);
  background: linear-gradient(90deg, rgba(251,191,36,.16), rgba(251,191,36,.03));
  color: var(--text);
}
.warn-icon {
  flex: 0 0 auto;
  width: 20px; height: 20px;
  display: grid; place-items: center;
  border-radius: 999px;
  font-weight: 1000;
  font-size: 12px;
  color: #1a1200;
  background: var(--amber);
}

.card {
  margin-top: 14px;
  border-radius: 16px;
  padding: 14px;
  border: 1px solid var(--border2);
  background: linear-gradient(135deg, rgba(99,102,241,.07), rgba(8,12,24,.85) 40%);
  box-shadow: 0 16px 34px rgba(0,0,0,.42);
  backdrop-filter: blur(10px);
}

[data-theme="light"] .card {
  background: linear-gradient(135deg, rgba(99,102,241,.04), rgba(255,255,255,.92) 40%);
  box-shadow: 0 16px 34px rgba(0,0,0,.08);
}

.row { display: flex; gap: 0; flex-wrap: wrap; align-items: center; }
.info-block {
  padding: 2px 22px;
  border-right: 1px solid var(--border2);
}
.info-block:first-child { padding-left: 4px; }
.info-block.accent {
  padding-left: 22px;
  padding-right: 22px;
  border-left: 2px solid rgba(52,211,153,.5);
}

.label { font-size: 12px; color: var(--muted); font-weight: 800; letter-spacing: .2px; }
.value {
  font-size: 28px;
  font-weight: 1000;
  margin-top: 4px;
  background: linear-gradient(90deg, #6ee7c0, var(--teal));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}
.muted { color: var(--muted); margin-top: 6px; }
.muted.small { font-size: 12px; margin-top: 2px; }

.table-card {
  margin-top: 14px;
  border-radius: 18px;
  overflow: hidden;
  border: 1px solid var(--border2);
  background: var(--panel2);
  box-shadow: 0 20px 48px rgba(0,0,0,.48);
}

[data-theme="light"] .table-card {
  box-shadow: 0 20px 48px rgba(0,0,0,.08);
}

.table-card-head {
  display: flex; align-items: center; justify-content: space-between;
  border-bottom: 1px solid var(--border2);
}
.pad { padding: 12px 14px; }

.table-scroll { overflow-x: auto; }

.table { width: 100%; border-collapse: collapse; min-width: 980px; }
.table th, .table td {
  padding: 13px 14px;
  border-bottom: 1px solid var(--border2);
  text-align: left;
}
.table th {
  position: sticky;
  top: 0;
  background: linear-gradient(90deg, rgba(56,189,248,.16), rgba(99,102,241,.16), rgba(244,114,182,.12));
  color: #f0f9ff;
  font-size: 11.5px;
  text-transform: uppercase;
  letter-spacing: .7px;
  font-weight: 1000;
  white-space: nowrap;
  border-bottom: 1px solid rgba(56,189,248,.3);
}

[data-theme="light"] .table th {
  background: linear-gradient(90deg, rgba(56,189,248,.10), rgba(99,102,241,.10), rgba(244,114,182,.08));
  color: #0f172a;
  border-bottom: 1px solid rgba(15,23,42,.18);
}

.table th.num, .table td.num { text-align: right; }

.table tbody tr { transition: background .12s ease; }
.table tbody tr:nth-child(even) { background: rgba(255,255,255,.025); }
.table tbody tr:hover { background: rgba(99,102,241,.09); }

[data-theme="light"] .table tbody tr:nth-child(even) { background: rgba(15,23,42,.03); }
[data-theme="light"] .table tbody tr:hover { background: rgba(99,102,241,.06); }

.table td { color: var(--text); font-size: 13.5px; }
.date-cell { color: var(--muted); font-size: 12.5px; }
.remarks { max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.empty { text-align: center; color: var(--muted); padding: 26px; }

.center-dot {
  display: inline-block;
  width: 7px; height: 7px;
  border-radius: 999px;
  background: var(--blue);
  margin-right: 8px;
  box-shadow: 0 0 0 3px rgba(56,189,248,.18);
}

.reason-chip {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(167,139,250,.18);
  border: 1px solid rgba(167,139,250,.35);
  color: #ede9ff;
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
}

[data-theme="light"] .reason-chip {
  background: rgba(167,139,250,.14);
  border: 1px solid rgba(167,139,250,.4);
  color: #5b21b6;
}

.badge {
  display: inline-flex;
  min-width: 26px;
  justify-content: center;
  padding: 4px 9px;
  border-radius: 999px;
  font-weight: 900;
  font-size: 13px;
}
.badge.green { background: rgba(52,211,153,.16); border: 1px solid rgba(52,211,153,.4); color: #a7f3d5; }
.badge.red { background: rgba(251,113,133,.14); border: 1px solid rgba(251,113,133,.4); color: #ffcdd6; }
.badge.amber { background: rgba(251,191,36,.14); border: 1px solid rgba(251,191,36,.4); color: #fde3a7; }
.badge.pink { background: rgba(244,114,182,.14); border: 1px solid rgba(244,114,182,.4); color: #ffd3ec; }

[data-theme="light"] .badge.green { background: rgba(52,211,153,.20); border: 1px solid rgba(52,211,153,.55); color: #047857; font-weight: 1000; }
[data-theme="light"] .badge.red { background: rgba(251,113,133,.20); border: 1px solid rgba(251,113,133,.55); color: #b91c1c; font-weight: 1000; }
[data-theme="light"] .badge.amber { background: rgba(251,191,36,.20); border: 1px solid rgba(251,191,36,.55); color: #92400e; font-weight: 1000; }
[data-theme="light"] .badge.pink { background: rgba(244,114,182,.20); border: 1px solid rgba(244,114,182,.55); color: #9d174d; font-weight: 1000; }

.total-pill {
  display: inline-flex;
  min-width: 32px;
  justify-content: center;
  padding: 5px 11px;
  border-radius: 999px;
  background: linear-gradient(135deg, rgba(56,189,248,.9), rgba(99,102,241,.9));
  color: #06121f;
  font-weight: 1000;
  font-size: 13.5px;
  box-shadow: 0 6px 16px rgba(99,102,241,.35);
}

[data-theme="light"] .total-pill {
  background: linear-gradient(135deg, #38bdf8, #6366f1);
  color: #ffffff;
}

.action-cell { display: flex; gap: 8px; }

.btn {
  border-radius: 14px;
  padding: 10px 14px;
  font-size: 13px;
  font-weight: 1000;
  border: 1px solid rgba(56,189,248,.22);
  cursor: pointer;
  background: rgba(38, 165, 219, 0.651);
  color: #cdefff;
  transition: transform .12s ease, background .12s ease, border-color .12s ease, box-shadow .12s ease;
}
.btn:hover:not(:disabled) { transform: translateY(-1px); background: rgba(56, 191, 248, 0.541); }
.btn:disabled { opacity: .55; cursor: not-allowed; transform: none; }

.btn.sm { padding: 7px 11px; font-size: 12px; border-radius: 10px; }

.btn.primary {
  position: relative;
  border: 0 !important;
  border-radius: 14px !important;
  padding: 14px 28px !important;
  font-weight: 700 !important;
  font-size: 0.95rem !important;
  cursor: pointer;
  color: #fff !important;
  background: linear-gradient(135deg, var(--blue, #38bdf8), var(--blue2, #6366f1) 50%, var(--violet, #a78bfa)) !important;
  box-shadow: 0 8px 28px rgba(99,102,241,.35) !important;
  transition: all .25s ease !important;
  letter-spacing: 0.3px !important;
  overflow: hidden !important;
}

.btn.primary::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255,255,255,.15), transparent 50%);
  border-radius: 14px;
  opacity: 0;
  transition: opacity .3s ease;
}

.btn.primary:hover:not(:disabled) {
  transform: translateY(-2px) scale(1.02) !important;
  box-shadow: 0 12px 40px rgba(99,102,241,.5) !important;
}

.btn.primary:hover:not(:disabled)::before {
  opacity: 1;
}

.btn.primary:active:not(:disabled) {
  transform: translateY(0) scale(.98) !important;
}

.btn.primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

.btn.ghost {
  background: rgba(2,6,23,.45);
  color: var(--text);
  border-color: rgba(255,255,255,.10);
  transition: all .25s ease !important;
}

[data-theme="light"] .btn.ghost {
  background: rgba(255,255,255,.9);
  border-color: rgba(15,23,42,.22);
  color: #0f172a;
}

.btn.ghost.teal {
  border-color: rgba(45,212,191,.35);
  color: #b6f5ec;
}
.btn.ghost.teal:hover:not(:disabled) {
  background: rgba(45,212,191,.14);
  border-color: rgba(45,212,191,.35);
  color: #b6f5ec;
  transform: translateY(-1px);
}

[data-theme="light"] .btn.ghost.teal {
  background: rgba(45,212,191,.10);
  border-color: rgba(45,212,191,.5);
  color: #0d9488;
  font-weight: 900;
}
[data-theme="light"] .btn.ghost.teal:hover:not(:disabled) {
  background: rgba(45,212,191,.18);
  border-color: rgba(45,212,191,.6);
  color: #0f766e;
}

.btn.ghost.amber {
  border-color: rgba(251,191,36,.35);
  color: #ffe6ad;
}
.btn.ghost.amber:hover:not(:disabled) {
  background: rgba(251,191,36,.14);
  border-color: rgba(251,191,36,.35);
  color: #ffe6ad;
  transform: translateY(-1px);
}

[data-theme="light"] .btn.ghost.amber {
  background: rgba(251,191,36,.10);
  border-color: rgba(251,191,36,.5);
  color: #92400e;
  font-weight: 900;
}
[data-theme="light"] .btn.ghost.amber:hover:not(:disabled) {
  background: rgba(251,191,36,.18);
  border-color: rgba(251,191,36,.6);
  color: #78350f;
}

.modal-actions .btn.ghost {
  border-radius: 12px !important;
  padding: 12px 28px !important;
  font-weight: 700 !important;
  font-size: 0.9rem !important;
  border: 2px solid var(--border2, rgba(255,255,255,.08)) !important;
  background: var(--field-bg, rgba(2,6,23,.55)) !important;
  color: var(--muted, rgba(229,231,235,.62)) !important;
  letter-spacing: 0.3px !important;
}

.modal-actions .btn.ghost:hover:not(:disabled) {
  border-color: var(--red) !important;
  color: var(--red) !important;
  background: rgba(239,68,68,.06) !important;
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(239,68,68,.1);
}

[data-theme="light"] .modal-actions .btn.ghost {
  border-color: rgba(15,23,42,.28) !important;
  background: #f1f5f9 !important;
  color: #334155 !important;
}
[data-theme="light"] .modal-actions .btn.ghost:hover:not(:disabled) {
  border-color: var(--red) !important;
  color: var(--red) !important;
  background: rgba(239,68,68,.08) !important;
}

.btn.danger {
  background: rgba(239,68,68,.85);
  color: #fff;
  border-color: rgba(239,68,68,.6);
  box-shadow: 0 4px 10px rgba(239,68,68,.20);
}
.btn.danger:hover:not(:disabled) {
  background: rgba(239,68,68,1);
  box-shadow: 0 3px 8px rgba(199, 54, 54, 0.589);
  transform: translateY(-1px);
}

[data-theme="light"] .btn.danger {
  background: #ef4444;
  border-color: #dc2626;
  color: #fff;
  box-shadow: 0 4px 10px rgba(239,68,68,.25);
}
[data-theme="light"] .btn.danger:hover:not(:disabled) {
  background: #dc2626;
}

.btn.ghost.close-btn {
  width: 40px !important;
  height: 40px !important;
  padding: 0 !important;
  border: 2px solid rgba(239,68,68,.25) !important;
  border-radius: 999px !important;
  background: rgba(239,68,68,.06) !important;
  color: #64748b !important;
  font-size: 1.6rem !important;
  font-weight: 300 !important;
  line-height: 1 !important;
  cursor: pointer;
  transition: all .4s ease !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  flex-shrink: 0 !important;
  min-width: 40px !important;
}

.btn.ghost.close-btn:hover:not(:disabled) {
  background: rgba(239,68,68,.85) !important;
  color: #ffffff !important;
  transform: rotate(90deg) !important;
  border-color: rgba(239,68,68,.85) !important;
}

[data-theme="light"] .btn.ghost.close-btn {
  color: #64748b !important;
  border-color: rgba(239,68,68,.3) !important;
  background: rgba(239,68,68,.08) !important;
}

[data-theme="light"] .btn.ghost.close-btn:hover:not(:disabled) {
  background: rgba(239,68,68,.85) !important;
  color: #ffffff !important;
}

.pager {
  display: flex; align-items: center; justify-content: flex-end; gap: 12px;
  padding: 12px 14px;
  border-top: 1px solid var(--border2);
}
.page-indicator { margin-top: 0; font-size: 12.5px; }

.backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,.60);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  z-index: 2000;
}
.modal {
  width: min(760px, 100%);
  max-height: 92vh;
  overflow-y: auto;
  border-radius: 18px;
  border: 1px solid rgba(99,102,241,.22);
  background:
    radial-gradient(1200px 520px at 20% -20%, rgba(99,102,241,.22), transparent 55%),
    linear-gradient(180deg, var(--modal-a), var(--modal-b));
  box-shadow: 0 30px 80px rgba(0,0,0,.62);
  padding: 16px;
  color: var(--text);
}

[data-theme="light"] .modal {
  background:
    radial-gradient(1200px 520px at 20% -20%, rgba(99,102,241,.22), transparent 55%),
    linear-gradient(180deg, var(--modal-a, rgba(10,14,28,.96)), var(--modal-b, rgba(6,9,18,.98)));
  border: 1px solid rgba(15,23,42,.14);
  box-shadow: 0 30px 80px rgba(0,0,0,.15);
}

.modal-actions {
  display: flex !important;
  justify-content: flex-end !important;
  gap: 14px !important;
  margin-top: 24px !important;
  padding-top: 18px !important;
  border-top: 2px solid var(--border2) !important;
  background: transparent !important;
  align-items: center !important;
}

[data-theme="light"] .modal-actions {
  border-top-color: rgba(15,23,42,.18) !important;
}

.modal-actions .btn {
  min-width: 120px !important;
  text-align: center !important;
}

.grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-top: 12px;
}
label { display: flex; flex-direction: column; gap: 6px; font-size: 13px; color: var(--muted); font-weight: 800; }
input, textarea, select {
  border: 1px solid var(--field-border, rgba(56,189,248,.18));
  background: var(--field-bg, rgba(2,6,23,.55));
  color: var(--text, #e5e7eb);
  border-radius: 14px;
  padding: 10px 12px;
  font-size: 13px;
  outline: none;
}
input:focus, textarea:focus, select:focus {
  border-color: rgba(99,102,241,.5);
  box-shadow: 0 0 0 4px rgba(99,102,241,.15);
}
.wide { grid-column: 1 / -1; }

[data-theme="light"] input,
[data-theme="light"] textarea,
[data-theme="light"] select {
  background: #ffffff;
  border-color: rgba(15,23,42,.18);
  color: #0f172a;
}

[data-theme="light"] input:focus,
[data-theme="light"] textarea:focus,
[data-theme="light"] select:focus {
  border-color: rgba(99,102,241,.4);
  box-shadow: 0 0 0 4px rgba(99,102,241,.10);
}

.vgrid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 10px;
}
@media (max-width: 760px) {
  .grid { grid-template-columns: 1fr; }
  .vgrid { grid-template-columns: 1fr 1fr; }
}

.error { margin-top: 10px; color: #fecaca; font-size: 13px; }

[data-theme="light"] .error { color: #b91c1c; }

.checkbox-section {
  background: rgba(255,255,255,0.03) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 14px !important;
  padding: 12px 14px !important;
}

[data-theme="light"] .checkbox-section {
  background: rgba(15,23,42,.02) !important;
}

.checkbox-section label.full,
.checkbox-section label {
  background: none !important;
  background-color: transparent !important;
}

.section-title {
  margin: 0 0 10px !important;
  font-weight: 800 !important;
  color: var(--text) !important;
  background: none !important;
}
.field-error {
  color: #fca5a5 !important;
  background: none !important;
  font-size: 12px;
}

[data-theme="light"] .field-error {
  color: #dc2626 !important;
}

/* ===================================================================
   GLOBAL-STYLE COLLISION OVERRIDES — light mode only
   Your app has global stylesheets (visible in devtools) that target
   .primary, .btn.primary, .save-btn, .add-btn, .submit-btn, .ghost,
   .cancel-btn, button[type='submit'] with !important and higher
   selector specificity than this component's own rules. These blocks
   use extra ancestor context (html + [data-theme] + .page + child
   class) to outrank them so this component's intended colors win.
   =================================================================== */
html[data-theme="light"] .page .actions .btn.primary,
html[data-theme="light"] .page .modal-actions .btn.primary,
html[data-theme="light"] .page form .btn.primary {
  background: linear-gradient(135deg, #38bdf8, #6366f1 50%, #a78bfa) !important;
  color: #ffffff !important;
  border-color: transparent !important;
  -webkit-text-fill-color: #ffffff !important;
}

html[data-theme="light"] .page .modal-actions .btn.ghost {
  border-color: rgba(15,23,42,.28) !important;
  background: #f1f5f9 !important;
  color: #334155 !important;
  -webkit-text-fill-color: #334155 !important;
}
html[data-theme="light"] .page .modal-actions .btn.ghost:hover:not(:disabled) {
  border-color: #ef4444 !important;
  color: #ef4444 !important;
  -webkit-text-fill-color: #ef4444 !important;
  background: rgba(239,68,68,.08) !important;
}

html[data-theme="light"] .page .action-cell .btn.ghost.teal {
  background: rgba(45,212,191,.10) !important;
  border-color: rgba(45,212,191,.5) !important;
  color: #0d9488 !important;
  -webkit-text-fill-color: #0d9488 !important;
}
html[data-theme="light"] .page .action-cell .btn.danger {
  background: #ef4444 !important;
  border-color: #dc2626 !important;
  color: #ffffff !important;
  -webkit-text-fill-color: #ffffff !important;
}

html[data-theme="light"] .page .badge.green { background: rgba(52,211,153,.20) !important; border-color: rgba(52,211,153,.55) !important; color: #047857 !important; -webkit-text-fill-color: #047857 !important; }
html[data-theme="light"] .page .badge.red   { background: rgba(251,113,133,.20) !important; border-color: rgba(251,113,133,.55) !important; color: #b91c1c !important; -webkit-text-fill-color: #b91c1c !important; }
html[data-theme="light"] .page .badge.amber { background: rgba(251,191,36,.20) !important; border-color: rgba(251,191,36,.55) !important; color: #92400e !important; -webkit-text-fill-color: #92400e !important; }
html[data-theme="light"] .page .badge.pink  { background: rgba(244,114,182,.20) !important; border-color: rgba(244,114,182,.55) !important; color: #9d174d !important; -webkit-text-fill-color: #9d174d !important; }
</style>