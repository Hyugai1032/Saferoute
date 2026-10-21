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
            <span>Most Likely Full (≥ 90%)</span>
          </div>
        </div>

        <div class="building-filter">
          <label v-for="type in buildingTypes" :key="type.value" class="filter-item">
            <input
              type="checkbox"
              :value="type.value"
              v-model="selectedTypes"
            />
            <span>{{ type.label }}</span>
          </label>
        </div>
        
        <div class="control-buttons">
          <button class="control-btn" @click="refreshData" title="Refresh Data">
            🔄
          </button>
          <button class="control-btn" @click="fitToBounds" title="Fit to Centers">
            🎯
          </button>
          <button class="control-btn" @click="suggestNearestCenter">
            🧭 Suggest Center
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
                <span class="info-value">{{ selectedCenter.municipality_name }} - {{ selectedCenter.barangay_name || "N/A" }}</span>
              </div>
              <!-- <div class="info-item">
                <span class="info-label">📞 Contact:</span>
                <span class="info-value">{{ selectedCenter.contact }}</span>
              </div> -->
              <div class="info-item">
                <span class="info-label">🕒 Last Update:</span>
                <span class="info-value">{{ selectedCenter.updated_at }}</span>
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
                    {{ getTotalOccupancy(selectedCenter) }} / {{ getTotalCapacity(selectedCenter) }} 
                    ({{ getOccupancyPercentage(selectedCenter) }}%)
                  </div>
                </div>
              </div>
            </div>

            <div class="metrics-section">
              <h4>Predicted Congestion</h4>

              <div class="progress-container">
                <div class="progress-bar large">
                  <div
                    class="progress-fill"
                    :class="getPercentLevel(getPredictedCongestion(selectedCenter))"
                    :style="{ width: (getPredictedCongestion(selectedCenter) || 0) + '%' }"
                  ></div>
                </div>

                <div class="progress-text">
                  <template v-if="getPredictedCongestion(selectedCenter) !== null">
                    {{ getPredictedCongestion(selectedCenter) }}%
                    — {{ getPredictedStatusText(selectedCenter) }}
                  </template>
                  <template v-else>
                    {{ predictionsReady ? 'Prediction unavailable' : 'Loading prediction…' }}
                  </template>
                </div>
              </div>
            </div>

            <div class="metrics-section" v-if="routeInfo">
              <h4>Route Info</h4>
              <div class="center-info">
                <div class="info-item">
                  <span class="info-label">📏 Distance:</span>
                  <span class="info-value">{{ routeInfo.distance_km }} km</span>
                </div>
                <div class="info-item">
                  <span class="info-label">⏱ Estimated Time of Arrival:</span>
                  <span class="info-value">{{ routeInfo.duration_min }} mins</span>
                </div>
              </div>
            </div>

            <!-- Supplies Section -->
            <!-- <div class="metrics-section">
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
            </div> -->

            <!-- Quick Actions -->
            <div class="action-buttons">
              <button class="action-btn primary" @click="routeToCenter(selectedCenter, true)">
                🧭 Route (Avoid Hazards)
              </button>

              <button class="action-btn secondary" @click="routeToCenter(selectedCenter, false)">
                🧭 Route (Shortest)
              </button>

              <button class="action-btn secondary" @click="clearRoute">
                ❌ Clear Route
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
import { ref, shallowRef, onMounted, onUnmounted, nextTick, watch, onActivated } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import api from '@/services/api'

// PERFORMANCE: a plain ref() wraps everything inside it in deep reactive proxies.
// For the Leaflet map/layers/markers and 300+ center objects that is slow and can
// even break Leaflet internals. shallowRef (or a plain Map) keeps them raw.
const centers = shallowRef([])
const hazards = shallowRef([])

const centerLayer = shallowRef(null)
const hazardLayer = shallowRef(null)
const gisLayer = shallowRef(null)
const routeLayer = shallowRef(null)

const osmLayer = shallowRef(null)
const routeInfo = ref(null) // { distance_km, duration_min }
const satelliteLayer = shallowRef(null)

// Non-reactive lookups (nothing in the template reads them).
const centerMarkers = new Map()   // center id -> { marker, sig, type }
let centersById = new Map()       // center id -> latest center data

// Fix for default markers in Leaflet
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

const map = shallowRef(null)
const selectedCenter = ref(null)

const selectedTypes = ref([
  'SCHOOL',
  'MULTIPURPOSE_HALL',
  'CHURCH',
  'PRIVATE_BUILDING',
  'GYM',
  'BARANGAY_HALL',
  'OTHER',
])

const buildingTypes = [
  { value: 'SCHOOL', label: '🏫 School' },
  { value: 'MULTIPURPOSE_HALL', label: '🏛 Hall' },
  { value: 'CHURCH', label: '⛪ Church' },
  { value: 'PRIVATE_BUILDING', label: '🏠 Private' },
  { value: 'GYM', label: '🏟 Gym' },
  { value: 'BARANGAY_HALL', label: '🏢 Barangay' },
  { value: 'OTHER', label: '📍 Other' },
]

// Methods

const getStatusColor = (center) => {
  const pct = getOccupancyPercentage(center)
  if (pct >= 90) return '#ef4444'
  if (pct >= 70) return '#f59e0b'
  return '#22c55e'
}

const getStatusLevel = (center) => {
  const pct = getOccupancyPercentage(center)
  if (pct >= 90) return 'critical'
  if (pct >= 70) return 'warning'
  return 'normal'
}

const getStatusText = (center) => {
  const pct = getOccupancyPercentage(center)
  if (pct >= 90) return 'Most Likely Full'
  if (pct >= 70) return 'Nearly Full'
  return 'Available'
}

const createCenterIcon = (center) => {
  const color = getStatusColor(center)
  const pulseClass = getOccupancyPercentage(center) >= 90 ? 'pulse-marker' : ''
  const buildingIcon = getBuildingIcon(center)
  const percentage = getOccupancyPercentage(center)
  const typeLabel = getBuildingType(center).replaceAll('_', ' ')
  const predicted = getPredictedCongestion(center)
  const predictedText = predicted != null
    ? `Pred: ${predicted}%`
    : (predictionsReady.value ? 'Pred: N/A' : 'Pred: …')

  return L.divIcon({
    className: `custom-marker ${pulseClass}`,
    html: `
      <div class="marker-pin" style="background: ${color}">
        <div class="marker-pulse"></div>
        <div class="marker-content">
          <span class="building-icon">${buildingIcon}</span>
        </div>
        <div class="marker-hover-badge">
          <span class="hover-badge-text">
            ${typeLabel}<br/>
            Now: ${percentage}%<br/>
            ${predictedText}
          </span>
        </div>
      </div>
    `,
    iconSize: [40, 40],
    iconAnchor: [20, 40],
    popupAnchor: [0, -40],
  })
}

const createHazardIcon = (hazard) => {
  // simple: red default marker (you can customize later)
  return L.divIcon({
    className: 'hazard-marker',
    html: `⚠️`,
    iconSize: [50, 50],
    iconAnchor: [15, 15],
  })
}

const getTotalCapacity = (c) =>
  Number(c.family_capacity_max || 0) + Number(c.individual_capacity_max || 0)

// until you compute occupancy, show 0
const getTotalOccupancy = (c) => 
  Number(c.current_total || 0)

const getOccupancyPercentage = (c) => {
  const cap = getTotalCapacity(c)
  const occ = getTotalOccupancy(c)
  if (!cap) return 0
  return Math.round((occ / cap) * 100)
}

// ---- API ----
// Client-side cache (sessionStorage, so it survives route changes and page reloads).
//  - younger than 60s: use it and make no network call
//  - up to 10 min old: show it instantly, then refresh in the background
const OVERVIEW_CACHE_KEY = 'gismap:overview:v1'
const OVERVIEW_FRESH_MS = 60 * 1000
const OVERVIEW_MAX_STALE_MS = 10 * 60 * 1000
const PREDICTION_KEYS = [
  'predicted_congestion_percent',
  'predicted_status',
  'prediction_note',
  'prediction_window_minutes',
]

const predictionsReady = ref(false)
let loadToken = 0
let hasFitted = false

const readOverviewCache = () => {
  try {
    const raw = sessionStorage.getItem(OVERVIEW_CACHE_KEY)
    if (!raw) return null
    const snap = JSON.parse(raw)
    if (!snap?.t || Date.now() - snap.t > OVERVIEW_MAX_STALE_MS) return null
    return snap
  } catch {
    return null
  }
}

const writeOverviewCache = () => {
  try {
    sessionStorage.setItem(
      OVERVIEW_CACHE_KEY,
      JSON.stringify({ t: Date.now(), centers: centers.value, hazards: hazards.value })
    )
  } catch {
    // Storage full/unavailable: the cache is only an optimisation, ignore.
  }
}

const applyOverview = (data) => {
  centers.value = data.centers || []
  hazards.value = data.hazards || []
  centersById = new Map(centers.value.map((c) => [c.id, c]))
}

// The fast (no-predictions) response has no prediction fields; keep the ones we
// already know so markers don't flicker back to "N/A" during a refresh.
const carryOverPredictions = (incoming) =>
  incoming.map((c) => {
    const old = centersById.get(c.id)
    if (!old) return c
    const out = { ...c }
    for (const k of PREDICTION_KEYS) {
      if (!(k in out) && k in old) out[k] = old[k]
    }
    return out
  })

const fitOnce = () => {
  if (hasFitted || !centers.value.length) return
  hasFitted = true
  fitToBounds()
}

const loadOverview = async ({ force = false } = {}) => {
  const token = ++loadToken
  const stillCurrent = () => token === loadToken && !isUnmounted.value && !!map.value

  // 1) Cached snapshot: instant paint.
  const snap = force ? null : readOverviewCache()
  if (snap) {
    applyOverview(snap)
    predictionsReady.value = true
    renderCenters()
    renderHazards()
    fitOnce()
    if (Date.now() - snap.t < OVERVIEW_FRESH_MS) return
  }

  // 2) Pins without predictions: quick, so the map is usable almost immediately.
  try {
    const fast = await api.get('/map/overview/', { publicOk: true, params: { predictions: 0 } })
    if (!stillCurrent()) return
    applyOverview({
      centers: carryOverPredictions(fast.data.centers || []),
      hazards: fast.data.hazards,
    })
    renderCenters()
    renderHazards()
    fitOnce()
  } catch (err) {
    console.error('Failed to load map pins:', err)
    return
  }

  // 3) Same data plus predictions. Slow only when the server cache is cold, and it no
  //    longer blocks the pins from showing.
  try {
    const full = await api.get('/map/overview/', { publicOk: true })
    if (!stillCurrent()) return
    applyOverview(full.data)
    renderHazards()
    writeOverviewCache()
  } catch (err) {
    console.error('Failed to load predictions:', err)
  } finally {
    if (stillCurrent()) {
      predictionsReady.value = true
      renderCenters()
    }
  }
}

const fetchCenterDetail = async (id) => {
  const res = await api.get(`/evac_centers/evac-centers/${id}/`, { publicOk: true })
  return res.data
}

const getBuildingType = (center) => {
  const name = (center.name || '').toUpperCase()

  if (name.includes('SCHOOL') || name.includes('ELEMENTARY') || name.includes('HIGHSCHOOL') || name.includes('MINSCAT') || name.includes('MINSU') || name.includes('NHS') || name.includes('COLLEGE') || name.includes('UNIVERSITY')) {
    return 'SCHOOL'
  }
  if (name.includes('CHURCH') || name.includes('CHAPEL') || name.includes('ADVENTIST') || name.includes('CHAPLAIN') || name.includes('IGLESIA')) {
    return 'CHURCH'
  }
  if (name.includes('GYM') || name.includes('GYMNASIUM')) {
    return 'GYM'
  }
  if (name.includes('MULTIPURPOSE')) {
    return 'MULTIPURPOSE_HALL'
  }
  if (name.includes('BARANGAY')) {
    return 'BARANGAY_HALL'
  }
  if (name.includes('PRIVATE') || name.includes('RESIDENCE') || name.includes('HOUSE')) {
    return 'PRIVATE_BUILDING'
  }

  return 'OTHER'
}

const getBuildingIcon = (center) => {
  switch (getBuildingType(center)) {
    case 'SCHOOL':
      return '🏫'
    case 'CHURCH':
      return '⛪'
    case 'GYM':
      return '🏟️'
    case 'MULTIPURPOSE_HALL':
      return '🏛️'
    case 'BARANGAY_HALL':
      return '🏢'
    case 'PRIVATE_BUILDING':
      return '🏠'
    default:
      return '📍'
  }
}


// ---- Rendering ----
// Markers are created once and then diffed: a marker is only touched when something it
// displays changed. Filtering by type adds/removes markers instead of rebuilding them.
const centerSignature = (c) =>
  [
    c.name,
    c.latitude,
    c.longitude,
    getOccupancyPercentage(c),
    getPredictedCongestion(c),
    predictionsReady.value ? 1 : 0,
  ].join('|')

const applyTypeFilter = () => {
  const layer = centerLayer.value
  if (!layer) return
  for (const { marker, type } of centerMarkers.values()) {
    const shouldShow = selectedTypes.value.includes(type)
    const isShown = layer.hasLayer(marker)
    if (shouldShow && !isShown) layer.addLayer(marker)
    else if (!shouldShow && isShown) layer.removeLayer(marker)
  }
}

const detailCache = new Map() // center id -> { t, data }
const DETAIL_TTL_MS = 30 * 1000

const getCenterDetail = async (id) => {
  const hit = detailCache.get(id)
  if (hit && Date.now() - hit.t < DETAIL_TTL_MS) return hit.data
  const data = await fetchCenterDetail(id)
  detailCache.set(id, { t: Date.now(), data })
  return data
}

const onCenterClick = async (id) => {
  const base = centersById.get(id)
  if (!base) return
  selectedCenter.value = base

  try {
    const full = await getCenterDetail(id)
    const merged = { ...(centersById.get(id) || base), ...full }

    // keep our data in sync so the next refresh/diff starts from the newest values
    centersById.set(id, merged)
    const idx = centers.value.findIndex((c) => c.id === id)
    if (idx !== -1) centers.value[idx] = merged

    const entry = centerMarkers.get(id)
    if (entry) {
      entry.marker.setIcon(createCenterIcon(merged))
      entry.sig = centerSignature(merged)
    }

    // ignore the response if the user has already clicked a different center
    if (selectedCenter.value?.id === id) selectedCenter.value = merged
  } catch (e) {
    console.error('Failed to fetch center detail:', e)
  }
}

const renderCenters = () => {
  const layer = centerLayer.value
  if (!layer) return

  const seen = new Set()

  for (const center of centers.value) {
    if (center.latitude == null || center.longitude == null) continue
    seen.add(center.id)

    const sig = centerSignature(center)
    const existing = centerMarkers.get(center.id)

    if (!existing) {
      const marker = L.marker([center.latitude, center.longitude], {
        icon: createCenterIcon(center),
      })
      marker.on('click', () => onCenterClick(center.id))
      centerMarkers.set(center.id, { marker, sig, type: getBuildingType(center) })
    } else if (existing.sig !== sig) {
      existing.marker.setLatLng([center.latitude, center.longitude])
      existing.marker.setIcon(createCenterIcon(center))
      existing.sig = sig
      existing.type = getBuildingType(center)
    }
  }

  // drop markers for centers that no longer exist
  for (const [id, entry] of centerMarkers) {
    if (!seen.has(id)) {
      layer.removeLayer(entry.marker)
      centerMarkers.delete(id)
    }
  }

  applyTypeFilter()
}

const renderHazards = () => {
  if (!hazardLayer.value) return
  hazardLayer.value.clearLayers()

  hazards.value.forEach((haz) => {
    if (haz.latitude == null || haz.longitude == null) return

    const marker = L.marker([haz.latitude, haz.longitude], {
      icon: createHazardIcon(haz),
    }).addTo(hazardLayer.value)

    marker.bindPopup(`
      <div>
        <b>${haz.title || 'Hazard'}</b><br/>
        Type: ${haz.hazard_type}<br/>
        Severity: ${haz.severity}<br/>
        Status: ${haz.status}
      </div>
    `)
  })
}

const drawRoute = (geometry, distanceM = 0, durationS = 0) => {
  if (!map.value || !routeLayer.value) return

  routeLayer.value.clearLayers()

  // Wrap as Feature to make Leaflet 100% happy
  const feature = {
    type: "Feature",
    properties: {},
    geometry, // {type:"LineString", coordinates:[[lng,lat],...]}
  }

  const routeGeo = L.geoJSON(feature, {
    style: { weight: 5 },
  }).addTo(routeLayer.value)

  safeFitBounds(routeGeo.getBounds(), 0.2)

  routeInfo.value = {
    distance_km: (Number(distanceM || 0) / 1000).toFixed(2),
    duration_min: Math.round(Number(durationS || 0) / 60),
  }

}

const routeToCenter = (center, avoidHazards = false) => {
  if (!center?.latitude || !center?.longitude) {
    alert("This center has no coordinates.")
    return
  }

  navigator.geolocation.getCurrentPosition(
    async (pos) => {
      try {
        const payload = {
          from: { lat: pos.coords.latitude, lng: pos.coords.longitude },
          to: { lat: Number(center.latitude), lng: Number(center.longitude) },
          avoid_hazards: avoidHazards,
        }

        const res = await api.post("/route/ors/", payload, { publicOk: true })
        drawRoute(res.data.geometry, res.data.distance_m, res.data.duration_s)
      } catch (e) {
        console.error("Routing failed:", e)
        alert("Routing failed. Check console / Network tab.")
      }
    },
    (err) => {
      console.error(err)
      alert("Please allow location access to route.")
    },
    { enableHighAccuracy: true, timeout: 15000 }
  )
}

const clearRoute = () => {
  routeLayer.value?.clearLayers()
  routeInfo.value = null
}

const fitMapToCenters = () => fitToBounds()

const isUnmounted = ref(false)

const waitForPaint = () =>
  new Promise(resolve => requestAnimationFrame(resolve))

const mapContainerExists = () => {
  const el = document.getElementById('map')
  return el && el.isConnected
}

const safeInvalidateSize = () => {
  if (!map.value || !mapContainerExists()) return

  requestAnimationFrame(() => {
    if (map.value && mapContainerExists()) {
      map.value.invalidateSize()
    }
  })
}

const safeFitBounds = (bounds, pad = 0.1) => {
  if (!map.value || !mapContainerExists()) return
  if (!bounds || !bounds.isValid || !bounds.isValid()) return

  requestAnimationFrame(() => {
    if (map.value && mapContainerExists()) {
      map.value.fitBounds(bounds.pad(pad))
    }
  })
}

const initializeMap = async () => {
  await nextTick()
  await waitForPaint()

  const el = document.getElementById('map')
  if (!el || map.value) return

  map.value = L.map(el, {
    zoomAnimation: false,
  }).setView([13.0, 121.1], 9)

  osmLayer.value = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors',
  })

  satelliteLayer.value = L.tileLayer('https://{s}.google.com/vt/lyrs=s&x={x}&y={z}', {
    maxZoom: 20,
    subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
    attribution: '&copy; Google',
  })

  osmLayer.value.addTo(map.value)

  centerLayer.value = L.layerGroup().addTo(map.value)
  hazardLayer.value = L.layerGroup().addTo(map.value)
  routeLayer.value = L.layerGroup().addTo(map.value)

  safeInvalidateSize()
  await loadOverview()
}

// ---- UI Buttons ----
const refreshData = async () => {
  if (!map.value) return
  await loadOverview({ force: true })
  safeInvalidateSize()
}

const fitToBounds = () => {
  const coords = centers.value
    .filter(c => c.latitude != null && c.longitude != null)
    .map(c => [c.latitude, c.longitude])

  if (!coords.length || !map.value) return

  safeFitBounds(L.latLngBounds(coords), 0.1)
}

const suggestNearestCenter = () => {
  navigator.geolocation.getCurrentPosition(
    async (pos) => {
      try {
        const payload = {
          from: {
            lat: pos.coords.latitude,
            lng: pos.coords.longitude,
          },
          avoid_hazards: true,
          recent_hours: 48,
          max_congestion_percent: 90,
          candidate_limit: 6,
        }

        const res = await api.post("/route/suggest-center/", payload, { publicOk: true })

        selectedCenter.value = res.data.center

        drawRoute(
          res.data.geometry,
          res.data.distance_m,
          res.data.duration_s
        )
      } catch (e) {
        console.error("Suggest center failed:", e)
        alert("Unable to suggest an available center.")
      }
    },
    (err) => {
      console.error(err)
      alert("Please allow location access.")
    },
    { enableHighAccuracy: true, timeout: 15000 }
  )
}

const getPredictedCongestion = (center) =>
  center.predicted_congestion_percent == null
    ? null
    : Number(center.predicted_congestion_percent)

const getPercentLevel = (pct) => {
  if (pct == null) return 'normal'
  if (pct >= 90) return 'critical'
  if (pct >= 70) return 'warning'
  return 'normal'
}

const getPredictedStatusText = (center) => {
  const pct = getPredictedCongestion(center)

  if (pct == null) return 'Prediction unavailable'
  if (pct >= 90) return 'Likely Full Soon'
  if (pct >= 70) return 'May Become Crowded'
  return 'Likely Available'
}

const handleResize = () => {
  safeInvalidateSize()
}

watch(selectedTypes, (val) => {
  localStorage.setItem('buildingFilter', JSON.stringify(val))
  applyTypeFilter()
}, { deep: true })

onMounted(async () => {
  isUnmounted.value = false

  const saved = localStorage.getItem('buildingFilter')
  if (saved) selectedTypes.value = JSON.parse(saved)

  await initializeMap()
  window.addEventListener('resize', handleResize)
})


onActivated(() => {
  safeInvalidateSize()
})

onUnmounted(() => {
  isUnmounted.value = true
  loadToken++            // any request still in flight will be ignored when it returns
  centerMarkers.clear()

  if (map.value) {
    map.value.stop()
    map.value.off()
    map.value.remove()
    map.value = null
  }

  centerLayer.value = null
  hazardLayer.value = null
  routeLayer.value = null
  osmLayer.value = null
  satelliteLayer.value = null

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
  /* Locked to its own dark palette on purpose: this component keeps a
     consistent look regardless of the app-wide light/dark toggle, so the
     map and its readouts never wash out. */
  color-scheme: dark;
  height: 100% !important;
  /* Also works when the parent is a flex column (e.g. the public wrapper
     below the navbar), without breaking the height:100% case above. */
  flex: 1 1 auto;
  min-height: 0;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #0c0f1d 0%, #1a1f38 100%) !important;
}

.map-header {
  background: rgba(15, 23, 42, 0.8) !important;
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
  color: #f1f5f9 !important;
  margin: 0 0 0.5rem 0;
}

.page-subtitle {
  color: #94a3b8 !important;
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
  background: rgba(15, 23, 42, 0.97) !important;
  backdrop-filter: blur(20px);
  border-left: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s;
  display: flex;
  flex-direction: column;
  z-index: 10;
  color-scheme: dark;
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
  background: transparent !important;
  color: #e2e8f0 !important;
}

.close-sidebar {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: rgba(255, 255, 255, 0.1) !important;
  border: none;
  color: #cbd5e1 !important;
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
  color: #f1f5f9 !important;
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
  gap: 0.6rem;
  background: rgba(255, 255, 255, 0.03) !important;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 0.9rem 1rem;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
}

.info-label {
  color: #94a3b8 !important;
  font-size: 0.8rem;
  white-space: nowrap;
}

.info-value {
  color: #e2e8f0 !important;
  font-size: 0.85rem;
  font-weight: 600;
  text-align: right;
  /* was inheriting an all-caps + wide letter-spacing look from elsewhere,
     which is what made "VICTORIA - VILLA CERVEZA" look oddly spaced out */
  text-transform: none;
  letter-spacing: normal;
}

.metrics-section {
  background: rgba(255, 255, 255, 0.035) !important;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 14px;
  padding: 1.1rem 1.25rem 1.25rem;
}

.metrics-section h4 {
  margin: 0 0 0.9rem 0;
  color: #f1f5f9 !important;
  font-size: 0.85rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: .06em;
  opacity: .85;
  text-align: center; 
}

.progress-container {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.progress-bar.large {
  height: 10px;
  background: rgba(255, 255, 255, 0.08) !important;
  border-radius: 999px;
  overflow: hidden;
  box-shadow: inset 0 0 0 1px rgba(255,255,255,0.06);
}

.progress-fill {
  height: 100%;
  border-radius: 999px;
  transition: width 0.3s;
}

.progress-fill.critical { background: linear-gradient(90deg, #ef4444, #f87171); }
.progress-fill.warning { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.progress-fill.normal { background: linear-gradient(90deg, #10b981, #34d399); }

.progress-text {
  color: #e2e8f0 !important;
  font-size: 0.85rem;
  font-weight: 700;
  text-align: left;

  text-align: center; 
  background: none;    
  padding: 0; 
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
  background: linear-gradient(135deg, #f6513b, #d8231d);
  color: white;
}

.action-btn.secondary {
  background: rgba(255, 255, 255, 0.1);
  color: #e1d5cb;
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
  background: transparent !important;
}

.placeholder-content {
  text-align: center;
  color: #94a3b8 !important;
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
  transition: transform 0.2s ease;
}

:deep(.marker-pin:hover) {
  z-index: 1000;
}

:deep(.marker-pin.shape-default .marker-content) {
  transform: translate(-50%, -50%) rotate(45deg);
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
  text-align: center;
  z-index: 2;
}

:deep(.building-icon) {
  font-size: 0.95rem;
  line-height: 1;
  display: inline-block;
}

:deep(.marker-hover-badge) {
  position: absolute;
  top: -38px;
  left: 50%;
  transform: translateX(-50%) rotate(45deg);
  background: rgba(15, 23, 42, 0.95);
  color: #fff;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.3rem 0.5rem;
  border-radius: 8px;
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s ease, transform 0.2s ease;
  border: 1px solid rgba(255, 255, 255, 0.15);
  z-index: 20;
}

:deep(.marker-pin:hover .marker-hover-badge) {
  opacity: 1;
  transform: translateX(-50%) translateY(-4px) rotate(45deg);
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

.building-filter {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  background: rgba(255,255,255,0.05) !important;
  padding: 0.75rem;
  border-radius: 12px;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.75rem;
  color: #cbd5e1 !important;
  background: rgba(255,255,255,0.05) !important;
  padding: 0.4rem 0.6rem;
  border-radius: 8px;
  cursor: pointer;
}

.filter-item input {
  cursor: pointer;
}

/* ---- Theme lock for the map itself ----
   Leaflet renders its tiles/canvas as plain <img>/<div> nodes injected
   directly into #map by JS, outside Vue's template — so Vue's scoped
   attribute never lands on them. If any global light/dark stylesheet
   applies a filter (a common trick for "instant" dark-mode maps), it can
   only reach these nodes through such a global rule. The :deep() + 
   !important below guarantees the map tiles always render exactly as
   fetched, regardless of what the app-wide theme toggle does elsewhere. */
.map-content :deep(.leaflet-container),
.map-content :deep(.leaflet-tile-pane),
.map-content :deep(.leaflet-layer),
.map-content :deep(.leaflet-tile) {
  filter: none !important;
  -webkit-filter: none !important;
}
</style>