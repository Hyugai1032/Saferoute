<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h1>Evacuation Logs</h1>
        <p class="muted">Record and review incoming/outgoing evacuees</p>
      </div>

      <div class="actions">
          <button class="btn" @click="openCreate" :disabled="!canCreate" :title="!canCreate ? 'Ask admin to assign you a center first' : ''">
            + Add Log
          </button>
            <div v-if="isStaff && !me.assigned_center_id" class="card warn">
                <b>Unassigned center</b>
            <div class="muted">You can’t add logs until an admin assigns you to an evacuation center.</div>
</div>
      </div>
    </div>

    <!-- FILTER / CONTROLS -->
    <div class="card">
      <div class="row" style="align-items: center;">
        <div>
          <div class="label">Logged in as</div>
          <div>
            <b>{{ me.email || "-" }}</b>
            <span class="muted">({{ me.role || "-" }})</span>
          </div>
        </div>

        <div v-if="isStaff">
          <div class="label">Assigned center</div>
          <div><b>{{ me.assigned_center_name || "Unassigned" }}</b></div>
        </div>

        <div>
          <div class="label">Current Total Evacuees</div>
          <div class="value">{{ currentEvacuees }}</div>
          <div class="muted">Based on latest log</div>
        </div>

        <div v-if="isAdminOrMunicipalOrResponse" style="min-width: 320px;">
          <div class="label">Filter by center</div>
          <select v-model.number="filters.center" @change="fetchLogs(1)" class="control">
            <option :value="null">All centers</option>
            <option v-for="c in centers" :key="c.id" :value="c.id">
              {{ c.name }} ({{ c.municipality_name }})
            </option>
          </select>
        </div>

        <div style="margin-left:auto; display:flex; gap:10px;">
          <button class="btn ghost" @click="fetchLogs(1)" :disabled="loading">
            Refresh logs
          </button>
          <button
            v-if="isAdminOrMunicipalOrResponse"
            class="btn ghost"
            @click="fetchCenters()"
          >
            Refresh centers
          </button>
        </div>
      </div>
    </div>

    <!-- TABLE -->
    <div class="table-card">
      <div class="pad" style="display:flex; align-items:center; justify-content:space-between;">
        <div>
          <b>Logs</b>
          <div class="muted" style="font-size: 12px;">
            {{ pagination.count || logs.length || 0 }} total
          </div>
        </div>

        <div class="muted" v-if="loading">Loading...</div>
      </div>

      <div class="pad" v-if="!loading">
        <table class="table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Center</th>
              <th>In (Ind)</th>
              <th>Out (Ind)</th>
              <th>Vulnerable</th>
              <th>Total Current</th>
              <th class="remarks">Remarks</th>
              <th style="width: 200px;">Actions</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="log in logs" :key="log.id">
              <td>{{ formatDate(log.date_recorded) }}</td>
              <td>{{ log.center_name || log.center }}</td>
              <td>{{ log.individuals_in }}</td>
              <td>{{ log.individuals_out }}</td>
              <td>{{ log.vulnerable_individuals }}</td>
              <td><b>{{ log.total_current }}</b></td>
              <td class="remarks">
                {{ log.remarks || "-" }}
              </td>
              <td style="display:flex; gap:8px;">
                <button class="btn ghost" @click="openEdit(log)">Edit</button>
                <button class="btn" @click="deleteLog(log)">Delete</button>
              </td>
            </tr>

            <tr v-if="logs.length === 0">
              <td colspan="8" class="empty">No logs found.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div class="pager" v-if="pagination.count > 0">
        <button class="btn ghost" :disabled="!pagination.previous" @click="fetchLogs(pagination.page - 1)">
          Prev
        </button>

        <div class="muted" style="align-self:center;">
          Page {{ pagination.page }} of {{ Math.ceil(pagination.count / pagination.page_size) }}
        </div>

        <button class="btn ghost" :disabled="!pagination.next" @click="fetchLogs(pagination.page + 1)">
          Next
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
          <button class="btn ghost" @click="closeModal" :disabled="saving">Close</button>
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
              <b style="color:black;">Vulnerable Breakdown</b>
              <span style="font-size:12px; opacity:.7;">
                Total: {{ vulnerableTotal }}
              </span>
            </div>

            <div class="vgrid">
              <label>
                Children
                <input v-model.number="modal.form.children" type="number" min="0" />
              </label>

              <label>
                Seniors
                <input v-model.number="modal.form.seniors" type="number" min="0" />
              </label>

              <label>
                PWD
                <input v-model.number="modal.form.pwd" type="number" min="0" />
              </label>

              <label>
                Pregnant
                <input v-model.number="modal.form.pregnant" type="number" min="0" />
              </label>

              <label>
                Lactating
                <input v-model.number="modal.form.lactating" type="number" min="0" />
              </label>
            </div>
          </div>

          <label class="wide">
            Remarks
            <textarea v-model="modal.form.remarks" rows="3" placeholder="Optional notes..."></textarea>
          </label>
        </div>

        <div class="error" v-if="modalError">
          {{ modalError }}
        </div>

        <div class="modal-actions">
          <button class="btn" @click="saveLog" :disabled="saving">
            {{ saving ? "Saving..." : "Save" }}
          </button>
          <button class="btn ghost" @click="closeModal" :disabled="saving">
            Cancel
          </button>
        </div>
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
      loading: false,
      saving: false,
      modalError: "",

      filters: {
        center: null, // admin filter
      },

      pagination: {
        page: 1,
        page_size: 10,
        count: 0,
        next: null,
        previous: null,
      },

      modal: {
        open: false,
        mode: "create", // create | edit
        id: null,
        form: {
          center: null,
          families_in: 0,
          individuals_in: 0,
          families_out: 0,
          individuals_out: 0,
          vulnerable_individuals: 0,
          remarks: "",
          children: 0,
          seniors: 0,
          pwd: 0,
          pregnant: 0,
          lactating: 0
        },
      },
    };
  },

  vulnerableTotal() {
  const f = this.modal.form;
  return (f.children||0)+(f.seniors||0)+(f.pwd||0)+(f.pregnant||0)+(f.lactating||0);
},

  computed: {
    isStaff() {
      return this.me.role === "EVAC_CENTER_STAFF";
    },
    isAdminOrMunicipalOrResponse() {
      return ["PROVINCIAL_ADMIN", "MUNICIPAL_ADMIN", "RESPONSE_TEAM"].includes(this.me.role);
    },
    canCreate() {
      // Staff can create only if assigned
      if (this.isStaff) return !!this.me.assigned_center_id;

      // Admin/municipal/response can create 
      return this.isAdminOrMunicipalOrResponse;
    },
    latestLog() {
      return (this.logs && this.logs.length) ? this.logs[0] : null;
    },
    currentEvacuees() {
      return this.latestLog ? (this.latestLog.total_current ?? 0) : 0;
    },
    lastUpdatedText() {
      if (!this.latestLog?.date_recorded) return "-";
      const d = new Date(this.latestLog.date_recorded);
      return isNaN(d.getTime()) ? this.latestLog.date_recorded : d.toLocaleString();
    },
    activeCenterLabel() {
      // For staff, show assigned center name
      if (this.isStaff) return this.me.assigned_center_name || "Unassigned";

      // For admin filter, show selected center name
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
    // console.log("ME:", res.data);
  },

  methods: {
    formatDate(dt) {
      if (!dt) return "-";
      const d = new Date(dt);
      return isNaN(d.getTime()) ? dt : d.toLocaleString();
    },

    async fetchMe() {
      // Use your existing profile endpoint because it includes assigned_center_name/id
      const res = await api.get("user/profile/");
      this.me = res.data;
    },

    async fetchCenters() {
      // IMPORTANT: evac module is under /api/evac_centers/
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

        // admin filter by center
        if (this.filters.center) params.append("center", this.filters.center);

        // staff: backend should already scope, but we can also pass center for clarity
        if (this.isStaff && this.me.assigned_center_id) {
          params.append("center", this.me.assigned_center_id);
        }

        const res = await api.get(`evac_centers/evacuation-logs/?${params.toString()}`);
        const data = res.data;

        // supports paginated or not
        this.logs = data.results || (Array.isArray(data) ? data : []);
        this.pagination.count = data.count || this.logs.length || 0;
        this.pagination.next = data.next || null;
        this.pagination.previous = data.previous || null;
        this.pagination.page = pageNum;
      } finally {
        this.loading = false;
      }
    },

    openCreate() {
      this.modalError = "";
      this.modal.open = true;
      this.modal.mode = "create";
      this.modal.id = null;

      this.modal.form = {
        center: this.isStaff ? (this.me.assigned_center_id || null) : null,
        families_in: 0,
        individuals_in: 0,
        families_out: 0,
        individuals_out: 0,
        children: 0,
        seniors: 0,
        pwd: 0,
        pregnant: 0,
        lactating: 0,
        vulnerable_individuals: 0,
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
        families_in: log.families_in ?? 0,
        individuals_in: log.individuals_in ?? 0,
        families_out: log.families_out ?? 0,
        individuals_out: log.individuals_out ?? 0,
        children: log.children ?? 0,
        seniors: log.seniors ?? 0,
        pwd: log.pwd ?? 0,
        pregnant: log.pregnant ?? 0,
        lactating: log.lactating ?? 0,
        vulnerable_individuals: log.vulnerable_individuals ?? 0,
        remarks: log.remarks || "",
      };
    },

    closeModal() {
      this.modal.open = false;
      this.modal.id = null;
      this.modalError = "";
    },

    async saveLog() {
      this.saving = true;
      this.modalError = "";
      try {
        // Staff must have assigned center
        if (this.isStaff) {
          if (!this.me.assigned_center_id) {
            this.modalError = "You have no assigned evacuation center.";
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
          families_in: this.modal.form.families_in ?? 0,
          individuals_in: this.modal.form.individuals_in ?? 0,
          families_out: this.modal.form.families_out ?? 0,
          individuals_out: this.modal.form.individuals_out ?? 0,

          children: this.modal.form.children ?? 0,
          seniors: this.modal.form.seniors ?? 0,
          pwd: this.modal.form.pwd ?? 0,
          pregnant: this.modal.form.pregnant ?? 0,
          lactating: this.modal.form.lactating ?? 0,

          remarks: this.modal.form.remarks || "",
        };

        if (this.modal.mode === "create") {
          await api.post("evac_centers/evacuation-logs/", payload);
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

.vgrid{
  display:grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 10px;
}
@media (max-width: 760px){
  .vgrid{ grid-template-columns: 1fr 1fr; }
}


.page { padding: 20px; }
.page-header { display:flex; align-items:flex-end; justify-content:space-between; gap: 12px; }
.actions { display:flex; gap: 10px; }
.card { margin-top: 14px; border: 1px solid #e5e7eb; border-radius: 14px; padding: 14px; }
.card.warn { border-color: #0b2ef555; }
.row { display:flex; gap: 24px; flex-wrap: wrap; }
.label { font-size: 12px; opacity: 0.7; }
.value { font-size: 22px; font-weight: 800; margin-top: 4px; }
.muted { opacity: 0.75; margin-top: 6px; }

.table-card { margin-top: 14px; border: 1px solid #e5e7eb; border-radius: 14px; overflow: hidden; }
.pad { padding: 12px; }
.table { width: 100%; border-collapse: collapse; }
.table th, .table td { padding: 12px; border-bottom: 1px solid #f1f5f9; text-align:left; }
.remarks { max-width: 460px; }
.empty { text-align:center; opacity:0.7; padding: 16px; }

.pager { display:flex; justify-content:flex-end; gap: 8px; padding: 12px; }

.btn { border: 1px solid #e5e7eb; border-radius: 10px; padding: 10px 12px; background: #111827; color: white; cursor:pointer; }
.btn:disabled { opacity: 0.6; cursor:not-allowed; }
.btn.ghost { background: white; color: #111827; }

.backdrop { position: fixed; inset: 0; background: rgba(0,0,0,.45); display:flex; align-items:center; justify-content:center; padding: 16px; z-index: 2000; }
.modal { background: white; width: min(720px, 100%); border-radius: 16px; padding: 16px; }
.grid { display:grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-top: 12px; }
label { display:flex; flex-direction:column; gap: 6px; font-size: 13px; }
input, textarea { border: 1px solid #e5e7eb; border-radius: 10px; padding: 10px; }
.wide { grid-column: 1 / -1; }
.error { margin-top: 10px; color: #b91c1c; font-size: 13px; }
.modal-actions { display:flex; justify-content:flex-end; gap: 10px; margin-top: 14px; }
.btn.danger { background: #b91c1c; border-color: #b91c1c; }
label {color: black;}
</style>
