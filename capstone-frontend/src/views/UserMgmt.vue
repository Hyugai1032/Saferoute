<template>
  <div>
    <h2>User Management</h2>
    <div class="panel" style="margin-top:12px;">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <div><strong>Users</strong><div style="font-size:13px;color:var(--muted)">Manage access & roles</div></div>
        <div><button class="btn">+ Add User</button></div>
      </div>

      <div class="table-wrap" style="margin-top:12px;">
        <table>
          <thead><tr><th>Name</th><th>Email</th><th>Role</th><th>Status</th></tr></thead>
          <tbody>
            <tr><td>Jane Santos</td><td>jane@dswd.gov.ph</td><td>Admin</td><td>Active</td></tr>
            <tr><td>Mark dela Cruz</td><td>mark@dswd.gov.ph</td><td>Staff</td><td>Active</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* === GENERAL PAGE LAYOUT === */
h2 {
  color: #fff;
  margin-bottom: 10px;
}

.panel {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.2);
  color: #fff;
}

/* === BUTTON STYLE === */
.btn {
  background: #3b82f6;
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 8px 16px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}
.btn:hover {
  background: #2563eb;
}

/* === TABLE STYLE === */
.table-wrap {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  color: #fff;
  font-size: 14px;
  min-width: 600px;
}

th, td {
  text-align: left;
  padding: 12px 16px;
}

th {
  background: rgba(255,255,255,0.1);
  font-weight: 600;
}

tbody tr:nth-child(even) {
  background: rgba(255,255,255,0.03);
}

tbody tr:hover {
  background: rgba(255,255,255,0.08);
}

/* === RESPONSIVE DESIGN === */
@media (max-width: 768px) {
  .panel {
    padding: 12px;
  }

  table {
    font-size: 12px;
    min-width: 100%;
  }

  th, td {
    padding: 10px;
  }

  .btn {
    width: 100%;
    padding: 10px;
  }

  h2 {
    font-size: 1.1rem;
  }
}
</style>
