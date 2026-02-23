<template>
  <div class="map-container">
    <div class="map-header">
      <div class="header-content">
        <h2 class="page-title">🌍 GIS Monitoring Map</h2>
        <p class="page-subtitle">Real-time evacuation center status across Oriental Mindoro</p>
      </div>
      
      <div class="map-controls">
        <div class="legend">
          <div class="legend-item">
            <div class="legend-color normal"></div>
            <span>Available (< 70%)</span>
          </div>
          <div class="legend-item">
            <div class="legend-color warning"></div>
            <span>Nearly Full (70-89%)</span>
          </div>
          <div class="legend-item">
            <div class="legend-color critical"></div>
            <span>Critical (≥ 90%)</span>
          </div>
        </div>
        
        <div class="control-buttons">
          <button class="control-btn" @click="refreshData" title="Refresh Data">
            🔄
          </button>
          <button class="control-btn" @click="toggleSatellite" title="Toggle Satellite View">
            🛰️
          </button>
          <button class="control-btn" @click="fitToBounds" title="Fit to Centers">
            🎯
          </button>
        </div>
      </div>
    </div>

    <div class="map-content">
      <div id="map" class="main-map"></div>
      
      <div class="map-sidebar" :class="{ 'sidebar-collapsed': !selectedCenter }">
        <div class="sidebar-content" v-if="selectedCenter">
          <button class="close-sidebar" @click="selectedCenter = null">×</button>
          
          <div class="center-details">
            <div class="center-header">
              <h3>{{ selectedCenter.name }}</h3>
              <span class="status-badge" :class="getStatusLevel(selectedCenter)">
                {{ getStatusText(selectedCenter) }}
              </span>
            </div>
            
            <div class="center-info">
              <div class="info-item">
                <span class="info-label">📍 Location:</span>
                <span class="info-value">{{ selectedCenter.municipality }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">📞 Contact:</span>
                <span class="info-value">{{ selectedCenter.contact }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">🕒 Last Update:</span>
                <span class="info-value">{{ selectedCenter.lastUpdate }}</span>
              </div>
            </div>

            <!-- Occupancy Section -->
            <div class="metrics-section">
              <h4>Occupancy</h4>
              <div class="occupancy-display">
                <div class="progress-container">
                  <div class="progress-bar large">
                    <div 
                      class="progress-fill" 
                      :class="getStatusLevel(selectedCenter)"
                      :style="{ width: getOccupancyPercentage(selectedCenter) + '%' }"
                    ></div>
                  </div>
                  <div class="progress-text">
                    {{ selectedCenter.occupants }} / {{ selectedCenter.capacity }} 
                    ({{ getOccupancyPercentage(selectedCenter) }}%)
                  </div>
                </div>
              </div>
            </div>

            <!-- Supplies Section -->
            <div class="metrics-section">
              <h4>Supplies Status</h4>
              <div class="supplies-grid">
                <div v-for="(value, key) in selectedCenter.supplies" :key="key" class="supply-card">
                  <div class="supply-header">
                    <span class="supply-name">{{ key }}</span>
                    <span class="supply-percentage" :class="getSupplyLevel(value)">
                      {{ value }}%
                    </span>
                  </div>
                  <div class="supply-bar">
                    <div 
                      class="supply-fill" 
                      :class="getSupplyLevel(value)"
                      :style="{ width: value + '%' }"
                    ></div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Quick Actions -->
            <div class="action-buttons">
              <button class="action-btn primary" @click="sendSupplies(selectedCenter)">
                🚚 Send Supplies
              </button>
              <button class="action-btn secondary" @click="viewEvacuees(selectedCenter)">
                👥 View Evacuees
              </button>
              <button class="action-btn secondary" @click="contactCenter(selectedCenter)">
                📞 Contact Center
              </button>
            </div>
          </div>
        </div>
        
        <div class="sidebar-placeholder" v-else>
          <div class="placeholder-content">
            <div class="placeholder-icon">🗺️</div>
            <h3>Select a Center</h3>
            <p>Select any evacuation center marker to view detailed information and manage operations.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch, onActivated } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import api from '@/services/api'

const centers = ref([])

const centerLayer = ref(null)
const hazardLayer = ref(null)
const gisLayer = ref(null)
const routeLayer = ref(null)

const osmLayer = ref(null)
const satelliteLayer = ref(null)

// Fix for default markers in Leaflet
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

const map = ref(null)
const selectedCenter = ref(null)
const isSatelliteView = ref(false)

// Methods
const getOccupancyPercentage = (center) => 
  Math.round((center.occupants / center.capacity) * 100)

const getSupplyLevel = (value) => {
  if (value < 30) return 'critical'
  if (value < 60) return 'warning'
  return 'normal'
}

const createCustomIcon = (center) => {
  const percentage = getOccupancyPercentage(center)
  let color = getStatusColor(center)
  let pulseClass = percentage >= 90 ? 'pulse-marker' : ''

  return L.divIcon({
    className: `custom-marker ${pulseClass}`,
    html: `
      <div class="marker-pin" style="background: ${color}">
        <div class="marker-pulse"></div>
        <div class="marker-content">
          <span class="occupancy-percent">${percentage}%</span>
        </div>
      </div>
    `,
    iconSize: [40, 40],
    iconAnchor: [20, 40],
    popupAnchor: [0, -40]
  })
}

// ---- API ----
const fetchCenters = async () => {
  // Adjust endpoint to your backend
  // Example expected response: [{id,name,lat,lng,capacity,occupants,municipality,contact,lastUpdate,supplies}, ...]
  const res = await api.get('/gis-layers/')
  centers.value = Array.isArray(res.data) ? res.data : (res.data.results || [])
}

// ---- Rendering ----
const renderCenters = () => {
  if (!centerLayer.value) return

  centerLayer.value.clearLayers()

  centers.value.forEach((center) => {
    // Guard: must have coordinates
    if (center.lat == null || center.lng == null) return

    const icon = createCustomIcon(center)
    const marker = L.marker([center.lat, center.lng], { icon })
      .addTo(centerLayer.value)

    marker.on('click', () => {
      selectedCenter.value = center
    })
  })
}

const fitMapToCenters = () => {
  const coords = centers.value
    .filter(c => c.lat != null && c.lng != null)
    .map(c => [c.lat, c.lng])

  if (!coords.length) return

  const group = L.featureGroup(coords.map(([lat, lng]) => L.marker([lat, lng])))
  map.value.fitBounds(group.getBounds().pad(0.1))
}

const initializeMap = async () => {
  await nextTick()

  map.value = L.map('map').setView([13.0, 121.1], 9)

  // base layers
  osmLayer.value = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors',
  })
  satelliteLayer.value = L.tileLayer('https://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', {
    maxZoom: 20,
    subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
    attribution: '&copy; Google',
  })

  osmLayer.value.addTo(map.value)

  // overlay groups (must be after map exists)
  centerLayer.value = L.layerGroup().addTo(map.value)
  hazardLayer.value = L.layerGroup().addTo(map.value)
  gisLayer.value = L.layerGroup().addTo(map.value)
  routeLayer.value = L.layerGroup().addTo(map.value)

  // fetch and render
  await fetchCenters()
  renderCenters()
  fitMapToCenters()

  map.value.invalidateSize()
}

// ---- UI Buttons ----
const refreshData = async () => {
  if (!map.value) return
  await fetchCenters()
  renderCenters()
  map.value.invalidateSize()
}

const toggleSatellite = () => {
  if (!map.value || !osmLayer.value || !satelliteLayer.value) return

  isSatelliteView.value = !isSatelliteView.value

  if (isSatelliteView.value) {
    if (map.value.hasLayer(osmLayer.value)) map.value.removeLayer(osmLayer.value)
    if (!map.value.hasLayer(satelliteLayer.value)) map.value.addLayer(satelliteLayer.value)
  } else {
    if (map.value.hasLayer(satelliteLayer.value)) map.value.removeLayer(satelliteLayer.value)
    if (!map.value.hasLayer(osmLayer.value)) map.value.addLayer(osmLayer.value)
  }

  map.value.invalidateSize()
}

const fitToBounds = () => {
  if (!map.value) return
  fitMapToCenters()
  map.value.invalidateSize()
}

const sendSupplies = (center) => {
  alert(`Initiating supply delivery to ${center.name}`)
  // Implement supply delivery logic
}

const viewEvacuees = (center) => {
  alert(`Showing evacuees at ${center.name}`)
  // Navigate to evacuees page filtered by center
}

const contactCenter = (center) => {
  alert(`Contacting ${center.name} at ${center.contact}`)
  // Implement contact logic
}

const handleResize = () => {
  if (map.value) {
    map.value.invalidateSize()
  }
}

onMounted(() => {
  initializeMap()
  window.addEventListener('resize', handleResize)
})

onActivated(() => {
  if (map.value) {
    map.value.invalidateSize()
  }
})

onUnmounted(() => {
  if (map.value) {
    map.value.remove()
  }
  window.removeEventListener('resize', handleResize)
})

watch(selectedCenter, () => {
  nextTick(() => {
    if (map.value) {
      map.value.invalidateSize()
    }
  })
})
</script>

<style scoped>
.map-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #0c0f1d 0%, #1a1f38 100%);
}

.map-header {
  background: rgba(15, 23, 42, 0.8);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 1.5rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 2rem;
}

.header-content {
  flex: 1;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0 0 0.5rem 0;
}

.page-subtitle {
  color: #94a3b8;
  margin: 0;
  font-size: 0.875rem;
}

.map-controls {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  align-items: flex-end;
}

.legend {
  display: flex;
  gap: 1rem;
  background: rgba(255, 255, 255, 0.05);
  padding: 0.75rem 1rem;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #cbd5e1;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.legend-color.normal { background: #10b981; }
.legend-color.warning { background: #f59e0b; }
.legend-color.critical { background: #ef4444; }

.control-buttons {
  display: flex;
  gap: 0.5rem;
}

.control-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #cbd5e1;
  padding: 0.75rem;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 1.125rem;
}

.control-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
}

.map-content {
  flex: 1;
  display: flex;
  position: relative;
  overflow: hidden;
}

.main-map {
  flex: 1;
  height: 1000px;
  border-radius: 0;
}

.map-sidebar {
  width: 400px;
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(20px);
  border-left: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s;
  display: flex;
  flex-direction: column;
  z-index: 10;
}

.map-sidebar.sidebar-collapsed {
  width: 0;
  min-width: 0;
}

.sidebar-content {
  padding: 1.5rem;
  flex: 1;
  overflow-y: auto;
  position: relative;
}

.close-sidebar {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: #cbd5e1;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  transition: all 0.3s;
}

.close-sidebar:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.1);
}

.center-details {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.center-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.center-header h3 {
  margin: 0;
  color: #f1f5f9;
  font-size: 1.25rem;
  line-height: 1.4;
}

.status-badge {
  padding: 0.375rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  white-space: nowrap;
}

.status-badge.critical {
  background: rgba(239, 68, 68, 0.2);
  color: #fca5a5;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.status-badge.warning {
  background: rgba(245, 158, 11, 0.2);
  color: #fcd34d;
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.status-badge.normal {
  background: rgba(16, 185, 129, 0.2);
  color: #6ee7b7;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.center-info {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-label {
  color: #94a3b8;
  font-size: 0.875rem;
}

.info-value {
  color: #cbd5e1;
  font-size: 0.875rem;
  font-weight: 500;
}

.metrics-section {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 1.25rem;
}

.metrics-section h4 {
  margin: 0 0 1rem 0;
  color: #f1f5f9;
  font-size: 1rem;
}

.progress-container {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.progress-bar.large {
  height: 12px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 6px;
  transition: width 0.3s;
}

.progress-fill.critical { background: linear-gradient(90deg, #ef4444, #f87171); }
.progress-fill.warning { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.progress-fill.normal { background: linear-gradient(90deg, #10b981, #34d399); }

.progress-text {
  color: #cbd5e1;
  font-size: 0.875rem;
  font-weight: 600;
  text-align: center;
}

.supplies-grid {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.supply-card {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 0.75rem;
}

.supply-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.supply-name {
  color: #cbd5e1;
  font-size: 0.875rem;
  text-transform: capitalize;
  font-weight: 500;
}

.supply-percentage {
  font-size: 0.75rem;
  font-weight: 600;
}

.supply-percentage.critical { color: #ef4444; }
.supply-percentage.warning { color: #f59e0b; }
.supply-percentage.normal { color: #10b981; }

.supply-bar {
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
}

.supply-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s;
}

.supply-fill.critical { background: #ef4444; }
.supply-fill.warning { background: #f59e0b; }
.supply-fill.normal { background: #10b981; }

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.action-btn {
  padding: 0.875rem 1rem;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.action-btn.primary {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: white;
}

.action-btn.secondary {
  background: rgba(255, 255, 255, 0.1);
  color: #cbd5e1;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.action-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}

.sidebar-placeholder {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.placeholder-content {
  text-align: center;
  color: #94a3b8;
}

.placeholder-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.placeholder-content h3 {
  color: #cbd5e1;
  margin: 0 0 0.5rem 0;
}

.placeholder-content p {
  margin: 0;
  font-size: 0.875rem;
  line-height: 1.5;
}

/* Custom Marker Styles */
:deep(.custom-marker) {
  background: transparent;
  border: none;
}

:deep(.marker-pin) {
  width: 40px;
  height: 40px;
  background: #3b82f6;
  border-radius: 50% 50% 50% 0;
  transform: rotate(-45deg);
  position: relative;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
  border: 3px solid white;
}

:deep(.marker-pulse) {
  position: absolute;
  top: -3px;
  left: -3px;
  right: -3px;
  bottom: -3px;
  border-radius: 50% 50% 50% 0;
  background: inherit;
  opacity: 0;
  animation: none;
}

:deep(.pulse-marker .marker-pulse) {
  animation: pulse 2s infinite;
}

:deep(.marker-content) {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) rotate(45deg);
  color: white;
  font-weight: 700;
  font-size: 0.75rem;
  text-align: center;
}

:deep(.occupancy-percent) {
  font-size: 0.7rem;
  line-height: 1;
}

:deep(.marker-popup) {
  color: #1f2937;
}

:deep(.marker-popup h4) {
  margin: 0 0 0.5rem 0;
  color: #1f2937;
}

:deep(.marker-popup p) {
  margin: 0.25rem 0;
  font-size: 0.875rem;
}

/* Animations */
@keyframes pulse {
  0% {
    transform: rotate(-45deg) scale(1);
    opacity: 1;
  }
  50% {
    transform: rotate(-45deg) scale(1.3);
    opacity: 0.5;
  }
  100% {
    transform: rotate(-45deg) scale(1);
    opacity: 0;
  }
}

/* Responsive Design */
@media (max-width: 1024px) {
  .map-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .map-controls {
    align-items: stretch;
  }
  
  .legend {
    justify-content: center;
  }
  
  .map-sidebar {
    position: absolute;
    right: 0;
    top: 0;
    bottom: 0;
    z-index: 1000;
    box-shadow: -10px 0 30px rgba(0, 0, 0, 0.5);
  }
}

@media (max-width: 768px) {
  .map-header {
    padding: 1rem;
  }
  
  .legend {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .map-sidebar {
    width: 100%;
  }
  
  .map-sidebar.sidebar-collapsed {
    width: 0;
  }
}
</style>