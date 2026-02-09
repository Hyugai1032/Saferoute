<!-- src/views/UserMgnt.vue - Create this file if you need user management -->
<template>
  <div class="user-management">
    <div class="page-header">
      <h1>User Management</h1>
      <p>Manage system users and permissions</p>
    </div>

    <div class="content">
      <!-- STATS -->
      <div class="stats-cards">
        <div class="stat-card">
          <h3>Total Users</h3>
          <p class="stat-number">{{ stats.total_users ?? "-" }}</p>
        </div>
        <div class="stat-card">
          <h3>Active Users</h3>
          <p class="stat-number">{{ stats.active_users ?? "-" }}</p>
        </div>
        <div class="stat-card">
          <h3>Citizens</h3>
          <p class="stat-number">{{ stats.by_role?.citizen ?? "-" }}</p>
        </div>
      </div>

      <!-- FILTERS -->
      <div style="display:flex; gap:10px; align-items:center; margin: 16px 0;">
        <input
          v-model="filters.search"
          placeholder="Search name/email/contact..."
          @keyup.enter="fetchUsers"
          style="padding:8px; width: 280px;"
        />

        <select v-model="filters.role" @change="fetchUsers" style="padding:8px;">
          <option value="">All roles</option>
          <option value="PROVINCIAL_ADMIN">Provincial Admin</option>
          <option value="MUNICIPAL_ADMIN">Municipal Admin</option>
          <option value="RESPONSE_TEAM">Response Team</option>
          <option value="EVAC_CENTER_STAFF">Evac Center Staff</option>
          <option value="CITIZEN">Citizen</option>
        </select>

        <select v-model="filters.is_active" @change="fetchUsers" style="padding:8px;">
          <option value="">All status</option>
          <option :value="true">Active</option>
          <option :value="false">Inactive</option>
        </select>

        <button @click="fetchUsers(1)" style="padding:8px 12px;">Refresh</button>

        <div style="margin-left:auto; opacity:.8;">
          Logged in as: <b>{{ me.email || "-" }}</b> ({{ me.role || "-" }})
        </div>
      </div>

      <!-- TABLE -->
      <div class="users-table">
        <h3>Registered Users</h3>

        <div v-if="loading" style="padding: 12px;">Loading...</div>
        <div v-else class="table-container">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Role</th>
                <th>Municipality</th>
                <th>Status</th>
                <th>Assigned Center</th>
                <th style="width: 260px;">Actions</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="u in safeUsers" :key="u.id">
                <td>{{ fullName(u) }}</td>
                <td>{{ u.email }}</td>
                <td>{{ u.role }}</td>
                <td>{{ u.municipality_name || "-" }}</td>
                <td>
                  <span class="status" :class="u.is_active ? 'active' : 'inactive'">
                    {{ u.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td>{{ u.assigned_center_name || "-" }}</td>

                <td style="display:flex; gap:8px; flex-wrap:wrap;">
                  <button class="btn-edit" @click="openEdit(u)" :disabled="!canEditUser(u)">
                    Edit
                  </button>

                  <button
                    class="btn-edit"
                    @click="toggleActive(u)"
                    :disabled="!canEditUser(u)"
                  >
                    {{ u.is_active ? 'Deactivate' : 'Activate' }}
                  </button>

                  <button
                    class="btn-edit"
                    @click="resetPassword(u)"
                    :disabled="!canEditUser(u)"
                  >
                    Reset PW
                  </button>

                  <button
                    class="btn-delete"
                    @click="deleteUser(u)"
                    :disabled="!canDeleteUser()"
                  >
                    Delete
                  </button>
                </td>
              </tr>

              <tr v-if="users.length === 0">
                <td colspan="6" style="padding: 12px; text-align:center; opacity:.7;">
                  No users found.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="pagination" v-if="pagination.count > 0">
        <button
          :disabled="!pagination.previous"
          @click="fetchUsers(Number(pagination.page) - 1)"
        >
          Prev
        </button>

        <span>
          Page {{ pagination.page }}
          of {{ Math.ceil(pagination.count / pagination.page_size) }}
          ({{ pagination.count }} users)
        </span>

        <button
          :disabled="!pagination.next"
          @click="fetchUsers(Number(pagination.page) + 1)"
        >
          Next
        </button>

      </div>


      <!-- EDIT MODAL (simple) -->
      <div v-if="edit.open" style="margin-top:16px; padding:12px; border:1px solid #ddd; border-radius:8px;">
        <h3 style="margin:0 0 8px 0;">Edit User: {{ edit.user.email }}</h3>

        <div style="display:flex; gap:12px; flex-wrap:wrap;">
          <input v-model="edit.form.first_name" placeholder="First name" style="padding:8px;" />
          <input v-model="edit.form.last_name" placeholder="Last name" style="padding:8px;" />
          <input v-model="edit.form.contact_number" placeholder="Contact number" style="padding:8px;" />

          <select v-model="edit.form.role" style="padding:8px;" :disabled="!canChangeRole()">
            <option value="PROVINCIAL_ADMIN">PROVINCIAL_ADMIN</option>
            <option value="MUNICIPAL_ADMIN">MUNICIPAL_ADMIN</option>
            <option value="RESPONSE_TEAM">RESPONSE_TEAM</option>
            <option value="EVAC_CENTER_STAFF">EVAC_CENTER_STAFF</option>
            <option value="CITIZEN">CITIZEN</option>
          </select>

          <select
            v-model.number="edit.form.municipality"
            style="padding:8px; width:240px;"
            :disabled="!canAssignMunicipality()"
            @change="onMunicipalityChanged"
          >
            <option :value="null">No municipality</option>
            <option v-for="m in municipalities" :key="m.id" :value="m.id">
              {{ m.name }}
            </option>
          </select>
        </div>

        <select
          v-if="edit.form.role === 'EVAC_CENTER_STAFF'"
          v-model.number="edit.form.assigned_center"
          style="padding:8px; width:260px;"
          :disabled="!isMunicipalOrHigher()"
        >
          <option :value="null">Unassigned</option>
          <option v-for="c in centers" :key="c.id" :value="c.id">
            {{ c.name }} ({{ c.municipality_name }})
          </option>
        </select>

        <div style="display:flex; gap:8px; margin-top:10px;">
          <button class="btn-edit" @click="saveEdit">Save</button>
          <button class="btn-delete" @click="closeEdit">Cancel</button>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import api from "../../services/api";

export default {
  name: "UserMgnt",
  data() {
    return {
      loading: false,
      users: [],
      stats: {},
      me: {},

      // ✅ dropdown data
      municipalities: [],
      centers: [],
      dropdownLoading: {
        municipalities: false,
        centers: false,
      },

      pagination: {
        page: 1,
        page_size: 10,
        count: 0,
        next: null,
        previous: null,
      },

      filters: {
        search: "",
        role: "",
        is_active: "",
      },

      edit: {
        open: false,
        user: null,
        form: {
          first_name: "",
          last_name: "",
          contact_number: "",
          role: "",
          municipality: null,
          assigned_center: null,
        },
      },
    };
  },

  computed: {
    safeUsers() {
      return (this.users || []).filter((u) => u && u.id != null);
    },
  },

  async mounted() {
    await this.fetchMe();
    await Promise.all([this.fetchStats(), this.fetchUsers()]);
    await this.fetchMunicipalities();

    // optional: preload all centers (or keep empty until a municipality is selected)
    // await this.fetchCenters();
  },

  methods: {
    fullName(u) {
      const fn = (u.first_name || "").trim();
      const ln = (u.last_name || "").trim();
      const name = `${fn} ${ln}`.trim();
      return name || "-";
    },

    async fetchMe() {
      const res = await api.get("users/me/");
      this.me = res.data;
    },

    async fetchStats() {
      try {
        const res = await api.get("users/stats/");
        this.stats = res.data;
      } catch {
        this.stats = {};
      }
    },

    async fetchUsers(page = this.pagination.page) {
      this.loading = true;
      try {
        const pageNum = Number(page) || 1;
        const params = new URLSearchParams();

        if (this.filters.search) params.append("search", this.filters.search);
        if (this.filters.role) params.append("role", this.filters.role);
        if (this.filters.is_active !== "")
          params.append("is_active", this.filters.is_active);

        params.append("page", pageNum);
        params.append("page_size", this.pagination.page_size);

        const res = await api.get(`users/?${params.toString()}`);
        const data = res.data;

        this.users = data.results || [];
        this.pagination.count = data.count || 0;
        this.pagination.next = data.next;
        this.pagination.previous = data.previous;
        this.pagination.page = pageNum;
      } finally {
        this.loading = false;
      }
    },

    // ✅ dropdown fetchers (works whether paginated or not)
    async fetchMunicipalities() {
      this.dropdownLoading.municipalities = true;
      try {
        const res = await api.get("municipalities/", { params: { page_size: 9999 } });
        const data = res.data;
        this.municipalities = Array.isArray(data) ? data : (data.results || []);
      } finally {
        this.dropdownLoading.municipalities = false;
      }
    },

    async fetchCenters(municipalityId = null) {
      this.dropdownLoading.centers = true;
      try {
        const params = {};
        if (municipalityId) params.municipality = municipalityId;

        const res = await api.get("evac_centers/evacuation-centers/", { params: { page_size: 9999 } });
        const data = res.data;

        // ✅ store in centers (NOT evacCenters)
        this.centers = Array.isArray(data) ? data : (data.results || []);
      } finally {
        this.dropdownLoading.centers = false;
      }
    },

    async onMunicipalityChanged() {
      await this.fetchCenters(this.edit.form.municipality);
      this.edit.form.assigned_center = null;
    },

    // RBAC helpers
    isProvincial() {
      return this.me.role === "PROVINCIAL_ADMIN";
    },
    isMunicipalOrHigher() {
      return ["PROVINCIAL_ADMIN", "MUNICIPAL_ADMIN"].includes(this.me.role);
    },
    isStaffOrHigher() {
      return ["PROVINCIAL_ADMIN", "MUNICIPAL_ADMIN", "RESPONSE_TEAM", "EVAC_CENTER_STAFF"].includes(this.me.role);
    },
    canDeleteUser() {
      return this.isProvincial();
    },
    canEditUser(targetUser) {
      if (!this.isStaffOrHigher()) return false;
      if (this.me.id === targetUser.id) return false;
      return true;
    },
    canChangeRole() {
      return this.isProvincial();
    },
    canAssignMunicipality() {
      return this.isProvincial() || this.me.role === "MUNICIPAL_ADMIN";
    },

    async openEdit(u) {
      this.edit.open = true;
      this.edit.user = u;

      this.edit.form = {
        first_name: u.first_name || "",
        last_name: u.last_name || "",
        contact_number: u.contact_number || "",
        role: u.role || "CITIZEN",
        municipality: u.municipality || null,
        assigned_center: u.assigned_center || null,
      };

      // ✅ load centers for that municipality so the dropdown has items
      await this.fetchCenters(this.edit.form.municipality);
    },

    closeEdit() {
      this.edit.open = false;
      this.edit.user = null;
    },

    async saveEdit() {
      if (!this.edit.user) return;

      const payload = {
        first_name: this.edit.form.first_name,
        last_name: this.edit.form.last_name,
        contact_number: this.edit.form.contact_number,
      };

      if (this.canChangeRole()) payload.role = this.edit.form.role;
      if (this.canAssignMunicipality()) payload.municipality = this.edit.form.municipality;

      if (this.edit.form.role === "EVAC_CENTER_STAFF") {
        payload.assigned_center = this.edit.form.assigned_center ?? null;
      } else {
        payload.assigned_center = null;
      }

      await api.patch(`users/${this.edit.user.id}/`, payload);
      this.closeEdit();
      await Promise.all([this.fetchUsers(), this.fetchStats()]);
    },

    async toggleActive(u) {
      const next = !u.is_active;
      await api.patch(`users/${u.id}/`, { is_active: next });
      await Promise.all([this.fetchUsers(), this.fetchStats()]);
    },

    async resetPassword(u) {
      const temp = prompt(`Set a temporary password for ${u.email}:`);
      if (!temp) return;
      await api.patch(`users/${u.id}/`, { password: temp });
      alert("Password reset successfully.");
    },

    async deleteUser(u) {
      if (!this.canDeleteUser()) return;
      const ok = confirm(`Delete user ${u.email}? This cannot be undone.`);
      if (!ok) return;
      await api.delete(`users/${u.id}/`);
      await Promise.all([this.fetchUsers(), this.fetchStats()]);
    },
  },
};
</script>


<style scoped>
.user-management {
  padding: 20px;
  color: white;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h1 {
  color: white;
  margin-bottom: 10px;
}

.page-header p {
  color: #888;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: rgba(30, 30, 40, 0.8);
  padding: 20px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.stat-card h3 {
  color: #888;
  font-size: 14px;
  margin-bottom: 10px;
}

.stat-number {
  color: #0096ff;
  font-size: 24px;
  font-weight: bold;
  margin: 0;
}

.users-table h3 {
  color: white;
  margin-bottom: 15px;
}

.table-container {
  background: rgba(30, 30, 40, 0.8);
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 15px;
  text-align: left;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

th {
  background: rgba(40, 40, 50, 0.8);
  color: #0096ff;
  font-weight: 600;
}

td {
  color: #ddd;
}

.status.active {
  background: rgba(0, 204, 102, 0.2);
  color: #00cc66;
  padding: 5px 10px;
  border-radius: 15px;
  font-size: 12px;
}

.btn-edit, .btn-delete {
  padding: 6px 12px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  margin-right: 5px;
  font-size: 12px;
}

.btn-edit {
  background: rgba(0, 150, 255, 0.2);
  color: #0096ff;
}

.btn-delete {
  background: rgba(255, 68, 68, 0.2);
  color: #ff4444;
}

.btn-edit:hover {
  background: #0096ff;
  color: white;
}

.btn-delete:hover {
  background: #ff4444;
  color: white;
}
</style>