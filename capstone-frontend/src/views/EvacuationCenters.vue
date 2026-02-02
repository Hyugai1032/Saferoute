<template>
  <div class="evac-manager">
    <h2>Evacuation Centers Manager</h2>

    <section class="upload">
      <h3>Upload Excel / CSV</h3>
      <input type="file" ref="fileInput" @change="onFileChange" accept=".csv,.xlsx" />
      <button @click="uploadFile" :disabled="!file || uploading">
        {{ uploading ? 'Uploading...' : 'Upload & Import' }}
      </button>
      <div v-if="uploadResult" class="upload-result">
        <p><strong>✅ Upload Complete!</strong></p>
        <p>Inserted: {{ uploadResult.inserted }} | Updated: {{ uploadResult.updated }} | Skipped: {{ uploadResult.skipped || 0 }}</p>
        <div v-if="uploadResult.errors && uploadResult.errors.length > 0">
          <p><strong>Errors ({{ uploadResult.total_errors || uploadResult.errors.length }}):</strong></p>
          <ul>
            <li v-for="(err, idx) in uploadResult.errors" :key="idx">{{ err }}</li>
          </ul>
        </div>
      </div>
    </section>

    <section class="create">
      <h3>Create new center</h3>
      <form @submit.prevent="createCenter">
        <div class="form-group">
          <label>Name *</label>
          <input v-model="form.name" placeholder="Facility Name" required/>
        </div>

        <div class="form-group">
          <label>Municipality *</label>
          <select v-model="form.municipality" required>
            <option value="">-- Select Municipality --</option>
            <option v-for="mun in municipalities" :key="mun.id" :value="mun.id">
              {{ mun.name }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label>Barangay</label>
          <select v-model="form.barangay">
            <option value="">-- Select Barangay --</option>
            <option v-for="brgy in filteredBarangays" :key="brgy.id" :value="brgy.id">
              {{ brgy.name }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label>Fund Source</label>
          <input v-model="form.fund_source" placeholder="BARANGAY, NATIONAL, etc."/>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>Family Capacity</label>
            <input v-model.number="form.family_capacity_max" placeholder="0" type="number" min="0"/>
          </div>

          <div class="form-group">
            <label>Individual Capacity</label>
            <input v-model.number="form.individual_capacity_max" placeholder="0" type="number" min="0"/>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>Latitude</label>
            <input v-model.number="form.latitude" placeholder="13.4117" type="number" step="0.000001"/>
          </div>

          <div class="form-group">
            <label>Longitude</label>
            <input v-model.number="form.longitude" placeholder="121.1803" type="number" step="0.000001"/>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>Flood Susceptibility</label>
            <select v-model="form.flood_susceptibility">
              <option value="LOW">Low</option>
              <option value="MEDIUM">Medium</option>
              <option value="HIGH">High</option>
            </select>
          </div>

          <div class="form-group">
            <label>Landslide Susceptibility</label>
            <select v-model="form.landslide_susceptibility">
              <option value="LOW">Low</option>
              <option value="MEDIUM">Medium</option>
              <option value="HIGH">High</option>
            </select>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>Status</label>
            <select v-model="form.status">
              <option value="PERMANENT">Permanent</option>
              <option value="TEMPORARY">Temporary</option>
            </select>
          </div>

          <div class="form-group">
            <label>Used for COVID?</label>
            <select v-model="form.used_for_covid">
              <option :value="false">No</option>
              <option :value="true">Yes</option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label>Remarks</label>
          <textarea v-model="form.remarks" placeholder="Additional notes" rows="3"></textarea>
        </div>

        <button type="submit" class="btn-primary">Create Center</button>
      </form>
    </section>

    <section class="list">
      <h3>Evacuation Centers ({{ centers.length }})</h3>
      <div v-if="loading" class="loading">Loading centers...</div>
      <div v-else-if="centers.length === 0" class="empty">No centers found</div>
      <table v-else>
        <thead>
          <tr>
            <th>Name</th>
            <th>Municipality</th>
            <th>Barangay</th>
            <th>Fund Source</th>
            <th>Fam Cap</th>
            <th>Ind Cap</th>
            <th>Status</th>
            <th>Coordinates</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in centers" :key="c.id">
            <td>{{ c.name }}</td>
            <td>{{ getMunicipalityName(c.municipality) }}</td>
            <td>{{ getBarangayName(c.barangay) }}</td>
            <td>{{ c.fund_source || '-' }}</td>
            <td>{{ c.family_capacity_max || 0 }}</td>
            <td>{{ c.individual_capacity_max || 0 }}</td>
            <td>
              <span :class="'badge badge-' + c.status.toLowerCase()">
                {{ c.status }}
              </span>
            </td>
            <td>
              <span v-if="c.latitude != null && c.longitude != null" class="coords">
                {{ formatCoord(c.latitude) }}, {{ formatCoord(c.longitude) }}
              </span>
              <span v-else class="text-muted">-</span>
            </td>
            <td>
              <button @click="startEdit(c)" class="btn-sm">Edit</button>
              <button @click="deleteCenter(c.id)" class="btn-sm btn-danger">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </section>

    <!-- Edit Modal -->
    <div v-if="editing" class="modal" @click.self="cancelEdit">
      <div class="modal-content">
        <h3>Edit Center</h3>
        <form @submit.prevent="submitEdit">
          <div class="form-group">
            <label>Name *</label>
            <input v-model="editForm.name" required />
          </div>

          <div class="form-group">
            <label>Municipality *</label>
            <select v-model="editForm.municipality" required>
              <option v-for="mun in municipalities" :key="mun.id" :value="mun.id">
                {{ mun.name }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label>Barangay</label>
            <select v-model="editForm.barangay">
              <option value="">-- None --</option>
              <option v-for="brgy in allBarangays" :key="brgy.id" :value="brgy.id">
                {{ brgy.name }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label>Fund Source</label>
            <input v-model="editForm.fund_source" />
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Family Capacity</label>
              <input v-model.number="editForm.family_capacity_max" type="number" min="0" />
            </div>

            <div class="form-group">
              <label>Individual Capacity</label>
              <input v-model.number="editForm.individual_capacity_max" type="number" min="0" />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Latitude</label>
              <input v-model.number="editForm.latitude" type="number" step="0.000001" />
            </div>

            <div class="form-group">
              <label>Longitude</label>
              <input v-model.number="editForm.longitude" type="number" step="0.000001" />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Status</label>
              <select v-model="editForm.status">
                <option value="PERMANENT">Permanent</option>
                <option value="TEMPORARY">Temporary</option>
              </select>
            </div>

            <div class="form-group">
              <label>Used for COVID?</label>
              <select v-model="editForm.used_for_covid">
                <option :value="false">No</option>
                <option :value="true">Yes</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>Remarks</label>
            <textarea v-model="editForm.remarks" rows="3"></textarea>
          </div>

          <div class="modal-actions">
            <button type="submit" class="btn-primary">Save Changes</button>
            <button type="button" @click="cancelEdit" class="btn-secondary">Cancel</button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<script setup>
import { getAuthHeader } from '../services/authService';
</script>

<script>
export default {
  name: 'EvacManager',
  data() {
    return {
      file: null,
      uploading: false,
      uploadResult: null,
      centers: [],
      municipalities: [],
      allBarangays: [],
      loading: false,
      form: {
        name: '',
        municipality: '',
        barangay: '',
        fund_source: '',
        family_capacity_max: 0,
        individual_capacity_max: 0,
        latitude: null,
        longitude: null,
        flood_susceptibility: 'LOW',
        landslide_susceptibility: 'LOW',
        status: 'TEMPORARY',
        used_for_covid: false,
        remarks: '',
      },
      editing: false,
      editForm: null,
    }
  },

  computed: {
    filteredBarangays() {
      if (!this.form.municipality) return [];
      return this.allBarangays.filter(b => b.municipality === this.form.municipality);
    }
  },

  mounted() {
    this.fetchMunicipalities();
    this.fetchBarangays();
    this.fetchCenters();
  },

  methods: {
    async fetchMunicipalities() {
      try {
        const res = await fetch('http://127.0.0.1:8000/api/municipalities/', {
          headers: getAuthHeader()
        });
        if (res.ok) {
          this.municipalities = await res.json();
        }
      } catch (err) {
        console.error('Failed to fetch municipalities:', err);
      }
    },

    async fetchBarangays() {
      try {
        const res = await fetch('http://127.0.0.1:8000/api/barangays/', {
          headers: getAuthHeader()
        });
        if (res.ok) {
          this.allBarangays = await res.json();
        }
      } catch (err) {
        console.error('Failed to fetch barangays:', err);
      }
    },

    getMunicipalityName(munId) {
      const mun = this.municipalities.find(m => m.id === munId);
      return mun ? mun.name : `ID: ${munId}`;
    },

    getBarangayName(brgyId) {
      if (!brgyId) return '-';
      const brgy = this.allBarangays.find(b => b.id === brgyId);
      return brgy ? brgy.name : `ID: ${brgyId}`;
    },

    onFileChange(e) {
      const f = e.target.files?.[0];
      if (f) {
        this.file = f;
        this.uploadResult = null;
      }
    },

    async uploadFile() {
      if (!this.file) {
        alert("Please select a file first.");
        return;
      }

      this.uploading = true;
      this.uploadResult = null;

      const formData = new FormData();
      formData.append("file", this.file);

      try {
        const res = await fetch("http://127.0.0.1:8000/api/evac_centers/evac-centers/upload/", {
          method: "POST",
          headers: {
            ...getAuthHeader(),
          },
          body: formData,
        });

        const data = await res.json();

        if (!res.ok) {
          throw new Error(data.error || data.detail || "Upload failed");
        }

        this.uploadResult = data;
        console.log("Upload successful:", data);

        // Reset file input
        if (this.$refs.fileInput) {
          this.$refs.fileInput.value = '';
        }
        this.file = null;

        // Refresh table
        await this.fetchCenters();

      } catch (err) {
        console.error("Upload error:", err);
        alert("Upload failed: " + err.message);
      } finally {
        this.uploading = false;
      }
    },

    async fetchCenters() {
      this.loading = true;

      try {
        const res = await fetch('http://127.0.0.1:8000/api/evac_centers/evac-centers/', {
          headers: getAuthHeader()
        });

        if (!res.ok) throw new Error('Failed to fetch');

        const data = await res.json();
        this.centers = Array.isArray(data) ? data : data.results || [];
      } catch (err) {
        console.error(err);
        alert('Failed to load centers');
      } finally {
        this.loading = false;
      }
    },

    async createCenter() {
      // Validate required fields
      if (!this.form.name || !this.form.municipality) {
        alert('Name and Municipality are required');
        return;
      }

      const payload = {
        name: this.form.name,
        province: 'Oriental Mindoro',
        municipality: parseInt(this.form.municipality),
        barangay: this.form.barangay ? parseInt(this.form.barangay) : null,
        fund_source: this.form.fund_source || '',
        family_capacity_max: this.form.family_capacity_max || 0,
        individual_capacity_max: this.form.individual_capacity_max || 0,
        latitude: this.form.latitude || null,
        longitude: this.form.longitude || null,
        flood_susceptibility: this.form.flood_susceptibility,
        landslide_susceptibility: this.form.landslide_susceptibility,
        status: this.form.status,
        used_for_covid: this.form.used_for_covid,
        remarks: this.form.remarks || '',
      };

      try {
        const res = await fetch('http://127.0.0.1:8000/api/evac_centers/evac-centers/', {
          method: 'POST',
          headers: {
            ...getAuthHeader(),
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        });

        if (!res.ok) {
          const errorData = await res.json();
          throw new Error(JSON.stringify(errorData));
        }

        alert('Center created successfully!');
        
        // Reset form
        this.form = {
          name: '',
          municipality: '',
          barangay: '',
          fund_source: '',
          family_capacity_max: 0,
          individual_capacity_max: 0,
          latitude: null,
          longitude: null,
          flood_susceptibility: 'LOW',
          landslide_susceptibility: 'LOW',
          status: 'TEMPORARY',
          used_for_covid: false,
          remarks: '',
        };

        await this.fetchCenters();
      } catch (err) {
        console.error(err);
        alert('Create failed: ' + err.message);
      }
    },

    startEdit(center) {
      this.editing = true;
      this.editForm = { ...center };
    },

    cancelEdit() {
      this.editing = false;
      this.editForm = null;
    },

    async submitEdit() {
      try {
        const payload = {
          ...this.editForm,
          municipality: parseInt(this.editForm.municipality),
          barangay: this.editForm.barangay ? parseInt(this.editForm.barangay) : null,
        };

        const res = await fetch(`http://127.0.0.1:8000/api/evac_centers/evac-centers/${this.editForm.id}/`, {
          method: 'PUT',
          headers: {
            ...getAuthHeader(),
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        });

        if (!res.ok) {
          const errorData = await res.json();
          throw new Error(JSON.stringify(errorData));
        }

        alert('Center updated successfully!');
        this.cancelEdit();
        await this.fetchCenters();
      } catch (err) {
        console.error(err);
        alert('Update failed: ' + err.message);
      }
    },

    async deleteCenter(id) {
      if (!confirm('Are you sure you want to delete this center?')) return;

      try {
        const res = await fetch(`http://127.0.0.1:8000/api/evac_centers/evac-centers/${id}/`, {
          method: 'DELETE',
          headers: getAuthHeader()
        });

        if (![200, 204].includes(res.status)) throw new Error('Delete failed');

        alert('Center deleted successfully!');
        await this.fetchCenters();
      } catch (err) {
        console.error(err);
        alert('Delete failed: ' + err.message);
      }
    },

    formatCoord(v) {
      const n = Number(v);
      return Number.isFinite(n) ? n.toFixed(4) : '-';
    },

  }
}
</script>

<style scoped>
.evac-manager {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  color: #f1f5f9;
}

.evac-manager h2 {
  font-size: 2rem;
  margin-bottom: 2rem;
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.upload, .create, .list {
  margin-bottom: 2rem;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.02));
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

.upload:hover, .create:hover, .list:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.upload h3, .create h3, .list h3 {
  font-size: 1.25rem;
  margin-bottom: 1rem;
  color: #f1f5f9;
}

input[type="file"], input, select {
  width: 100%;
  padding: 0.75rem 1rem;
  margin-bottom: 1rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #cbd5e1;
  font-size: 1rem;
  transition: all 0.3s ease;
}

input:focus, select:focus {
  border-color: rgba(79, 172, 254, 0.5);
  box-shadow: 0 0 0 2px rgba(79, 172, 254, 0.1);
  outline: none;
}

button {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

button:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(59, 130, 246, 0.4);
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.list table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  border-radius: 8px;
  overflow: hidden;
}

.list th {
  background: rgba(255, 255, 255, 0.05);
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #94a3b8;
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.list td {
  padding: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  color: #cbd5e1;
}

.list tr:last-child td {
  border-bottom: none;
}

.list tr:hover {
  background: rgba(255, 255, 255, 0.05);
}

.list td button {
  padding: 0.5rem 1rem;
  margin-right: 0.5rem;
  font-size: 0.875rem;
}

.list td button:last-child {
  background: linear-gradient(135deg, #ef4444, #dc2626);
}

.list td button:last-child:hover {
  box-shadow: 0 5px 15px rgba(239, 68, 68, 0.4);
}

.modal {
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.7);
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

.modal-content {
  background: #1a1a2e;
  padding: 2rem;
  border-radius: 16px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
  animation: slideUp 0.3s ease;
}

.modal-content h3 {
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
  color: #f1f5f9;
}

.modal-content button[type="submit"] {
  width: 100%;
  margin-top: 1rem;
}

.modal-content button[type="button"] {
  width: 100%;
  margin-top: 0.5rem;
  background: rgba(255, 255, 255, 0.1);
  color: #cbd5e1;
}

.modal-content button[type="button"]:hover {
  background: rgba(255, 255, 255, 0.2);
  box-shadow: none;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { transform: translateY(50px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

/* Loading states */
div[v-if="uploading"], div[v-if="loading"] {
  color: #94a3b8;
  font-style: italic;
  margin-top: 1rem;
}

@media (max-width: 768px) {
  .evac-manager {
    padding: 1rem;
  }

  .upload, .create, .list {
    padding: 1rem;
  }

  .list table {
    font-size: 0.875rem;
  }

  .list th, .list td {
    padding: 0.75rem;
  }
}
</style>