<template>
  <div class="dashboard-container">
    <div class="main-content" :style="mainContentStyle">

      <!-- Dashboard Header with Logout -->
      <div class="dashboard-header">
        <div class="header-info">
          <h1>Admin Dashboard</h1>
          <p>Emergency Management System</p>
        </div>


        <div class="header-actions">
          <button class="logout-btn" @click="logout">
            <i class="icon-logout"></i>
            Logout
          </button>
        </div>
      </div>

      <!-- Emergency Alert Banner -->
      <div class="alert-banner warning" v-if="criticalCenters.length > 0">
        <div class="alert-content">
          <span class="alert-icon">⚠️</span>
          <div class="alert-text">
            <strong>Critical Alert:</strong> {{ criticalCenters.length }} evacuation center(s) are at critical capacity
          </div>
          <button class="alert-action" @click="showCriticalCenters">View Details</button>
        </div>
      </div>

      <!-- Key Metrics -->
      <div class="metrics-grid">
        <div class="metric-card">
          <div class="metric-icon total">👥</div>
          <div class="metric-content">
            <h3>Total Evacuees</h3>
            <p class="metric-value">{{ totalEvacuees.toLocaleString() }}</p>
            <p class="metric-label">Across {{ centers.length }} centers</p>
          </div>
          <div class="metric-trend positive">+12%</div>
        </div>

        <div class="metric-card">
          <div class="metric-icon active">🏠</div>
          <div class="metric-content">
            <h3>Active Centers</h3>
            <p class="metric-value">{{ centers.length }}</p>
            <p class="metric-label">Real-time monitoring</p>
          </div>
          <div class="metric-trend neutral">±0</div>
        </div>

        <div class="metric-card">
          <div class="metric-icon warning">📦</div>
          <div class="metric-content">
            <h3>Supplies Alert</h3>
            <p class="metric-value">{{ lowSupplyCenters.length }}</p>
            <p class="metric-label">Centers need supplies</p>
          </div>
          <div class="metric-trend negative">-3</div>
        </div>

        <div class="metric-card">
          <div class="metric-icon critical">📊</div>
          <div class="metric-content">
            <h3>Risk Level</h3>
            <p class="metric-value">{{ overallRisk }}%</p>
            <p class="metric-label">48h forecast</p>
          </div>
          <div class="risk-indicator" :class="riskLevel"></div>
        </div>
      </div>

      <!-- Main Content Grid -->
      <div class="content-grid">
        <!-- Center Status (replaced Evacuees Overview in large panel) -->
        <div class="content-panel large">
          <div class="panel-header">
            <h3>📍 Center Status</h3>
            <div class="view-toggle">
              <button class="toggle-btn active">List</button>
              <button class="toggle-btn" @click="navigateToFullMap">Full Map</button>
            </div>
          </div>
          
          <div class="centers-list">
            <div v-for="center in sortedCenters" :key="center.id" class="center-item" @click="selectCenter(center)">
              <div class="center-header">
                <h4>{{ center.name }}</h4>
                <span class="status-indicator" :class="getStatusLevel(center)"></span>
              </div>
              <p class="center-location">{{ center.municipality }}</p>
              
              <div class="occupancy-info">
                <div class="progress-bar">
                  <div 
                    class="progress-fill" 
                    :class="getStatusLevel(center)"
                    :style="{ width: getOccupancyPercentage(center) + '%' }"
                  ></div>
                </div>
                <span class="occupancy-text">
                  {{ center.occupants }} / {{ center.capacity }} ({{ getOccupancyPercentage(center) }}%)
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Map View (replaced original Center Status) -->
        <div class="content-panel">
          <div class="panel-header">
            <h3>🗺️ Quick Map View</h3>
            <button class="btn-secondary" @click="navigateToFullMap">Full View</button>
          </div>
          
          <div id="quick-map" class="quick-map-container"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { centers, getStatusLevel } from '@/data/centers'

const router = useRouter()
const sidebarCollapsed = ref(false)

// Update your main content style to be responsive to sidebar state
const mainContentStyle = computed(() => ({
  marginLeft: sidebarCollapsed.value ? '0px' : '280px',
  transition: 'margin-left 0.4s cubic-bezier(0.4, 0, 0.2, 1)'
}))

// Computed properties
const totalEvacuees = computed(() => 
  centers.reduce((sum, center) => sum + center.occupants, 0)
)

const criticalCenters = computed(() =>
  centers.filter(center => getStatusLevel(center) === 'critical')
)

const lowSupplyCenters = computed(() =>
  centers.filter(center => 
    Object.values(center.supplies).some(supply => supply < 50)
  )
)

const overallRisk = computed(() => 
  Math.round(60 + Math.random() * 20)
)

const riskLevel = computed(() => 
  overallRisk.value >= 70 ? 'high' : overallRisk.value >= 50 ? 'medium' : 'low'
)

const sortedCenters = computed(() =>
  [...centers].sort((a, b) => (b.occupants / b.capacity) - (a.occupants / a.capacity))
)

// Methods
const logout = () => {
  localStorage.removeItem('isAuthenticated')
  localStorage.removeItem('userData')
  router.push('/auth/login')
}

const getOccupancyPercentage = (center) => 
  Math.round((center.occupants / center.capacity) * 100)


const selectCenter = (center) => {
  // Navigate to GIS map with center selected
  console.log('Selected center:', center)
}

const showCriticalCenters = () => {
  alert(`Critical centers:\n${criticalCenters.value.map(c => `• ${c.name} (${getOccupancyPercentage(c)}%)`).join('\n')}`)
}

const navigateToFullMap = () => {
  router.push('/admin/map')
}

let quickMap

const initializeQuickMap = () => {
  quickMap = L.map('quick-map').setView([13.0, 121.1], 9)  // Oriental Mindoro coordinates

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(quickMap)

  centers.forEach(center => {
    const percentage = getOccupancyPercentage(center)
    const color = percentage >= 90 ? '#ef4444' : percentage >= 70 ? '#f59e0b' : '#10b981'

    const marker = L.circleMarker([center.lat, center.lon], {
      radius: 8,
      color: '#fff',
      weight: 1,
      fillColor: color,
      fillOpacity: 0.8
    }).addTo(quickMap)

    marker.bindPopup(`
      <strong>${center.name}</strong><br>
      Occupancy: ${percentage}%<br>
      ${center.municipality}
    `)
  })

  // Fit bounds
  const group = L.featureGroup(centers.map(c => L.marker([c.lat, c.lon])))
  quickMap.fitBounds(group.getBounds().pad(0.1))
}

onMounted(() => {
  // Load sidebar state from localStorage
  const savedState = localStorage.getItem('sidebarCollapsed');
  if (savedState) {
    sidebarCollapsed.value = savedState === 'true';
  }

  initializeQuickMap()
})
</script>

<style scoped>
.admin-layout {
  background: linear-gradient(135deg, #1a365d 0%, #1a1a2e 100%);
  min-height: 100vh;
  color: white;
}

.dashboard-container {
  display: flex;
  min-height: 100vh;
}

.main-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  min-height: 100vh;
  transition: margin-left 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  margin-left: 280px; /* Default sidebar width */
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding: 1rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.header-info h1 {
  margin: 0;
  color: #f1f5f9;
  font-size: 2rem;
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.header-info p {
  color: #94a3b8;
  margin: 0.5rem 0 0 0;
  font-size: 1rem;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logout-btn {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s;
}

.logout-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(239, 68, 68, 0.3);
}

/* Alert Banner */
.alert-banner {
  padding: 1rem 1.5rem;
  border-radius: 12px;
  margin-bottom: 1rem;
}

.alert-banner.warning {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(245, 158, 11, 0.1));
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.alert-content {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.alert-icon {
  font-size: 1.25rem;
}

.alert-text {
  flex: 1;
  color: #fbbf24;
}

.alert-action {
  background: rgba(245, 158, 11, 0.2);
  border: 1px solid rgba(245, 158, 11, 0.4);
  color: #fbbf24;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.alert-action:hover {
  background: rgba(245, 158, 11, 0.3);
}

/* Metrics Grid */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.metric-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.02));
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
}

.metric-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, var(--accent-color), transparent);
}

.metric-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.metric-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.metric-icon.total { background: linear-gradient(135deg, #3b82f6, #1d4ed8); }
.metric-icon.active { background: linear-gradient(135deg, #10b981, #059669); }
.metric-icon.warning { background: linear-gradient(135deg, #f59e0b, #d97706); }
.metric-icon.critical { background: linear-gradient(135deg, #ef4444, #dc2626); }

.metric-content {
  flex: 1;
}

.metric-value {
  font-size: 2rem;
  font-weight: 800;
  margin: 0.25rem 0;
  background: linear-gradient(135deg, #f1f5f9, #cbd5e1);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.metric-label {
  color: #94a3b8;
  font-size: 0.875rem;
  margin: 0;
}

.metric-trend {
  font-weight: 600;
  font-size: 0.875rem;
}

.metric-trend.positive { color: #10b981; }
.metric-trend.negative { color: #ef4444; }
.metric-trend.neutral { color: #6b7280; }

.risk-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.risk-indicator.high { background: #ef4444; animation: pulse 2s infinite; }
.risk-indicator.medium { background: #f59e0b; }
.risk-indicator.low { background: #10b981; }

/* Content Grid */
.content-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1.5rem;
}

.content-panel {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.02));
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 1.5rem;
}

.content-panel.large {
  grid-column: 1;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
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

.btn-primary, .btn-secondary {
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

.btn-primary:hover, .btn-secondary:hover {
  transform: translateY(-1px);
}

/* Table Styles */
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

.name-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.avatar-small {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #8b5cf6, #a855f7);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
  color: white;
}

.center-badge, .status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
}

.center-badge.critical, .status-badge.needs-aid {
  background: rgba(239, 68, 68, 0.2);
  color: #fca5a5;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.center-badge.warning, .status-badge.chronic-illness {
  background: rgba(245, 158, 11, 0.2);
  color: #fcd34d;
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.center-badge.normal, .status-badge.stable {
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

/* Centers List */
.centers-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.center-item {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.3s;
}

.center-item:hover {
  background: rgba(255, 255, 255, 0.05);
  transform: translateX(4px);
  border-color: rgba(59, 130, 246, 0.3);
}

.center-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.center-header h4 {
  margin: 0;
  color: #f1f5f9;
  font-size: 1rem;
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-indicator.critical { background: #ef4444; animation: pulse 2s infinite; }
.status-indicator.warning { background: #f59e0b; }
.status-indicator.normal { background: #10b981; }

.center-location {
  color: #94a3b8;
  font-size: 0.875rem;
  margin: 0 0 1rem 0;
}

.occupancy-info {
  margin-bottom: 1rem;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.progress-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s;
}

.progress-fill.critical { background: linear-gradient(90deg, #ef4444, #f87171); }
.progress-fill.warning { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.progress-fill.normal { background: linear-gradient(90deg, #10b981, #34d399); }

.occupancy-text {
  font-size: 0.875rem;
  color: #cbd5e1;
}

.supplies-overview {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.supply-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.supply-label {
  font-size: 0.75rem;
  color: #94a3b8;
  min-width: 60px;
  text-transform: capitalize;
}

.supply-bar {
  flex: 1;
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  overflow: hidden;
}

.supply-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.3s;
}

.supply-fill.critical { background: #ef4444; }
.supply-fill.warning { background: #f59e0b; }
.supply-fill.normal { background: #10b981; }

/* View Toggle */
.view-toggle {
  display: flex;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 4px;
}

.toggle-btn {
  padding: 0.5rem 1rem;
  border: none;
  background: transparent;
  color: #94a3b8;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.3s;
}

.toggle-btn.active {
  background: rgba(59, 130, 246, 0.2);
  color: #60a5fa;
}

/* Icon styles */
.icon-logout::before { content: "🚪"; }

/* Animations */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Responsive Design */
@media (max-width: 1200px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
  
  .content-panel.large {
    grid-column: 1;
  }
}

@media (max-width: 768px) {
  .main-content {
    margin-left: 0 !important;
    padding: 15px;
  }

  .dashboard-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .header-actions {
    width: 100%;
    justify-content: center;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
  }
  
  .panel-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .panel-actions {
    width: 100%;
    justify-content: flex-end;
  }
}

/* Quick Map Styles */
.quick-map-container {
  height: 900px;
  border-radius: 12px;
  overflow: hidden;
}
</style>