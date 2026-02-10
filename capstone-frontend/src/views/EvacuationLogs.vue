<template>
  <div class="page">
    <div class="header">
      <div>
        <h1>Evacuation Logs</h1>
        <p>Record incoming/outgoing evacuees per center.</p>
      </div>

      <div class="actions">
        <select v-model="selectedCenter" @change="refreshAll">
          <option disabled value="">Select center</option>
          <option v-for="c in centers" :key="c.id" :value="c.id">
            {{ c.name }}
          </option>
        </select>

        <button :disabled="!selectedCenter" @click="openModal = true">
          + Add Log
        </button>
      </div>
    </div>

    <div class="cards" v-if="selectedCenter">
      <div class="card">
        <div class="label">Current Total (Individuals)</div>
        <div class="value">{{ latestTotal }}</div>
        <div class="sub">Last update: {{ latestDate || "—" }}</div>
      </div>
    </div>

    <div class="tableWrap" v-if="selectedCenter">
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
          <tr v-for="row in logs" :key="row.id">
            <td>{{ formatDT(row.date_recorded) }}</td>
            <td>{{ row.individuals_in }}</td>
            <td>{{ row.individuals_out }}</td>
            <td>{{ row.vulnerable_individuals }}</td>
            <td>{{ row.total_current }}</td>
            <td class="remarks">{{ row.remarks || "—" }}</td>
          </tr>
          <tr v-if="!loading && logs.length === 0">
            <td colspan="6" class="empty">No logs yet.</td>
          </tr>
        </tbody>
      </table>

      <div class="pagination">
        <button :disabled="!prevUrl" @click="go(prevUrl)">Prev</button>
        <button :disabled="!nextUrl" @click="go(nextUrl)">Next</button>
      </div>
    </div>

    <div v-if="openModal" class="modalBackdrop" @click.self="closeModal">
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

          <div class="modalActions">
            <button type="button" @click="closeModal">Cancel</button>
            <button type="submit" :disabled="submitting">
              {{ submitting ? "Saving..." : "Save Log" }}
            </button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<script>
import { evacLogsApi } from "@/services/evacLogsApi";
// You likely already have centers API; replace this with your own:
import axios from "@/services/axios";

export default {
  name: "EvacuationLogs",
  data() {
    return {
      centers: [],
      selectedCenter: "",

      logs: [],
      nextUrl: null,
      prevUrl: null,
      loading: false,

      latestTotal: 0,
      latestDate: null,

      openModal: false,
      submitting: false,
      error: "",
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
  async mounted() {
    await this.loadCenters();
  },
  methods: {
    async loadCenters() {
      // Replace endpoint with yours:
      const res = await axios.get("/evacuation-centers/");
      this.centers = res.data.results ?? res.data;
    },
    async refreshAll() {
      await Promise.all([this.fetchLogs(), this.fetchLatest()]);
    },
    async fetchLogs(url = null) {
      if (!this.selectedCenter) return;
      this.loading = true;
      try {
        const res = url
          ? await axios.get(url)
          : await evacLogsApi.list({ center: this.selectedCenter });

        const data = res.data;
        this.logs = data.results ?? data;
        this.nextUrl = data.next ?? null;
        this.prevUrl = data.previous ?? null;
      } finally {
        this.loading = false;
      }
    },
    async fetchLatest() {
      if (!this.selectedCenter) return;
      const res = await evacLogsApi.latestByCenter(this.selectedCenter);
      this.latestTotal = res.data.total_current ?? 0;
      this.latestDate = res.data.date_recorded ?? null;
    },
    go(url) {
      this.fetchLogs(url);
    },
    open() {
      this.openModal = true;
    },
    closeModal() {
      this.openModal = false;
      this.error = "";
      this.resetForm();
    },
    resetForm() {
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
      if (!this.selectedCenter) return;

      // quick client-side checks
      if (this.form.individuals_out > this.form.individuals_in + this.latestTotal) {
        this.error = "Individuals out is too high versus current total.";
        return;
      }

      this.submitting = true;
      try {
        await evacLogsApi.create({
          center: this.selectedCenter,
          ...this.form,
        });
        this.closeModal();
        await this.refreshAll();
      } catch (e) {
        this.error =
          e?.response?.data?.detail ||
          "Failed to save log. Check your inputs or permissions.";
      } finally {
        this.submitting = false;
      }
    },
    formatDT(dt) {
      if (!dt) return "—";
      return new Date(dt).toLocaleString();
    },
  },
};
</script>

<style scoped>
.page { padding: 20px; }
.header { display:flex; justify-content:space-between; gap:16px; align-items:flex-end; }
.actions { display:flex; gap:10px; align-items:center; }
.cards { margin: 16px 0; display:grid; grid-template-columns: 1fr; gap: 12px; }
.card { border:1px solid #e5e7eb; border-radius:14px; padding:14px; }
.label { font-size: 12px; opacity: .7; }
.value { font-size: 30px; font-weight: 800; margin-top: 4px; }
.sub { font-size: 12px; opacity: .7; margin-top: 4px; }
.tableWrap { border:1px solid #e5e7eb; border-radius:14px; overflow:hidden; }
.table { width:100%; border-collapse: collapse; }
.table th, .table td { padding: 12px; border-bottom: 1px solid #f1f5f9; }
.remarks { max-width: 420px; }
.empty { text-align:center; padding: 18px; opacity: .7; }
.pagination { display:flex; justify-content:flex-end; gap:8px; padding: 12px; }

.modalBackdrop { position:fixed; inset:0; background:rgba(0,0,0,.45); display:flex; align-items:center; justify-content:center; padding: 16px; }
.modal { background:white; width:min(720px, 100%); border-radius:16px; padding:16px; }
.grid { display:grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-top: 12px; }
label { display:flex; flex-direction:column; gap:6px; font-size: 13px; }
input, textarea, select { border:1px solid #e5e7eb; border-radius:10px; padding:10px; }
.wide { grid-column: 1 / -1; }
.error { margin-top: 10px; color:#b91c1c; font-size: 13px; }
.modalActions { display:flex; justify-content:flex-end; gap:10px; margin-top: 14px; }
button { border:1px solid #e5e7eb; border-radius:10px; padding:10px 12px; background:white; cursor:pointer; }
button:disabled { opacity:.6; cursor:not-allowed; }
</style>
