<template>
  <div class="donation-page">
    <header class="page-header">
      <div>
        <p class="eyebrow">Donation Drive</p>
        <h1>{{ isStaff ? "Staff Donation Drive" : "Donation Drive Monitoring" }}</h1>
        <p class="subtext">
          Manage donation needs, received donations, and distribution logs.
        </p>
      </div>
    </header>

    <section class="center-card">
      <div v-if="isStaff" class="assigned-center-box">
        <span>Assigned Evacuation Center</span>
        <strong>{{ assignedCenterName }}</strong>
      </div>

      <div v-else class="admin-center-filter">
        <label>
          Filter by Evacuation Center
          <select v-model="selectedCenter" @change="refreshAll">
            <option value="">All Centers</option>
            <option v-for="center in centers" :key="center.id" :value="center.id">
              {{ center.name }}
            </option>
          </select>
        </label>
      </div>
    </section>

    <section class="summary-grid">
      <div class="summary-card">
        <span>Open Needs</span>
        <strong>{{ summary.openNeeds }}</strong>
      </div>

      <div class="summary-card">
        <span>Urgent Needs</span>
        <strong>{{ summary.urgentNeeds }}</strong>
      </div>

      <div class="summary-card">
        <span>Received Donations</span>
        <strong>{{ donations.length }}</strong>
      </div>

      <div class="summary-card">
        <span>Distribution Logs</span>
        <strong>{{ distributions.length }}</strong>
      </div>
    </section>

    <section class="tabs">
      <button :class="{ active: activeTab === 'needs' }" @click="activeTab = 'needs'">
        Donation Needs
      </button>

      <button :class="{ active: activeTab === 'donations' }" @click="activeTab = 'donations'">
        Received Donations
      </button>

      <button :class="{ active: activeTab === 'distributions' }" @click="activeTab = 'distributions'">
        Distribution Logs
      </button>
    </section>

    <p v-if="error" class="error-text">{{ error }}</p>

    <!-- NEEDS TAB -->
    <section v-if="activeTab === 'needs'" class="content-grid">
      <form class="form-card" @submit.prevent="saveNeed">
        <h2>Add Donation Need</h2>

        <label>
          Item Name
          <input v-model="needForm.item_name" required placeholder="Example: Bottled Water" />
        </label>

        <label>
          Category
          <select v-model="needForm.category" required>
            <option value="FOOD">Food</option>
            <option value="WATER">Water</option>
            <option value="CLOTHING">Clothing</option>
            <option value="MEDICAL">Medical</option>
            <option value="HYGIENE">Hygiene</option>
            <option value="BEDDING">Bedding</option>
            <option value="BABY_SUPPLIES">Baby Supplies</option>
            <option value="OTHER">Other</option>
          </select>
        </label>

        <div class="two-col">
          <label>
            Quantity Needed
            <input v-model.number="needForm.quantity_needed" type="number" min="1" required />
          </label>

          <label>
            Unit
            <input v-model="needForm.unit" required placeholder="pcs, packs, bottles" />
          </label>
        </div>

        <label>
          Priority
          <select v-model="needForm.priority" required>
            <option value="LOW">Low</option>
            <option value="MEDIUM">Medium</option>
            <option value="HIGH">High</option>
            <option value="URGENT">Urgent</option>
          </select>
        </label>

        <label>
          Remarks
          <textarea v-model="needForm.remarks" rows="3" placeholder="Optional notes"></textarea>
        </label>

        <button class="primary-btn" :disabled="saving">
          {{ saving ? "Saving..." : "Add Need" }}
        </button>
      </form>

      <div class="table-card">
        <div class="table-header">
          <h2>Donation Needs</h2>
          <button class="ghost-btn" @click="fetchNeeds">Refresh</button>
        </div>

        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Item</th>
                <th>Center</th>
                <th>Needed</th>
                <th>Received</th>
                <th>Remaining</th>
                <th>Priority</th>
                <th>Status</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="need in needs" :key="need.id">
                <td>
                  <strong>{{ need.item_name }}</strong>
                  <span>{{ formatCategory(need.category) }}</span>
                </td>
                <td>{{ need.center_name }}</td>
                <td>{{ need.quantity_needed }} {{ need.unit }}</td>
                <td>{{ need.quantity_received }} {{ need.unit }}</td>
                <td>{{ need.remaining_quantity }} {{ need.unit }}</td>
                <td>
                  <span class="pill" :class="need.priority.toLowerCase()">
                    {{ formatText(need.priority) }}
                  </span>
                </td>
                <td>
                  <span class="pill neutral">
                    {{ formatText(need.status) }}
                  </span>
                </td>
              </tr>

              <tr v-if="needs.length === 0">
                <td colspan="7" class="empty-text">No donation needs found.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- DONATIONS TAB -->
    <section v-if="activeTab === 'donations'" class="content-grid">
      <form class="form-card" @submit.prevent="saveDonation">
        <h2>Record Donation</h2>

        <label>
          Related Need
          <select v-model="donationForm.need" @change="fillDonationFromNeed">
            <option value="">No specific need</option>
            <option v-for="need in needs" :key="need.id" :value="need.id">
              {{ need.item_name }} — {{ need.remaining_quantity }} {{ need.unit }} remaining
            </option>
          </select>
        </label>

        <label>
          Donor Name
          <input v-model="donationForm.donor_name" required placeholder="Donor name" />
        </label>

        <label>
          Donor Contact
          <input v-model="donationForm.donor_contact" placeholder="Contact number" />
        </label>

        <label>
          Donor Address
          <textarea v-model="donationForm.donor_address" rows="2"></textarea>
        </label>

        <label>
          Item Name
          <input v-model="donationForm.item_name" required />
        </label>

        <label>
          Category
          <select v-model="donationForm.category" required>
            <option value="FOOD">Food</option>
            <option value="WATER">Water</option>
            <option value="CLOTHING">Clothing</option>
            <option value="MEDICAL">Medical</option>
            <option value="HYGIENE">Hygiene</option>
            <option value="BEDDING">Bedding</option>
            <option value="BABY_SUPPLIES">Baby Supplies</option>
            <option value="OTHER">Other</option>
          </select>
        </label>

        <div class="two-col">
          <label>
            Quantity
            <input v-model.number="donationForm.quantity" type="number" min="1" required />
          </label>

          <label>
            Unit
            <input v-model="donationForm.unit" required />
          </label>
        </div>

        <label>
          Status
          <select v-model="donationForm.status">
            <option value="RECEIVED">Received</option>
            <option value="PLEDGED">Pledged</option>
          </select>
        </label>

        <label>
          Remarks
          <textarea v-model="donationForm.remarks" rows="3"></textarea>
        </label>

        <button class="primary-btn" :disabled="saving">
          {{ saving ? "Saving..." : "Record Donation" }}
        </button>
      </form>

      <div class="table-card">
        <div class="table-header">
          <h2>Received / Pledged Donations</h2>
          <button class="ghost-btn" @click="fetchDonations">Refresh</button>
        </div>

        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Donor</th>
                <th>Item</th>
                <th>Center</th>
                <th>Quantity</th>
                <th>Status</th>
                <th>Date</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="donation in donations" :key="donation.id">
                <td>
                  <strong>{{ donation.donor_name }}</strong>
                  <span>{{ donation.donor_contact || "No contact" }}</span>
                </td>
                <td>{{ donation.item_name }}</td>
                <td>{{ donation.center_name }}</td>
                <td>{{ donation.quantity }} {{ donation.unit }}</td>
                <td>
                  <span class="pill neutral">{{ formatText(donation.status) }}</span>
                </td>
                <td>{{ formatDate(donation.created_at) }}</td>
              </tr>

              <tr v-if="donations.length === 0">
                <td colspan="6" class="empty-text">No donations found.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- DISTRIBUTIONS TAB -->
    <section v-if="activeTab === 'distributions'" class="content-grid">
      <form class="form-card" @submit.prevent="saveDistribution">
        <h2>Log Distribution</h2>

        <label>
          Donation Source
          <select v-model="distributionForm.donation" required @change="fillDistributionFromDonation">
            <option value="" disabled>Select donation</option>
            <option v-for="donation in receivedDonations" :key="donation.id" :value="donation.id">
              {{ donation.item_name }} — {{ donation.quantity }} {{ donation.unit }}
            </option>
          </select>
        </label>

        <label>
          Item Name
          <input v-model="distributionForm.item_name" required />
        </label>

        <div class="two-col">
          <label>
            Quantity Distributed
            <input
              v-model.number="distributionForm.quantity_distributed"
              type="number"
              min="1"
              required
            />
          </label>

          <label>
            Unit
            <input v-model="distributionForm.unit" required />
          </label>
        </div>

        <label>
          Distributed To
          <input
            v-model="distributionForm.distributed_to"
            placeholder="Family head, evacuee, group, or general distribution"
          />
        </label>

        <label>
          Remarks
          <textarea v-model="distributionForm.remarks" rows="3"></textarea>
        </label>

        <button class="primary-btn" :disabled="saving">
          {{ saving ? "Saving..." : "Log Distribution" }}
        </button>
      </form>

      <div class="table-card">
        <div class="table-header">
          <h2>Distribution History</h2>
          <button class="ghost-btn" @click="fetchDistributions">Refresh</button>
        </div>

        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Item</th>
                <th>Center</th>
                <th>Quantity</th>
                <th>Distributed To</th>
                <th>Distributed By</th>
                <th>Date</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="dist in distributions" :key="dist.id">
                <td>{{ dist.item_name }}</td>
                <td>{{ dist.center_name }}</td>
                <td>{{ dist.quantity_distributed }} {{ dist.unit }}</td>
                <td>{{ dist.distributed_to || "General distribution" }}</td>
                <td>{{ dist.distributed_by_name || "-" }}</td>
                <td>{{ formatDate(dist.distributed_at) }}</td>
              </tr>

              <tr v-if="distributions.length === 0">
                <td colspan="6" class="empty-text">No distribution logs found.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import api from "@/services/api";

export default {
  name: "DonationDrivePanel",

  props: {
    mode: {
      type: String,
      default: "staff",
    },
  },

  data() {
    return {
      activeTab: "needs",
      centers: [],
      assignedCenter: null,
      selectedCenter: "",

      needs: [],
      donations: [],
      distributions: [],

      saving: false,
      error: "",

      needForm: this.emptyNeedForm(),
      donationForm: this.emptyDonationForm(),
      distributionForm: this.emptyDistributionForm(),

    };
  },

  computed: {
    isStaff() {
      return this.mode === "staff";
    },

    assignedCenterName() {
      return this.assignedCenter?.name || "No assigned center found";
    },

    activeCenterId() {
      if (this.isStaff) {
        return this.assignedCenter?.id || "";
      }

      return this.selectedCenter || "";
    },

    receivedDonations() {
      return this.donations.filter((item) => item.status === "RECEIVED");
    },

    summary() {
      return {
        openNeeds: this.needs.filter((item) =>
          ["OPEN", "PARTIALLY_FULFILLED"].includes(item.status)
        ).length,
        urgentNeeds: this.needs.filter((item) => item.priority === "URGENT").length,
      };
    },
  },

  async mounted() {
    await this.fetchCenters();
    await this.refreshAll();
  },

  methods: {
    emptyNeedForm() {
      return {
        item_name: "",
        category: "FOOD",
        quantity_needed: 1,
        unit: "pcs",
        priority: "MEDIUM",
        remarks: "",
      };
    },

    emptyDonationForm() {
      return {
        need: "",
        donor_name: "",
        donor_contact: "",
        donor_address: "",
        item_name: "",
        category: "FOOD",
        quantity: 1,
        unit: "pcs",
        status: "RECEIVED",
        remarks: "",
      };
    },

    emptyDistributionForm() {
      return {
        donation: "",
        item_name: "",
        quantity_distributed: 1,
        unit: "pcs",
        distributed_to: "",
        remarks: "",
      };
    },

    async fetchCenters() {
      try {
        const res = await api.get("/evac_centers/evac-center-dropdown/");

        this.centers = Array.isArray(res.data)
          ? res.data
          : res.data.results || [];

        if (this.isStaff) {
          this.assignedCenter = this.centers.length > 0 ? this.centers[0] : null;
        }
      } catch (err) {
        console.error(err);
        this.error = "Failed to load evacuation centers.";
      }
    },

    async refreshAll() {
      await Promise.all([
        this.fetchNeeds(),
        this.fetchDonations(),
        this.fetchDistributions(),
      ]);
    },

    buildParams() {
      const params = {};

      if (this.activeCenterId) {
        params.center = this.activeCenterId;
      }

      return params;
    },

    requireCenter() {
      if (!this.activeCenterId) {
        this.error = "No evacuation center selected or assigned.";
        return false;
      }

      return true;
    },

    async fetchNeeds() {
      try {
        const res = await api.get("evac_centers/donation-needs/", {
          params: this.buildParams(),
        });

        this.needs = Array.isArray(res.data) ? res.data : res.data.results || [];
      } catch (err) {
        console.error(err);
        this.error = "Failed to load donation needs.";
      }
    },

    async fetchDonations() {
      try {
        const res = await api.get("evac_centers/donations/", {
          params: this.buildParams(),
        });

        this.donations = Array.isArray(res.data) ? res.data : res.data.results || [];
      } catch (err) {
        console.error(err);
        this.error = "Failed to load donations.";
      }
    },

    async fetchDistributions() {
      try {
        const res = await api.get("evac_centers/donation-distributions/", {
          params: this.buildParams(),
        });

        this.distributions = Array.isArray(res.data) ? res.data : res.data.results || [];
      } catch (err) {
        console.error(err);
        this.error = "Failed to load distribution logs.";
      }
    },

    async saveNeed() {
      if (!this.requireCenter()) return;

      this.saving = true;
      this.error = "";

      try {
        const payload = {
          ...this.needForm,
          center: this.activeCenterId,
          quantity_needed: Number(this.needForm.quantity_needed || 0),
        };

        await api.post("evac_centers/donation-needs/", payload);

        this.needForm = this.emptyNeedForm();
        await this.fetchNeeds();
      } catch (err) {
        console.error(err);
        this.error = this.extractError(err, "Failed to save donation need.");
      } finally {
        this.saving = false;
      }
    },

    fillDonationFromNeed() {
      const need = this.needs.find((item) => item.id === Number(this.donationForm.need));

      if (!need) return;

      this.donationForm.item_name = need.item_name;
      this.donationForm.category = need.category;
      this.donationForm.unit = need.unit;
    },

    async saveDonation() {
      if (!this.requireCenter()) return;

      this.saving = true;
      this.error = "";

      try {
        const payload = {
          ...this.donationForm,
          center: this.activeCenterId,
          need: this.donationForm.need || null,
          quantity: Number(this.donationForm.quantity || 0),
        };

        await api.post("evac_centers/donations/", payload);

        this.donationForm = this.emptyDonationForm();
        await Promise.all([this.fetchDonations(), this.fetchNeeds()]);
      } catch (err) {
        console.error(err);
        this.error = this.extractError(err, "Failed to save donation.");
      } finally {
        this.saving = false;
      }
    },

    fillDistributionFromDonation() {
      const donation = this.donations.find(
        (item) => item.id === Number(this.distributionForm.donation)
      );

      if (!donation) return;

      this.distributionForm.item_name = donation.item_name;
      this.distributionForm.unit = donation.unit;
    },

    async saveDistribution() {
      if (!this.requireCenter()) return;

      this.saving = true;
      this.error = "";

      try {
        const payload = {
          ...this.distributionForm,
          center: this.activeCenterId,
          quantity_distributed: Number(this.distributionForm.quantity_distributed || 0),
        };

        await api.post("evac_centers/donation-distributions/", payload);

        this.distributionForm = this.emptyDistributionForm();
        await this.fetchDistributions();
      } catch (err) {
        console.error(err);
        this.error = this.extractError(err, "Failed to save distribution log.");
      } finally {
        this.saving = false;
      }
    },

    extractError(err, fallback) {
      if (err.response?.data) {
        return typeof err.response.data === "string"
          ? err.response.data
          : JSON.stringify(err.response.data);
      }

      return fallback;
    },

    formatDate(value) {
      if (!value) return "-";

      return new Date(value).toLocaleDateString("en-PH", {
        year: "numeric",
        month: "short",
        day: "2-digit",
      });
    },

    formatText(value) {
      if (!value) return "-";

      return String(value)
        .replaceAll("_", " ")
        .toLowerCase()
        .replace(/\b\w/g, (char) => char.toUpperCase());
    },

    formatCategory(value) {
      return this.formatText(value);
    },
  },
};
</script>

<style scoped>
.donation-page {
  padding: 24px;
  color: #111827;
}

.page-header {
  margin-bottom: 18px;
}

.eyebrow {
  margin: 0 0 4px;
  color: #2563eb;
  font-size: 0.76rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

h1,
h2 {
  margin: 0;
}

.subtext {
  margin: 6px 0 0;
  color: #6b7280;
}

.center-card,
.form-card,
.table-card,
.summary-card {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  box-shadow: 0 10px 25px rgba(15, 23, 42, 0.06);
}

.center-card {
  padding: 16px;
  margin-bottom: 16px;
}

.assigned-center-box span {
  display: block;
  color: #2563eb;
  font-size: 0.78rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.assigned-center-box strong {
  display: block;
  margin-top: 4px;
  color: #1e3a8a;
}

.admin-center-filter label,
.form-card label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 0.85rem;
  font-weight: 700;
}

input,
select,
textarea {
  width: 100%;
  border: 1px solid #d1d5db;
  border-radius: 10px;
  padding: 10px 12px;
  font: inherit;
  background: #ffffff;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
  margin-bottom: 16px;
}

.summary-card {
  padding: 16px;
}

.summary-card span {
  color: #6b7280;
  font-size: 0.82rem;
  font-weight: 700;
}

.summary-card strong {
  display: block;
  margin-top: 6px;
  font-size: 1.8rem;
}

.tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.tabs button {
  border: 0;
  border-radius: 999px;
  padding: 10px 16px;
  background: #f3f4f6;
  color: #374151;
  font-weight: 800;
  cursor: pointer;
}

.tabs button.active {
  background: #2563eb;
  color: #ffffff;
}

.content-grid {
  display: grid;
  grid-template-columns: 360px 1fr;
  gap: 16px;
  align-items: start;
}

.form-card {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 13px;
}

.two-col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.primary-btn,
.ghost-btn {
  border: 0;
  border-radius: 10px;
  padding: 10px 14px;
  font-weight: 800;
  cursor: pointer;
}

.primary-btn {
  background: #2563eb;
  color: #ffffff;
}

.primary-btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.ghost-btn {
  background: #f3f4f6;
  color: #111827;
}

.table-card {
  padding: 16px;
  min-width: 0;
}

.table-header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.table-wrap {
  overflow-x: auto;
}

table {
  width: 100%;
  min-width: 900px;
  border-collapse: collapse;
}

th,
td {
  padding: 11px 10px;
  border-bottom: 1px solid #e5e7eb;
  text-align: left;
  vertical-align: top;
}

th {
  color: #6b7280;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

td span {
  display: block;
  margin-top: 3px;
  color: #6b7280;
  font-size: 0.78rem;
}

.pill {
  display: inline-flex;
  padding: 5px 9px;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 800;
}

.pill.urgent {
  background: #fee2e2;
  color: #991b1b;
}

.pill.high {
  background: #ffedd5;
  color: #9a3412;
}

.pill.medium {
  background: #fef9c3;
  color: #854d0e;
}

.pill.low {
  background: #dcfce7;
  color: #166534;
}

.pill.neutral {
  background: #e5e7eb;
  color: #374151;
}

.error-text {
  padding: 12px 14px;
  margin-bottom: 14px;
  border-radius: 12px;
  background: #fee2e2;
  color: #991b1b;
  font-weight: 700;
}

.empty-text {
  text-align: center;
  color: #6b7280;
  padding: 24px;
}

@media (max-width: 1100px) {
  .content-grid {
    grid-template-columns: 1fr;
  }

  .summary-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 700px) {
  .donation-page {
    padding: 16px;
  }

  .summary-grid {
    grid-template-columns: 1fr;
  }

  .two-col {
    grid-template-columns: 1fr;
  }
}
</style>