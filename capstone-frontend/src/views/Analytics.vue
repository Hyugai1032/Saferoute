<!-- Updated Vue component: AnalyticsDashboard.vue -->
<template>
  <div class="panel">
    <div class="analytics-container">
      <h2 class="page-title">📊 Analytics Dashboard</h2>

        <!-- Quick Stats -->
        <div class="stats-row">
          <div class="stat-card">
            <h3>{{ stats.totalEvacuees }}</h3>
            <p>Total Evacuees</p>
          </div>
        </div>

      <!-- Congestion Charts Grid -->
      <div class="congestion-charts">
        <!-- Row 1 -->
        <div class="chart-card chart-sm">
          <div class="chart-header">
            <h4>Evacuation Center Status</h4>
          </div>
          <div class="chart-body">
            <canvas id="riskDistributionChart"></canvas>
          </div>
        </div>

        <div class="chart-card chart-sm">
          <div class="chart-header">
            <h4>Selected Center: Current vs Predicted</h4>
          </div>
          <div class="chart-body">
            <canvas id="selectedCenterComparison"></canvas>
          </div>
        </div>

        <!-- Row 2 -->
        <div class="chart-card chart-lg">
          <div class="chart-header">
            <h4>Top 5 Predicted Occupancy</h4>
          </div>
          <div class="chart-body">
            <canvas id="topRiskChart"></canvas>
          </div>
        </div>
      </div>

      <!-- Congestion Prediction Section -->
      <div class="card-section">
        <h3 class="section-title">🏟️ Evacuation Center Congestion Forecast</h3>

        <div class="controls-row">
          <div class="control">
            <label class="control-label">Select Center</label>
            <select class="control-input" v-model="selectedCenterId" @change="loadSelectedCenterRisk">
              <option value="" disabled>Select evacuation center</option>
              <option v-for="c in centers" :key="c.id" :value="c.id">
                {{ c.name }}
              </option>
            </select>
          </div>

          <div class="control">
            <label class="control-label">Window (mins)</label>
            <input class="control-input" type="number" min="5" max="1440" v-model.number="windowMinutes" @change="loadSelectedCenterRisk" />
          </div>

          <div class="control">
            <label class="control-label">Horizon (mins)</label>
            <input class="control-input" type="number" min="5" max="360" v-model.number="horizonMinutes" @change="loadSelectedCenterRisk" />
          </div>

          <button class="btn-refresh" @click="refreshCongestion">Refresh</button>
        </div>

        <!-- Selected Center Summary -->
        <div v-if="selectedRisk" class="risk-grid">
          <div class="risk-card">
            <div class="risk-card-title">Risk Level</div>
            <div class="risk-badge" :class="riskClass(selectedRisk.risk_level)">
              {{ selectedRisk.risk_level }}
            </div>
            <div class="muted-sm">{{ selectedRisk.recommendation }}</div>
          </div>

          <div class="risk-card">
            <div class="risk-card-title">Occupancy Now</div>
            <div class="big-metric">
              {{ Math.round(selectedRisk.occupancy * 100) }}%
            </div>
            <div class="progress">
              <div class="progress-bar" :style="{ width: clampPct(selectedRisk.occupancy) }"></div>
            </div>
            <div class="muted-sm">
              {{ selectedRisk.current_total }} / {{ selectedRisk.capacity }}
            </div>
          </div>

          <div class="risk-card">
            <div class="risk-card-title">Predicted Occupancy ({{ horizonMinutes }}m)</div>
            <div class="big-metric">
              {{ Math.round(selectedRisk.predicted_occupancy * 100) }}%
            </div>
            <div class="progress">
              <div class="progress-bar warn" :style="{ width: clampPct(selectedRisk.predicted_occupancy) }"></div>
            </div>
            <div class="muted-sm">
              {{ selectedRisk.predicted_total }} / {{ selectedRisk.capacity }}
            </div>
          </div>

          <div class="risk-card">
            <div class="risk-card-title">Net Inflow Rate</div>
            <div class="big-metric">
              {{ selectedRisk.net_rate_per_min }} / min
            </div>
            <div class="muted-sm">
              Last {{ windowMinutes }} mins: +{{ selectedRisk.total_in_window }} IN, -{{ selectedRisk.total_out_window }} OUT
            </div>
          </div>
        </div>

        <!-- Centers Overview Table -->
        <div class="table-wrap styled-scroll">
          <div class="control">
            <label class="control-label">Search Center</label>
            <input
              class="control-input"
              v-model="searchQuery"
              placeholder="Search by center name..."
            />
          </div>

          <div class="control">
            <label class="control-label">Municipality</label>
            <select class="control-input" v-model="selectedMunicipality">
              <option value="">All</option>
              <option v-for="m in municipalities" :key="m" :value="m">
                {{ m }}
              </option>
            </select>
          </div>

          <button class="btn-refresh" @click="exportToCSV">
            Export CSV
          </button>

          <table class="dark-table compact">
            <thead>
              <tr>
                <th>Center</th>
                <th>Current</th>
                <th>Predicted</th>
                <th>Risk</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in paginatedCenterRisks" :key="row.center_id">
                <td>{{ centerName(row.center_id) }}</td>
                <td>{{ row.current_total }}</td>
                <td>{{ row.predicted_total }}</td>
                <td>
                  <span class="risk-pill" :class="riskClass(row.risk_level)">
                    {{ row.risk_level }}
                  </span>
                </td>
                <td>
                  <button class="btn-mini" @click="selectCenter(row.center_id)">View</button>
                </td>
              </tr>

              <tr v-if="centers.length && !centerRisks.length">
                <td colspan="5" class="muted-sm">Loading congestion data…</td>
              </tr>
            </tbody>
          </table>
        </div>
        <!-- Pagination Controls -->
        <div class="pagination-bar">
          <div class="pagination-info">
            Showing
            {{
              centerRisks.length
                ? (currentPage - 1) * rowsPerPage + 1
                : 0
            }}
            –
            {{
              Math.min(currentPage * rowsPerPage, centerRisks.length)
            }}
            of {{ centerRisks.length }} centers
          </div>

          <div class="pagination-controls">
            <button
              class="page-btn"
              :disabled="currentPage === 1"
              @click="goToPage(currentPage - 1)"
            >
              ◀ Prev
            </button>

            <span class="page-number">
              Page {{ currentPage }} of {{ totalPages }}
            </span>

            <button
              class="page-btn"
              :disabled="currentPage === totalPages"
              @click="goToPage(currentPage + 1)"
            >
              Next ▶
            </button>

            <select v-model.number="rowsPerPage" class="rows-select">
              <option :value="5">5</option>
              <option :value="10">10</option>
              <option :value="20">20</option>
              <option :value="50">50</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Weather Forecast Section -->
      <div class="weather-section" v-if="weatherPredictions.length > 0">
        <h3 class="weather-title">🌤️ 72-Hour Weather Forecast</h3>

        <!-- Weather Summary Cards -->
        <div class="weather-summary-row">
          <div class="weather-summary-card">
            <h4>{{ weatherPredictions[0].TAVG.toFixed(1) }}°C</h4>
            <p>Current Temperature</p>
          </div>
          <div class="weather-summary-card">
            <h4>{{ stats.predictedRisk }}%</h4>
            <p>48h Rainfall-Risk</p>
          </div>
          <div class="weather-summary-card">
            <h4>{{ avgHumidity }}%</h4>
            <p>Avg Humidity</p>
          </div>
          <div class="weather-summary-card">
            <h4>{{ maxWind }} m/s</h4>
            <p>Peak Wind Speed</p>
          </div>
        </div>

        <!-- Weather Data Table -->
        <div class="weather-table-container styled-scroll">
          <table class="weather-table dark-table">
            <thead>
              <tr>
                <th>Time</th>
                <th>Temp</th>
                <th>Precip</th>
                <th>Humidity</th>
                <th>Wind</th>
                <th>Pressure</th>
                <th>Clouds</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(pred, index) in weatherPredictions" :key="index">
                <td>{{ formatDate(pred.datetime) }}</td>
                <td>{{ pred.TAVG.toFixed(1) }}°C</td>
                <td>{{ pred.PRCP.toFixed(2) }} mm</td>
                <td>{{ pred.RH.toFixed(0) }}%</td>
                <td>{{ pred.WDSP.toFixed(1) }} m/s</td>
                <td>{{ pred.pressure.toFixed(0) }} hPa</td>
                <td>{{ pred.cloud_cover.toFixed(0) }}%</td>
              </tr>
            </tbody>
          </table>
        </div>

        
      </div>

      <div v-else>
        <p class="loading-text">🔄 Fetching weather data...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted, watch } from 'vue'
import { Chart, registerables } from 'chart.js'

const API_BASE = import.meta.env.VITE_API_BASE_URL

// --- Congestion Risk (Hybrid Real-time Model) ---
const centers = ref([])                 // list of centers for dropdown/table
const centerRisks = ref([])             // computed risk results for each center
const selectedCenterId = ref('')        // selected center
const selectedRisk = ref(null)          // risk payload for selected center
const windowMinutes = ref(60)
const horizonMinutes = ref(60)
let refreshTimer
let riskChart

const API_BASE = import.meta.env.VITE_API_BASE_URL;

Chart.register(...registerables)

const currentPage = ref(1)
const rowsPerPage = ref(10)

// --- Risk Order Map ---
const riskPriority = {
  FULL: 4,
  HIGH: 3,
  MODERATE: 2,
  LOW: 1
}

// Search + Municipality filters
const searchQuery = ref('')
const selectedMunicipality = ref('')

// Filtered + Sorted Centers
const filteredAndSortedCenters = computed(() => {
  let filtered = centerRisks.value

  // Filter by search
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    filtered = filtered.filter(row =>
      centerName(row.center_id).toLowerCase().includes(q)
    )
  }

  // Filter by municipality (if your center object has municipality)
  if (selectedMunicipality.value) {
    filtered = filtered.filter(row => {
      const center = centers.value.find(c => c.id === row.center_id)
      return center?.municipality_name === selectedMunicipality.value
    })
  }

  // Sort by risk priority (highest first)
  return [...filtered].sort((a,b)=> 
    (riskPriority[b.risk_level] || 0) - (riskPriority[a.risk_level] || 0)
  )
})

const totalPages = computed(() =>
  Math.ceil(filteredAndSortedCenters.value.length / rowsPerPage.value) || 1
)

const paginatedCenterRisks = computed(() => {
  const start = (currentPage.value - 1) * rowsPerPage.value
  const end = start + rowsPerPage.value
  return filteredAndSortedCenters.value.slice(start, end)
})

function goToPage(page) {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
}

const riskDistribution = computed(() => {
  const counts = {
    LOW: 0,
    MODERATE: 0,
    HIGH: 0,
    FULL: 0
  }

  filteredAndSortedCenters.value.forEach(row => {
    if (counts[row.risk_level] !== undefined) {
      counts[row.risk_level]++
    }
  })

  return counts
})

const municipalities = computed(() => {
  const set = new Set(
    centers.value
      .map(c => c.municipality_name)
      .filter(Boolean)
  )
  return Array.from(set).sort()
})

// Helpers
function riskClass(level) {
  return {
    LOW: 'low',
    MODERATE: 'moderate',
    CRITICAL: 'high',
    FULL: 'full'
  }[level] || 'low'
}

function clampPct(x) {
  const pct = Math.round((x || 0) * 100)
  return `${Math.max(0, Math.min(100, pct))}%`
}

function centerName(centerId) {
  const c = centers.value.find(x => x.id === centerId)
  return c ? c.name : `Center #${centerId}`
}

function selectCenter(id) {
  selectedCenterId.value = id
  loadSelectedCenterRisk()
}

async function fetchCenters() {
  // CHANGE this endpoint if yours differs:
  const res = await fetch(`${API_BASE}evac_centers/evacuation-centers/`, {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('access_token')}`
    }
  })
  if (!res.ok) throw new Error(`Failed to load centers: ${res.status}`)
  const data = await res.json()

  // Handle both paginated and non-paginated responses
  centers.value = Array.isArray(data) ? data : (data.results || [])
  if (!selectedCenterId.value && centers.value.length) {
    selectedCenterId.value = centers.value[0].id
  }
}

async function fetchCenterRisk(centerId) {
  const url = `${API_BASE}analytics/centers/${centerId}/congestion-risk/?window=${windowMinutes.value}&horizon=${horizonMinutes.value}`
  const res = await fetch(url, {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('access_token')}`
    }
  })
  if (!res.ok) {
    const txt = await res.text()
    throw new Error(`Risk fetch failed (${res.status}): ${txt}`)
  }
  return await res.json()
}

async function loadSelectedCenterRisk() {
  if (!selectedCenterId.value) return
  try {
    selectedRisk.value = await fetchCenterRisk(selectedCenterId.value)
  } catch (e) {
    console.error(e)
    selectedRisk.value = null
  }
}

async function refreshCongestion() {
  try {
    if (!centers.value.length) await fetchCenters()

    const results = await Promise.all(
      centers.value.map(c => fetchCenterRisk(c.id).catch(() => null))
    )

    centerRisks.value = results.filter(Boolean)   // ✅ MISSING LINE
    currentPage.value = 1

    await loadSelectedCenterRisk()
  } catch (e) {
    console.error('Failed to refresh congestion:', e)
  }
}

function initRiskDistributionChart() {
  const ctx = document.getElementById('riskDistributionChart')
  if (!ctx) return

  if (riskChart) riskChart.destroy()

  riskChart = new Chart(ctx, {
    type: 'doughnut',
    cutout: '60%',
    plugins: {
      legend: { position: 'top' }
    },
    data: {
      labels: ['LOW', 'MODERATE', 'HIGH', 'FULL'],
      datasets: [{
        data: [
          riskDistribution.value.LOW,
          riskDistribution.value.MODERATE,
          riskDistribution.value.HIGH,
          riskDistribution.value.FULL
        ],
        backgroundColor: [
          '#00ff7f',
          '#ffc107',
          '#ff4d4d',
          '#ff0050'
        ]
      }]
    },
    options: {
      maintainAspectRatio: false,
      responsive: true,
      plugins: {
        legend: {
          labels: { color: '#e5e7eb' }
        }
      }
    }
  })
}

watch(filteredAndSortedCenters, () => {
  initRiskDistributionChart()
})

async function fetchAnalyticsStats() {
  const res = await fetch(`${API_BASE}analytics/stats/`, {
    headers: {
      Authorization: `Bearer ${localStorage.getItem('access_token')}`
    }
  })
  if (!res.ok) throw new Error(`Stats fetch failed: ${res.status}`)
  const data = await res.json()

  stats.value.totalEvacuees = data.total_evacuees ?? 0
  stats.value.activeCenters = data.active_centers ?? 0
}

const stats = ref({
  totalEvacuees: 0,
  activeCenters: 0,
  predictedRisk: 0
})

const weatherPredictions = ref([])  // Store fetched predictions


const avgHumidity = computed(() => {
  if (weatherPredictions.value.length === 0) return 0
  return Math.round(
    weatherPredictions.value.slice(0, 72).reduce((acc, p) => acc + p.RH, 0) / 72
  )
})

const maxWind = computed(() => {
  if (weatherPredictions.value.length === 0) return 0
  return Math.max(...weatherPredictions.value.map(p => p.WDSP.toFixed(1)))
})


const currentChart = ref('Evacuees')
let barChart, pieChart, lineChart, weatherChart

onMounted(async () => {
  // Fetch predictions and update risk + weather data
  try {
    const response = await fetch('${API_BASE}analytics/weather/predict/')  // Use relative URL for same-origin; adjust if needed
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    const data = await response.json()
    if (data.error) {
      console.error(data.error)
      stats.value.predictedRisk = 78  // Fallback
    } else {
      weatherPredictions.value = data.predictions.slice(0, 72)  // All 72 hours for table/diagram
      let prcp_sum = 0
      weatherPredictions.value.slice(0, 48).forEach(pred => {  // First 48h for risk
        prcp_sum += pred.PRCP || 0
      })
      // Arbitrary risk calculation: e.g., 2% per mm precipitation
      stats.value.predictedRisk = Math.min(100, Math.round(prcp_sum * 2))
      
      // Initialize Weather Chart after data is fetched
      initWeatherChart()
    }
  } catch (error) {
    console.error('Failed to fetch predictions:', error)
    stats.value.predictedRisk = 78  // Fallback
  }

  try {
    await fetchCenters()
    await refreshCongestion()
    await fetchAnalyticsStats()
  } catch (e) {
    console.error("Congestion load failed:", e)
  }

  refreshTimer = setInterval(async () => {
    await fetchAnalyticsStats()
    await refreshCongestion()
  }, 60000)

})

onUnmounted(() => {
  clearInterval(refreshTimer)
})

function exportToCSV() {
  const rows = filteredAndSortedCenters.value

  const headers = [
    'Center',
    'Current',
    'Predicted',
    'Risk'
  ]

  const csvContent = [
    headers.join(','),
    ...rows.map(row => [
      `"${centerName(row.center_id)}"`,
      row.current_total,
      row.predicted_total,
      row.risk_level
    ].join(','))
  ].join('\n')

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)

  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', 'evacuation_center_analytics.csv')
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

let topRiskChart

function initTopRiskChart() {
  const ctx = document.getElementById('topRiskChart')
  if (!ctx) return

  if (topRiskChart) topRiskChart.destroy()

  const top5 = [...filteredAndSortedCenters.value]
    .sort((a, b) => b.predicted_occupancy - a.predicted_occupancy)
    .slice(0, 5)

  topRiskChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: top5.map(r => centerName(r.center_id)),
      datasets: [{
        label: 'Predicted Occupancy (%)',
        data: top5.map(r => Math.round(r.predicted_occupancy * 100)),
        backgroundColor: '#ff4d4d'
      }]
    },
    options: {
      indexAxis: 'y',
      maintainAspectRatio: false,
      responsive: true,
      plugins: {
        legend: { labels: { color: '#e5e7eb' } }
      },
      scales: {
        x: {
          ticks: { color: '#9ca3af' }
        },
        y: {
          ticks: { color: '#9ca3af' }
        }
      }
    }
  })
}

watch(filteredAndSortedCenters, () => {
  initRiskDistributionChart()
  initTopRiskChart()
})

let selectedCenterChart

function initSelectedCenterChart() {
  if (!selectedRisk.value) return

  const ctx = document.getElementById('selectedCenterComparison')
  if (!ctx) return

  if (selectedCenterChart) selectedCenterChart.destroy()

  selectedCenterChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Current', 'Predicted'],
      datasets: [{
        label: 'Occupancy (%)',
        data: [
          Math.round(selectedRisk.value.occupancy * 100),
          Math.round(selectedRisk.value.predicted_occupancy * 100)
        ],
        backgroundColor: ['#00b4ff', '#ffb020']
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: '#e5e7eb' } }
      }
    }
  })
}

watch(selectedRisk, () => {
  initSelectedCenterChart()
})

// Format datetime for display
function formatDate(isoString) {
  const date = new Date(isoString)
  return date.toLocaleString('en-US', { weekday: 'short', hour: 'numeric', minute: 'numeric' })
}

// --- Chart Options ---
function chartOptions() {
  return {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 1200, easing: 'easeOutQuart' },
    plugins: {
      legend: {
        labels: { color: '#9ca3af', font: { size: 13 } }
      },
      tooltip: {
        backgroundColor: '#1e293b',
        titleColor: '#00b4ff',
        bodyColor: '#fff',
        borderWidth: 1,
        borderColor: '#00b4ff',
        padding: 10
      }
    },
    scales: {
      x: {
        ticks: { color: '#9ca3af' },
        grid: { color: 'rgba(255,255,255,0.05)' }
      },
      y: {
        ticks: { color: '#9ca3af' },
        grid: { color: 'rgba(255,255,255,0.05)' }
      }
    }
  }
}

// --- Chart Data Toggle ---
function updateChart(type) {
  currentChart.value = type
  if (type === 'Supplies') {
    barChart.data.datasets[0].data = [40, 55, 70]
    barChart.data.datasets[0].label = 'Low Supplies'
    barChart.data.datasets[0].backgroundColor = '#ffc107'
  } else if (type === 'Risk') {
    barChart.data.datasets[0].data = [65, 80, 95]
    barChart.data.datasets[0].label = 'Predicted Risk (%)'
    barChart.data.datasets[0].backgroundColor = '#ff4d4d'
  } else {
    barChart.data.datasets[0].data = [50, 95, 80]
    barChart.data.datasets[0].label = 'Evacuees'
    barChart.data.datasets[0].backgroundColor = '#00b4ff'
  }
  barChart.update()
}
</script>

<style scoped>
.analytics-container {
  padding: 1rem 1.5rem;
  color: white;
}

.page-title {
  color: #4dc3ff;
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1rem;
  text-shadow: 0 0 8px rgba(77, 195, 255, 0.4);
}

/* STATS CARDS */
.stats-row {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  flex: 1;
  min-width: 150px;
  background: linear-gradient(145deg, #0f1a25, #0b121a);
  border: 1px solid rgba(0, 204, 255, 0.2);
  border-radius: 12px;
  text-align: center;
  padding: 1rem;
  box-shadow: 0 0 12px rgba(0, 204, 255, 0.1);
  transition: all 0.3s ease;
}
.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 0 16px rgba(0, 204, 255, 0.4);
}
.stat-card h3 {
  color: #4dc3ff;
  font-size: 1.6rem;
  margin: 0;
}
.stat-card p {
  color: #9ca3af;
  margin: 4px 0 0;
  font-size: 0.9rem;
}

/* TOGGLE BUTTONS */
.chart-controls {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}
.chart-controls button {
  background: #0f1a25;
  border: 1px solid rgba(0, 204, 255, 0.3);
  color: #4dc3ff;
  padding: 6px 14px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: 0.3s;
}
.chart-controls button:hover {
  background: #1a2735;
}
.chart-controls .active {
  background: #00b4ff;
  color: #fff;
  border-color: #00b4ff;
}

/* CHART LAYOUT */
.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
}

.chart-card {
  background: linear-gradient(145deg, #0f1a25, #0b121a);
  padding: 1rem;
  border-radius: 12px;
  border: 1px solid rgba(0, 204, 255, 0.15);
  box-shadow: 0 0 10px rgba(0, 204, 255, 0.1);
  height: 320px;
  transition: all 0.3s ease;
}
.chart-card:hover {
  transform: scale(1.02);
  box-shadow: 0 0 20px rgba(0, 204, 255, 0.3);
}

.chart-card.full-width {
  grid-column: 1 / -1;
  height: 360px;
}

/* WEATHER SECTION */
.weather-section {
  margin-top: 2rem;
  padding: 1.5rem;
  background: linear-gradient(145deg, #0f1a25, #0a131c);
  border-radius: 14px;
  border: 1px solid rgba(0, 204, 255, 0.25);
  box-shadow: 0 0 14px rgba(0, 204, 255, 0.15);
  color: #cfe7ff;
}

.weather-title {
  font-size: 1.4rem;
  margin-bottom: 1rem;
  color: #4dc3ff;
  font-weight: 600;
  text-shadow: 0 0 10px rgba(0, 204, 255, 0.3);
}

/* SUMMARY CARDS */
.weather-summary-row {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 1.5rem;
}

.weather-summary-card {
  flex: 1;
  min-width: 150px;
  padding: 1rem;
  background: linear-gradient(145deg, #0b1620, #09101a);
  border: 1px solid rgba(0, 204, 255, 0.2);
  border-radius: 10px;
  text-align: center;
  box-shadow: 0 0 10px rgba(0, 204, 255, 0.1);
  transition: 0.3s;
}

.weather-summary-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 0 18px rgba(0, 204, 255, 0.4);
}

.weather-summary-card h4 {
  color: #4dc3ff;
  font-size: 1.4rem;
  margin: 0;
}

.weather-summary-card p {
  color: #9ca3af;
  font-size: 0.85rem;
  margin-top: 4px;
}

/* TABLE */
.weather-table-container {
  border-radius: 12px;
  overflow-x: auto;
  margin-bottom: 1.5rem;
  max-height: 320px;
  overflow-y: auto;
}

.styled-scroll::-webkit-scrollbar {
  height: 6px;
  width: 6px;
}
.styled-scroll::-webkit-scrollbar-thumb {
  background: rgba(0, 204, 255, 0.3);
  border-radius: 10px;
}
.styled-scroll::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
}

.dark-table {
  width: 100%;
  border-collapse: collapse;
  background: #0d1b27;
  color: #d5eaff;
}

.dark-table th {
  background: rgba(0, 204, 255, 0.15);
  color: #4dc3ff;
  padding: 10px;
  font-size: 0.85rem;
  text-transform: uppercase;
  border-bottom: 1px solid rgba(0, 204, 255, 0.2);
}

.dark-table td {
  padding: 8px;
  border-bottom: 1px solid rgba(0, 204, 255, 0.1);
}

.dark-table tr:hover td {
  background: rgba(0, 204, 255, 0.05);
}

/* WEATHER CHART CARD MATCH FIX */
.weather-chart-card {
  border-color: rgba(0, 204, 255, 0.3) !important;
  background: linear-gradient(145deg, #0f1a25, #0b121a) !important;
}

/* Loading text */
.loading-text {
  color: #9ca3af;
  padding: 1rem;
  text-align: center;
}

@media (max-width: 768px) {
  .chart-card {
    height: 250px;
  }
}

thead {
  position: static;
  top: 0;
  z-index: 10;
}

.card-section{
  margin-top: 1.5rem;
  padding: 1rem;
  border-radius: 14px;
  border: 1px solid rgba(0, 204, 255, 0.15);
  background: linear-gradient(145deg, #0f1a25, #0b121a);
  box-shadow: 0 0 12px rgba(0, 204, 255, 0.08);
}

.section-title{
  margin: 0 0 0.8rem;
  color: #4dc3ff;
  font-weight: 600;
}

.controls-row{
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  align-items: end;
  margin-bottom: 1rem;
}

.control{
  min-width: 180px;
  flex: 1;
}

.control-label{
  display: block;
  font-size: 0.85rem;
  color: #9ca3af;
  margin-bottom: 0.35rem;
}

.control-input{
  width: 100%;
  background: #0f1a25;
  border: 1px solid rgba(0, 204, 255, 0.25);
  color: #e5e7eb;
  border-radius: 10px;
  padding: 8px 10px;
  outline: none;
}

.btn-refresh{
  padding: 9px 14px;
  border-radius: 10px;
  border: 1px solid rgba(0, 204, 255, 0.35);
  background: #0f1a25;
  color: #4dc3ff;
  cursor: pointer;
}

.risk-grid{
  display: grid;
  grid-template-columns: repeat(4, minmax(180px, 1fr));
  gap: 0.75rem;
  margin-bottom: 1rem;
}
@media (max-width: 1100px){
  .risk-grid{ grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 650px){
  .risk-grid{ grid-template-columns: 1fr; }
}

.risk-card{
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 12px;
  padding: 0.85rem;
}

.risk-card-title{
  font-size: 0.85rem;
  color: #9ca3af;
  margin-bottom: 0.4rem;
}

.big-metric{
  font-size: 1.4rem;
  font-weight: 700;
  color: #e5e7eb;
  margin-bottom: 0.5rem;
}

.muted-sm{
  font-size: 0.82rem;
  color: #9ca3af;
  margin-top: 0.4rem;
}

.progress{
  width: 100%;
  height: 10px;
  border-radius: 999px;
  background: rgba(255,255,255,0.06);
  overflow: hidden;
}
.progress-bar{
  height: 100%;
  border-radius: 999px;
  background: #00b4ff;
}
.progress-bar.warn{
  background: #ffb020;
}

.risk-badge{
  display: inline-block;
  padding: 6px 10px;
  border-radius: 999px;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.risk-pill{
  display: inline-block;
  padding: 5px 10px;
  border-radius: 999px;
  font-weight: 700;
  font-size: 0.8rem;
}

.low{ background: rgba(0,255,127,0.12); color: #00ff7f; border: 1px solid rgba(0,255,127,0.25); }
.moderate{ background: rgba(255,193,7,0.12); color: #ffc107; border: 1px solid rgba(255,193,7,0.25); }
.high{ background: rgba(255,77,77,0.12); color: #ff4d4d; border: 1px solid rgba(255,77,77,0.25); }
.full{ background: rgba(255,0,80,0.12); color: #ff0050; border: 1px solid rgba(255,0,80,0.25); }

.table-wrap{
  margin-top: 0.75rem;
}

.dark-table.compact th, .dark-table.compact td{
  padding: 10px 10px;
}

.btn-mini{
  padding: 6px 10px;
  border-radius: 10px;
  border: 1px solid rgba(0, 204, 255, 0.25);
  background: transparent;
  color: #4dc3ff;
  cursor: pointer;
}

.pagination-bar{
  display:flex;
  justify-content:space-between;
  align-items:center;
  margin-top:1rem;
  flex-wrap:wrap;
  gap:10px;
}

.pagination-info{
  font-size:0.85rem;
  color:#9ca3af;
}

.pagination-controls{
  display:flex;
  align-items:center;
  gap:8px;
}

.page-btn{
  padding:6px 10px;
  border-radius:8px;
  border:1px solid rgba(0,204,255,0.25);
  background:transparent;
  color:#4dc3ff;
  cursor:pointer;
}

.page-btn:disabled{
  opacity:0.4;
  cursor:not-allowed;
}

.page-number{
  font-size:0.85rem;
  color:#e5e7eb;
}

.rows-select{
  background:#0f1a25;
  border:1px solid rgba(0,204,255,0.25);
  color:#e5e7eb;
  border-radius:8px;
  padding:4px 6px;
}

.congestion-charts{
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
  margin: 14px 0 18px;
}

/* Make the "Top 5" chart span full width */
.chart-lg{
  grid-column: 1 / -1;
}

/* Small charts have same height */
.chart-sm{
  height: 300px;
}

/* Large chart has more height */
.chart-lg{
  height: 340px;
}

.chart-card{
  border-radius: 14px;
  border: 1px solid rgba(0, 204, 255, 0.12);
  background: linear-gradient(145deg, #0f1a25, #0b121a);
  padding: 12px 12px 10px;
}

.chart-header{
  display:flex;
  align-items:center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.chart-header h4{
  margin: 0;
  font-size: 0.95rem;
  color: #e5e7eb;
  font-weight: 600;
}

.chart-body{
  height: calc(100% - 28px);
}

/* Ensures canvas fills the container */
.chart-body canvas{
  width: 100% !important;
  height: 100% !important;
}

/* Responsive: stack on small screens */
@media (max-width: 900px){
  .congestion-charts{
    grid-template-columns: 1fr;
  }
  .chart-lg{
    grid-column: auto;
  }
}
</style>
