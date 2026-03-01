<!-- src/views/UserHazardReport.vue -->
<template>
  <div class="hazard-report">
    <div class="report-header">
      <h1>Report a Hazard</h1>
      <p>Help keep your community safe by reporting potential dangers</p>
    </div>
    
    <div class="report-container">
      <form class="report-form" @submit.prevent="submitReport">
        <!-- Hazard Type -->
        <div class="form-section">
          <h3>Hazard Type</h3>
          <div class="hazard-types">
            <label 
              v-for="type in hazardTypes" 
              :key="type.id"
              :class="['hazard-type', { active: formData.type === type.id }]"
            >
              <input 
                type="radio" 
                v-model="formData.type" 
                :value="type.id"
                required
              >
              <div class="type-icon">
                <i :class="type.icon"></i>
              </div>
              <span>{{ type.name }}</span>
            </label>
          </div>
        </div>
        
        <!-- Location -->
        <div class="form-section">
          <h3>Location</h3>
          <div class="location-inputs">
            <div class="input-group">
              <label for="address">Address</label>
              <input 
                type="text" 
                id="address" 
                v-model="formData.address"
                placeholder="Enter the exact address"
                required
              >
            </div>
            <div class="coordinates">
              <div class="input-group">
                <label>Latitude</label>
                <input 
                  type="text" 
                  v-model="formData.latitude"
                  placeholder="Auto-detected"
                  required
                >
              </div>
              <div class="input-group">
                <label>Longitude</label>
                <input 
                  type="text" 
                  v-model="formData.longitude"
                  placeholder="Auto-detected"
                  required
                >
              </div>
            </div>
            <button 
              type="button" 
              class="location-btn"
              @click="getCurrentLocation"
              :disabled="gettingLocation"
            >
              <i class="icon-location"></i>
              {{ gettingLocation ? 'Detecting...' : 'Use My Location' }}
            </button>
          </div>
        </div>
        
        <!-- Description -->
        <div class="form-section">
          <h3>Description</h3>
          <div class="input-group">
            <label for="title">Brief Title</label>
            <input 
              type="text" 
              id="title" 
              v-model="formData.title"
              placeholder="e.g., Flooded intersection at Main St"
              required
              maxlength="100"
            >
            <span class="char-count">{{ formData.title.length }}/100</span>
          </div>
          <div class="input-group">
            <label for="description">Detailed Description</label>
            <textarea 
              id="description" 
              v-model="formData.description"
              placeholder="Please provide as much detail as possible about the hazard..."
              rows="4"
              required
            ></textarea>
          </div>
        </div>
        
        <!-- Photo Evidence -->
        <div class="form-section">
          <h3>Photo Evidence</h3>
          <div class="photo-upload">
            <div 
              class="upload-area"
              @click="triggerFileInput"
              @drop="handleDrop"
              @dragover.prevent
              @dragenter.prevent
            >
              <input 
                type="file" 
                ref="fileInput"
                @change="handleFileSelect"
                accept="image/*"
                multiple
                style="display: none"
              >
              <i class="icon-upload"></i>
              <p>Drag & drop photos here or click to browse</p>
              <small>Maximum 5 photos, 5MB each</small>
            </div>
            <div class="photo-preview" v-if="formData.photos.length">
              <div 
                v-for="(photo, index) in formData.photos" 
                :key="index"
                class="preview-item"
              >
                <img :src="photo.preview" alt="Preview">
                <button 
                  type="button" 
                  class="remove-photo"
                  @click="removePhoto(index)"
                >
                  ×
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Severity -->
        <div class="form-section">
          <h3>Severity Level</h3>
          <div class="severity-levels">
            <label 
              v-for="level in severityLevels" 
              :key="level.id"
              :class="['severity-level', { active: formData.severity === level.id }]"
            >
              <input 
                type="radio" 
                v-model="formData.severity" 
                :value="level.id"
                required
              >
              <div class="level-indicator" :class="level.id"></div>
              <span>{{ level.name }}</span>
              <small>{{ level.description }}</small>
            </label>
          </div>
        </div>
        
        <!-- Emergency Contact -->
        <div class="form-section">
          <h3>Your Contact Information</h3>
          <div class="contact-fields">
            <div class="input-group">
              <label for="contactName">Name</label>
              <input 
                type="text" 
                id="contactName" 
                v-model="formData.contactName"
                placeholder="Your full name"
                required
              >
            </div>
            <div class="input-group">
              <label for="contactPhone">Phone Number</label>
              <input 
                type="tel" 
                id="contactPhone" 
                v-model="formData.contactPhone"
                placeholder="Your phone number"
                required
              >
            </div>
          </div>
        </div>
        
        <!-- Submit -->
        <div class="form-actions">
          <button 
            type="button" 
            class="cancel-btn"
            @click="$router.go(-1)"
          >
            Cancel
          </button>
          <button 
            type="submit" 
            class="submit-btn"
            :disabled="submitting"
          >
            <span v-if="submitting">Submitting...</span>
            <span v-else>Submit Report</span>
          </button>
        </div>
      </form>
      
      <!-- Report Preview -->
      <div class="report-preview">
        <h3>Report Preview</h3>
        <div class="preview-card">
          <div class="preview-header">
            <div class="hazard-badge" :class="formData.type">
              <i :class="getHazardIcon(formData.type)"></i>
              {{ getHazardName(formData.type) }}
            </div>
            <div class="severity-badge" :class="formData.severity">
              {{ getSeverityName(formData.severity) }}
            </div>
          </div>
          <div class="preview-content">
            <h4>{{ formData.title || 'Hazard Title' }}</h4>
            <p>{{ formData.description || 'Hazard description will appear here...' }}</p>
            <div class="preview-location">
              <i class="icon-location"></i>
              <span>{{ formData.address || 'Location not specified' }}</span>
            </div>
            <div class="preview-photos" v-if="formData.photos.length">
              <div class="photos-count">
                <i class="icon-camera"></i>
                {{ formData.photos.length }} photo(s)
              </div>
            </div>
          </div>
          <div class="preview-footer">
            <span class="status pending">Pending Verification</span>
            <span class="timestamp">Just now</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from "@/services/api";
export default {
  name: 'UserHazardReport',
  data() {
    return {
      gettingLocation: false,
      submitting: false,
      hazardTypes: [
        { id: 'FLOOD', name: 'Flood', icon: 'icon-flood' },
        { id: 'LANDSLIDE', name: 'Landslide', icon: 'icon-landslide' },
        { id: 'FIRE', name: 'Fire', icon: 'icon-fire' },
        { id: 'TREE', name: 'Fallen Tree', icon: 'icon-tree' },
        { id: 'ROAD_DAMAGE', name: 'Road Damage', icon: 'icon-road' },
        { id: 'BUILDING_DAMAGE', name: 'Building Damage', icon: 'icon-building' },
        { id: 'UTILITY', name: 'Utility Hazard', icon: 'icon-utility' },
        { id: 'OTHER', name: 'Other', icon: 'icon-other' }
      ],
      severityLevels: [
        { id: 'LOW', name: 'Low', description: 'Minor issue' },
        { id: 'MEDIUM', name: 'Medium', description: 'Moderate risk' },
        { id: 'HIGH', name: 'High', description: 'Serious danger' },
        { id: 'CRITICAL', name: 'Critical', description: 'Immediate threat' }
      ],
      formData: {
        type: '',
        title: '',
        description: '',
        address: '',
        latitude: '',
        longitude: '',
        severity: 'MEDIUM',
        photos: [],
        contactName: '',
        contactPhone: '',
        municipality: "Calapan"
      }
    }
  },
  mounted() {
    // Auto-detect location on component mount
    this.getCurrentLocation()

    const user = JSON.parse(localStorage.getItem("userData") || "{}");
    if (user.municipality) {
      this.formData.municipality = user.municipality;
    }
  },
  methods: {
    async getCurrentLocation() {
      this.gettingLocation = true
      
      if (!navigator.geolocation) {
        alert('Geolocation is not supported by your browser')
        this.gettingLocation = false
        return
      }
      
      try {
        const position = await new Promise((resolve, reject) => {
          navigator.geolocation.getCurrentPosition(resolve, reject, {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0
          })
        })
        
        this.formData.latitude = position.coords.latitude.toFixed(6)
        this.formData.longitude = position.coords.longitude.toFixed(6)
        
        // Reverse geocoding would go here in a real implementation
        this.formData.address = 'Location detected (reverse geocoding needed)'
        
      } catch (error) {
        console.error('Error getting location:', error)
        alert('Unable to retrieve your location. Please enter it manually.')
      } finally {
        this.gettingLocation = false
      }
    },
    
    triggerFileInput() {
      this.$refs.fileInput.click()
    },
    
    handleFileSelect(event) {
      const files = Array.from(event.target.files)
      this.processFiles(files)
    },
    
    handleDrop(event) {
      event.preventDefault()
      const files = Array.from(event.dataTransfer.files)
      this.processFiles(files)
    },
    
    processFiles(files) {
      const remainingSlots = 5 - this.formData.photos.length
      const filesToProcess = files.slice(0, remainingSlots)
      
      filesToProcess.forEach(file => {
        if (file.type.startsWith('image/') && file.size <= 5 * 1024 * 1024) {
          const reader = new FileReader()
          reader.onload = (e) => {
            this.formData.photos.push({
              file: file,
              preview: e.target.result
            })
          }
          reader.readAsDataURL(file)
        }
      })
    },
    
    removePhoto(index) {
      this.formData.photos.splice(index, 1)
    },
    
    getHazardIcon(type) {
      const hazard = this.hazardTypes.find(t => t.id === type)
      return hazard ? hazard.icon : 'icon-other'
    },
    
    getHazardName(type) {
      const hazard = this.hazardTypes.find(t => t.id === type)
      return hazard ? hazard.name : 'Other'
    },
    
    getSeverityName(severity) {
      const level = this.severityLevels.find(s => s.id === severity)
      return level ? level.name : 'Medium'
    },
    
async submitReport() {
  this.submitting = true;

  try {
    const form = new FormData();

    form.append("hazard_type", this.formData.type);
    form.append("municipality", this.formData.municipality);
    form.append("title", this.formData.title || "");
    form.append("description", this.formData.description);
    form.append("address", this.formData.address || "");
    form.append("latitude", this.formData.latitude);
    form.append("longitude", this.formData.longitude);
    form.append("severity", this.formData.severity); // must be UPPERCASE

    form.append("contact_name", this.formData.contactName || "");
    form.append("contact_phone", this.formData.contactPhone || "");

    this.formData.photos.forEach(p => {
      form.append("uploaded_photos", p.file);
    });

    // IMPORTANT: use axios api instance so token is included automatically
 await api.post("hazards/", form, {
  headers: { "Content-Type": "multipart/form-data" },
});

 // ✅ add this EXACTLY here (only runs if POST succeeded)
    window.dispatchEvent(new CustomEvent("alerts:newReport"));

    alert("Report submitted!");
    this.$router.push("/user/dashboard");

  } catch (err) {
    console.error("Submit failed:", err?.response?.data || err);
    alert("Submit failed: " + JSON.stringify(err?.response?.data || err.message));
  } finally {
    this.submitting = false;
  }
}

  }
}
</script>

<style scoped>
.hazard-report {
  padding: 20px;
  background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
  min-height: 100vh;
  color: white;
}

.report-header {
  text-align: center;
  margin-bottom: 40px;
}

.report-header h1 {
  font-size: 32px;
  margin-bottom: 10px;
  background: linear-gradient(90deg, #ffffff, #0096ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.report-header p {
  color: #888;
  font-size: 16px;
}

.report-container {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 40px;
  max-width: 1400px;
  margin: 0 auto;
}

.report-form {
  background: rgba(30, 30, 40, 0.8);
  border-radius: 20px;
  padding: 30px;
  border: 1px solid rgba(100, 100, 120, 0.2);
}

.form-section {
  margin-bottom: 40px;
}

.form-section h3 {
  color: white;
  margin-bottom: 20px;
  font-size: 20px;
  border-bottom: 2px solid rgba(0, 150, 255, 0.3);
  padding-bottom: 10px;
}

.hazard-types {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 15px;
}

.hazard-type {
  background: rgba(40, 40, 50, 0.8);
  border: 2px solid rgba(100, 100, 120, 0.3);
  border-radius: 12px;
  padding: 20px 15px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.hazard-type input {
  display: none;
}

.hazard-type.active {
  border-color: #0096ff;
  background: rgba(0, 150, 255, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(0, 150, 255, 0.2);
}

.type-icon {
  width: 40px;
  height: 40px;
  background: rgba(0, 150, 255, 0.2);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 10px;
  font-size: 18px;
}

.hazard-type.active .type-icon {
  background: rgba(0, 150, 255, 0.4);
}

.hazard-type span {
  color: #ddd;
  font-size: 14px;
  font-weight: 500;
}

.location-inputs {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.coordinates {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.input-group {
  display: flex;
  flex-direction: column;
  position: relative;
}

.input-group label {
  color: #ddd;
  font-size: 14px;
  margin-bottom: 8px;
  font-weight: 500;
}

.input-group input,
.input-group textarea {
  padding: 15px;
  background: rgba(40, 40, 50, 0.8);
  border: 1px solid rgba(100, 100, 120, 0.3);
  border-radius: 10px;
  color: white;
  font-size: 16px;
  transition: all 0.3s ease;
  font-family: inherit;
}

.input-group input:focus,
.input-group textarea:focus {
  outline: none;
  border-color: #0096ff;
  box-shadow: 0 0 0 2px rgba(0, 150, 255, 0.2);
}

.input-group input::placeholder,
.input-group textarea::placeholder {
  color: #666;
}

.char-count {
  position: absolute;
  right: 10px;
  bottom: 10px;
  color: #888;
  font-size: 12px;
}

.location-btn {
  background: rgba(0, 150, 255, 0.2);
  border: 1px solid #0096ff;
  color: #0096ff;
  padding: 12px 20px;
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s ease;
  font-size: 14px;
}

.location-btn:hover:not(:disabled) {
  background: #0096ff;
  color: white;
  transform: translateY(-2px);
}

.location-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.photo-upload {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.upload-area {
  border: 2px dashed rgba(100, 100, 120, 0.5);
  border-radius: 12px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: rgba(40, 40, 50, 0.5);
}

.upload-area:hover {
  border-color: #0096ff;
  background: rgba(0, 150, 255, 0.1);
}

.upload-area i {
  font-size: 48px;
  color: #0096ff;
  margin-bottom: 15px;
  display: block;
}

.upload-area p {
  color: #ddd;
  margin-bottom: 8px;
  font-size: 16px;
}

.upload-area small {
  color: #888;
  font-size: 12px;
}

.photo-preview {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 10px;
}

.preview-item {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  aspect-ratio: 1;
}

.preview-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-photo {
  position: absolute;
  top: 5px;
  right: 5px;
  background: rgba(255, 68, 68, 0.9);
  border: none;
  color: white;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  line-height: 1;
}

.severity-levels {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
}

.severity-level {
  background: rgba(40, 40, 50, 0.8);
  border: 2px solid rgba(100, 100, 120, 0.3);
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.severity-level input {
  display: none;
}

.severity-level.active {
  border-color: #0096ff;
  background: rgba(0, 150, 255, 0.2);
  transform: translateY(-2px);
}

.level-indicator {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  margin: 0 auto 10px;
  border: 2px solid transparent;
}

.level-indicator.low {
  background: #00cc66;
  border-color: #00cc66;
}

.level-indicator.medium {
  background: #ffaa00;
  border-color: #ffaa00;
}

.level-indicator.high {
  background: #ff6b6b;
  border-color: #ff6b6b;
}

.level-indicator.critical {
  background: #ff4444;
  border-color: #ff4444;
  animation: pulse 2s infinite;
}

.severity-level span {
  display: block;
  color: #ddd;
  font-weight: 600;
  margin-bottom: 5px;
}

.severity-level small {
  color: #888;
  font-size: 12px;
}

.contact-fields {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.form-actions {
  display: flex;
  gap: 15px;
  justify-content: flex-end;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid rgba(100, 100, 120, 0.3);
}

.cancel-btn {
  background: transparent;
  border: 1px solid #666;
  color: #888;
  padding: 12px 30px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.cancel-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.submit-btn {
  background: linear-gradient(135deg, #0096ff, #0066cc);
  border: none;
  color: white;
  padding: 12px 30px;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  min-width: 150px;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(0, 150, 255, 0.3);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.report-preview {
  background: rgba(30, 30, 40, 0.8);
  border-radius: 20px;
  padding: 30px;
  border: 1px solid rgba(100, 100, 120, 0.2);
  height: fit-content;
  position: sticky;
  top: 20px;
}

.report-preview h3 {
  color: white;
  margin-bottom: 20px;
  font-size: 20px;
  border-bottom: 2px solid rgba(0, 150, 255, 0.3);
  padding-bottom: 10px;
}

.preview-card {
  background: rgba(40, 40, 50, 0.8);
  border-radius: 15px;
  overflow: hidden;
  border: 1px solid rgba(100, 100, 120, 0.3);
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: rgba(50, 50, 60, 0.8);
  border-bottom: 1px solid rgba(100, 100, 120, 0.3);
}

.hazard-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: rgba(0, 150, 255, 0.2);
  border-radius: 20px;
  color: #0096ff;
  font-size: 12px;
  font-weight: 600;
}

.severity-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.severity-badge.low {
  background: rgba(0, 204, 102, 0.2);
  color: #00cc66;
}

.severity-badge.medium {
  background: rgba(255, 170, 0, 0.2);
  color: #ffaa00;
}

.severity-badge.high {
  background: rgba(255, 107, 107, 0.2);
  color: #ff6b6b;
}

.severity-badge.critical {
  background: rgba(255, 68, 68, 0.2);
  color: #ff4444;
}

.preview-content {
  padding: 20px;
}

.preview-content h4 {
  color: white;
  margin-bottom: 10px;
  font-size: 18px;
}

.preview-content p {
  color: #888;
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 15px;
}

.preview-location {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #aaa;
  font-size: 14px;
  margin-bottom: 15px;
}

.preview-photos {
  margin-top: 15px;
}

.photos-count {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #888;
  font-size: 14px;
}

.preview-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: rgba(50, 50, 60, 0.8);
  border-top: 1px solid rgba(100, 100, 120, 0.3);
}

.status {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
}

.status.pending {
  background: rgba(255, 170, 0, 0.2);
  color: #ffaa00;
}

.timestamp {
  color: #666;
  font-size: 12px;
}

/* Icon placeholders */
.icon-location::before { content: "📍"; }
.icon-upload::before { content: "📤"; }
.icon-camera::before { content: "📷"; }
.icon-flood::before { content: "🌊"; }
.icon-landslide::before { content: "⛰️"; }
.icon-fire::before { content: "🔥"; }
.icon-tree::before { content: "🌳"; }
.icon-road::before { content: "🛣️"; }
.icon-building::before { content: "🏢"; }
.icon-utility::before { content: "⚡"; }
.icon-other::before { content: "⚠️"; }

@media (max-width: 1024px) {
  .report-container {
    grid-template-columns: 1fr;
  }
  
  .report-preview {
    position: static;
  }
}

@media (max-width: 768px) {
  .hazard-types,
  .severity-levels {
    grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  }
  
  .contact-fields,
  .coordinates {
    grid-template-columns: 1fr;
  }
  
  .form-actions {
    flex-direction: column;
  }
}
</style>