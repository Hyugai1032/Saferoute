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
            <option v-for="mun in municipalities" :key="mun.id" :value="mun.id" v-if="mun">
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
            <label>Shelter Category</label>
            <select v-model="form.shelter_category">
              <option value="INSIDE_EC">Inside Evacuation Center</option>
              <option value="OUTSIDE_EC">Outside Evacuation Center</option>
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

<div class="form-group full-width">
  <label>Remarks</label>
  <textarea
    v-model="form.remarks"
    placeholder="Additional notes"
    rows="4"
  ></textarea>
</div>

        <button type="submit" class="btn-primary">Create Center</button>
      </form>
    </section>

    <section class="list">
      <h3>Evacuation Centers ({{ centers.length }})</h3>
      <section class="filters">
        <h3>Filter Centers</h3>

        <div class="filter-row">
          <select v-model="filters.municipality">
            <option value="">All Municipalities</option>
            <option v-for="m in municipalities" :key="m.id" :value="m.id">
              {{ m.name }}
            </option>
          </select>

          <select v-model="filters.barangay">
            <option value="">All Barangays</option>
            <option
              v-for="b in allBarangays.filter(br => !filters.municipality || br.municipality === filters.municipality)"
              :key="b.id"
              :value="b.id"
            >
              {{ b.name }}
            </option>
          </select>

          <select v-model="filters.status">
            <option value="">All Status</option>
            <option value="PERMANENT">Permanent</option>
            <option value="TEMPORARY">Temporary</option>
          </select>

          <select v-model="filters.flood_susceptibility">
            <option value="">Flood Risk</option>
            <option value="LOW">Low</option>
            <option value="MEDIUM">Medium</option>
            <option value="HIGH">High</option>
          </select>

          <select v-model="filters.landslide_susceptibility">
            <option value="">Landslide Risk</option>
            <option value="LOW">Low</option>
            <option value="MEDIUM">Medium</option>
            <option value="HIGH">High</option>
          </select>

          <select v-model="filters.used_for_covid">
            <option value="">COVID Usage</option>
            <option :value="true">Used</option>
            <option :value="false">Not Used</option>
          </select>

          <input
            v-model="filters.search"
            placeholder="Search name / remarks"
            type="text"
          />

          <button @click="fetchCenters(1)">Apply</button>
          <button @click="resetFilters">Reset</button>
        </div>
      </section>
      <div v-if="loading" class="loading">Loading centers...</div>
      <div v-else-if="centers.length === 0" class="empty">No centers found</div>


<div v-else class="table-shell">
  <div class="table-toolbar">
    <div class="table-title">
      <span class="dot"></span>
      <div>
        <div class="title">Centers</div>
        <div class="subtitle">Manage evacuation centers (edit, delete, view info)</div>
      </div>
    </div>
  </div>

  <div class="table-wrap">
    <table class="centers-table">
      <thead>
        <tr>
          <th>Name</th>
          <th>Municipality</th>
          <th>Barangay</th>
          <th>Fund Source</th>
          <th class="num">Fam Cap</th>
          <th class="num">Ind Cap</th>
          <th>Status</th>
          <th>Shelter Category</th>
          <th>Coordinates</th>
          <th class="actions">Actions</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="c in centers" :key="c.id">
          <td class="name-cell">
            <div class="name-main">{{ c.name }}</div>
            <div class="name-sub muted">
              {{ c.remarks ? c.remarks : 'No remarks' }}
            </div>
          </td>

          <td>{{ c.municipality_name || '-' }}</td>
          <td>{{ c.barangay_name || '-' }}</td>
          <td>{{ c.fund_source || '-' }}</td>

          <td class="num">
            <span class="pill">{{ c.family_capacity_max || 0 }}</span>
          </td>

          <td class="num">
            <span class="pill">{{ c.individual_capacity_max || 0 }}</span>
          </td>

          <td>
            <span :class="['badge', 'badge-' + (c.status || '').toLowerCase()]">
              {{ c.status }}
            </span>
          </td>

          <td>
            <span class="badge" :class="c.shelter_category === 'OUTSIDE_EC' ? 'badge-outside' : 'badge-inside'">
              {{ c.shelter_category === 'OUTSIDE_EC' ? 'Outside EC' : 'Inside EC' }}
            </span>
          </td>

          <td>
            <span v-if="c.latitude != null && c.longitude != null" class="coords">
              {{ formatCoord(c.latitude) }}, {{ formatCoord(c.longitude) }}
            </span>
            <span v-else class="text-muted">-</span>
          </td>

          <td class="actions">
            <div class="btn-group">
              <button @click="startEdit(c)" class="btn-sm btn-ghost">Edit</button>
              <button @click="deleteCenter(c.id)" class="btn-sm btn-danger">Delete</button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</div>
      <div class="pager" v-if="pagination.count > 0">
        <button :disabled="!pagination.previous" @click="fetchCenters(Number(pagination.page) - 1)">
          Prev
        </button>

        <span>
          Page {{ pagination.page }} of {{ Math.ceil(pagination.count / pagination.page_size) }}
          ({{ pagination.count }} total)
        </span>

        <button :disabled="!pagination.next" @click="fetchCenters(Number(pagination.page) + 1)">
          Next
        </button>
      </div>
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
              <label>Shelter Category</label>
              <select v-model="form.shelter_category">
                <option value="INSIDE_EC">Inside Evacuation Center</option>
                <option value="OUTSIDE_EC">Outside Evacuation Center</option>
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
const API_BASE = import.meta.env.VITE_API_BASE_URL;
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
        shelter_category: 'INSIDE_EC',
        used_for_covid: false,
        remarks: '',
      },
      filters: {
        municipality: '',
        barangay: '',
        status: '',
        flood_susceptibility: '',
        landslide_susceptibility: '',
        used_for_covid: '',
        search: '',
      },
      editing: false,
      editForm: null,
      pagination: {
        page: 1,
        page_size: 10,
        count: 0,
        next: null,
        previous: null,
      },
    }
  },

  computed: {
    filteredBarangays() {
      if (!this.form.municipality) return [];
      return this.allBarangays.filter(b => b.municipality === Number(this.form.municipality));
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
        const res = await fetch(`${API_BASE}municipalities/?page_size=9999`, {
          headers: getAuthHeader()
        });
        if (!res.ok) return;

        const data = await res.json();
        const list = Array.isArray(data) ? data : (data.results || []);

        this.municipalities = list.filter(m => m && m.id != null);
      } catch (err) {
        console.error('Failed to fetch municipalities:', err);
      }
    },

    async fetchBarangays() {
      try {
        const res = await fetch(`${API_BASE}barangays/?page_size=9999`, {
          headers: getAuthHeader()
        });
        if (!res.ok) return;

        const data = await res.json();
        const list = Array.isArray(data) ? data : (data.results || []);

        this.allBarangays = list.filter(b => b && b.id != null);
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
        const res = await fetch(`${API_BASE}evac_centers/evac-centers/upload/`, {
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

    async fetchCenters(page = this.pagination.page) {
      this.loading = true;

      try {
        const pageNum = Number(page) || 1; // ✅ force numeric

        const params = new URLSearchParams();

        // filters
        Object.entries(this.filters).forEach(([key, val]) => {
          if (val !== '' && val !== null) {
            params.append(key, val);
          }
        });

        // pagination
        params.set("page", pageNum);
        params.set("page_size", Number(this.pagination.page_size) || 10);

        const url = `${API_BASE}evac_centers/evac-centers/?${params.toString()}`;

        const res = await fetch(url, { headers: getAuthHeader() });
        if (!res.ok) throw new Error('Failed to fetch');

        const data = await res.json();

        this.centers = data.results || [];
        this.pagination.count = data.count || 0;
        this.pagination.next = data.next;
        this.pagination.previous = data.previous;
        this.pagination.page = pageNum; // ✅ store numeric
      } catch (err) {
        console.error(err);
        alert('Failed to load centers');
      } finally {
        this.loading = false;
      }
    },

    resetFilters() {
      this.filters = {
        municipality: '',
        barangay: '',
        status: '',
        flood_susceptibility: '',
        landslide_susceptibility: '',
        used_for_covid: '',
        search: '',
      };
      this.fetchCenters(1);
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
        shelter_category: this.form.shelter_category,
        used_for_covid: this.form.used_for_covid,
        remarks: this.form.remarks || '',
      };

      try {
        const res = await fetch(`${API_BASE}evac_centers/evac-centers/`, {
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
      this.editForm = { ...center,
      shelter_category: center.shelter_category || 'INSIDE_EC', };
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
          shelter_category: this.editForm.shelter_category || 'INSIDE_EC',
        };

        const res = await fetch(`${API_BASE}evac_centers/evac-centers/${this.editForm.id}/`, {
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
        const res = await fetch(`${API_BASE}evac_centers/evac-centers/${id}/`, {
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



/* ====== TABLE UI (Cleaner Dashboard Look) ====== */
.table-shell {
  margin-top: 12px;
  border-radius: 16px;
  border: 1px solid rgba(255,255,255,0.10);
  background: linear-gradient(135deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02));
  box-shadow: 0 10px 30px rgba(0,0,0,0.25);
  overflow: hidden;
}

.table-toolbar {
  padding: 14px 16px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.table-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.table-title .dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: #3b82f6;
  box-shadow: 0 0 0 4px rgba(59,130,246,0.15);
}

.table-title .title {
  font-weight: 700;
  color: #e5e7eb;
  line-height: 1.1;
}

.table-title .subtitle {
  font-size: 12px;
  color: rgba(203,213,225,0.75);
}

.table-wrap {
  width: 100%;
  overflow: auto;
}

.centers-table {
  width: 100%;
  min-width: 980px; /* keeps columns readable; scrolls on small screens */
  border-collapse: separate;
  border-spacing: 0;
}

.centers-table thead th {
  position: sticky;
  top: 0;
  z-index: 2;
  text-align: left;
  font-size: 12px;
  letter-spacing: .08em;
  text-transform: uppercase;
  color: rgba(148,163,184,0.95);
  background: rgba(10,10,20,0.85);
  backdrop-filter: blur(8px);
  padding: 14px 14px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
}

.centers-table tbody td {
  padding: 14px 14px;
  color: rgba(226,232,240,0.95);
  border-bottom: 1px solid rgba(255,255,255,0.06);
  vertical-align: top;
}

.centers-table tbody tr:nth-child(odd) {
  background: rgba(255,255,255,0.02);
}

.centers-table tbody tr:hover {
  background: rgba(59,130,246,0.08);
}

.num {
  text-align: right;
}

.actions {
  width: 180px;
}

.name-cell .name-main {
  font-weight: 700;
  color: #f1f5f9;
  margin-bottom: 4px;
}

.name-cell .name-sub {
  font-size: 12px;
  max-width: 420px;
  color: rgba(148,163,184,0.9);
}

.muted, .text-muted {
  color: rgba(148,163,184,0.9);
}

.pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 44px;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.10);
  font-weight: 700;
}

.coords {
  display: inline-flex;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(0,150,255,0.10);
  border: 1px solid rgba(0,150,255,0.22);
  color: rgba(191,219,254,0.95);
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
  font-size: 12px;
}

.badge {
  display: inline-flex;
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: .06em;
}

.badge-permanent {
  background: rgba(16,185,129,0.12);
  border: 1px solid rgba(16,185,129,0.25);
  color: #34d399;
}

.badge-temporary {
  background: rgba(245,158,11,0.12);
  border: 1px solid rgba(245,158,11,0.25);
  color: #fbbf24;
}

.btn-group {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.btn-sm {
  padding: 8px 12px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 700;
}

.btn-ghost {
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.12);
  color: rgba(226,232,240,0.95);
}

.btn-ghost:hover {
  background: rgba(59,130,246,0.15);
  border-color: rgba(59,130,246,0.35);
  transform: translateY(-1px);
}

.btn-danger {
  background: rgba(239,68,68,0.12);
  border: 1px solid rgba(239,68,68,0.25);
  color: #fecaca;
}

.btn-danger:hover {
  background: rgba(239,68,68,0.18);
  transform: translateY(-1px);
}



.filters .filter-row {
  display: grid;
  grid-template-columns: repeat(6, minmax(140px, 1fr));
  gap: 10px;
  align-items: end;
}

.filters .filter-row input,
.filters .filter-row select {
  margin-bottom: 0;
}

.filters .filter-row button {
  height: 44px;
}

@media (max-width: 1100px) {
  .filters .filter-row {
    grid-template-columns: repeat(2, minmax(160px, 1fr));
  }
  .create form {
  grid-template-columns: 1fr;
}
.form-group.full-width {
  grid-column: auto;
}
}

textarea {
  resize: vertical;
  min-height: 90px;
  line-height: 1.4;
}

textarea::placeholder {
  color: rgba(203, 213, 225, 0.6);
}



/* --- form layout --- */
.create form {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.form-row {
  display: contents; /* keeps your existing markup working but flows in grid */
}

.form-group {
  margin: 0; /* remove extra spacing, grid handles spacing */
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #e2e8f0;
  font-size: 0.95rem;
}

/* make remarks span both columns */
.form-group.full-width {
  grid-column: 1 / -1;
}

/* --- inputs look consistent --- */
.evac-manager input,
.evac-manager select,
.evac-manager textarea {
  width: 100%;
  display: block;
  padding: 0.85rem 1rem;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 12px;
  color: #e5e7eb;
  font-size: 1rem;
  transition: all 0.25s ease;
  box-sizing: border-box;
}

.evac-manager textarea {
  min-height: 120px;
  resize: vertical;
  line-height: 1.5;
}

.evac-manager input:focus,
.evac-manager select:focus,
.evac-manager textarea:focus {
  outline: none;
  border-color: rgba(79, 172, 254, 0.6);
  box-shadow: 0 0 0 3px rgba(79, 172, 254, 0.12);
}

.evac-manager textarea::placeholder,
.evac-manager input::placeholder {
  color: rgba(203, 213, 225, 0.55);
}
</style>