<template>
  <div class="evacuees-page">
    <header class="page-header">
      <div>
        <p class="eyebrow">Evacuee Management</p>
        <h1>Evacuee Records</h1>
        <p class="subtext">
          Register and manage basic information of evacuees assigned to your evacuation center.
        </p>
      </div>

      <button class="primary-btn" @click="openCreateModal">
        + Add Evacuee
      </button>
    </header>

    <section class="filters-card">
      <div class="search-box">
        <label>Search</label>
        <input
          v-model="filters.search"
          type="text"
          placeholder="Search name, family head, contact, address..."
          @input="fetchEvacuees"
        />
      </div>

      <div class="filter-box">
        <label>Status</label>
        <select v-model="filters.is_active" @change="fetchEvacuees">
          <option value="">All</option>
          <option value="true">Active</option>
          <option value="false">Inactive</option>
        </select>
      </div>

      <div class="filter-box">
        <label>Category</label>
        <select v-model="filters.category" @change="fetchEvacuees">
          <option value="">All</option>
          <option value="is_child">Child</option>
          <option value="is_senior">Senior</option>
          <option value="is_pwd">PWD</option>
          <option value="is_pregnant">Pregnant</option>
          <option value="is_lactating">Lactating</option>
        </select>
      </div>

      <button class="secondary-btn" @click="fetchEvacuees">
        Apply
      </button>

      <button class="ghost-btn" @click="resetFilters">
        Reset
      </button>
    </section>

    <section class="table-card">
      <div class="table-header">
        <div>
          <h2>Registered Evacuees</h2>
          <p>{{ evacuees.length }} record(s) shown</p>
        </div>
      </div>

      <div v-if="loading" class="state-text">
        Loading evacuees...
      </div>

      <div v-else-if="error" class="error-text">
        {{ error }}
      </div>

      <div v-else-if="evacuees.length === 0" class="state-text">
        No evacuee records found.
      </div>

      <div v-else class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Age/Sex</th>
              <th>Family Role</th>
              <th>Family Head</th>
              <th>Contact</th>
              <th>Categories</th>
              <th>Status</th>
              <th>Date Registered</th>
              <th class="actions-col">Actions</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="evacuee in evacuees" :key="evacuee.id">
              <td>
                <strong>{{ fullName(evacuee) }}</strong>
                <span class="small-muted">{{ evacuee.address || "No address" }}</span>
              </td>

              <td>
                {{ evacuee.age ?? 0 }} / {{ formatSex(evacuee.sex) }}
              </td>

              <td>
                <span v-if="evacuee.is_family_head" class="status-pill active">
                    Family Head
                </span>
                <span v-else class="status-pill inactive">
                    Member
                </span>
              </td>

              <td>
                <span v-if="evacuee.is_family_head">
                    {{ fullName(evacuee) }}
                </span>
                <span v-else>
                    {{ evacuee.family_head_name || "-" }}
                </span>
              </td>

              <td>
                {{ evacuee.contact_number || "-" }}
              </td>

              <td>
                <div class="chips">
                  <span v-if="evacuee.is_child" class="chip">Child</span>
                  <span v-if="evacuee.is_senior" class="chip">Senior</span>
                  <span v-if="evacuee.is_pwd" class="chip">PWD</span>
                  <span v-if="evacuee.is_pregnant" class="chip">Pregnant</span>
                  <span v-if="evacuee.is_lactating" class="chip">Lactating</span>
                  <span
                    v-if="!hasCategory(evacuee)"
                    class="small-muted"
                  >
                    None
                  </span>
                </div>
              </td>

              <td>
                <span
                  class="status-pill"
                  :class="evacuee.is_active ? 'active' : 'inactive'"
                >
                  {{ evacuee.is_active ? "Active" : "Inactive" }}
                </span>
              </td>

              <td>
                {{ formatDate(evacuee.date_registered) }}
              </td>

              <td class="actions">
                <button class="table-btn" @click="openEditModal(evacuee)">
                  Edit
                </button>

                <button
                  class="table-btn danger"
                  @click="toggleActive(evacuee)"
                >
                  {{ evacuee.is_active ? "Mark Left" : "Reactivate" }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <div v-if="modal.open" class="modal-backdrop" @click.self="closeModal">
      <div class="modal">
        <div class="modal-header">
          <div>
            <p class="eyebrow">
              {{ modal.mode === "create" ? "New Record" : "Update Record" }}
            </p>
            <h2>
              {{ modal.mode === "create" ? "Add Evacuee" : "Edit Evacuee" }}
            </h2>
          </div>

          <button class="close-btn" @click="closeModal">
            ×
          </button>
        </div>

        <form @submit.prevent="saveEvacuee">
          <div class="form-grid">
            <div class="assigned-center-box full">
                <span class="label">Assigned Evacuation Center</span>
                <strong>{{ assignedCenterName }}</strong>
            </div>

            <label>
              First Name
              <input
                v-model="modal.form.first_name"
                type="text"
                required
              />
            </label>

            <label>
              Middle Name
              <input
                v-model="modal.form.middle_name"
                type="text"
              />
            </label>

            <label>
              Last Name
              <input
                v-model="modal.form.last_name"
                type="text"
                required
              />
            </label>

            <label>
              Age
              <input
                v-model.number="modal.form.age"
                type="number"
                min="0"
                required
              />
            </label>

            <label>
              Sex
              <select v-model="modal.form.sex" required>
                <option value="" disabled>Select sex</option>
                <option value="MALE">Male</option>
                <option value="FEMALE">Female</option>
                <option value="OTHER">Other</option>
              </select>
            </label>

            <label>
              Contact Number
              <input
                v-model="modal.form.contact_number"
                type="text"
                placeholder="09XXXXXXXXX"
              />
            </label>

            <label class="full">
              Address
              <textarea
                v-model="modal.form.address"
                rows="2"
                placeholder="Complete address"
              ></textarea>
            </label>

            <label v-if="!modal.form.is_family_head" class="full">
                Family Head Name
                <input
                    v-model="modal.form.family_head_name"
                    type="text"
                    placeholder="Name of family head"
                />
            </label>

            <label class="check-label full">
                <input v-model="modal.form.is_family_head" type="checkbox" />
                This evacuee is the family head
            </label>
          </div>

          <div class="checkbox-section">
            <p class="section-title">Category / Special Condition</p>

            <div class="checkbox-grid">
              <label class="check-label">
                <input v-model="modal.form.is_child" type="checkbox" />
                Child
              </label>

              <label class="check-label">
                <input v-model="modal.form.is_senior" type="checkbox" />
                Senior Citizen
              </label>

              <label class="check-label">
                <input v-model="modal.form.is_pwd" type="checkbox" />
                PWD
              </label>

              <label class="check-label">
                <input v-model="modal.form.is_pregnant" type="checkbox" />
                Pregnant
              </label>

              <label class="check-label">
                <input v-model="modal.form.is_lactating" type="checkbox" />
                Lactating
              </label>

              <label class="check-label">
                <input v-model="modal.form.is_active" type="checkbox" />
                Active in Center
              </label>
            </div>
          </div>

          <label class="remarks-label">
            Remarks
            <textarea
              v-model="modal.form.remarks"
              rows="3"
              placeholder="Optional notes..."
            ></textarea>
          </label>

          <div v-if="modalError" class="error-text modal-error">
            {{ modalError }}
          </div>

          <div class="modal-actions">
            <button type="button" class="ghost-btn" @click="closeModal">
              Cancel
            </button>

            <button type="submit" class="primary-btn" :disabled="saving">
              {{ saving ? "Saving..." : "Save Record" }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import api from "@/services/api";

export default {
  name: "StaffEvacuees",

  data() {
    return {
      evacuees: [],
      assignedCenter: null,
      loading: false,
      saving: false,
      error: "",
      modalError: "",

      filters: {
        search: "",
        is_active: "true",
        category: "",
      },

      modal: {
        open: false,
        mode: "create",
        id: null,
        form: this.emptyForm(),
      },
    };
  },

  mounted() {
    this.fetchCenters();
    this.fetchEvacuees();
  },

  computed: {
    assignedCenterName() {
        return this.assignedCenter?.name || "No assigned center found";
    },
  },

  methods: {
    emptyForm() {
      return {
        center: "",
        first_name: "",
        middle_name: "",
        last_name: "",
        age: 0,
        sex: "",
        contact_number: "",
        address: "",
        is_family_head: false,
        family_head_name: "",   
        is_child: false,
        is_senior: false,
        is_pwd: false,
        is_pregnant: false,
        is_lactating: false,
        is_active: true,
        remarks: "",
      };
    },

    async fetchCenters() {
        try {
            const res = await api.get("evac_centers/evacuation-centers/");
            this.centers = Array.isArray(res.data) ? res.data : res.data.results || [];

            this.assignedCenter = this.centers.length > 0 ? this.centers[0] : null;

            if (this.assignedCenter) {
            this.modal.form.center = this.assignedCenter.id;
            }
        } catch (err) {
            console.error(err);
            this.error = "Failed to load assigned evacuation center.";
        }
    },

    async fetchEvacuees() {
      this.loading = true;
      this.error = "";

      try {
        const params = {};

        if (this.filters.search) {
          params.search = this.filters.search;
        }

        if (this.filters.is_active !== "") {
          params.is_active = this.filters.is_active;
        }

        if (this.filters.category) {
          params[this.filters.category] = true;
        }

        const res = await api.get("evac_centers/evacuees/", { params });
        this.evacuees = Array.isArray(res.data) ? res.data : res.data.results || [];
      } catch (err) {
        console.error(err);
        this.error = "Failed to load evacuee records.";
      } finally {
        this.loading = false;
      }
    },

    resetFilters() {
      this.filters = {
        search: "",
        is_active: "true",
        category: "",
      };

      this.fetchEvacuees();
    },

    handleSearchInput() {
      clearTimeout(this.searchTimer);

      this.searchTimer = setTimeout(() => {
        this.fetchEvacuees();
      }, 400);
    },

    openCreateModal() {
        this.modalError = "";

        if (!this.assignedCenter) {
            this.modalError = "No assigned evacuation center found for this staff account.";
            return;
        }

        this.modal.mode = "create";
        this.modal.id = null;
        this.modal.form = this.emptyForm();
        this.modal.form.center = this.assignedCenter.id;

        this.modal.open = true;
    },

    openEditModal(evacuee) {
      this.modalError = "";
      this.modal.mode = "edit";
      this.modal.id = evacuee.id;

      this.modal.form = {
        center: evacuee.center || "",
        first_name: evacuee.first_name || "",
        middle_name: evacuee.middle_name || "",
        last_name: evacuee.last_name || "",
        age: evacuee.age ?? 0,
        sex: evacuee.sex || "",
        contact_number: evacuee.contact_number || "",
        address: evacuee.address || "",
        is_family_head: Boolean(evacuee.is_family_head),
        family_head_name: evacuee.family_head_name || "",
        is_child: Boolean(evacuee.is_child),
        is_senior: Boolean(evacuee.is_senior),
        is_pwd: Boolean(evacuee.is_pwd),
        is_pregnant: Boolean(evacuee.is_pregnant),
        is_lactating: Boolean(evacuee.is_lactating),
        is_active: Boolean(evacuee.is_active),
        remarks: evacuee.remarks || "",
      };

      this.modal.open = true;
    },

    closeModal() {
      this.modal.open = false;
      this.modalError = "";
    },

    async saveEvacuee() {
        this.saving = true;
        this.modalError = "";

        try {
            if (!this.assignedCenter) {
            this.modalError = "No assigned evacuation center found for this staff account.";
            return;
            }

            const payload = {
            ...this.modal.form,
            center: this.assignedCenter.id,
            age: Number(this.modal.form.age || 0),
            };

            if (payload.is_family_head) {
                payload.family_head_name = [
                    payload.last_name,
                    payload.first_name,
                    payload.middle_name,
                ]
                    .filter(Boolean)
                    .join(", ");
            }

            if (this.modal.mode === "create") {
            await api.post("evac_centers/evacuees/", payload);
            } else {
            await api.patch(`evac_centers/evacuees/${this.modal.id}/`, payload);
            }

            this.closeModal();
            await this.fetchEvacuees();
        } catch (err) {
            console.error(err);

            if (err.response?.data) {
            this.modalError = JSON.stringify(err.response.data);
            } else {
            this.modalError = "Failed to save evacuee record.";
            }
        } finally {
            this.saving = false;
        }
    },

    async toggleActive(evacuee) {
      const action = evacuee.is_active ? "mark this evacuee as left/inactive" : "reactivate this evacuee";

      if (!confirm(`Are you sure you want to ${action}?`)) {
        return;
      }

      try {
        await api.patch(`evac_centers/evacuees/${evacuee.id}/`, {
          is_active: !evacuee.is_active,
        });

        await this.fetchEvacuees();
      } catch (err) {
        console.error(err);
        alert("Failed to update evacuee status.");
      }
    },

    fullName(evacuee) {
        const lastName = evacuee.last_name || "";
        const givenNames = [
            evacuee.first_name,
            evacuee.middle_name,
        ]
            .filter(Boolean)
            .join(" ");

        return [lastName, givenNames]
            .filter(Boolean)
            .join(", ");
    },

    formatSex(sex) {
      if (!sex) return "-";

      const map = {
        MALE: "Male",
        FEMALE: "Female",
        OTHER: "Other",
      };

      return map[sex] || sex;
    },

    formatDate(value) {
      if (!value) return "-";

      return new Date(value).toLocaleDateString("en-PH", {
        year: "numeric",
        month: "short",
        day: "2-digit",
      });
    },

    hasCategory(evacuee) {
      return (
        evacuee.is_child ||
        evacuee.is_senior ||
        evacuee.is_pwd ||
        evacuee.is_pregnant ||
        evacuee.is_lactating
      );
    },
  },
};
</script>

<style scoped>
.evacuees-page {
  padding: 24px;
  color: #1f2937;
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 20px;
}

.eyebrow {
  margin: 0 0 4px;
  font-size: 0.75rem;
  font-weight: 700;
  color: #2563eb;
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

.filters-card,
.table-card {
  background: #ffffff;
  border-radius: 16px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 10px 25px rgba(15, 23, 42, 0.06);
}

.filters-card {
  display: grid;
  grid-template-columns: 1.5fr 180px 180px auto auto;
  gap: 12px;
  align-items: end;
  padding: 16px;
  margin-bottom: 18px;
}

.search-box,
.filter-box,
.form-grid label,
.remarks-label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 0.85rem;
  font-weight: 600;
}

input,
select,
textarea {
  width: 100%;
  border: 1px solid #d1d5db;
  border-radius: 10px;
  padding: 10px 12px;
  font: inherit;
  outline: none;
  background: #ffffff;
}

input:focus,
select:focus,
textarea:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12);
}

.primary-btn,
.secondary-btn,
.ghost-btn,
.table-btn {
  border: 0;
  border-radius: 10px;
  padding: 10px 14px;
  font-weight: 700;
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

.secondary-btn {
  background: #111827;
  color: #ffffff;
}

.ghost-btn {
  background: #f3f4f6;
  color: #111827;
}

.table-card {
  padding: 16px;
}

.table-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.table-header p {
  margin: 4px 0 0;
  color: #6b7280;
}

.table-wrap {
  width: 100%;
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  min-width: 1050px;
}

th,
td {
  padding: 12px 10px;
  border-bottom: 1px solid #e5e7eb;
  text-align: left;
  vertical-align: top;
}

th {
  font-size: 0.78rem;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.small-muted {
  display: block;
  margin-top: 3px;
  font-size: 0.78rem;
  color: #6b7280;
}

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.chip {
  padding: 4px 8px;
  border-radius: 999px;
  background: #eff6ff;
  color: #1d4ed8;
  font-size: 0.75rem;
  font-weight: 700;
}

.status-pill {
  display: inline-flex;
  padding: 5px 9px;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 700;
}

.status-pill.active {
  background: #dcfce7;
  color: #166534;
}

.status-pill.inactive {
  background: #fee2e2;
  color: #991b1b;
}

.actions-col {
  width: 160px;
}

.actions {
  display: flex;
  gap: 8px;
}

.table-btn {
  padding: 8px 10px;
  background: #e5e7eb;
  color: #111827;
  font-size: 0.8rem;
}

.table-btn.danger {
  background: #fee2e2;
  color: #991b1b;
}

.state-text,
.error-text {
  padding: 24px;
  text-align: center;
}

.error-text {
  color: #b91c1c;
  font-weight: 700;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 50;
  background: rgba(15, 23, 42, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 18px;
}

.modal {
  width: min(860px, 100%);
  max-height: 92vh;
  overflow-y: auto;
  background: #ffffff;
  border-radius: 18px;
  padding: 20px;
  box-shadow: 0 25px 60px rgba(15, 23, 42, 0.28);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.close-btn {
  width: 36px;
  height: 36px;
  border: 0;
  border-radius: 999px;
  background: #f3f4f6;
  font-size: 1.5rem;
  cursor: pointer;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.full {
  grid-column: 1 / -1;
}

.checkbox-section {
  margin-top: 18px;
  padding: 14px;
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  background: #f9fafb;
}

.section-title {
  margin: 0 0 10px;
  font-weight: 800;
}

.checkbox-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.check-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.check-label input {
  width: auto;
}

.remarks-label {
  margin-top: 16px;
}

.modal-error {
  text-align: left;
  padding: 12px 0 0;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 18px;
}

.assigned-center-box {
  padding: 12px 14px;
  border: 1px solid #dbeafe;
  border-radius: 12px;
  background: #eff6ff;
}

.assigned-center-box .label {
  display: block;
  margin-bottom: 4px;
  font-size: 0.78rem;
  font-weight: 700;
  color: #2563eb;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.assigned-center-box strong {
  color: #1e3a8a;
}

@media (max-width: 900px) {
  .page-header {
    flex-direction: column;
  }

  .filters-card {
    grid-template-columns: 1fr;
  }

  .form-grid,
  .checkbox-grid {
    grid-template-columns: 1fr;
  }

  .actions {
    flex-direction: column;
  }
}
</style>