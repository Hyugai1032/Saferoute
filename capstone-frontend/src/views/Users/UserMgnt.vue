<!-- src/views/UserMgnt.vue - Create this file if you need user management -->
<template>
  <div class="user-management">
    <div class="page-header">
      <h1>User Management</h1>
      <p>Manage system users and permissions</p>
    </div>
    
    <div class="content">
      <div class="stats-cards">
        <div class="stat-card">
          <h3>Total Users</h3>
          <p class="stat-number">1,234</p>
        </div>
        <div class="stat-card">
          <h3>Active Today</h3>
          <p class="stat-number">567</p>
        </div>
        <div class="stat-card">
          <h3>New This Week</h3>
          <p class="stat-number">89</p>
        </div>
      </div>

      <div class="users-table">
        <h3>Registered Users</h3>
        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Role</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>John Doe</td>
                <td>john@example.com</td>
                <td>User</td>
                <td><span class="status active">Active</span></td>
                <td>
                  <button class="btn-edit">Edit</button>
                  <button class="btn-delete">Delete</button>
                </td>
              </tr>
              <tr>
                <td>Jane Smith</td>
                <td>jane@example.com</td>
                <td>Admin</td>
                <td><span class="status active">Active</span></td>
                <td>
                  <button class="btn-edit">Edit</button>
                  <button class="btn-delete">Delete</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'UserMgnt'
}
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