<template>
  <div class="dashboard-container">
    <div class="main-content">

      <!-- Dashboard Header with Logout -->
      <div class="dashboard-header">
        <div class="header-info">
          <h1>Admin Dashboard</h1>
          <p>Emergency Management System</p>
        </div>


        <div class="header-actions">
          <button class="btn-logout" @click="logout">
            Logout
          </button>
        </div>
      </div>

      <!-- Emergency Alert Banner -->
      <!-- <div class="alert-banner warning" v-if="criticalCenters.length > 0">
        <div class="alert-content">
          <span class="alert-icon">⚠️</span>
          <div class="alert-text">
            <strong>Critical Alert:</strong> {{ criticalCenters.length }} evacuation center(s) are at critical capacity
          </div>
          <button class="alert-action" @click="showCriticalCenters">View Details</button>
        </div>
      </div> -->

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

        <!-- <div class="metric-card">
          <div class="metric-icon warning">📦</div>
          <div class="metric-content">
            <h3>Supplies Alert</h3>
            <p class="metric-value">{{ lowSupplyCenters.length }}</p>
            <p class="metric-label">Centers need supplies</p>
          </div>
          <div class="metric-trend negative">-3</div>
        </div> -->

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
            <h3>📍 Most Congested Centers</h3>
            <div class="view-toggle">
              <button class="toggle-btn active">List</button>
              <button class="toggle-btn" @click="router.push('/admin/analytics')">Full List</button>
            </div>
          </div>
          
          <div class="centers-list">
            <div v-for="center in top5StatusCenters" :key="center.id" class="center-item" @click="selectCenter(center)">
              <div class="center-header">
                <h4>{{ center.name }}</h4>
                <span class="status-indicator" :class="getStatusLevel(center)"></span>
              </div>
              <p class="center-location">{{ center.municipality }}</p>
              
              <div class="occupancy-info">
                <div
                  class="progress-fill"
                  :class="center.riskLevel?.toLowerCase()"
                  :style="{ width: center.predictedPct + '%' }"
                ></div>

                <span class="occupancy-text">
                  {{ center.predictedTotal }} / {{ center.capacity }} ({{ center.predictedPct }}%)
                </span>

                <small class="muted">Current: {{ center.occupants }}</small>
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
import { ref, computed, onMounted, nextTick, watch, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const router = useRouter()
const API_BASE = import.meta.env.VITE_API_BASE_URL

const centers = ref([])
const centerRisks = ref([])
const loading = ref(false)
const error = ref('')
const mapCenters = ref([])
let quickMap = null
let mapLayerGroup = null

const getAuthHeaders = () => {
  const token = localStorage.getItem('access_token')
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {})
  }
}

const normalizeCenter = (center) => ({
  id: center.id,
  name: center.name || 'Unnamed Center',
  municipality:
    center.municipality_name ||
    center.municipality?.name ||
    center.municipality ||
    'Unknown Municipality',

  capacity: Number(
    center.capacity ??
    center.family_capacity_max ??
    center.individual_capacity_max ??
    0
  ),

  occupants: Number(
    center.current_evacuees ??
    center.current_total_evacuees ??
    center.current_total ??
    center.occupants ??
    0
  ),

  lat: Number(
    center.latitude ??
    center.lat ??
    center.location_lat ??
    center.location_lng_lat ??
    center.coordinates?.lat ??
    center.geometry?.coordinates?.[1] ??
    0
  ),

  lon: Number(
    center.longitude ??
    center.lon ??
    center.lng ??
    center.location_lon ??
    center.location_lng ??
    center.coordinates?.lng ??
    center.coordinates?.lon ??
    center.geometry?.coordinates?.[0] ??
    0
  ),
})

const fetchCenters = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await fetch(`${API_BASE}evac_centers/evacuation-centers/`, {
      method: 'GET',
      headers: getAuthHeaders()
    })

    if (!response.ok) {
      throw new Error(`Failed to load centers: ${response.status}`)
    }

    const data = await response.json()
    const rawCenters = Array.isArray(data) ? data : (data.results || [])
    console.log('raw center sample:', rawCenters[0])
    centers.value = rawCenters.map(normalizeCenter)

    console.log('Centers loaded:', centers.value)
  } catch (err) {
    console.error('Dashboard fetch error:', err)
    error.value = err.message || 'Failed to load dashboard data.'
  } finally {
    loading.value = false
  }
}

const normalizeMapCenter = (center) => ({
  id: center.id,
  name: center.name || 'Unnamed Center',
  municipality:
    center.municipality_name ||
    center.municipality?.name ||
    center.municipality ||
    'Unknown Municipality',

  latitude: Number(center.latitude ?? 0),
  longitude: Number(center.longitude ?? 0),

  capacity: Number(
    center.capacity ??
    (Number(center.family_capacity_max || 0) + Number(center.individual_capacity_max || 0))
  ),

  occupants: Number(
    center.current_total ??
    center.current_evacuees ??
    center.current_total_evacuees ??
    0
  )
})

const fetchMapOverview = async () => {
  try {
    const response = await fetch(`${API_BASE}map/overview/`, {
      method: 'GET',
      headers: getAuthHeaders()
    })

    if (!response.ok) {
      throw new Error(`Failed to load map overview: ${response.status}`)
    }

    const data = await response.json()
    mapCenters.value = (data.centers || []).map(normalizeMapCenter)
  } catch (err) {
    console.error('Map overview fetch error:', err)
  }
}

// IMPORTANT:
// Change this URL if your Analytics.vue uses a different analytics endpoint.

const fetchCenterRisk = async (centerId) => {
  const response = await fetch(
    `${API_BASE}analytics/centers/${centerId}/congestion-risk/?window=60&horizon=60`,
    {
      method: 'GET',
      headers: getAuthHeaders()
    }
  )

  if (!response.ok) {
    const txt = await response.text()
    throw new Error(`Risk fetch failed (${response.status}): ${txt}`)
  }

  return await response.json()
}

const refreshDashboardRisks = async () => {
  if (!centers.value.length) return

  const results = await Promise.all(
    centers.value.map(center => fetchCenterRisk(center.id).catch(() => null))
  )

  centerRisks.value = results.filter(Boolean)
  console.log(
  'center ids sample:',
  centers.value.slice(0, 5).map(c => ({ id: c.id, type: typeof c.id, lat: c.lat, lon: c.lon }))
)

console.log(
  'risk ids sample:',
  centerRisks.value.slice(0, 5).map(r => ({ center_id: r.center_id, type: typeof r.center_id }))
)
}

const getOccupancyPercentage = (center) => {
  if (!center.capacity) return 0
  return Math.round((center.occupants / center.capacity) * 100)
}

const chartLabels = computed(() =>
  top5PredictedOccupancy.value.map(c => c.center_name || `Center ${c.center_id}`)
)

const chartValues = computed(() =>
  top5PredictedOccupancy.value.map(c =>
    Number(c.predicted_occupancy ?? 0) <= 1
      ? Math.round(Number(c.predicted_occupancy ?? 0) * 100)
      : Math.round(Number(c.predicted_occupancy ?? 0))
  )
)

const getPredictedPercentage = (center) => {
  if (typeof center.predictedPct === 'number') return center.predictedPct
  return getOccupancyPercentage(center)
}

const getStatusLevel = (center) => {
  const percentage = getPredictedPercentage(center)
  if (percentage >= 90) return 'critical'
  if (percentage >= 70) return 'warning'
  return 'safe'
}

// Merge center metadata + analytics risk rows
const statusCenters = computed(() => {
  const centerMap = new Map(
    centers.value.map(c => [String(c.id), c])
  )

  if (!centerRisks.value.length) {
    return centers.value.map(center => ({
      ...center,
      predictedTotal: center.occupants ?? 0,
      predictedPct: getOccupancyPercentage(center),
      riskLevel: getStatusLevel(center),
    }))
  }

  return centerRisks.value.map(risk => {
    const rawCenterId =
      risk.center_id ??
      risk.center ??
      risk.evacuation_center_id ??
      risk.id

    const center = centerMap.get(String(rawCenterId)) || {}

    const capacity = Number(
      risk.capacity ??
      center.capacity ??
      center.family_capacity_max ??
      center.individual_capacity_max ??
      0
    )

    const occupants = Number(
      risk.current_total ??
      center.occupants ??
      center.current_total ??
      center.current_evacuees ??
      center.current_total_evacuees ??
      0
    )

    const predictedPct =
      risk.predicted_occupancy != null
        ? Math.round(
            Number(risk.predicted_occupancy) <= 1
              ? Number(risk.predicted_occupancy) * 100
              : Number(risk.predicted_occupancy)
          )
        : capacity > 0
          ? Math.round((occupants / capacity) * 100)
          : 0

    return {
      id: rawCenterId,
      name: center.name || risk.center_name || `Center #${rawCenterId}`,
      municipality:
        center.municipality_name ||
        center.municipality?.name ||
        center.municipality ||
        risk.municipality_name ||
        'Unknown Municipality',

      occupants,
      capacity,
      predictedTotal: Number(risk.predicted_total ?? occupants),
      predictedPct,
      riskLevel: (risk.risk_level || '').toLowerCase() || getStatusLevel({ predictedPct }),

      lat: Number(center.lat ?? center.latitude ?? risk.lat ?? risk.latitude ?? 0),
      lon: Number(center.lon ?? center.longitude ?? risk.lon ?? risk.longitude ?? 0),
    }
  })
})

const top5StatusCenters = computed(() =>
  [...statusCenters.value]
    .sort((a, b) => getPredictedPercentage(b) - getPredictedPercentage(a))
    .slice(0, 5)
)

const totalEvacuees = computed(() =>
  statusCenters.value.reduce((sum, center) => sum + Number(center.occupants || 0), 0)
)

const criticalCenters = computed(() =>
  statusCenters.value.filter(center => getStatusLevel(center) === 'critical')
)

const lowSupplyCenters = computed(() =>
  statusCenters.value.filter(center =>
    center.supplies &&
    Object.values(center.supplies).some(supply => Number(supply) < 50)
  )
)

const overallRisk = computed(() => {
  if (!statusCenters.value.length) return 0

  const avgOccupancy =
    statusCenters.value.reduce((sum, center) => sum + getPredictedPercentage(center), 0) /
    statusCenters.value.length

  return Math.round(avgOccupancy)
})

const riskLevel = computed(() =>
  overallRisk.value >= 70 ? 'high' : overallRisk.value >= 50 ? 'medium' : 'low'
)

const sortedCenters = computed(() => statusCenters.value)

const logout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('isAuthenticated')
  localStorage.removeItem('userData')
  router.push('/auth/login')
}

const selectCenter = (center) => {
  console.log('Selected center:', center)
}

const showCriticalCenters = () => {
  alert(
    `Critical centers:\n${criticalCenters.value
      .map(c => `• ${c.name} (${getPredictedPercentage(c)}%)`)
      .join('\n')}`
  )
}

const navigateToFullMap = () => {
  router.push('/admin/map')
}

const initializeQuickMap = async () => {
  await nextTick()

  if (quickMap) {
    quickMap.remove()
    quickMap = null
  }

  quickMap = L.map('quick-map').setView([13.0, 121.1], 9)

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(quickMap)

  mapLayerGroup = L.layerGroup().addTo(quickMap)
  updateMapMarkers()
}

const updateMapMarkers = () => {
  if (!quickMap || !mapLayerGroup) return

  mapLayerGroup.clearLayers()

  const riskById = new Map(
    statusCenters.value.map(center => [center.id, center])
  )

  const validCenters = mapCenters.value.filter(center =>
    Number.isFinite(center.latitude) &&
    Number.isFinite(center.longitude) &&
    !(center.latitude === 0 && center.longitude === 0)
  )

  validCenters.forEach(center => {
    const riskCenter = riskById.get(center.id)

    const percentage = riskCenter
      ? getPredictedPercentage(riskCenter)
      : (center.capacity > 0
          ? Math.round((center.occupants / center.capacity) * 100)
          : 0)

    const color =
      percentage >= 90 ? '#ef4444' :
      percentage >= 70 ? '#f59e0b' :
      '#10b981'

    const marker = L.circleMarker([center.latitude, center.longitude], {
      radius: 8,
      color: '#fff',
      weight: 1,
      fillColor: color,
      fillOpacity: 0.8
    })

    marker.bindPopup(`
      <strong>${center.name}</strong><br>
      Municipality: ${center.municipality}<br>
      Current: ${riskCenter?.occupants ?? center.occupants} / ${riskCenter?.capacity ?? center.capacity}<br>
      Predicted: ${riskCenter?.predictedTotal ?? center.occupants} (${percentage}%)
    `)

    mapLayerGroup.addLayer(marker)
  })

  if (validCenters.length > 0) {
    const bounds = L.latLngBounds(validCenters.map(c => [c.latitude, c.longitude]))
    quickMap.fitBounds(bounds.pad(0.1))
  }
}

watch(statusCenters, () => {
  updateMapMarkers()
}, { deep: true })

onMounted(async () => {
  await fetchCenters()
  await refreshDashboardRisks()
  await fetchMapOverview()
  await initializeQuickMap()
})

onBeforeUnmount(() => {
  if (quickMap) {
    quickMap.remove()
    quickMap = null
  }
})
</script>

<style scoped>
.admin-layout {
  background: linear-gradient(135deg, #1a365d 0%, #1a1a2e 100%);
  min-height: 100vh;
  color: white;
}

.dashboard-container {
  min-height: 100vh;
  color: white;
}


.main-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  min-height: 100vh;
  min-width: 0;
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
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1.5rem;
  align-items: stretch;
}

.content-panel,
.content-panel.large {
  min-width: 0;
  grid-column: span 1;
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