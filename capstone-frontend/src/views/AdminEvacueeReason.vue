<template>
  <div class="dashboard-container">
    <div class="main-content">
 
      <div class="dashboard-header">
        <div class="header-info">
          <h1>Evacuation Reasons</h1>
          <p>Manage the list of reasons staff can select when registering an evacuee</p>
        </div>
      </div>
 
      <div class="content-grid single">
        <div class="content-panel large">
          <div class="panel-header">
            <h3>📋 Reasons</h3>
            <div class="panel-actions">
              <button class="btn-secondary" @click="fetchReasons" :disabled="loading">
                {{ loading ? "Refreshing…" : "Refresh" }}
              </button>
              <button class="btn-primary" @click="openCreateModal">+ Add Reason</button>
            </div>
          </div>
 
          <p v-if="error" class="error-text">{{ error }}</p>
          <p v-if="actionError" class="error-text">{{ actionError }}</p>
 
          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Status</th>
                  <th>Evacuees Assigned</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="loading && !reasons.length">
                  <td colspan="4">Loading…</td>
                </tr>
                <tr v-else-if="!reasons.length">
                  <td colspan="4">No evacuation reasons yet. Add one to get started.</td>
                </tr>
                <tr v-for="reason in reasons" :key="reason.id">
                  <td>{{ reason.name }}</td>
                  <td>
                    <span
                      class="status-badge"
                      :class="reason.is_active ? 'stable' : 'pending'"
                    >
                      {{ reason.is_active ? "Active" : "Inactive" }}
                    </span>
                  </td>
                  <td>{{ reason.evacuee_count }}</td>
                  <td>
                    <div class="action-buttons">
                      <button
                        class="btn-icon"
                        title="Edit"
                        @click="openEditModal(reason)"
                      >
                        ✏️
                      </button>
                      <button
                        class="btn-icon"
                        :title="reason.is_active ? 'Deactivate' : 'Activate'"
                        @click="toggleActive(reason)"
                        :disabled="togglingId === reason.id"
                      >
                        {{ reason.is_active ? "🚫" : "✅" }}
                      </button>
                      <button
                        class="btn-icon"
                        title="Delete"
                        @click="confirmDelete(reason)"
                        :disabled="deletingId === reason.id"
                      >
                        🗑️
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
 
    <!-- Create / Edit Modal -->
    <div v-if="modal.open" class="modal-backdrop" @click.self="closeModal">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ modal.mode === "create" ? "Add Evacuation Reason" : "Edit Evacuation Reason" }}</h3>
          <button class="close-btn" @click="closeModal">&times;</button>
        </div>
 
        <p v-if="modalError" class="error-text">{{ modalError }}</p>
 
        <form @submit.prevent="saveReason">
          <label class="full">
            Name
            <input
              v-model="modal.form.name"
              type="text"
              placeholder="e.g. Typhoon, Flood, Armed Conflict"
              required
              maxlength="100"
            />
          </label>
 
          <label class="check-label full">
            <input v-model="modal.form.is_active" type="checkbox" />
            Active (visible in the staff dropdown)
          </label>
 
          <div class="modal-actions">
            <button type="button" class="btn-secondary" @click="closeModal">Cancel</button>
            <button type="submit" class="btn-primary" :disabled="saving">
              {{ saving ? "Saving…" : "Save" }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
 
<script setup>
import { ref, onMounted } from "vue";
 
const API_BASE = import.meta.env.VITE_API_BASE_URL
 
const reasons = ref([])
const loading = ref(false)
const error = ref("")
const actionError = ref("")
const saving = ref(false)
const togglingId = ref(null)
const deletingId = ref(null)
 
const modal = ref({
  open: false,
  mode: "create",
  id: null,
  form: emptyForm(),
  error: "",
})
const modalError = ref("")
 
function emptyForm() {
  return {
    name: "",
    is_active: true,
  }
}
 
const getAuthHeaders = () => {
  const token = localStorage.getItem("access_token")
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  }
}
 
const fetchReasons = async () => {
  loading.value = true
  error.value = ""
 
  try {
    const response = await fetch(`${API_BASE}evac_centers/evacuation-reasons/`, {
      method: "GET",
      headers: getAuthHeaders(),
    })
 
    if (!response.ok) {
      throw new Error(`Failed to load reasons: ${response.status}`)
    }
 
    const data = await response.json()
    reasons.value = Array.isArray(data) ? data : data.results || []
  } catch (err) {
    console.error("Fetch evacuation reasons error:", err)
    error.value = err.message || "Failed to load evacuation reasons."
  } finally {
    loading.value = false
  }
}
 
const openCreateModal = () => {
  modal.value = {
    open: true,
    mode: "create",
    id: null,
    form: emptyForm(),
  }
  modalError.value = ""
}
 
const openEditModal = (reason) => {
  modal.value = {
    open: true,
    mode: "edit",
    id: reason.id,
    form: {
      name: reason.name,
      is_active: reason.is_active,
    },
  }
  modalError.value = ""
}
 
const closeModal = () => {
  modal.value.open = false
  modalError.value = ""
}
 
const saveReason = async () => {
  saving.value = true
  modalError.value = ""
 
  const isEdit = modal.value.mode === "edit"
  const url = isEdit
    ? `${API_BASE}evac_centers/evacuation-reasons/${modal.value.id}/`
    : `${API_BASE}evac_centers/evacuation-reasons/`
 
  try {
    const response = await fetch(url, {
      method: isEdit ? "PATCH" : "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify(modal.value.form),
    })
 
    if (!response.ok) {
      const body = await response.json().catch(() => ({}))
      const message =
        body.name?.[0] || body.detail || `Failed to save (${response.status}).`
      throw new Error(message)
    }
 
    closeModal()
    await fetchReasons()
  } catch (err) {
    console.error("Save evacuation reason error:", err)
    modalError.value = err.message || "Failed to save evacuation reason."
  } finally {
    saving.value = false
  }
}
 
const toggleActive = async (reason) => {
  togglingId.value = reason.id
  actionError.value = ""
 
  try {
    const response = await fetch(
      `${API_BASE}evac_centers/evacuation-reasons/${reason.id}/`,
      {
        method: "PATCH",
        headers: getAuthHeaders(),
        body: JSON.stringify({ is_active: !reason.is_active }),
      }
    )
 
    if (!response.ok) {
      throw new Error(`Failed to update status (${response.status}).`)
    }
 
    await fetchReasons()
  } catch (err) {
    console.error("Toggle active error:", err)
    actionError.value = err.message || "Failed to update status."
  } finally {
    togglingId.value = null
  }
}
 
const confirmDelete = async (reason) => {
  if (!window.confirm(`Delete "${reason.name}"? This can't be undone.`)) {
    return
  }
 
  deletingId.value = reason.id
  actionError.value = ""
 
  try {
    const response = await fetch(
      `${API_BASE}evac_centers/evacuation-reasons/${reason.id}/`,
      {
        method: "DELETE",
        headers: getAuthHeaders(),
      }
    )
 
    if (!response.ok) {
      const body = await response.json().catch(() => ({}))
      throw new Error(body.detail || `Failed to delete (${response.status}).`)
    }
 
    await fetchReasons()
  } catch (err) {
    console.error("Delete evacuation reason error:", err)
    actionError.value = err.message || "Failed to delete evacuation reason."
  } finally {
    deletingId.value = null
  }
}
 
onMounted(() => {
  fetchReasons()
})
</script>
 
<style scoped>
.dashboard-container {
  min-height: 100vh;
  background: #0f172a;
}
 
.main-content {
  padding: 2rem;
  max-width: 1100px;
  margin: 0 auto;
}
 
.dashboard-header {
  margin-bottom: 1.5rem;
}
 
.header-info h1 {
  margin: 0;
  color: #f1f5f9;
  font-size: 1.75rem;
}
 
.header-info p {
  margin: 0.25rem 0 0;
  color: #94a3b8;
}
 
.content-grid.single {
  display: block;
}
 
.content-panel {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 1.5rem;
}
 
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
  gap: 1rem;
  flex-wrap: wrap;
}
 
.panel-header h3 {
  margin: 0;
  color: #f1f5f9;
  font-size: 1.25rem;
}
 
.panel-actions {
  display: flex;
  gap: 0.75rem;
}
 
.btn-primary,
.btn-secondary {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s;
}
 
.btn-primary {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: white;
}
 
.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: #cbd5e1;
  border: 1px solid rgba(255, 255, 255, 0.2);
}
 
.btn-primary:hover,
.btn-secondary:hover {
  transform: translateY(-1px);
}
 
.btn-primary:disabled,
.btn-secondary:disabled,
.btn-icon:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}
 
.table-container {
  overflow-x: auto;
}
 
.data-table {
  width: 100%;
  border-collapse: collapse;
}
 
.data-table th {
  background: rgba(255, 255, 255, 0.05);
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #94a3b8;
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
 
.data-table td {
  padding: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  color: #cbd5e1;
}
 
.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
}
 
.status-badge.stable {
  background: rgba(16, 185, 129, 0.2);
  color: #6ee7b7;
  border: 1px solid rgba(16, 185, 129, 0.3);
}
 
.status-badge.pending {
  background: rgba(100, 116, 139, 0.2);
  color: #cbd5e1;
  border: 1px solid rgba(100, 116, 139, 0.3);
}
 
.action-buttons {
  display: flex;
  gap: 0.5rem;
}
 
.btn-icon {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 0.5rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
}
 
.btn-icon:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.1);
}
 
.error-text {
  color: #fca5a5;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  font-size: 0.875rem;
}
 
/* Modal */
.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 50;
  background: rgba(15, 23, 42, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 18px;
}
 
.modal {
  width: min(480px, 100%);
  background: #1e293b;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 18px;
  padding: 1.5rem;
  box-shadow: 0 25px 60px rgba(15, 23, 42, 0.5);
}
 
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 1rem;
}
 
.modal-header h3 {
  margin: 0;
  color: #f1f5f9;
}
 
.close-btn {
  width: 36px;
  height: 36px;
  border: 0;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.1);
  color: #cbd5e1;
  font-size: 1.5rem;
  cursor: pointer;
}
 
.modal label.full {
  display: block;
  margin-bottom: 1rem;
  color: #cbd5e1;
  font-size: 0.875rem;
  font-weight: 600;
}
 
.modal label.full input[type="text"] {
  display: block;
  width: 100%;
  margin-top: 0.4rem;
  padding: 0.6rem 0.75rem;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.05);
  color: #f1f5f9;
  font-size: 0.95rem;
}
 
.check-label {
  display: flex !important;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500 !important;
}
 
.check-label input[type="checkbox"] {
  width: 16px;
  height: 16px;
}
 
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.25rem;
}
</style>