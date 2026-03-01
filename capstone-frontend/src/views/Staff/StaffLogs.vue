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
          <div class="muted">Computed from all logs</div>        </div>

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
    <button class="btn" type="submit" :disabled="saving">
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
          remarks: "",
          children_count: 0,
          senior_count: 0,
          pwd_count: 0,
          pregnant_count: 0,
          lactating_count: 0
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
      // Staff can create only if assigned
      if (this.isStaff) return !!this.me.assigned_center_id;

      // Admin/municipal/response can create 
      return this.isAdminOrMunicipalOrResponse;
    },
    latestLog() {
      if (!this.logs?.length) return null;

      // pick newest by date_recorded, fallback to id if dates are equal/missing
      return this.logs.reduce((latest, cur) => {
        const a = new Date(latest?.date_recorded || 0).getTime();
        const b = new Date(cur?.date_recorded || 0).getTime();

        if (b > a) return cur;
        if (b === a) return (cur.id ?? 0) > (latest.id ?? 0) ? cur : latest;
        return latest;
      }, this.logs[0]);
    },
    currentEvacuees() {
      return this.summary?.total_current ?? 0;
    },
    lastUpdatedText() {
      if (!this.latestLog?.date_recorded) return "-";
      const d = new Date(this.latestLog.date_recorded);
      return isNaN(d.getTime()) ? this.latestLog.date_recorded : d.toLocaleString();
    },
    vulnerableTotal() {
      const f = this.modal.form || {};
      return (
        (f.children_count || 0) +
        (f.senior_count || 0) +
        (f.pwd_count || 0) +
        (f.pregnant_count || 0) +
        (f.lactating_count || 0)
      );
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

// prevent stale filter affecting staff
if (this.me.role === "EVAC_CENTER_STAFF") {
  this.filters.center = null;
}
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

      // ✅ Only ONE center param allowed
      if (this.isStaff && this.me.assigned_center_id) {
        params.append("center", this.me.assigned_center_id);
      } else if (this.filters.center) {
        params.append("center", this.filters.center);
      }

        const res = await api.get(`evac_centers/evacuation-logs/?${params.toString()}`);
        const data = res.data;

        // supports paginated or not
        this.logs = data.results || (Array.isArray(data) ? data : []);
        this.pagination.count = data.count || this.logs.length || 0;
        this.pagination.next = data.next || null;
        this.pagination.previous = data.previous || null;
        this.pagination.page = pageNum;
        await this.fetchSummary();  // ✅ ADD THIS
      } finally {
        this.loading = false;
      }
    },

    async fetchSummary() {
  try {
    let url = "evac_centers/evacuation-logs/staff_summary/";

    // If not staff, pass center filter
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
      families_in: 0,
      individuals_in: 0,
      families_out: 0,
      individuals_out: 0,
      children_count: 0,
      senior_count: 0,
      pwd_count: 0,
      pregnant_count: 0,
      lactating_count: 0,
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
      children_count: log.children_count ?? 0,
      senior_count: log.senior_count ?? 0,
      pwd_count: log.pwd_count ?? 0,
      pregnant_count: log.pregnant_count ?? 0,
      lactating_count: log.lactating_count ?? 0,
      remarks: log.remarks || "",
    };
  },

    closeModal() {
      this.modal.open = false;
      this.modal.id = null;
      this.modalError = "";
    },

    async saveLog() {
      alert("saveLog triggered");

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
        // Staff must have assigned center
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
      families_in: this.modal.form.families_in ?? 0,
      individuals_in: this.modal.form.individuals_in ?? 0,
      families_out: this.modal.form.families_out ?? 0,
      individuals_out: this.modal.form.individuals_out ?? 0,

      children_count: this.modal.form.children_count ?? 0,
      senior_count: this.modal.form.senior_count ?? 0,
      pwd_count: this.modal.form.pwd_count ?? 0,
      pregnant_count: this.modal.form.pregnant_count ?? 0,
      lactating_count: this.modal.form.lactating_count ?? 0,

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
        }else {
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


.page{
  --bg:#060912;
  --panel:rgba(10,14,28,.65);
  --panel2:rgba(8,12,24,.82);
  --border:rgba(56,189,248,.16);
  --border2:rgba(255,255,255,.08);
  --text:#e5e7eb;
  --muted:rgba(229,231,235,.62);
  --blue:#38bdf8;
  --blue2:#2563eb;
  --green:#22c55e;
  --red:#ef4444;

  padding: 20px;
  color: var(--text);
}

.page-header{
  display:flex;
  align-items:flex-end;
  justify-content:space-between;
  gap:12px;
  margin-bottom: 12px;
}
.page-header h1{ margin:0; font-size:1.6rem; color:#f8fafc; }
.page-header p{ margin:6px 0 0; color:var(--muted); font-size:13px; }

.actions{ display:flex; align-items:center; gap:10px; flex-wrap:wrap; }

/* cards */
.card{
  margin-top: 14px;
  border-radius:16px;
  padding:14px;
  border:1px solid var(--border2);
  background: linear-gradient(180deg, rgba(10,14,28,.72), rgba(8,12,24,.78));
  box-shadow: 0 16px 34px rgba(0,0,0,.42);
  backdrop-filter: blur(10px);
}
.card.warn{
  border-color: rgba(245,158,11,.35);
  background: linear-gradient(180deg, rgba(245,158,11,.10), rgba(8,12,24,.78));
}

.row{ display:flex; gap:24px; flex-wrap:wrap; align-items:center; }
.label{ font-size:12px; color:var(--muted); font-weight:800; letter-spacing:.2px; }
.value{ font-size:26px; font-weight:1000; margin-top:4px; color:#dbeafe; }
.muted{ color:var(--muted); margin-top:6px; }

/* table */
.table-card{
  margin-top: 14px;
  border-radius:18px;
  overflow:hidden;
  border:1px solid var(--border2);
  background: var(--panel2);
  box-shadow: 0 20px 48px rgba(0,0,0,.48);
}
.pad{ padding: 12px 14px; }
.table{ width:100%; border-collapse:collapse; }
.table th, .table td{
  padding: 12px 14px;
  border-bottom:1px solid rgba(255,255,255,.06);
  text-align:left;
}
.table th{
  background: rgba(5,8,18,.85);
  color: rgba(56,189,248,.95);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing:.7px;
  font-weight: 1000;
}
.table td{ color: rgba(229,231,235,.88); font-size:13.5px; }
.remarks{ max-width: 460px; }
.empty{ text-align:center; color:var(--muted); padding: 16px; }

/* buttons */
.btn{
  border-radius:14px;
  padding: 10px 14px;
  font-size: 13px;
  font-weight: 1000;
  border:1px solid rgba(56,189,248,.22);
  cursor:pointer;
  background: rgba(56,189,248,.10);
  color:#cdefff;
  transition: transform .12s ease, background .12s ease, border-color .12s ease;
}
.btn:hover:not(:disabled){ transform: translateY(-1px); background: rgba(56,189,248,.16); }
.btn:disabled{ opacity:.55; cursor:not-allowed; }

.btn.ghost{
  background: rgba(2,6,23,.45);
  color: var(--text);
  border-color: rgba(255,255,255,.10);
}
.btn.ghost:hover:not(:disabled){ background: rgba(56,189,248,.10); }

.pager{ display:flex; justify-content:flex-end; gap: 8px; padding: 12px; }

/* modal */
.backdrop{
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,.60);
  display:flex;
  align-items:center;
  justify-content:center;
  padding: 16px;
  z-index: 2000;
}
.modal{
  width: min(760px, 100%);
  border-radius: 18px;
  border: 1px solid rgba(56,189,248,.16);
  background:
    radial-gradient(1200px 520px at 20% -20%, rgba(56,189,248,.22), transparent 55%),
    linear-gradient(180deg, rgba(10,14,28,.92), rgba(6,9,18,.92));
  box-shadow: 0 30px 80px rgba(0,0,0,.62);
  padding: 16px;
  color: var(--text);
}
.grid{
  display:grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-top: 12px;
}
label{ display:flex; flex-direction:column; gap: 6px; font-size: 13px; color: rgba(229,231,235,.72); font-weight:800; }
input, textarea, select{
  border:1px solid rgba(56,189,248,.18);
  background: rgba(2,6,23,.55);
  color: var(--text);
  border-radius: 14px;
  padding: 10px 12px;
  font-size: 13px;
  outline:none;
}
input:focus, textarea:focus, select:focus{
  border-color: rgba(56,189,248,.45);
  box-shadow:0 0 0 4px rgba(56,189,248,.12);
}
.wide{ grid-column: 1 / -1; }

.vgrid{
  display:grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 10px;
}
@media (max-width: 760px){
  .grid{ grid-template-columns: 1fr; }
  .vgrid{ grid-template-columns: 1fr 1fr; }
}

.error{ margin-top: 10px; color: #fecaca; font-size: 13px; }
.modal-actions{ display:flex; justify-content:flex-end; gap: 10px; margin-top: 14px; }</style>
