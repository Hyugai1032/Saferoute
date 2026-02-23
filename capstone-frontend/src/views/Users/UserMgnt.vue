<template>
  <div class="user-management">
    <!-- Header -->
    <div class="page-header">
      <div class="title-wrap">
        <h1>User Management</h1>
        <p>Manage system users and permissions</p>
      </div>
    </div>

    <div class="content">
      <!-- STATS -->
      <div class="stats-cards">
        <div class="stat-card">
          <div class="stat-top">
            <span class="stat-label">Total Users</span>
            <span class="stat-dot"></span>
          </div>
          <p class="stat-number">{{ stats.total_users ?? "-" }}</p>
          <p class="stat-hint">All registered accounts</p>
        </div>

        <div class="stat-card">
          <div class="stat-top">
            <span class="stat-label">Active Users</span>
            <span class="stat-dot blue"></span>
          </div>
          <p class="stat-number">{{ stats.active_users ?? "-" }}</p>
          <p class="stat-hint">Currently enabled</p>
        </div>

        <div class="stat-card">
          <div class="stat-top">
            <span class="stat-label">Citizens</span>
            <span class="stat-dot green"></span>
          </div>
          <p class="stat-number">{{ stats.by_role?.citizen ?? "-" }}</p>
          <p class="stat-hint">Citizen accounts</p>
        </div>
      </div>

      <!-- FILTER BAR (sticky) -->
      <div class="filters">
        <div class="filters-left">
          <div class="search">
            <span class="search-ico">🔎</span>
            <input
              v-model="filters.search"
              placeholder="Search name, email, or contact..."
              @keyup.enter="fetchUsers"
            />
          </div>

          <select v-model="filters.role" @change="fetchUsers">
            <option value="">All roles</option>
            <option value="PROVINCIAL_ADMIN">Provincial Admin</option>
            <option value="MUNICIPAL_ADMIN">Municipal Admin</option>
            <option value="RESPONSE_TEAM">Response Team</option>
            <option value="EVAC_CENTER_STAFF">Evac Center Staff</option>
            <option value="CITIZEN">Citizen</option>
          </select>

          <select v-model="filters.is_active" @change="fetchUsers">
            <option value="">All status</option>
            <option :value="true">Active</option>
            <option :value="false">Inactive</option>
          </select>

          <button @click="fetchUsers(1)" style="padding:8px 12px;">Refresh</button>
        </div>

        <div class="filters-right">
          <div class="me-pill">
            <span class="me-ico">👤</span>
            <div class="me-meta">
              <div class="me-email">{{ me.email || "-" }}</div>
              <div class="me-role">{{ me.role || "-" }}</div>
            </div>
          </div>
        </div>
      

      <!-- TABLE -->
      <div class="users-table">
        <div class="table-head">
          <h3>Registered Users</h3>
          <div class="table-sub">
            <span class="chip">{{ users.length }} shown</span>
          </div>
        </div>

        <div class="table-container">
          <div v-if="loading" class="loading">
            <div class="skeleton-row" v-for="n in 5" :key="n"></div>
          </div>

          <table v-else>
            <thead>
              <tr>
                <th>User</th>
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
                  <div class="user-cell">
                    <div class="avatar" :class="{ dim: !u.is_active }">
                      {{ initials(u) }}
                    </div>

                    <div class="user-meta">
                      <div class="user-name">{{ fullName(u) }}</div>
                      <div class="user-email">{{ u.email }}</div>
                      <div v-if="u.contact_number" class="user-contact">
                        {{ u.contact_number }}
                      </div>
                    </div>
                  </div>
                </td>

                <!-- ROLE -->
                <td>
                  <span class="pill role" :class="roleClass(u.role)">
                    {{ u.role }}
                  </span>
                </td>
                <td>{{ u.assigned_center_name || "-" }}</td>

                <td class="muted">{{ u.municipality_name || "-" }}</td>

                <!-- STATUS -->
                <td>
                  <span class="pill status" :class="u.is_active ? 'active' : 'inactive'">
                    <span class="dot" :class="u.is_active ? 'g' : 'r'"></span>
                    {{ u.is_active ? "Active" : "Inactive" }}
                  </span>
                </td>

                <!-- ACTIONS -->
                <td>
                  <div class="actions">
                    <button class="a-btn" @click="openEdit(u)" :disabled="!canEditUser(u)" title="Edit">
                      ✎ <span>Edit</span>
                    </button>

                    <button class="a-btn" @click="toggleActive(u)" :disabled="!canEditUser(u)" title="Toggle active">
                      {{ u.is_active ? "⛔" : "✅" }} <span>{{ u.is_active ? "Deactivate" : "Activate" }}</span>
                    </button>

                    <button class="a-btn" @click="resetPassword(u)" :disabled="!canEditUser(u)" title="Reset password">
                      🔑 <span>Reset PW</span>
                    </button>

                    <button class="a-btn danger" @click="deleteUser(u)" :disabled="!canDeleteUser()" title="Delete">
                      🗑 <span>Delete</span>
                    </button>
                  </div>
                </td>
              </tr>

              <tr v-if="users.length === 0">
                <td colspan="5" class="empty">
                  <div class="empty-box">
                    <div class="empty-ico">🧾</div>
                    <div class="empty-title">No users found</div>
                    <div class="empty-text">Try changing filters or searching a different keyword.</div>
                    <button class="btn ghost" @click="() => { filters.search=''; filters.role=''; filters.is_active=''; fetchUsers(); }">
                      Clear filters
                    </button>
                  </div>
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

          <div class="modal-body">
            <div class="form-grid">
              <div class="field">
                <label>First name</label>
                <input v-model="edit.form.first_name" placeholder="First name" />
              </div>

              <div class="field">
                <label>Last name</label>
                <input v-model="edit.form.last_name" placeholder="Last name" />
              </div>

              <div class="field">
                <label>Contact number</label>
                <input v-model="edit.form.contact_number" placeholder="Contact number" />
              </div>

              <div class="field">
                <label>Role</label>
                <select v-model="edit.form.role" :disabled="!canChangeRole()">
                  <option value="PROVINCIAL_ADMIN">PROVINCIAL_ADMIN</option>
                  <option value="MUNICIPAL_ADMIN">MUNICIPAL_ADMIN</option>
                  <option value="RESPONSE_TEAM">RESPONSE_TEAM</option>
                  <option value="EVAC_CENTER_STAFF">EVAC_CENTER_STAFF</option>
                  <option value="CITIZEN">CITIZEN</option>
                </select>
              </div>

              <div class="field">
                <label>Municipality ID</label>
                <input
                  v-model.number="edit.form.municipality"
                  placeholder="Municipality ID"
                  :disabled="!canAssignMunicipality()"
                />
              </div>
            </div>
          </div>

          <div class="modal-actions">
            <button class="btn ghost" @click="closeEdit">Cancel</button>
            <button class="btn primary" @click="saveEdit">Save changes</button>
          </div>
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

    initials(u) {
  const name = this.fullName(u);
  if (!name || name === "-") return "??";
  const parts = name.split(" ").filter(Boolean);
  const a = parts[0]?.[0] || "?";
  const b = parts[1]?.[0] || (parts[0]?.[1] || "");
  return (a + b).toUpperCase();
},
roleClass(role) {
  const map = {
    PROVINCIAL_ADMIN: "prov",
    MUNICIPAL_ADMIN: "muni",
    RESPONSE_TEAM: "resp",
    EVAC_CENTER_STAFF: "evac",
    CITIZEN: "cit",
  };
  return map[role] || "cit";
},


    async fetchMe() {
      try {
        const res = await api.get("users/me/");
        this.me = res.data || {};
      } catch {
        this.me = {};
      }
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
.user-management{
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
  justify-content:space-between;
  align-items:flex-end;
  margin-bottom:14px;
}
.title-wrap h1{ margin:0; font-size:1.6rem; color:#f8fafc; letter-spacing:.2px;}
.title-wrap p{ margin:6px 0 0; color:var(--muted); font-size:13px; }

.content{
  display: flex;
  flex-direction: column;
  gap: 14px;
}


/* ===== STATS ===== */
.stats-cards{
  display:grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap:12px;
}
.stat-card{
  position:relative;
  border-radius:16px;
  padding:16px;
  background:
    radial-gradient(1200px 500px at 20% -20%, rgba(56,189,248,.25), transparent 50%),
    radial-gradient(900px 400px at 110% 20%, rgba(37,99,235,.18), transparent 55%),
    linear-gradient(180deg, rgba(10,14,28,.72), rgba(6,9,18,.82));
  border:1px solid var(--border);
  box-shadow: 0 18px 40px rgba(0,0,0,.45);
  overflow:hidden;
}
.stat-top{ display:flex; align-items:center; justify-content:space-between; margin-bottom:10px; }
.stat-label{ font-size:12px; text-transform:uppercase; letter-spacing:.7px; color:rgba(229,231,235,.65); font-weight:700; }
.stat-dot{ width:10px; height:10px; border-radius:999px; background:rgba(255,255,255,.25); box-shadow:0 0 0 6px rgba(255,255,255,.04);}
.stat-dot.blue{ background:var(--blue); box-shadow:0 0 0 6px rgba(56,189,248,.10);}
.stat-dot.green{ background:var(--green); box-shadow:0 0 0 6px rgba(34,197,94,.10);}

.stat-number{ margin:0; font-size:30px; font-weight:900; color:#dbeafe; letter-spacing:.2px;}
.stat-hint{ margin:6px 0 0; font-size:12px; color:rgba(229,231,235,.45); }

/* ===== FILTERS (sticky) ===== */
.filters{
  position: sticky;
  top: 12px;
  z-index: 5;
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:12px;
  padding:12px;
  border-radius:16px;
  border:1px solid var(--border2);
  background:
    linear-gradient(180deg, rgba(10,14,28,.72), rgba(8,12,24,.78));
  box-shadow: 0 16px 34px rgba(0,0,0,.42);
  backdrop-filter: blur(10px);
}
.filters-left{ display:flex; gap:10px; align-items:center; flex-wrap:wrap;}
.search{
  display:flex; align-items:center; gap:10px;
  padding: 10px 12px;
  border-radius:14px;
  border:1px solid rgba(56,189,248,.18);
  background: rgba(2,6,23,.55);
  min-width: 340px;
}
.search-ico{ opacity:.85; }
.search input{
  border:none; outline:none; background:transparent; color:var(--text);
  width: 100%;
  font-size: 13px;
}
select{
  border:1px solid rgba(56,189,248,.18);
  background: rgba(2,6,23,.55);
  color: var(--text);
  border-radius:14px;
  padding: 10px 12px;
  font-size: 13px;
  outline:none;
}
select:focus, .search:focus-within{
  border-color: rgba(56,189,248,.45);
  box-shadow:0 0 0 4px rgba(56,189,248,.12);
}

.me-pill{
  display:flex; align-items:center; gap:10px;
  padding:10px 12px;
  border-radius:16px;
  border:1px solid rgba(56,189,248,.14);
  background: rgba(2,6,23,.45);
}
.me-ico{ opacity:.9; }
.me-email{ font-size:12.5px; font-weight:800; color:#e0f2fe; }
.me-role{ font-size:11.5px; color:rgba(229,231,235,.55); }

/* ===== BUTTONS ===== */
.btn{
  border-radius:14px;
  padding: 10px 14px;
  font-size: 13px;
  font-weight: 900;
  border: 1px solid rgba(56,189,248,.22);
  cursor:pointer;
  transition: transform .12s ease, box-shadow .12s ease, background .12s ease, border-color .12s ease;
  display:inline-flex; align-items:center; gap:8px;
}
.btn-ico{ opacity:.95; }
.btn.primary{
  color:#06121f;
  background: linear-gradient(135deg, rgba(56,189,248,1), rgba(37,99,235,1));
  border-color: rgba(56,189,248,.45);
  box-shadow: 0 18px 40px rgba(37,99,235,.28);
}
.btn.primary:hover{ transform: translateY(-1px); box-shadow: 0 22px 48px rgba(37,99,235,.38); }
.btn.ghost{
  background: rgba(56,189,248,.10);
  color:#cdefff;
}
.btn.ghost:hover{ transform: translateY(-1px); background: rgba(56,189,248,.16); }

/* ===== TABLE ===== */
.users-table{ margin-top:2px; }
.table-head{
  display:flex;
  justify-content:space-between;
  align-items:center;
  margin: 4px 2px 10px;
}
.users-table h3{ margin:0; color:#f8fafc; font-size: 1.05rem; }
.table-sub .chip{
  padding:6px 10px;
  border-radius:999px;
  border:1px solid rgba(56,189,248,.18);
  background: rgba(56,189,248,.10);
  color:#bfe9ff;
  font-size:12px;
  font-weight:800;
}

.table-container{
  border-radius:18px;
  overflow:hidden;
  border:1px solid var(--border2);
  background: var(--panel2);
  box-shadow: 0 20px 48px rgba(0,0,0,.48);
}
table{ width:100%; border-collapse:collapse; }
th, td{
  padding: 14px 14px;
  border-bottom:1px solid rgba(255,255,255,.06);
  vertical-align: middle;
}
th{
  background: rgba(5,8,18,.85);
  color: rgba(56,189,248,.95);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: .7px;
  font-weight: 900;
}
td{ font-size: 13.5px; color: rgba(229,231,235,.88); }
tbody tr{ transition: background .12s ease; }
tbody tr:hover{ background: rgba(56,189,248,.08); }
.muted{ color: rgba(229,231,235,.60); }

/* user cell */
.user-cell{ display:flex; align-items:center; gap:12px; }
.avatar{
  width:40px; height:40px;
  border-radius:14px;
  display:flex; align-items:center; justify-content:center;
  font-weight: 1000;
  color: #06121f;
  background: linear-gradient(135deg, rgba(56,189,248,1), rgba(37,99,235,1));
  box-shadow: 0 14px 34px rgba(37,99,235,.22);
}
.avatar.dim{ opacity:.65; }
.user-name{ font-weight: 900; color:#f8fafc; }
.user-email{ color: rgba(229,231,235,.62); font-size: 12.5px; margin-top:2px; }
.user-contact{ color: rgba(229,231,235,.45); font-size: 12px; margin-top:3px; }

/* pills */
.pill{
  display:inline-flex; align-items:center; gap:8px;
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 1000;
  border:1px solid rgba(255,255,255,.08);
}
.pill .dot{ width:8px; height:8px; border-radius:999px; }
.pill .dot.g{ background: var(--green); }
.pill .dot.r{ background: var(--red); }

.pill.status.active{ background: rgba(34,197,94,.14); color:#86efac; border-color: rgba(34,197,94,.22); }
.pill.status.inactive{ background: rgba(239,68,68,.12); color:#fecaca; border-color: rgba(239,68,68,.22); }

/* role colors */
.pill.role{ background: rgba(56,189,248,.10); border-color: rgba(56,189,248,.18); color:#bfe9ff; }
.pill.role.prov{ background: rgba(37,99,235,.16); border-color: rgba(37,99,235,.28); color:#c7d2fe; }
.pill.role.muni{ background: rgba(56,189,248,.12); border-color: rgba(56,189,248,.22); color:#bfe9ff; }
.pill.role.resp{ background: rgba(245,158,11,.14); border-color: rgba(245,158,11,.22); color:#fde68a; }
.pill.role.evac{ background: rgba(34,197,94,.12); border-color: rgba(34,197,94,.20); color:#bbf7d0; }
.pill.role.cit{ background: rgba(148,163,184,.12); border-color: rgba(148,163,184,.20); color:#e2e8f0; }

/* actions */
.actions{ display:flex; gap:8px; flex-wrap:wrap; }
.a-btn{
  padding: 8px 10px;
  border-radius: 12px;
  background: rgba(37,99,235,.14);
  border: 1px solid rgba(37,99,235,.22);
  color: #c7d2fe;
  font-size: 12px;
  font-weight: 1000;
  cursor:pointer;
  transition: transform .12s ease, background .12s ease, border-color .12s ease;
  display:inline-flex; align-items:center; gap:8px;
}
.a-btn span{ font-weight: 900; }
.a-btn:hover:not(:disabled){ transform: translateY(-1px); background: rgba(37,99,235,.26); border-color: rgba(37,99,235,.40); }
.a-btn:disabled{ opacity:.45; cursor:not-allowed; transform:none; }
.a-btn.danger{
  background: rgba(239,68,68,.12);
  border-color: rgba(239,68,68,.22);
  color: #fecaca;
}
.a-btn.danger:hover:not(:disabled){ background: rgba(239,68,68,.24); border-color: rgba(239,68,68,.42); }

/* loading skeleton */
.loading{ padding: 14px; }
.skeleton-row{
  height: 46px;
  border-radius: 12px;
  margin-bottom: 10px;
  background: linear-gradient(90deg, rgba(255,255,255,.04), rgba(56,189,248,.08), rgba(255,255,255,.04));
  background-size: 200% 100%;
  animation: shimmer 1.2s infinite linear;
}
@keyframes shimmer{
  0%{ background-position: 0% 0; }
  100%{ background-position: 200% 0; }
}

/* empty state */
.empty{ padding: 18px; text-align:center; }
.empty-box{ padding: 18px; border-radius: 18px; border:1px dashed rgba(56,189,248,.22); background: rgba(2,6,23,.40); }
.empty-ico{ font-size: 26px; opacity:.9; }
.empty-title{ margin-top: 6px; font-weight: 1000; color:#e0f2fe; }
.empty-text{ margin-top: 6px; color: rgba(229,231,235,.55); font-size: 12.5px; }

/* modal */
.modal-backdrop{
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,.55);
  display:flex;
  align-items:center;
  justify-content:center;
  padding: 18px;
  z-index: 50;
}
.modal{
  width: min(860px, 96vw);
  border-radius: 18px;
  border: 1px solid rgba(56,189,248,.16);
  background:
    radial-gradient(1200px 520px at 20% -20%, rgba(56,189,248,.22), transparent 55%),
    linear-gradient(180deg, rgba(10,14,28,.92), rgba(6,9,18,.92));
  box-shadow: 0 30px 80px rgba(0,0,0,.62);
  overflow:hidden;
}
.modal-head{
  display:flex;
  align-items:flex-start;
  justify-content:space-between;
  padding: 14px 14px 10px;
  border-bottom: 1px solid rgba(255,255,255,.06);
}
.modal-title{ font-weight: 1000; color:#f8fafc; }
.modal-sub{ margin-top:4px; font-size: 12.5px; color: rgba(229,231,235,.55); }
.icon-btn{
  width: 40px; height: 40px;
  border-radius: 14px;
  border: 1px solid rgba(56,189,248,.16);
  background: rgba(2,6,23,.35);
  color: #bfe9ff;
  cursor:pointer;
}
.icon-btn:hover{ background: rgba(56,189,248,.12); }

.modal-body{ padding: 14px; }
.form-grid{
  display:grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}
.field{ display:flex; flex-direction:column; gap:8px; }
.field label{ font-size: 12px; color: rgba(229,231,235,.55); font-weight: 900; letter-spacing:.2px; }
.field input, .field select{
  border:1px solid rgba(56,189,248,.18);
  background: rgba(2,6,23,.55);
  color: var(--text);
  border-radius: 14px;
  padding: 10px 12px;
  font-size: 13px;
  outline:none;
}
.field input:focus, .field select:focus{
  border-color: rgba(56,189,248,.45);
  box-shadow:0 0 0 4px rgba(56,189,248,.12);
}

.modal-actions{
  display:flex;
  justify-content:flex-end;
  gap: 10px;
  padding: 12px 14px 14px;
  border-top: 1px solid rgba(255,255,255,.06);
}

@media (max-width: 900px){
  .stats-cards{ grid-template-columns: 1fr; }
  .search{ min-width: 100%; }
  .filters{ position: static; }
  .form-grid{ grid-template-columns: 1fr; }
}
</style>
