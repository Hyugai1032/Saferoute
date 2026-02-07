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

        <button @click="fetchUsers" style="padding:8px 12px;">Refresh</button>

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
                <th style="width: 260px;">Actions</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="u in users" :key="u.id">
                <td>{{ fullName(u) }}</td>
                <td>{{ u.email }}</td>
                <td>{{ u.role }}</td>
                <td>{{ u.municipality_name || "-" }}</td>
                <td>
                  <span class="status" :class="u.is_active ? 'active' : 'inactive'">
                    {{ u.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>

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

          <input
            v-model.number="edit.form.municipality"
            placeholder="Municipality ID"
            style="padding:8px; width:160px;"
            :disabled="!canAssignMunicipality()"
          />
        </div>

        <div style="display:flex; gap:8px; margin-top:10px;">
          <button class="btn-edit" @click="saveEdit">Save</button>
          <button class="btn-delete" @click="closeEdit">Cancel</button>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import api from "../../services/api"; // uses your api.js (JWT + refresh) :contentReference[oaicite:2]{index=2}

export default {
  name: "UserMgnt",
  data() {
    return {
      loading: false,
      users: [],
      stats: {},
      me: {},

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
        },
      },
    };
  },
  async mounted() {
    await this.fetchMe();
    await Promise.all([this.fetchStats(), this.fetchUsers()]);
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
      // If stats is restricted by role, handle errors gracefully
      try {
        const res = await api.get("users/stats/");
        this.stats = res.data;
      } catch {
        this.stats = {};
      }
    },

    async fetchUsers() {
      this.loading = true;
      try {
        const params = {};
        if (this.filters.search) params.search = this.filters.search;
        if (this.filters.role) params.role = this.filters.role;
        if (this.filters.is_active !== "" && this.filters.is_active !== null)
          params.is_active = this.filters.is_active;

        const res = await api.get("users/", { params });
        this.users = res.data;
      } finally {
        this.loading = false;
      }
    },

    // RBAC helpers (frontend-only convenience; backend still enforces)
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
      // backend already scopes list; this is just UI gating
      if (!this.isStaffOrHigher()) return false;
      if (this.me.id === targetUser.id) return false; // prevent editing self here (use /me)
      return true;
    },
    canChangeRole() {
      // safest: only provincial can assign roles
      return this.isProvincial();
    },
    canAssignMunicipality() {
      return this.isProvincial() || this.me.role === "MUNICIPAL_ADMIN";
    },

    openEdit(u) {
      this.edit.open = true;
      this.edit.user = u;
      this.edit.form = {
        first_name: u.first_name || "",
        last_name: u.last_name || "",
        contact_number: u.contact_number || "",
        role: u.role || "CITIZEN",
        municipality: u.municipality || null, // expects id
      };
    },
    closeEdit() {
      this.edit.open = false;
      this.edit.user = null;
    },

    async saveEdit() {
      if (!this.edit.user) return;

      // Prepare payload (only send what you allow)
      const payload = {
        first_name: this.edit.form.first_name,
        last_name: this.edit.form.last_name,
        contact_number: this.edit.form.contact_number,
      };

      if (this.canChangeRole()) payload.role = this.edit.form.role;
      if (this.canAssignMunicipality()) payload.municipality = this.edit.form.municipality;

      await api.patch(`users/${this.edit.user.id}/`, payload);
      this.closeEdit();
      await this.fetchUsers();
      await this.fetchStats();
    },

    async toggleActive(u) {
      const next = !u.is_active;
      await api.patch(`users/${u.id}/`, { is_active: next });
      await this.fetchUsers();
      await this.fetchStats();
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
      await this.fetchUsers();
      await this.fetchStats();
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