<!-- src/views/Users/UserMap.vue -->
<template>
  <div class="user-map-container">
    <!-- Header with Interactive Controls -->
    <div class="map-header">
      <div class="header-content">
        <h1 class="map-title">Emergency Map</h1>
        <p class="map-subtitle">Real-time hazard locations & evacuation centers</p>
      </div>
      <div class="map-controls">
        <div class="control-group">
          <button class="control-btn" @click="toggleLayers" :class="{ active: showLayers }">
            <i class="icon-layers"></i>
            Layers
          </button>
          <button class="control-btn" @click="locateUser" :disabled="locating">
            <i class="icon-location"></i>
            {{ locating ? 'Locating...' : 'My Location' }}
          </button>
          <button class="control-btn" @click="toggleFilters" :class="{ active: showFilters }">
            <i class="icon-filter"></i>
            Filters
          </button>
        </div>
      </div>
    </div>

    <!-- Main Map Container -->
    <div class="map-content">
      <!-- Sidebar Panels -->
      <div class="map-sidebar">
        <!-- Layers Panel -->
        <transition name="slide-right">
          <div v-if="showLayers" class="sidebar-panel layers-panel">
            <h3>Map Layers</h3>
            <div class="layer-list">
              <label v-for="layer in mapLayers" :key="layer.id" class="layer-item">
                <input 
                  type="checkbox" 
                  v-model="layer.visible"
                  @change="toggleLayer(layer.id)"
                >
                <span class="custom-checkbox"></span>
                <div class="layer-icon" :class="layer.type">
                  <i :class="layer.icon"></i>
                </div>
                <span class="layer-name">{{ layer.name }}</span>
                <span class="layer-count" v-if="layer.count">({{ layer.count }})</span>
              </label>
            </div>
          </div>
        </transition>

        <!-- Filters Panel -->
        <transition name="slide-right">
          <div v-if="showFilters" class="sidebar-panel filters-panel">
            <h3>Filter Centers</h3>
            <div class="filter-group">
              <label>Municipality</label>
              <select v-model="filters.municipality" class="filter-select">
                <option value="">All Municipalities</option>
                <option v-for="municipality in municipalities" :key="municipality" :value="municipality">
                  {{ municipality }}
                </option>
              </select>
            </div>
            <div class="filter-group">
              <label>Hazard Type</label>
              <div class="hazard-filters">
                <label v-for="type in hazardTypes" :key="type.id" class="hazard-filter">
                  <input type="checkbox" v-model="filters.hazardTypes" :value="type.id">
                  <span class="custom-checkbox"></span>
                  <i :class="type.icon"></i>
                  <span>{{ type.name }}</span>
                </label>
              </div>
            </div>
            <div class="filter-group">
              <label>Distance</label>
              <div class="distance-slider">
                <input 
                  type="range" 
                  min="1" 
                  max="50" 
                  v-model="filters.distance"
                  class="slider"
                >
                <span class="distance-value">{{ filters.distance }} km</span>
              </div>
            </div>
          </div>
        </transition>
      </div>

      <!-- Map Visualization -->
      <div class="map-visualization">
        <!-- Interactive Map Canvas -->
        <div class="map-canvas" ref="mapCanvas">
          <!-- Map would be integrated here (Leaflet, Google Maps, etc.) -->
          <div class="map-placeholder">
            <div class="floating-elements">
              <div 
                v-for="marker in visibleMarkers" 
                :key="marker.id"
                :class="['map-marker', marker.type, { pulsating: marker.urgent }]"
                :style="{
                  left: marker.x + '%',
                  top: marker.y + '%'
                }"
                @click="selectMarker(marker)"
              >
                <i :class="marker.icon"></i>
                <div class="marker-tooltip" v-if="selectedMarker === marker.id">
                  {{ marker.title }}
                </div>
              </div>
            </div>
            <div class="map-grid"></div>
            <div class="user-location" v-if="userLocation" :style="{
              left: userLocation.x + '%',
              top: userLocation.y + '%'
            }">
              <div class="pulse-ring"></div>
              <div class="location-dot"></div>
            </div>
          </div>
        </div>

        <!-- Quick Actions Overlay -->
        <div class="map-overlay">
          <button class="action-btn primary" @click="$router.push('/user/report')">
            <i class="icon-report"></i>
            Report Hazard
          </button>
          <button class="action-btn" @click="showDirections = !showDirections">
            <i class="icon-directions"></i>
            Get Directions
          </button>
        </div>

        <!-- Selected Location Card -->
        <transition name="slide-up">
          <div v-if="selectedLocation" class="location-card">
            <div class="card-header">
              <div class="location-type" :class="selectedLocation.type">
                <i :class="selectedLocation.icon"></i>
                {{ selectedLocation.type === 'shelter' ? 'Evacuation Center' : 'Hazard' }}
              </div>
              <button class="close-btn" @click="selectedLocation = null">×</button>
            </div>
            <div class="card-content">
              <h3>{{ selectedLocation.title }}</h3>
              <p>{{ selectedLocation.description }}</p>
              <div class="location-details">
                <div class="detail-item">
                  <i class="icon-location"></i>
                  <span>{{ selectedLocation.address }}</span>
                </div>
                <div class="detail-item">
                  <i class="icon-distance"></i>
                  <span>{{ selectedLocation.distance }} away</span>
                </div>
                <div v-if="selectedLocation.type === 'shelter'" class="detail-item">
                  <i class="icon-capacity"></i>
                  <span>Capacity: {{ selectedLocation.capacity }}/{{ selectedLocation.maxCapacity }}</span>
                  <div class="capacity-bar">
                    <div 
                      class="capacity-fill" 
                      :class="selectedLocation.capacityStatus"
                      :style="{ width: selectedLocation.capacityPercent + '%' }"
                    ></div>
                  </div>
                </div>
                <div v-if="selectedLocation.type === 'hazard'" class="detail-item">
                  <i class="icon-severity"></i>
                  <span>Severity: </span>
                  <span class="severity-badge" :class="selectedLocation.severity">
                    {{ selectedLocation.severity }}
                  </span>
                </div>
              </div>
            </div>
            <div class="card-actions">
              <button v-if="selectedLocation.type === 'shelter'" class="action-btn primary">
                <i class="icon-navigate"></i>
                Navigate Here
              </button>
              <button class="action-btn">
                <i class="icon-share"></i>
                Share
              </button>
            </div>
          </div>
        </transition>
      </div>
    </div>

    <!-- Bottom Sheet for Mobile -->
    <transition name="slide-up">
      <div v-if="mobileView && (showLayers || showFilters)" class="mobile-panel">
        <div class="panel-header">
          <h3>{{ showLayers ? 'Map Layers' : 'Filters' }}</h3>
          <button class="close-btn" @click="closePanels">×</button>
        </div>
        <div class="panel-content">
          <div v-if="showLayers" class="mobile-layers">
            <!-- Mobile layers content -->
          </div>
          <div v-if="showFilters" class="mobile-filters">
            <!-- Mobile filters content -->
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
export default {
  name: 'UserMap',
  data() {
    return {
      showLayers: false,
      showFilters: false,
      showDirections: false,
      locating: false,
      mobileView: false,
      selectedLocation: null,
      selectedMarker: null,
      userLocation: null,
      mapLayers: [
        { id: 'shelters', name: 'Evacuation Centers', type: 'shelter', icon: 'icon-shelter', visible: true, count: 12 },
        { id: 'hazards', name: 'Hazard Reports', type: 'hazard', icon: 'icon-hazard', visible: true, count: 8 },
        { id: 'floods', name: 'Flood Areas', type: 'flood', icon: 'icon-flood', visible: false, count: 3 },
        { id: 'landslides', name: 'Landslide Risks', type: 'landslide', icon: 'icon-landslide', visible: false, count: 2 }
      ],
      filters: {
        municipality: '',
        hazardTypes: [],
        distance: 10
      },
      municipalities: ['Downtown', 'North District', 'South Hills', 'East Valley', 'West Park'],
      hazardTypes: [
        { id: 'flood', name: 'Flood', icon: 'icon-flood' },
        { id: 'fire', name: 'Fire', icon: 'icon-fire' },
        { id: 'landslide', name: 'Landslide', icon: 'icon-landslide' },
        { id: 'building', name: 'Building Damage', icon: 'icon-building' }
      ],
      visibleMarkers: [
        { id: 1, type: 'shelter', icon: 'icon-shelter', title: 'Central High School', x: 30, y: 40, urgent: false },
        { id: 2, type: 'shelter', icon: 'icon-shelter', title: 'Community Center', x: 60, y: 35, urgent: false },
        { id: 3, type: 'hazard', icon: 'icon-flood', title: 'Flooded Street', x: 45, y: 55, urgent: true },
        { id: 4, type: 'hazard', icon: 'icon-fire', title: 'Building Fire', x: 70, y: 60, urgent: true }
      ]
    }
  },
  mounted() {
    this.checkMobileView()
    window.addEventListener('resize', this.checkMobileView)
    this.getUserLocation()
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.checkMobileView)
  },
  methods: {
    checkMobileView() {
      this.mobileView = window.innerWidth < 768
    },
    toggleLayers() {
      this.showLayers = !this.showLayers
      if (this.mobileView && this.showLayers) this.showFilters = false
    },
    toggleFilters() {
      this.showFilters = !this.showFilters
      if (this.mobileView && this.showFilters) this.showLayers = false
    },
    closePanels() {
      this.showLayers = false
      this.showFilters = false
    },
    async locateUser() {
      this.locating = true
      try {
        // Simulate location detection
        await new Promise(resolve => setTimeout(resolve, 1500))
        this.userLocation = { x: 50, y: 50 }
      } catch (error) {
        console.error('Error getting location:', error)
      } finally {
        this.locating = false
      }
    },
    getUserLocation() {
      // Initial user location
      this.userLocation = { x: 50, y: 50 }
    },
    toggleLayer(layerId) {
      const layer = this.mapLayers.find(l => l.id === layerId)
      console.log(`Toggled ${layer.name} layer:`, layer.visible)
    },
    selectMarker(marker) {
      this.selectedMarker = marker.id
      this.selectedLocation = {
        id: marker.id,
        type: marker.type,
        icon: marker.icon,
        title: marker.title,
        description: marker.type === 'shelter' 
          ? 'Safe evacuation center with medical facilities and supplies' 
          : 'Reported hazard requiring immediate attention',
        address: '123 Main Street, Downtown',
        distance: '2.3 km',
        capacity: 45,
        maxCapacity: 100,
        capacityPercent: 45,
        capacityStatus: 'medium',
        severity: 'high'
      }
    }
  }
}
</script>

<style scoped>
.user-map-container {
  height: 100vh;
  background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
  display: flex;
  flex-direction: column;
  color: white;
  overflow: hidden;
}

.map-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: rgba(15, 15, 20, 0.9);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.header-content h1 {
  font-size: 28px;
  margin-bottom: 5px;
  background: linear-gradient(90deg, #ffffff, #0096ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.header-content p {
  color: #888;
  font-size: 14px;
}

.control-group {
  display: flex;
  gap: 10px;
}

.control-btn {
  background: rgba(40, 40, 50, 0.8);
  border: 1px solid rgba(100, 100, 120, 0.3);
  color: #ddd;
  padding: 10px 15px;
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  font-size: 14px;
}

.control-btn:hover,
.control-btn.active {
  background: rgba(0, 150, 255, 0.2);
  border-color: #0096ff;
  color: #0096ff;
  transform: translateY(-2px);
}

.map-content {
  flex: 1;
  display: flex;
  position: relative;
  overflow: hidden;
}

.map-sidebar {
  width: 300px;
  background: rgba(20, 20, 30, 0.9);
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  padding: 20px;
  overflow-y: auto;
}

.sidebar-panel h3 {
  color: white;
  margin-bottom: 20px;
  font-size: 18px;
  border-bottom: 2px solid rgba(0, 150, 255, 0.3);
  padding-bottom: 10px;
}

.layer-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.layer-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(40, 40, 50, 0.6);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.layer-item:hover {
  background: rgba(50, 50, 60, 0.8);
  transform: translateX(5px);
}

.layer-item input {
  display: none;
}

.custom-checkbox {
  width: 18px;
  height: 18px;
  border: 2px solid #444;
  border-radius: 4px;
  position: relative;
  transition: all 0.3s ease;
}

.layer-item input:checked + .custom-checkbox {
  background: #0096ff;
  border-color: #0096ff;
}

.layer-item input:checked + .custom-checkbox::after {
  content: '';
  position: absolute;
  left: 4px;
  top: 1px;
  width: 5px;
  height: 10px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.layer-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.layer-icon.shelter {
  background: rgba(0, 204, 102, 0.2);
  color: #00cc66;
}

.layer-icon.hazard {
  background: rgba(255, 170, 0, 0.2);
  color: #ffaa00;
}

.layer-icon.flood {
  background: rgba(0, 150, 255, 0.2);
  color: #0096ff;
}

.layer-icon.landslide {
  background: rgba(153, 102, 255, 0.2);
  color: #9966ff;
}

.layer-name {
  flex: 1;
  color: #ddd;
  font-weight: 500;
}

.layer-count {
  color: #666;
  font-size: 12px;
}

.filter-group {
  margin-bottom: 20px;
}

.filter-group label {
  display: block;
  color: #ddd;
  margin-bottom: 8px;
  font-size: 14px;
}

.filter-select {
  width: 100%;
  padding: 12px;
  background: rgba(40, 40, 50, 0.8);
  border: 1px solid rgba(100, 100, 120, 0.3);
  border-radius: 8px;
  color: white;
  font-size: 14px;
}

.hazard-filters {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.hazard-filter {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px;
  background: rgba(40, 40, 50, 0.6);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.hazard-filter:hover {
  background: rgba(50, 50, 60, 0.8);
}

.distance-slider {
  display: flex;
  align-items: center;
  gap: 15px;
}

.slider {
  flex: 1;
  height: 4px;
  background: rgba(100, 100, 120, 0.3);
  border-radius: 2px;
  outline: none;
  -webkit-appearance: none;
}

.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 20px;
  height: 20px;
  background: #0096ff;
  border-radius: 50%;
  cursor: pointer;
  box-shadow: 0 0 10px rgba(0, 150, 255, 0.5);
}

.distance-value {
  color: #0096ff;
  font-weight: 600;
  min-width: 50px;
}

.map-visualization {
  flex: 1;
  position: relative;
  background: #0a0a0a;
}

.map-canvas {
  width: 100%;
  height: 100%;
  position: relative;
  overflow: hidden;
}

.map-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(45deg, #1a1a2e 0%, #16213e 100%);
  position: relative;
}

.map-grid {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: 
    linear-gradient(rgba(0, 150, 255, 0.1) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 150, 255, 0.1) 1px, transparent 1px);
  background-size: 50px 50px;
}

.floating-elements {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.map-marker {
  position: absolute;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transform: translate(-50%, -50%);
  transition: all 0.3s ease;
  font-size: 18px;
  z-index: 10;
}

.map-marker.shelter {
  background: rgba(0, 204, 102, 0.9);
  box-shadow: 0 0 20px rgba(0, 204, 102, 0.5);
}

.map-marker.hazard {
  background: rgba(255, 170, 0, 0.9);
  box-shadow: 0 0 20px rgba(255, 170, 0, 0.5);
}

.map-marker.pulsating {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { transform: translate(-50%, -50%) scale(1); }
  50% { transform: translate(-50%, -50%) scale(1.1); }
  100% { transform: translate(-50%, -50%) scale(1); }
}

.marker-tooltip {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.9);
  color: white;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 12px;
  white-space: nowrap;
  margin-bottom: 10px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.marker-tooltip::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 5px solid transparent;
  border-top-color: rgba(0, 0, 0, 0.9);
}

.user-location {
  position: absolute;
  transform: translate(-50%, -50%);
  z-index: 20;
}

.pulse-ring {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 30px;
  height: 30px;
  border: 2px solid #0096ff;
  border-radius: 50%;
  animation: sonar 2s infinite;
}

@keyframes sonar {
  0% { 
    width: 30px; 
    height: 30px; 
    opacity: 1; 
  }
  100% { 
    width: 100px; 
    height: 100px; 
    opacity: 0; 
  }
}

.location-dot {
  width: 12px;
  height: 12px;
  background: #0096ff;
  border-radius: 50%;
  position: relative;
  z-index: 2;
  box-shadow: 0 0 10px rgba(0, 150, 255, 0.8);
}

.map-overlay {
  position: absolute;
  top: 20px;
  right: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  z-index: 30;
}

.action-btn {
  background: rgba(40, 40, 50, 0.9);
  border: 1px solid rgba(100, 100, 120, 0.3);
  color: #ddd;
  padding: 12px 16px;
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  font-size: 14px;
  backdrop-filter: blur(10px);
}

.action-btn.primary {
  background: linear-gradient(135deg, #0096ff, #0066cc);
  border-color: #0096ff;
  color: white;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
}

.location-card {
  position: absolute;
  bottom: 20px;
  left: 20px;
  right: 20px;
  background: rgba(20, 20, 30, 0.95);
  border-radius: 15px;
  padding: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  z-index: 40;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.location-type {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
}

.location-type.shelter {
  background: rgba(0, 204, 102, 0.2);
  color: #00cc66;
}

.location-type.hazard {
  background: rgba(255, 170, 0, 0.2);
  color: #ffaa00;
}

.close-btn {
  background: none;
  border: none;
  color: #888;
  font-size: 20px;
  cursor: pointer;
  transition: color 0.3s ease;
}

.close-btn:hover {
  color: white;
}

.card-content h3 {
  color: white;
  margin-bottom: 10px;
  font-size: 18px;
}

.card-content p {
  color: #888;
  margin-bottom: 15px;
  font-size: 14px;
  line-height: 1.5;
}

.location-details {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #aaa;
  font-size: 14px;
}

.capacity-bar {
  flex: 1;
  height: 6px;
  background: rgba(100, 100, 120, 0.3);
  border-radius: 3px;
  overflow: hidden;
  margin-left: 10px;
}

.capacity-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
}

.capacity-fill.low { background: #00cc66; }
.capacity-fill.medium { background: #ffaa00; }
.capacity-fill.high { background: #ff6b6b; }

.severity-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
}

.severity-badge.high {
  background: rgba(255, 107, 107, 0.2);
  color: #ff6b6b;
}

.card-actions {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}

.mobile-panel {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(20, 20, 30, 0.95);
  border-radius: 20px 20px 0 0;
  padding: 20px;
  backdrop-filter: blur(20px);
  z-index: 50;
  max-height: 70vh;
  overflow-y: auto;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

/* Transitions */
.slide-right-enter-active,
.slide-right-leave-active {
  transition: all 0.3s ease;
}

.slide-right-enter-from,
.slide-right-leave-to {
  opacity: 0;
  transform: translateX(-100%);
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(100%);
}

/* Responsive Design */
@media (max-width: 768px) {
  .map-header {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }
  
  .map-sidebar {
    display: none;
  }
  
  .map-overlay {
    top: auto;
    bottom: 20px;
    right: 20px;
    left: 20px;
    flex-direction: row;
    justify-content: space-between;
  }
  
  .action-btn {
    flex: 1;
    justify-content: center;
  }
  
  .location-card {
    bottom: 80px;
  }
}

@media (max-width: 480px) {
  .map-header {
    padding: 15px;
  }
  
  .header-content h1 {
    font-size: 24px;
  }
  
  .control-group {
    width: 100%;
    justify-content: space-between;
  }
  
  .control-btn {
    flex: 1;
    justify-content: center;
  }
}

/* Icon placeholders */
.icon-layers::before { content: "🔲"; }
.icon-location::before { content: "📍"; }
.icon-filter::before { content: "🔧"; }
.icon-shelter::before { content: "🏠"; }
.icon-hazard::before { content: "⚠️"; }
.icon-flood::before { content: "🌊"; }
.icon-fire::before { content: "🔥"; }
.icon-landslide::before { content: "⛰️"; }
.icon-building::before { content: "🏢"; }
.icon-report::before { content: "📝"; }
.icon-directions::before { content: "🧭"; }
.icon-distance::before { content: "📏"; }
.icon-capacity::before { content: "👥"; }
.icon-severity::before { content: "🔴"; }
.icon-navigate::before { content: "🚀"; }
.icon-share::before { content: "📤"; }
</style>