<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h1>Evacuation Logs</h1>
        <p>Record incoming/outgoing evacuees for your assigned center.</p>
      </div>

      <div class="actions">
        <button class="btn" @click="openModal = true" :disabled="!centerId">
          + Add Log
        </button>
      </div>
    </div>

    <!-- Center info -->
    <div class="card" v-if="centerName">
      <div class="row">
        <div>
          <div class="label">Center</div>
          <div class="value">{{ centerName }}</div>
        </div>
        <div>
          <div class="label">Current Total (Individuals)</div>
          <div class="value">{{ currentTotal }}</div>
        </div>
      </div>
    </div>

    <div v-if="!centerId" class="card warn">
      <b>No assigned center found.</b>
      <div class="muted">
        Ask admin to assign your evacuation center (CustomUser.assigned_center).
      </div>
    </div>

    <!-- Table -->
    <div class="table-card" v-if="centerId">
      <div v-if="loading" class="pad">Loading...</div>

      <div v-else>
        <table class="table">
          <thead>
            <tr>
              <th>Date</th>
              <th>In (Ind)</th>
              <th>Out (Ind)</th>
              <th>Vulnerable</th>
              <th>Total Current</th>
              <th>Remarks</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="log in logs" :key="log.id">
              <td>{{ formatDT(log.date_recorded) }}</td>
              <td>{{ log.individuals_in }}</td>
              <td>{{ log.individuals_out }}</td>
              <td>{{ log.vulnerable_individuals }}</td>
              <td><b>{{ log.total_current }}</b></td>
              <td class="remarks">{{ log.remarks || "-" }}</td>
            </tr>

            <tr v-if="!loading && logs.length === 0">
              <td colspan="6" class="empty">No logs yet.</td>
            </tr>
          </tbody>
        </table>

        <div class="pager">
          <button class="btn ghost" :disabled="!prevUrl" @click="fetchLogsByUrl(prevUrl)">Prev</button>
          <button class="btn ghost" :disabled="!nextUrl" @click="fetchLogsByUrl(nextUrl)">Next</button>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <div v-if="openModal" class="backdrop" @click.self="closeModal">
      <div class="modal">
        <h3>Add Log</h3>

        <form @submit.prevent="submit">
          <div class="grid">
            <label>
              Individuals In
              <input type="number" min="0" v-model.number="form.individuals_in" />
            </label>

            <label>
              Individuals Out
              <input type="number" min="0" v-model.number="form.individuals_out" />
            </label>

            <label>
              Families In
              <input type="number" min="0" v-model.number="form.families_in" />
            </label>

            <label>
              Families Out
              <input type="number" min="0" v-model.number="form.families_out" />
            </label>

            <label>
              Vulnerable Individuals
              <input type="number" min="0" v-model.number="form.vulnerable_individuals" />
            </label>

            <label class="wide">
              Remarks
              <textarea rows="3" v-model="form.remarks"></textarea>
            </label>
          </div>

          <div class="error" v-if="error">{{ error }}</div>

          <div class="modal-actions">
            <button type="button" class="btn ghost" @click="closeModal">Cancel</button>
            <button type="submit" class="btn" :disabled="submitting">
              {{ submitting ? "Saving..." : "Save" }}
            </button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<script>
import api from "@/services/api"; // your axios instance with baseURL + auth header
import { getUserProfile } from "@/services/authService";

export default {
  name: "StaffLogs",
  data() {
    return {
      loading: false,
      submitting: false,
      openModal: false,
      error: "",

      centerId: null,
      centerName: "",
      logs: [],

      nextUrl: null,
      prevUrl: null,

      form: {
        families_in: 0,
        individuals_in: 0,
        families_out: 0,
        individuals_out: 0,
        vulnerable_individuals: 0,
        remarks: "",
      },
    };
  },

  computed: {
    currentTotal() {
      // newest log is first (ordering -date_recorded), so total_current is at logs[0]
      return this.logs.length ? (this.logs[0].total_current ?? 0) : 0;
    },
  },

  async mounted() {
    await this.loadCenterFromProfile();
    if (this.centerId) {
      await this.fetchLogs();
    }
  },

  methods: {
    async loadCenterFromProfile() {
      // Expect profile to include assigned_center_id + assigned_center_name (recommended)
      const profile = await getUserProfile();
      this.centerId = profile.assigned_center_id ?? null;
      this.centerName = profile.assigned_center_name ?? "";
    },

    async fetchLogs() {
      this.loading = true;
      try {
        const res = await api.get("evacuation-logs/", { params: { center: this.centerId } });
        const data = res.data;
        this.logs = (data.results || []).filter(l => l && l.id != null);
        this.nextUrl = data.next;
        this.prevUrl = data.previous;

        // If backend includes center_name in logs, we can derive it
        if (!this.centerName && this.logs.length && this.logs[0].center_name) {
          this.centerName = this.logs[0].center_name;
        }
      } finally {
        this.loading = false;
      }
    },

    async fetchLogsByUrl(url) {
      this.loading = true;
      try {
        const res = await api.get(url);
        const data = res.data;
        this.logs = (data.results || []).filter(l => l && l.id != null);
        this.nextUrl = data.next;
        this.prevUrl = data.previous;
      } finally {
        this.loading = false;
      }
    },

    closeModal() {
      this.openModal = false;
      this.error = "";
      this.form = {
        families_in: 0,
        individuals_in: 0,
        families_out: 0,
        individuals_out: 0,
        vulnerable_individuals: 0,
        remarks: "",
      };
    },

    async submit() {
      this.error = "";
      if (!this.centerId) return;

      // basic client guard
      if (this.form.individuals_out > (this.currentTotal + this.form.individuals_in)) {
        this.error = "Individuals out is too high compared to current total.";
        return;
      }

      this.submitting = true;
      try {
        await api.post("evacuation-logs/", {
          center: this.centerId,
          ...this.form,
        });
        this.closeModal();
        await this.fetchLogs();
      } catch (e) {
        const msg =
          e?.response?.data?.detail ||
          (typeof e?.response?.data === "string" ? e.response.data : null) ||
          "Failed to save log.";
        this.error = msg;
      } finally {
        this.submitting = false;
      }
    },

    formatDT(dt) {
      if (!dt) return "-";
      return new Date(dt).toLocaleString();
    },
  },
};
</script>

<style scoped>
.page { padding: 20px; }
.page-header { display:flex; align-items:flex-end; justify-content:space-between; gap: 12px; }
.actions { display:flex; gap: 10px; }
.card { margin-top: 14px; border: 1px solid #e5e7eb; border-radius: 14px; padding: 14px; }
.card.warn { border-color: #f59e0b55; background: #fff7ed; }
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
</style>
