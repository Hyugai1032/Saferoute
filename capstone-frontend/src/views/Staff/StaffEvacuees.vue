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
              <th>Reason for Evacuation</th>
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
                <span v-if="evacuee.reason_for_evacuation_display" class="reason-chip">
                  {{ evacuee.reason_for_evacuation_display }}
                </span>
                <span v-else class="small-muted">-</span>
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
                Family Head
                <select
                    v-model="modal.form.family_head_selection"
                    @change="onFamilyHeadSelectionChange"
                >
                    <option value="">-- Select family head --</option>
                    <option
                        v-for="name in familyHeadOptions"
                        :key="name"
                        :value="name"
                    >
                        {{ name }}
                    </option>
                    <option value="__OTHER__">+ Not listed / New family head</option>
                </select>
            </label>

            <label
                v-if="!modal.form.is_family_head && modal.form.family_head_selection === '__OTHER__'"
                class="full"
            >
                New Family Head Name
                <input
                    v-model="modal.form.family_head_name"
                    type="text"
                    placeholder="Enter family head name"
                    required
                />
            </label>

            <label class="check-label full">
                <input v-model="modal.form.is_family_head" type="checkbox" />
                This evacuee is the family head
            </label>
          </div>

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

      reasonOptions: [],
      reasonsLoading: false,
      reasonsError: "",

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
    this.fetchReasonOptions();
  },

  computed: {
    assignedCenterName() {
        return this.assignedCenter?.name || "No assigned center found";
    },

    familyHeadOptions() {
      const names = new Set();

      this.evacuees.forEach((evacuee) => {
        const name = evacuee.is_family_head
          ? this.fullName(evacuee)
          : evacuee.family_head_name;

        if (name) {
          names.add(name);
        }
      });

      return Array.from(names).sort((a, b) => a.localeCompare(b));
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
  },

  methods: {
    emptyForm() {
      return {
        center: "",
        first_name: "",
        middle_name: "",
        last_name: "",
        age: null,
        sex: "",
        contact_number: "",
        address: "",
        is_family_head: false,
        family_head_name: "",
        family_head_selection: "",
        reason_for_evacuation: null,
        reason_for_evacuation_name: "",
        is_child: false,
        is_senior: false,
        is_pwd: false,
        is_pregnant: false,
        is_lactating: false,
        is_active: true,
        remarks: "",
      };
    },

    async fetchReasonOptions() {
      this.reasonsLoading = true;
      this.reasonsError = "";
 
      try {
        const res = await api.get("evac_centers/evacuation-reasons/", {
          params: { active_only: "true" },
        });
        this.reasonOptions = Array.isArray(res.data) ? res.data : res.data.results || [];
      } catch (err) {
        console.error(err);
        this.reasonsError = "Failed to load evacuation reasons.";
      } finally {
        this.reasonsLoading = false;
      }
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

      const existingFamilyHeadName = evacuee.family_head_name || "";
      const isKnownFamilyHead =
        existingFamilyHeadName && this.familyHeadOptions.includes(existingFamilyHeadName);

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
        family_head_name: existingFamilyHeadName,
        family_head_selection: existingFamilyHeadName
          ? (isKnownFamilyHead ? existingFamilyHeadName : "__OTHER__")
          : "",
        reason_for_evacuation: evacuee.reason_for_evacuation || null,
        reason_for_evacuation_name: evacuee.reason_for_evacuation_display || "",
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

    onFamilyHeadSelectionChange() {
      if (this.modal.form.family_head_selection === "__OTHER__") {
        this.modal.form.family_head_name = "";
      } else {
        this.modal.form.family_head_name = this.modal.form.family_head_selection;
      }
    },

    async saveEvacuee() {
        this.saving = true;
        this.modalError = "";

        try {
            if (!this.assignedCenter) {
            this.modalError = "No assigned evacuation center found for this staff account.";
            return;
            }

            const { family_head_selection, reason_for_evacuation_name, ...formData } = this.modal.form;

            const payload = {
            ...formData,
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
  /* Dark theme (default palette for this page) */
  --bg: #060912;
  --panel2: rgba(8,12,24,.85);
  --border2: rgba(255,255,255,.08);
  --text: #e5e7eb;
  --muted: rgba(229,231,235,.62);
  --field-bg: rgba(2,6,23,.55);
  --field-border: rgba(56,189,248,.18);
  --surface-tint: rgba(255,255,255,.05);
  --surface-tint-strong: rgba(255,255,255,.14);
  --modal-a: rgba(10,14,28,.96);
  --modal-b: rgba(6,9,18,.98);
  --heading: #f8fafc;

  --blue: #38bdf8;
  --blue2: #6366f1;
  --violet: #a78bfa;
  --pink: #f472b6;
  --green: #34d399;
  --red: #fb7185;
  --amber: #fbbf24;
  --teal: #2dd4bf;

  color-scheme: dark;
  padding: 24px 32px;
  color: var(--text) !important;
  min-height: 100vh;
  box-sizing: border-box;
  background:
    radial-gradient(900px 400px at 8% -10%, rgba(99,102,241,.10), transparent 60%),
    radial-gradient(700px 380px at 100% 0%, rgba(244,114,182,.08), transparent 55%),
    var(--bg) !important;
}

/* Light theme */
html[data-theme="light"] .evacuees-page {
  --bg: #f0f4fa;
  --panel2: rgba(255,255,255,.96);
  --border2: rgba(15,23,42,.10);
  --text: #0f172a;
  --muted: rgba(15,23,42,.55);
  --field-bg: rgba(255,255,255,.95);
  --field-border: rgba(15,23,42,.14);
  --surface-tint: rgba(15,23,42,.04);
  --surface-tint-strong: rgba(15,23,42,.07);
  --modal-a: rgba(255,255,255,.98);
  --modal-b: rgba(244,246,251,.98);
  --heading: #0f172a;

  color-scheme: light;
}

/* Reset conflicting global styles */
.modal-backdrop .full,
.modal-backdrop .checkbox-section,
.modal-backdrop label {
  background: transparent !important;
  box-shadow: none !important;
}

.modal-backdrop .assigned-center-box.full {
  background: rgba(56,189,248,.08) !important;
  border: 1px solid rgba(56,189,248,.25) !important;
}

.modal-backdrop .checkbox-section {
  background: var(--surface-tint) !important;
  border: 1px solid var(--border2) !important;
}

.modal-backdrop input:invalid,
.modal-backdrop select:invalid,
.modal-backdrop textarea:invalid,
.modal-backdrop input:-moz-ui-invalid,
.modal-backdrop select:-moz-ui-invalid,
.modal-backdrop textarea:-moz-ui-invalid {
  box-shadow: none !important;
  outline: none !important;
}

input[type="number"] {
  -moz-appearance: textfield;
  appearance: textfield;
}
input[type="number"]::-webkit-outer-spin-button,
input[type="number"]::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

/* ===== PAGE HEADER ===== */
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 28px;
  flex-wrap: wrap;
}

.page-header .eyebrow {
  margin: 0 0 4px;
  font-size: 0.7rem;
  font-weight: 800;
  color: var(--blue) !important;
  text-transform: uppercase;
  letter-spacing: 0.12em;
}

.page-header h1 {
  margin: 0;
  font-size: 2rem;
  font-weight: 900;
  background: linear-gradient(135deg, var(--heading), var(--blue) 60%, var(--violet));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent !important;
}

.page-header .subtext {
  margin: 6px 0 0;
  color: var(--muted) !important;
  font-size: 0.95rem;
}

/* Enhanced Primary Button */
.primary-btn {
  position: relative;
  border: 0;
  border-radius: 14px;
  padding: 14px 28px;
  font-weight: 700;
  font-size: 0.95rem;
  cursor: pointer;
  color: #fff !important;
  background: linear-gradient(135deg, var(--blue), var(--blue2) 50%, var(--violet)) !important;
  box-shadow: 0 8px 28px rgba(99,102,241,.35);
  transition: all .25s ease;
  letter-spacing: 0.3px;
  overflow: hidden;
}

.primary-btn::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255,255,255,.15), transparent 50%);
  border-radius: 14px;
  opacity: 0;
  transition: opacity .3s ease;
}

.primary-btn:hover:not(:disabled) {
  transform: translateY(-2px) scale(1.02);
  box-shadow: 0 12px 40px rgba(99,102,241,.5);
}

.primary-btn:hover:not(:disabled)::before {
  opacity: 1;
}

.primary-btn:active:not(:disabled) {
  transform: translateY(0) scale(.98);
}

.primary-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* ===== FILTERS CARD ===== */
.filters-card {
  background: var(--panel2) !important;
  padding: 20px 24px;
  border-radius: 18px;
  border: 1px solid var(--border2);
  box-shadow: 0 8px 32px rgba(0,0,0,.25);
  display: grid;
  grid-template-columns: 1.8fr 160px 160px auto auto;
  gap: 14px;
  align-items: end;
  margin-bottom: 24px;
  backdrop-filter: blur(8px);
}

.filters-card label {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--muted) !important;
  background: none !important;
}

.filters-card input,
.filters-card select {
  width: 100%;
  border: 1px solid var(--field-border) !important;
  border-radius: 12px;
  padding: 10px 14px;
  font: inherit;
  font-size: 0.9rem;
  outline: none;
  background: var(--field-bg) !important;
  color: var(--text) !important;
  transition: all .2s ease;
}

.filters-card input:focus,
.filters-card select:focus {
  border-color: var(--blue) !important;
  box-shadow: 0 0 0 4px rgba(56,189,248,.15);
}

/* Enhanced Secondary Button */
.secondary-btn {
  border: 0;
  border-radius: 12px;
  padding: 10px 20px;
  font-weight: 700;
  font-size: 0.85rem;
  cursor: pointer;
  background: linear-gradient(135deg, var(--blue2), var(--violet)) !important;
  color: #fff !important;
  box-shadow: 0 4px 16px rgba(99,102,241,.3);
  transition: all .2s ease;
  letter-spacing: 0.3px;
  align-self: end;
}

.secondary-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 24px rgba(99,102,241,.4);
}

.secondary-btn:active {
  transform: translateY(0);
}

/* Enhanced Ghost Button */
.ghost-btn {
  border: 2px solid var(--border2) !important;
  border-radius: 12px;
  padding: 10px 20px;
  font-weight: 700;
  font-size: 0.85rem;
  cursor: pointer;
  background: var(--field-bg) !important;
  color: var(--text) !important;
  transition: all .2s ease;
  align-self: end;
}

.ghost-btn:hover {
  border-color: var(--blue) !important;
  background: rgba(56,189,248,.08) !important;
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(56,189,248,.15);
}

/* ===== TABLE CARD ===== */
.table-card {
  background: var(--panel2) !important;
  overflow: hidden;
  border-radius: 18px;
  border: 1px solid var(--border2);
  box-shadow: 0 8px 32px rgba(0,0,0,.25);
  backdrop-filter: blur(8px);
}

.table-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 24px;
  border-radius: 18px 18px 0 0;
  background: linear-gradient(135deg, rgba(56,189,248,.10), rgba(99,102,241,.10), rgba(244,114,182,.06)) !important;
  border-bottom: 1px solid var(--border2);
}

.table-header h2 {
  font-size: 1.1rem;
  font-weight: 800;
  color: var(--heading) !important;
}

.table-header p {
  margin: 4px 0 0;
  font-size: 0.82rem;
  color: var(--muted) !important;
}

.table-wrap {
  padding: 0 24px 24px;
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  min-width: 1050px;
}

th {
  padding: 14px 12px;
  font-size: 0.7rem;
  color: var(--muted) !important;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: 800;
  background: var(--surface-tint);
  border-bottom: 2px solid var(--border2);
  text-align: left;
}

td {
  padding: 14px 12px;
  border-bottom: 1px solid var(--border2);
  text-align: left;
  vertical-align: middle;
  color: var(--text) !important;
  font-size: 0.9rem;
}

tbody tr {
  transition: background .15s ease;
}

tbody tr:nth-child(even) { background: var(--surface-tint); }
tbody tr:hover { background: rgba(99,102,241,.06); }

/* Table Buttons */
.table-btn {
  padding: 6px 14px;
  border: 1px solid rgba(45,212,191,.3) !important;
  border-radius: 8px;
  background: rgba(45,212,191,.10) !important;
  color: #b6f5ec !important;
  font-size: 0.75rem;
  font-weight: 700;
  cursor: pointer;
  transition: all .2s ease;
  letter-spacing: 0.3px;
}

.table-btn:hover {
  background: rgba(45,212,191,.2) !important;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(45,212,191,.15);
}

.table-btn.danger {
  border-color: rgba(239,68,68,.35) !important;
  background: rgba(239,68,68,.12) !important;
  color: #ffd0d6 !important;
}

.table-btn.danger:hover {
  background: rgba(239,68,68,.25) !important;
  box-shadow: 0 4px 12px rgba(239,68,68,.15);
}

/* ===== MODAL ===== */
.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: rgba(0,0,0,0.7);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 18px;
  overflow-y: auto;
  animation: fadeIn .25s ease;
}

@keyframes fadeIn {
  from { opacity: 0; backdrop-filter: blur(0); }
  to { opacity: 1; backdrop-filter: blur(6px); }
}

.modal {
  width: min(880px, 100%);
  max-height: 90vh;
  overflow-y: auto;
  background:
    radial-gradient(1200px 520px at 20% -20%, rgba(99,102,241,.15), transparent 55%),
    linear-gradient(180deg, var(--modal-a), var(--modal-b)) !important;
  border: 1px solid rgba(99,102,241,.2);
  border-radius: 24px;
  padding: 28px 32px;
  box-shadow: 0 40px 100px rgba(0,0,0,.6);
  color: var(--text) !important;
  margin: auto;
  animation: slideUp .3s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px) scale(.96);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* FIX: Make sure modal content background is consistent */
.modal > * {
  background: transparent !important;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 2px solid var(--border2);
  background: transparent !important;
}

.modal-header .eyebrow {
  margin: 0 0 2px;
  font-size: 0.65rem;
  font-weight: 800;
  color: var(--blue) !important;
  text-transform: uppercase;
  letter-spacing: 0.12em;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--heading) !important;
}

/* Enhanced Close Button */
.close-btn {
  width: 40px;
  height: 40px;
  border: 2px solid rgba(239,68,68,.25) !important;
  border-radius: 999px;
  background: rgba(239,68,68,.06) !important;
  color: var(--muted) !important;
  font-size: 1.4rem;
  line-height: 1;
  cursor: pointer;
  transition: all .25s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.close-btn:hover {
  background: rgba(239,68,68,.85) !important;
  color: #fff !important;
  transform: rotate(90deg) scale(1.05);
  border-color: rgba(239,68,68,.85) !important;
}

/* Form Grid */
.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

/* FIX: Ensure form background is transparent */
.modal form {
  background: transparent !important;
}

.form-grid label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--muted) !important;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  background: transparent !important;
}

.form-grid label input,
.form-grid label select,
.form-grid label textarea {
  width: 100%;
  border: 1.5px solid var(--field-border) !important;
  border-radius: 12px;
  padding: 10px 14px;
  font: inherit;
  font-size: 0.9rem;
  font-weight: 500;
  outline: none;
  background: var(--field-bg) !important;
  color: var(--text) !important;
  transition: all .2s ease;
  text-transform: none;
}

/* FIX: Custom dropdown arrow that works in both themes */
/* .form-grid label select {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath d='M1 1l5 5 5-5' stroke='%236366f1' stroke-width='1.5' fill='none' stroke-linecap='round'/%3E%3C/svg%3E") !important;
  background-repeat: no-repeat !important;
  background-position: right 14px center !important;
  background-size: 12px !important;
  padding-right: 40px !important;
} */

/* FIX: Ensure dropdown options are visible */
.form-grid label select option {
  background: var(--modal-b) !important;
  color: var(--text) !important;
  padding: 8px;
}

/* FIX: Specifically target the reason dropdown */
.full select {
  background-color: var(--field-bg) !important;
  border: 1.5px solid var(--field-border) !important;
  color: var(--text) !important;
}

.form-grid label input:focus,
.form-grid label select:focus,
.form-grid label textarea:focus {
  border-color: var(--blue) !important;
  box-shadow: 0 0 0 4px rgba(56,189,248,.12);
}

.full { grid-column: 1 / -1; }

/* Assigned Center Box */
.assigned-center-box {
  padding: 14px 18px;
  border: 1.5px solid rgba(56,189,248,.25) !important;
  border-radius: 14px;
  background: rgba(56,189,248,.06) !important;
  transition: all .2s ease;
}

.assigned-center-box:hover {
  border-color: rgba(56,189,248,.4) !important;
  background: rgba(56,189,248,.10) !important;
}

.assigned-center-box .label {
  display: block;
  margin-bottom: 4px;
  font-size: 0.7rem;
  font-weight: 800;
  color: var(--blue) !important;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  background: none !important;
}

.assigned-center-box strong {
  font-size: 1.05rem;
  color: var(--heading) !important;
}

/* Checkbox Section */
.checkbox-section {
  margin-top: 20px;
  padding: 18px 20px;
  border: 1.5px solid var(--border2) !important;
  border-radius: 16px;
  background: var(--surface-tint) !important;
  transition: all .2s ease;
}

.checkbox-section:hover {
  border-color: rgba(56,189,248,.15) !important;
}

.section-title {
  margin: 0 0 14px;
  font-weight: 800;
  font-size: 0.85rem;
  color: var(--heading) !important;
  background: none !important;
  letter-spacing: 0.3px;
}

.checkbox-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.check-label {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
  font-size: 0.88rem;
  color: var(--text) !important;
  cursor: pointer;
  transition: color .2s ease;
  padding: 4px 0;
}

.check-label:hover {
  color: var(--blue) !important;
}

.check-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: var(--blue);
  border-radius: 4px;
  flex-shrink: 0;
}

/* Remarks */
.remarks-label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-top: 18px;
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--muted) !important;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  background: transparent !important;
}

.remarks-label textarea {
  width: 100%;
  border: 1.5px solid var(--field-border) !important;
  border-radius: 12px;
  padding: 12px 14px;
  font: inherit;
  font-size: 0.9rem;
  outline: none;
  background: var(--field-bg) !important;
  color: var(--text) !important;
  transition: all .2s ease;
  resize: vertical;
}

.remarks-label textarea:focus {
  border-color: var(--blue) !important;
  box-shadow: 0 0 0 4px rgba(56,189,248,.12);
}

/* Modal Actions */
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 14px;
  margin-top: 24px;
  padding-top: 18px;
  border-top: 2px solid var(--border2);
  background: transparent !important;
}

/* ===== FIX: Modal actions container background in light mode ===== */
.modal .modal-actions {
  background: transparent !important;
  background-color: transparent !important;
}

html[data-theme="light"] .modal .modal-actions {
  background: transparent !important;
  background-color: transparent !important;
}

/* Ensure no background bleed from parent elements */
html[data-theme="light"] .modal form,
html[data-theme="light"] .modal .modal-header,
html[data-theme="light"] .modal .form-grid,
html[data-theme="light"] .modal .checkbox-section,
html[data-theme="light"] .modal .remarks-label {
  background: transparent !important;
  background-color: transparent !important;
}

/* Modal Cancel Button - Enhanced */
.modal-actions .ghost-btn {
  padding: 12px 28px;
  border-radius: 12px;
  font-weight: 700;
  font-size: 0.9rem;
  cursor: pointer;
  background: var(--field-bg) !important;
  color: var(--muted) !important;
  border: 2px solid var(--border2) !important;
  transition: all .25s ease;
  letter-spacing: 0.3px;
}

.modal-actions .ghost-btn:hover {
  border-color: var(--red) !important;
  color: var(--red) !important;
  background: rgba(239,68,68,.06) !important;
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(239,68,68,.1);
}

/* Modal Save Button - Enhanced */
.modal-actions .primary-btn {
  padding: 12px 32px;
  border-radius: 12px;
  font-weight: 700;
  font-size: 0.9rem;
  cursor: pointer;
  color: #fff !important;
  background: linear-gradient(135deg, var(--blue), var(--blue2) 50%, var(--violet)) !important;
  box-shadow: 0 6px 24px rgba(99,102,241,.35);
  border: none;
  transition: all .25s ease;
  letter-spacing: 0.3px;
}

.modal-actions .primary-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(99,102,241,.5);
}

.modal-actions .primary-btn:active:not(:disabled) {
  transform: translateY(0) scale(.98);
}

.modal-actions .primary-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* ===== LIGHT MODE SPECIFIC FIXES ===== */
html[data-theme="light"] .modal {
  background:
    radial-gradient(1200px 520px at 20% -20%, rgba(99,102,241,.08), transparent 55%),
    linear-gradient(180deg, var(--modal-a), var(--modal-b)) !important;
}

html[data-theme="light"] .modal-header {
  background: transparent !important;
}

html[data-theme="light"] .modal form {
  background: transparent !important;
}

html[data-theme="light"] .form-grid label {
  background: transparent !important;
}

html[data-theme="light"] .form-grid label select {
  background-color: #ffffff !important;
  border-color: rgba(15,23,42,.2) !important;
  color: #0f172a !important;
}

html[data-theme="light"] .form-grid label select option {
  background: #ffffff !important;
  color: #0f172a !important;
}

html[data-theme="light"] .form-grid label input,
html[data-theme="light"] .form-grid label textarea {
  background-color: #ffffff !important;
  border-color: rgba(15,23,42,.2) !important;
  color: #0f172a !important;
}

html[data-theme="light"] .form-grid label input:focus,
html[data-theme="light"] .form-grid label select:focus,
html[data-theme="light"] .form-grid label textarea:focus {
  border-color: var(--blue) !important;
  box-shadow: 0 0 0 4px rgba(56,189,248,.12);
}

html[data-theme="light"] .checkbox-section {
  background: rgba(15,23,42,.04) !important;
}

html[data-theme="light"] .modal-actions {
  background: transparent !important;
}

html[data-theme="light"] .modal-actions .ghost-btn {
  background: #ffffff !important;
  border-color: rgba(15,23,42,.15) !important;
  color: #475569 !important;
}

html[data-theme="light"] .modal-actions .ghost-btn:hover {
  border-color: var(--red) !important;
  color: var(--red) !important;
  background: rgba(239,68,68,.06) !important;
}

html[data-theme="light"] .modal-actions .primary-btn {
  background: linear-gradient(135deg, #38bdf8, #6366f1 50%, #a78bfa) !important;
}

html[data-theme="light"] .remarks-label {
  background: transparent !important;
}

html[data-theme="light"] .remarks-label textarea {
  background: #ffffff !important;
  border-color: rgba(15,23,42,.15) !important;
  color: #0f172a !important;
}

html[data-theme="light"] .assigned-center-box {
  background: rgba(56,189,248,.06) !important;
  border-color: rgba(56,189,248,.2) !important;
}

html[data-theme="light"] .table-card {
  background: var(--panel2) !important;
}

html[data-theme="light"] .filters-card {
  background: var(--panel2) !important;
}

html[data-theme="light"] .filters-card input,
html[data-theme="light"] .filters-card select {
  background: #ffffff !important;
  border-color: rgba(15,23,42,.14) !important;
  color: #0f172a !important;
}

html[data-theme="light"] .filters-card input:focus,
html[data-theme="light"] .filters-card select:focus {
  border-color: var(--blue) !important;
  box-shadow: 0 0 0 4px rgba(56,189,248,.12);
}

/* ===== STATUS PILLS ===== */
.status-pill {
  display: inline-flex;
  padding: 4px 14px;
  border-radius: 999px;
  font-size: 0.7rem;
  font-weight: 800;
  letter-spacing: 0.3px;
  text-transform: uppercase;
}

.status-pill.active {
  background: rgba(52,211,153,.14) !important;
  color: #a7f3d5 !important;
  border: 1px solid rgba(52,211,153,.3);
}

.status-pill.inactive {
  background: rgba(251,113,133,.12) !important;
  color: #ffcdd6 !important;
  border: 1px solid rgba(251,113,133,.3);
}

/* ===== CHIPS ===== */
.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.chip {
  padding: 3px 10px;
  border-radius: 999px;
  background: rgba(167,139,250,.14) !important;
  border: 1px solid rgba(167,139,250,.25);
  color: #ede9ff !important;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.3px;
}

.reason-chip {
  display: inline-block;
  padding: 3px 12px;
  border-radius: 999px;
  background: rgba(56,189,248,.12) !important;
  border: 1px solid rgba(56,189,248,.25);
  color: #e0f6ff !important;
  font-size: 0.7rem;
  font-weight: 700;
  white-space: nowrap;
  letter-spacing: 0.3px;
}

/* ===== MISC ===== */
.small-muted {
  display: block;
  margin-top: 2px;
  font-size: 0.75rem;
  color: var(--muted) !important;
}

.state-text,
.error-text {
  padding: 32px 24px;
  text-align: center;
}

.error-text {
  color: #fca5a5 !important;
  font-weight: 700;
}

.modal-error {
  text-align: left;
  padding: 12px 0 0;
}

.field-error {
  color: #fca5a5 !important;
  background: none !important;
  font-size: 11px;
  margin-top: 4px;
}

/* ===== RESPONSIVE ===== */
@media (max-width: 900px) {
  .page-header {
    flex-direction: column;
  }
  .filters-card {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  .form-grid {
    grid-template-columns: 1fr;
  }
  .checkbox-grid {
    grid-template-columns: 1fr 1fr;
  }
  .actions {
    flex-direction: column;
    gap: 4px;
  }
  .modal {
    padding: 20px 16px;
  }
  .modal-actions {
    flex-direction: column-reverse;
  }
  .modal-actions .primary-btn,
  .modal-actions .ghost-btn {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 600px) {
  .evacuees-page {
    padding: 16px;
  }
  .checkbox-grid {
    grid-template-columns: 1fr;
  }
  .page-header h1 {
    font-size: 1.4rem;
  }
}

/* ===== FIX: Modal actions buttons positioning ===== */
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 14px;
  margin-top: 24px;
  padding-top: 18px;
  border-top: 2px solid var(--border2);
  background: transparent !important;
  align-items: center;
}

/* ===== FIX: Reason for Evacuation dropdown ===== */
.checkbox-section .full select {
  width: 100%;
  padding: 10px 14px;
  border-radius: 12px;
  border: 1.5px solid var(--field-border);
  background: var(--field-bg);
  color: var(--text);
  font-size: 0.9rem;
  font-weight: 500;
  outline: none;
  transition: all .2s ease;
  cursor: pointer;
  appearance: auto;
  -webkit-appearance: auto;
  -moz-appearance: auto;
}

.checkbox-section .full select:focus {
  border-color: var(--blue) !important;
  box-shadow: 0 0 0 4px rgba(56,189,248,.12);
}

.checkbox-section .full select option {
  background: var(--modal-b);
  color: var(--text);
  padding: 8px;
}

/* Light mode specific for reason dropdown */
html[data-theme="light"] .checkbox-section .full select {
  background: #ffffff !important;
  border-color: rgba(15, 23, 42, 0.2) !important;
  color: #0f172a !important;
}

html[data-theme="light"] .checkbox-section .full select option {
  background: #ffffff !important;
  color: #0f172a !important;
}

html[data-theme="light"] .checkbox-section .full select:focus {
  border-color: var(--blue) !important;
  box-shadow: 0 0 0 4px rgba(56,189,248,.12);
}

/* ===== FIX: Ensure modal actions buttons are visible and properly positioned ===== */
.modal-actions .ghost-btn,
.modal-actions .primary-btn {
  min-width: 120px;
  text-align: center;
}

/* Light mode specific for modal actions */
html[data-theme="light"] .modal-actions {
  background: transparent !important;
  background-color: transparent !important;
  border-top-color: rgba(15, 23, 42, 0.1) !important;
}

html[data-theme="light"] .modal-actions .ghost-btn {
  background: #ffffff !important;
  background-color: #ffffff !important;
  border: 2px solid rgba(15, 23, 42, 0.15) !important;
  color: #475569 !important;
}

html[data-theme="light"] .modal-actions .ghost-btn:hover {
  border-color: var(--red) !important;
  color: var(--red) !important;
  background: rgba(239, 68, 68, 0.06) !important;
  background-color: rgba(239, 68, 68, 0.06) !important;
}

html[data-theme="light"] .modal-actions .primary-btn {
  background: linear-gradient(135deg, #38bdf8, #6366f1 50%, #a78bfa) !important;
  background-color: transparent !important;
  color: #ffffff !important;
}
</style>