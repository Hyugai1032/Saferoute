<template>
  <div ref="dashRoot" class="dashboard-container">
    <div class="main-content">

      <!-- Dashboard Header with Logout -->
      <div class="dashboard-header">
        <div class="header-info">
          <h1>Admin Dashboard</h1>
          <p>Emergency Management System</p>
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

        <!-- <div class="metric-card">
          <div class="metric-icon warning">📦</div>
          <div class="metric-content">
            <h3>Supplies Alert</h3>
            <p class="metric-value">{{ lowSupplyCenters.length }}</p>
            <p class="metric-label">Centers need supplies</p>
          </div>
          <div class="metric-trend negative">-3</div>
        </div> -->

        <!-- <div class="metric-card">
          <div class="metric-icon critical">📊</div>
          <div class="metric-content">
            <h3>Risk Level</h3>
            <p class="metric-value">{{ overallRisk }}%</p>
            <p class="metric-label">48h forecast</p>
          </div>
          <div class="risk-indicator" :class="riskLevel"></div>
        </div> -->
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
            <div v-for="center in topStatusCenters" :key="center.id" class="center-item" @click="selectCenter(center)">
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
const dashRoot = ref(null)
const listCount = ref(5)
let quickMap = null
let mapResizeObserver = null
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
    (Number(center.family_capacity_max || 0) + Number(center.individual_capacity_max || 0))
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

// The full /evac-centers/ endpoint includes capacity, current_total and coordinates.
// (/evacuation-centers/ is the lightweight dropdown endpoint and does not.)
// Follows DRF `next` links in case global pagination is enabled.
const fetchAllPages = async (url) => {
  const all = []
  let next = url
  let pages = 0

  while (next && pages < 50) {
    const response = await fetch(next, {
      method: 'GET',
      headers: getAuthHeaders()
    })

    if (!response.ok) {
      throw new Error(`Failed to load centers: ${response.status}`)
    }

    const data = await response.json()

    if (Array.isArray(data)) return [...all, ...data]

    all.push(...(data.results || data.centers || []))
    // Behind a proxy (Railway), Django can emit `next` as http://. Upgrade it
    // so the browser doesn't block it as mixed content.
    next = data.next
      ? data.next.replace(/^http:\/\//, window.location.protocol === 'https:' ? 'https://' : 'http://')
      : null
    pages++
  }

  return all
}

const fetchCenters = async () => {
  loading.value = true
  error.value = ''

  try {
    const rawCenters = await fetchAllPages(`${API_BASE}evac_centers/evac-centers/`)
    centers.value = rawCenters.map(normalizeCenter)
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

const fetchBulkCenterRisk = async (ids) => {
  const response = await fetch(
    `${API_BASE}analytics/centers/congestion-risk-bulk/?center_ids=${ids.join(',')}&window=60&horizon=60`,
    { method: 'GET', headers: getAuthHeaders() }
  )
  if (!response.ok) throw new Error(`Bulk risk fetch failed: ${response.status}`)
  return await response.json()
}

const refreshDashboardRisks = async () => {
  if (!centers.value.length) return

  try {
    centerRisks.value = await fetchBulkCenterRisk(centers.value.map(c => c.id))
  } catch (err) {
    console.error('Bulk risk fetch failed:', err)
    centerRisks.value = []
  }
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

// How many centers to list: always at least 5 (as before), more on
// screens that are taller relative to their scale (16:10, 4:3, etc.).
const updateListCount = () => {
  if (!dashRoot.value) return
  if (window.innerWidth <= 1200) { listCount.value = 5; return } // stacked layout
  const unit = parseFloat(getComputedStyle(dashRoot.value).fontSize) || 16
  const viewportEm = window.innerHeight / unit
  const CHROME_EM = 27 // header + metric cards + paddings
  const ROW_EM = 9     // one center card incl. gap
  listCount.value = Math.min(12, Math.max(5, Math.floor((viewportEm - CHROME_EM) / ROW_EM)))
}

const topStatusCenters = computed(() =>
  [...statusCenters.value]
    .sort((a, b) => getPredictedPercentage(b) - getPredictedPercentage(a))
    .slice(0, listCount.value)
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

const waitForPaint = () =>
  new Promise(resolve => requestAnimationFrame(resolve))

const quickMapContainerExists = () => {
  const el = document.getElementById('quick-map')
  return el && el.isConnected
}

const safeQuickMapInvalidate = () => {
  if (!quickMap || !quickMapContainerExists()) return

  requestAnimationFrame(() => {
    if (quickMap && quickMapContainerExists()) {
      quickMap.invalidateSize()
    }
  })
}

const initializeQuickMap = async () => {
  await nextTick()
  await waitForPaint()

  const el = document.getElementById('quick-map')
  if (!el) return

  if (quickMap) {
    quickMap.stop()
    quickMap.off()
    quickMap.remove()
    quickMap = null
  }

  quickMap = L.map(el, {
    zoomAnimation: false,
  }).setView([13.0, 121.1], 9)

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(quickMap)

  mapLayerGroup = L.layerGroup().addTo(quickMap)

  updateMapMarkers()
  safeQuickMapInvalidate()

  // Keep Leaflet in sync whenever its panel changes size (window resize,
  // switching to a TV, sidebar collapse). This also prevents the dark
  // empty square / unloaded tiles after a resize.
  if (mapResizeObserver) mapResizeObserver.disconnect()
  if (typeof ResizeObserver !== 'undefined') {
    mapResizeObserver = new ResizeObserver(() => safeQuickMapInvalidate())
    mapResizeObserver.observe(el)
  }
}

const updateMapMarkers = () => {
  if (!quickMap || !mapLayerGroup) return

  mapLayerGroup.clearLayers()

  const riskById = new Map(
    statusCenters.value.map(center => [center.id, center])
  )

  const validCenters = mapCenters.value
  .map(center => ({
    ...center,
    latitude: Number(center.latitude),
    longitude: Number(center.longitude),
  }))
  .filter(center =>
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
    if (bounds.isValid()) {
      requestAnimationFrame(() => {
        if (quickMap && quickMapContainerExists()) {
          quickMap.fitBounds(bounds.pad(0.1))
        }
      })
    }
  }
}

watch(statusCenters, () => {
  updateMapMarkers()
}, { deep: true })

onMounted(async () => {
  updateListCount()
  window.addEventListener('resize', updateListCount)
  await fetchCenters()
  await refreshDashboardRisks()
  await fetchMapOverview()
  await initializeQuickMap()
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', updateListCount)
  if (mapResizeObserver) {
    mapResizeObserver.disconnect()
    mapResizeObserver = null
  }
  if (quickMap) {
    quickMap.stop()
    quickMap.off()
    quickMap.remove()
    quickMap = null
  }

  mapLayerGroup = null
})
</script>

<style scoped>
/* CHANGED: was hardcoded dark gradient + color:white; this class is also
   unused in the template (you use .dashboard-container), so it's dead
   weight either way — left as-is per your request, not touched further. */
.admin-layout {
  background: linear-gradient(135deg, #1a365d 0%, #1a1a2e 100%);
  min-height: 100vh;
  color: white;
}

/* ===== LARGE-SCREEN / TV SCALING =====
   --u is the size of "1rem" for this page. It equals 16px on anything up to
   1080p (so laptops/desktops look exactly like before) and grows on bigger
   screens. It uses the SMALLER of width-based and height-based scaling, so
   16:9, 16:10, 21:9 and 4:3 displays all get a layout that fits.
   The first font-size line is a fallback for old TV browsers without min()/clamp(). */
.dashboard-container {
  --u: 16px;
  font-size: var(--u);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  color: var(--text-primary); /* CHANGED: was hardcoded white */
  background: var(--bg-page, transparent); /* CHANGED: let theme control page bg */
}

@supports (font-size: clamp(16px, min(1vw, 1vh), 48px)) {
  .dashboard-container {
    --u: clamp(16px, min(0.8333vw, 1.4815vh), 48px);
  }
}


.main-content {
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  flex: 1;
  padding: calc(1.25 * var(--u));
  overflow-y: auto;
  min-height: 0;
  min-width: 0;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--u);
  padding: var(--u) 0;
  border-bottom: 1px solid var(--border-light); /* CHANGED: was rgba(255,255,255,0.1) */
}

.header-info h1 {
  margin: 0;
  font-size: calc(2 * var(--u));
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  /* NOTE: kept as a blue gradient clip-text on purpose — this one reads
     fine on both light and dark since it's a saturated gradient, not a
     near-white one. If you'd rather it follow --text-primary exactly,
     say so and I'll swap it too. */
}

.header-info p {
  color: var(--text-secondary); /* CHANGED: was #94a3b8 */
  margin: calc(0.5 * var(--u)) 0 0 0;
  font-size: var(--u);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: var(--u);
}

.logout-btn {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
  border: none;
  padding: calc(0.75 * var(--u)) calc(1.5 * var(--u));
  border-radius: calc(0.625 * var(--u));
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: calc(0.5 * var(--u));
  transition: all 0.3s;
}

.logout-btn:hover {
  transform: translateY(calc(-0.125 * var(--u)));
  box-shadow: 0 calc(0.625 * var(--u)) calc(1.25 * var(--u)) rgba(239, 68, 68, 0.3);
}

/* Alert Banner */
.alert-banner {
  padding: var(--u) calc(1.5 * var(--u));
  border-radius: calc(0.75 * var(--u));
  margin-bottom: var(--u);
}

.alert-banner.warning {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(245, 158, 11, 0.1));
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.alert-content {
  display: flex;
  align-items: center;
  gap: var(--u);
}

.alert-icon {
  font-size: calc(1.25 * var(--u));
}

.alert-text {
  flex: 1;
  color: #fbbf24;
}

.alert-action {
  background: rgba(245, 158, 11, 0.2);
  border: 1px solid rgba(245, 158, 11, 0.4);
  color: #fbbf24;
  padding: calc(0.5 * var(--u)) var(--u);
  border-radius: calc(0.5 * var(--u));
  cursor: pointer;
  transition: all 0.3s;
}

.alert-action:hover {
  background: rgba(245, 158, 11, 0.3);
}

/* Metrics Grid */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(calc(13.75 * var(--u)), 1fr));
  gap: var(--u);
  margin-bottom: calc(1.5 * var(--u));
}

.metric-card {
  background: var(--surface-elevated); /* CHANGED: was a white-tinted gradient that only worked on dark bg */
  border: 1px solid var(--border-light); /* CHANGED: was rgba(255,255,255,0.1) */
  border-radius: calc(1 * var(--u));
  padding: calc(1.5 * var(--u));
  display: flex;
  align-items: center;
  gap: var(--u);
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
  box-shadow: var(--shadow-soft); /* CHANGED: added so cards keep depth in light mode too */
}

.metric-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: calc(0.125 * var(--u));
  background: linear-gradient(90deg, var(--accent-color), transparent);
}

.metric-card:hover {
  transform: translateY(calc(-0.25 * var(--u)));
  box-shadow: 0 calc(1.25 * var(--u)) calc(2.5 * var(--u)) rgba(0, 0, 0, 0.3);
}

.metric-icon {
  width: calc(3.75 * var(--u));
  height: calc(3.75 * var(--u));
  border-radius: calc(0.75 * var(--u));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: calc(1.5 * var(--u));
}

.metric-icon.total { background: linear-gradient(135deg, #3b82f6, #1d4ed8); }
.metric-icon.active { background: linear-gradient(135deg, #10b981, #059669); }
.metric-icon.warning { background: linear-gradient(135deg, #f59e0b, #d97706); }
.metric-icon.critical { background: linear-gradient(135deg, #ef4444, #dc2626); }

.metric-content {
  flex: 1;
}

.metric-value {
  font-size: calc(2 * var(--u));
  font-weight: 800;
  margin: calc(0.25 * var(--u)) 0;
  /* CHANGED: this was the main bug — a near-white gradient clipped to
     text (#f1f5f9 -> #cbd5e1). On a light background that's basically
     white-on-white, so the big numbers vanished. Swapped to a solid
     theme-aware color instead of a clip-text gradient. */
  color: var(--text-primary);
  background: none;
  -webkit-background-clip: unset;
  -webkit-text-fill-color: unset;
}

.metric-label {
  color: var(--text-secondary); /* CHANGED: was #94a3b8 */
  font-size: calc(0.875 * var(--u));
  margin: 0;
}

.metric-trend {
  font-weight: 600;
  font-size: calc(0.875 * var(--u));
}

.metric-trend.positive { color: #10b981; }
.metric-trend.negative { color: #ef4444; }
.metric-trend.neutral { color: #6b7280; }

.risk-indicator {
  width: calc(0.5 * var(--u));
  height: calc(0.5 * var(--u));
  border-radius: 50%;
}

.risk-indicator.high { background: #ef4444; animation: pulse 2s infinite; }
.risk-indicator.medium { background: #f59e0b; }
.risk-indicator.low { background: #10b981; }

/* Content Grid */
.content-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: calc(1.5 * var(--u));
  align-items: stretch;
  flex: 1 1 auto; /* fill whatever height is left under the metric cards */
}

/* Very wide screens (21:9, 32:9 video walls): give the map more room */
@media (min-aspect-ratio: 2/1) and (min-width: 1201px) {
  .content-grid {
    grid-template-columns: minmax(0, 1fr) minmax(0, 1.4fr);
  }
}

.content-panel,
.content-panel.large {
  min-width: 0;
  grid-column: span 1;
  /* CHANGED: panels themselves had no background/border before — they
     were relying on the dark page gradient behind them. Give them an
     explicit theme-aware surface so they read correctly in light mode. */
  background: var(--surface-elevated);
  border: 1px solid var(--border-light);
  border-radius: calc(1 * var(--u));
  padding: calc(1.5 * var(--u));
  box-shadow: var(--shadow-soft);
  display: flex;
  flex-direction: column;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: calc(1.5 * var(--u));
  gap: var(--u); /* CHANGED: added so title + toggle don't collide on narrower panels */
  flex-wrap: wrap; /* CHANGED: lets the toggle drop to its own line instead of overlapping the title */
}

.panel-header h3 {
  margin: 0;
  color: var(--text-primary); /* CHANGED: was #f1f5f9 */
  font-size: calc(1.25 * var(--u));
}

.panel-actions {
  display: flex;
  gap: calc(0.75 * var(--u));
}

.btn-primary, .btn-secondary, .toggle-btn {
  font-size: calc(0.8333 * var(--u));
}

.btn-primary, .btn-secondary {
  padding: calc(0.5 * var(--u)) var(--u);
  border: none;
  border-radius: calc(0.5 * var(--u));
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s;
}

.btn-primary {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: white;
}

.btn-secondary {
  background: var(--surface-elevated); /* CHANGED: was rgba(255,255,255,0.1) */
  color: var(--text-secondary); /* CHANGED: was #cbd5e1 */
  border: 1px solid var(--border-light); /* CHANGED: was rgba(255,255,255,0.2) */
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
  background: var(--surface-elevated); /* CHANGED: was rgba(255,255,255,0.05) */
  padding: var(--u);
  text-align: left;
  font-weight: 600;
  color: var(--text-secondary); /* CHANGED: was #94a3b8 */
  font-size: calc(0.875 * var(--u));
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.data-table td {
  padding: var(--u);
  border-bottom: 1px solid var(--border-light); /* CHANGED: was rgba(255,255,255,0.05) */
  color: var(--text-primary); /* CHANGED: was #cbd5e1 */
}

.name-cell {
  display: flex;
  align-items: center;
  gap: calc(0.75 * var(--u));
}

.avatar-small {
  width: calc(2 * var(--u));
  height: calc(2 * var(--u));
  background: linear-gradient(135deg, #8b5cf6, #a855f7);
  border-radius: calc(0.5 * var(--u));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: calc(0.75 * var(--u));
  font-weight: 600;
  color: white;
}

.center-badge, .status-badge {
  padding: calc(0.25 * var(--u)) calc(0.75 * var(--u));
  border-radius: calc(1.25 * var(--u));
  font-size: calc(0.75 * var(--u));
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
  color: var(--text-secondary); /* CHANGED: was #cbd5e1 */
  border: 1px solid rgba(100, 116, 139, 0.3);
}

.action-buttons {
  display: flex;
  gap: calc(0.5 * var(--u));
}

.btn-icon {
  background: var(--surface-elevated); /* CHANGED: was rgba(255,255,255,0.1) */
  border: 1px solid var(--border-light); /* CHANGED: was rgba(255,255,255,0.2) */
  padding: calc(0.5 * var(--u));
  border-radius: calc(0.375 * var(--u));
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
  gap: var(--u);
}

.center-item {
  background: var(--surface-elevated); /* CHANGED: was rgba(255,255,255,0.03) */
  border: 1px solid var(--border-light); /* CHANGED: was rgba(255,255,255,0.1) */
  border-radius: calc(0.75 * var(--u));
  padding: var(--u);
  cursor: pointer;
  transition: all 0.3s;
}

.center-item:hover {
  background: rgba(255, 255, 255, 0.05);
  transform: translateX(calc(0.25 * var(--u)));
  border-color: rgba(59, 130, 246, 0.3);
}

.center-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: calc(0.5 * var(--u));
}

.center-header h4 {
  margin: 0;
  color: var(--text-primary); /* CHANGED: was #f1f5f9 */
  font-size: var(--u);
}

.status-indicator {
  width: calc(0.5 * var(--u));
  height: calc(0.5 * var(--u));
  border-radius: 50%;
}

.status-indicator.critical { background: #ef4444; animation: pulse 2s infinite; }
.status-indicator.warning { background: #f59e0b; }
.status-indicator.normal { background: #10b981; }

.center-location {
  color: var(--text-secondary); /* CHANGED: was #94a3b8 */
  font-size: calc(0.875 * var(--u));
  margin: 0 0 var(--u) 0;
}

.occupancy-info {
  margin-bottom: var(--u);
}

.progress-bar {
  width: 100%;
  height: calc(0.5 * var(--u));
  background: var(--border-light); /* CHANGED: was rgba(255,255,255,0.1) */
  border-radius: calc(0.25 * var(--u));
  overflow: hidden;
  margin-bottom: calc(0.5 * var(--u));
}

.progress-fill {
  height: 100%;
  border-radius: calc(0.25 * var(--u));
  transition: width 0.3s;
}

.progress-fill.critical { background: linear-gradient(90deg, #ef4444, #f87171); }
.progress-fill.warning { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.progress-fill.normal { background: linear-gradient(90deg, #10b981, #34d399); }

.occupancy-text {
  font-size: calc(0.875 * var(--u));
  color: var(--text-primary); /* CHANGED: was #cbd5e1 */
}

.supplies-overview {
  display: flex;
  flex-direction: column;
  gap: calc(0.5 * var(--u));
}

.supply-item {
  display: flex;
  align-items: center;
  gap: calc(0.75 * var(--u));
}

.supply-label {
  font-size: calc(0.75 * var(--u));
  color: var(--text-secondary); /* CHANGED: was #94a3b8 */
  min-width: calc(3.75 * var(--u));
  text-transform: capitalize;
}

.supply-bar {
  flex: 1;
  height: calc(0.25 * var(--u));
  background: var(--border-light); /* CHANGED: was rgba(255,255,255,0.1) */
  border-radius: calc(0.125 * var(--u));
  overflow: hidden;
}

.supply-fill {
  height: 100%;
  border-radius: calc(0.125 * var(--u));
  transition: width 0.3s;
}

.supply-fill.critical { background: #ef4444; }
.supply-fill.warning { background: #f59e0b; }
.supply-fill.normal { background: #10b981; }

/* View Toggle */
.view-toggle {
  display: flex;
  background: var(--surface-elevated); /* CHANGED: was rgba(255,255,255,0.05) */
  border-radius: calc(0.5 * var(--u));
  padding: calc(0.25 * var(--u));
  flex-shrink: 0; /* CHANGED: stop it from squishing against the h3 title */
}

.toggle-btn {
  padding: calc(0.5 * var(--u)) var(--u);
  border: none;
  background: transparent;
  color: var(--text-secondary); /* CHANGED: was #94a3b8 */
  cursor: pointer;
  border-radius: calc(0.375 * var(--u));
  transition: all 0.3s;
  white-space: nowrap; /* CHANGED: keep "Full List" from wrapping awkwardly */
}

.toggle-btn.active {
  background: rgba(59, 130, 246, 0.2);
  color: var(--accent-primary); /* CHANGED: was #60a5fa */
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
    padding: calc(0.9375 * var(--u));
  }

  .dashboard-header {
    flex-direction: column;
    gap: var(--u);
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
    gap: var(--u);
    align-items: flex-start;
  }
  
  .panel-actions {
    width: 100%;
    justify-content: flex-end;
  }
}

/* Quick Map Styles */
.quick-map-container {
  flex: 1 1 0;                       /* stretch to the bottom of the panel */
  min-height: calc(30 * var(--u));   /* never collapse on short screens */
  border-radius: calc(0.75 * var(--u));
  overflow: hidden;
}

/* CHANGED: added — mirrors the exact override already used in the GIS
   map component. Without this, any global dark-mode filter rule applied
   to Leaflet tiles elsewhere in the app still hits this map (since
   Leaflet injects its DOM outside Vue's scoped-style reach), which is
   why this map looked "inverted"/wrong in dark mode while the GIS tab
   didn't. */
.quick-map-container :deep(.leaflet-container),
.quick-map-container :deep(.leaflet-tile-pane),
.quick-map-container :deep(.leaflet-layer),
.quick-map-container :deep(.leaflet-tile) {
  filter: none !important;
  -webkit-filter: none !important;
}
</style>