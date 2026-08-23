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

      <!-- Weather Forecast Section
      <div class="weather-section" v-if="weatherPredictions.length > 0">
        <h3 class="weather-title">🌤️ 72-Hour Weather Forecast</h3>

         Weather Summary Cards 
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

         Weather Data Table 
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
      </div> -->
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

Chart.register(...registerables)

function cssVar(name, fallback) {
  if (typeof window === 'undefined') return fallback
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim() || fallback
}

function chartTheme() {
  return {
    text: cssVar('--text-primary', '#e5e7eb'),
    muted: cssVar('--text-muted', '#9ca3af'),
    grid: cssVar('--border-light', 'rgba(255,255,255,0.08)'),
    tooltipBg: cssVar('--surface-elevated', '#1e293b'),
    accent: cssVar('--brand-blue', '#00b4ff')
  }
}

// --- Visual helpers (presentation only, no data/logic impact) ---
function makeGradient(ctx, canvas, colorFrom, colorTo, vertical = false) {
  const g = vertical
    ? ctx.createLinearGradient(0, 0, 0, canvas.height)
    : ctx.createLinearGradient(0, 0, canvas.width, 0)
  g.addColorStop(0, colorFrom)
  g.addColorStop(1, colorTo)
  return g
}

const RISK_COLORS = {
  LOW: '#17e0a0',
  MODERATE: '#ffb020',
  HIGH: '#ff5d73',
  FULL: '#ff2f7e'
}

// Draws the total count in the center of a doughnut chart
const centerTextPlugin = {
  id: 'sr_centerText',
  afterDraw(chart) {
    if (chart.config.type !== 'doughnut') return
    const { ctx, chartArea } = chart
    const total = chart.data.datasets[0].data.reduce((a, b) => a + b, 0)
    const cx = (chartArea.left + chartArea.right) / 2
    const cy = (chartArea.top + chartArea.bottom) / 2
    ctx.save()
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillStyle = chartTheme().text
    ctx.font = '700 26px system-ui, sans-serif'
    ctx.fillText(total, cx, cy - 8)
    ctx.fillStyle = chartTheme().muted
    ctx.font = '600 11px system-ui, sans-serif'
    ctx.fillText('CENTERS', cx, cy + 14)
    ctx.restore()
  }
}

function rebuildThemeCharts() {
  initRiskDistributionChart()
  initTopRiskChart()
  initSelectedCenterChart()
}

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
    cutout: '68%',
    plugins: [centerTextPlugin],
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
          RISK_COLORS.LOW,
          RISK_COLORS.MODERATE,
          RISK_COLORS.HIGH,
          RISK_COLORS.FULL
        ],
        borderColor: chartTheme().tooltipBg,
        borderWidth: 3,
        spacing: 4,
        borderRadius: 6,
        hoverOffset: 14,
        hoverBorderWidth: 0
      }]
    },
    options: {
      maintainAspectRatio: false,
      responsive: true,
      animation: { duration: 900, easing: 'easeOutQuart' },
      interaction: { mode: 'nearest', intersect: true },
      plugins: {
        legend: {
          position: 'top',
          labels: {
            color: chartTheme().muted,
            usePointStyle: true,
            pointStyle: 'circle',
            padding: 16,
            font: { size: 12, weight: '600' }
          }
        },
        tooltip: {
          backgroundColor: chartTheme().tooltipBg,
          titleColor: chartTheme().accent,
          bodyColor: chartTheme().text,
          borderColor: chartTheme().accent,
          borderWidth: 1,
          padding: 10,
          cornerRadius: 8,
          displayColors: true,
          boxPadding: 4
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

// const weatherPredictions = ref([])  // Store fetched predictions


// const avgHumidity = computed(() => {
//   if (weatherPredictions.value.length === 0) return 0
//   return Math.round(
//     weatherPredictions.value.slice(0, 72).reduce((acc, p) => acc + p.RH, 0) / 72
//   )
// })

// const maxWind = computed(() => {
//   if (weatherPredictions.value.length === 0) return 0
//   return Math.max(...weatherPredictions.value.map(p => p.WDSP.toFixed(1)))
// })


const currentChart = ref('Evacuees')
let barChart, pieChart, lineChart, weatherChart

onMounted(async () => {
  // Fetch predictions and update risk + weather data
  // try {
  //   const response = await fetch(`${API_BASE}analytics/weather/predict/`)  // Use relative URL for same-origin; adjust if needed
  //   if (!response.ok) {
  //     throw new Error(`HTTP error! status: ${response.status}`)
  //   }
  //   const data = await response.json()
  //   if (data.error) {
  //     console.error(data.error)
  //     stats.value.predictedRisk = 78  // Fallback
  //   } else {
  //     weatherPredictions.value = data.predictions.slice(0, 72)  // All 72 hours for table/diagram
  //     let prcp_sum = 0
  //     weatherPredictions.value.slice(0, 48).forEach(pred => {  // First 48h for risk
  //       prcp_sum += pred.PRCP || 0
  //     })
  //     // Arbitrary risk calculation: e.g., 2% per mm precipitation
  //     stats.value.predictedRisk = Math.min(100, Math.round(prcp_sum * 2))
      
  //     // Initialize Weather Chart after data is fetched
  //     initWeatherChart()
  //   }
  // } catch (error) {
  //   console.error('Failed to fetch predictions:', error)
  //   stats.value.predictedRisk = 78  // Fallback
  // }

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

  window.addEventListener('saferoute:theme-change', rebuildThemeCharts)
})

onUnmounted(() => {
  clearInterval(refreshTimer)
  window.removeEventListener('saferoute:theme-change', rebuildThemeCharts)
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

  const barGradient = makeGradient(
    ctx.getContext('2d'), ctx,
    'rgba(255, 93, 115, 0.55)', '#ff5d73'
  )
  const barGradientHover = makeGradient(
    ctx.getContext('2d'), ctx,
    'rgba(255, 47, 126, 0.65)', '#ff2f7e'
  )

  topRiskChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: top5.map(r => centerName(r.center_id)),
      datasets: [{
        label: 'Predicted Occupancy (%)',
        data: top5.map(r => Math.round(r.predicted_occupancy * 100)),
        backgroundColor: barGradient,
        hoverBackgroundColor: barGradientHover,
        borderRadius: 8,
        borderSkipped: false,
        maxBarThickness: 26
      }]
    },
    options: {
      indexAxis: 'y',
      maintainAspectRatio: false,
      responsive: true,
      animation: { duration: 900, easing: 'easeOutQuart' },
      plugins: {
        legend: {
          labels: { color: chartTheme().muted, usePointStyle: true, pointStyle: 'rectRounded', font: { size: 12, weight: '600' } }
        },
        tooltip: {
          backgroundColor: chartTheme().tooltipBg,
          titleColor: chartTheme().accent,
          bodyColor: chartTheme().text,
          borderColor: chartTheme().accent,
          borderWidth: 1,
          padding: 10,
          cornerRadius: 8,
          callbacks: {
            label: (item) => ` ${item.formattedValue}% predicted occupancy`
          }
        }
      },
      scales: {
        x: {
          ticks: { color: chartTheme().muted },
          grid: { color: chartTheme().grid, drawTicks: false }
        },
        y: {
          ticks: { color: chartTheme().muted, font: { size: 12, weight: '600' } },
          grid: { display: false }
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

  const c2d = ctx.getContext('2d')
  const currentGradient = makeGradient(c2d, ctx, 'rgba(0, 180, 255, 0.35)', '#00b4ff', true)
  const predictedGradient = makeGradient(c2d, ctx, 'rgba(255, 176, 32, 0.35)', '#ffb020', true)

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
        backgroundColor: [currentGradient, predictedGradient],
        borderRadius: 10,
        borderSkipped: false,
        maxBarThickness: 90
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 900, easing: 'easeOutQuart' },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: chartTheme().tooltipBg,
          titleColor: chartTheme().accent,
          bodyColor: chartTheme().text,
          borderColor: chartTheme().accent,
          borderWidth: 1,
          padding: 10,
          cornerRadius: 8,
          callbacks: {
            label: (item) => ` ${item.formattedValue}% occupancy`
          }
        }
      },
      scales: {
        x: {
          ticks: { color: chartTheme().muted, font: { size: 13, weight: '700' } },
          grid: { display: false }
        },
        y: {
          ticks: { color: chartTheme().muted, callback: (v) => v + '%' },
          grid: { color: chartTheme().grid },
          beginAtZero: true,
          max: 100
        }
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
        labels: { color: chartTheme().muted, font: { size: 13 } }
      },
      tooltip: {
        backgroundColor: chartTheme().tooltipBg,
        titleColor: chartTheme().accent,
        bodyColor: chartTheme().text,
        borderWidth: 1,
        borderColor: chartTheme().accent,
        padding: 10
      }
    },
    scales: {
      x: {
        ticks: { color: chartTheme().muted },
        grid: { color: chartTheme().grid }
      },
      y: {
        ticks: { color: chartTheme().muted },
        grid: { color: chartTheme().grid }
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
/* ==========================================================================
   SafeRoute+ · Congestion Analytics — visual layer only
   Command-console aesthetic: translucent glass panels, a single cyan
   signal color, and status colors that carry real meaning (LOW → FULL).
   Every surface below derives from theme variables that are already being
   read for the charts (--text-primary, --text-muted, --border-light,
   --surface-elevated, --brand-blue), with safe fallbacks, plus
   color-mix() so panels stay correct in both light and dark mode without
   hardcoding an absolute background.
   ========================================================================== */

.analytics-container {
  /* ---- tokens ---- */
  --sr-accent: var(--brand-blue, #00b4ff);
  --sr-accent-2: #22d3c7;
  --sr-text: var(--text-primary, #e8eef6);
  --sr-muted: var(--text-muted, #8ea0b8);
  --sr-border: var(--border-light, color-mix(in srgb, var(--sr-text) 16%, transparent));
  --sr-surface: var(--surface-elevated, color-mix(in srgb, var(--sr-text) 5%, transparent));
  --sr-surface-2: color-mix(in srgb, var(--sr-text) 3%, transparent);
  --sr-ring: color-mix(in srgb, var(--sr-accent) 30%, transparent);

  --sr-low: #17e0a0;
  --sr-moderate: #ffb020;
  --sr-high: #ff5d73;
  --sr-full: #ff2f7e;

  --sr-radius-lg: 18px;
  --sr-radius-md: 12px;
  --sr-radius-sm: 9px;
  --sr-ease: cubic-bezier(.22, 1, .36, 1);

  padding: 0.25rem 0.25rem 1rem;
  color: var(--sr-text);
  font-variant-numeric: tabular-nums;
  animation: sr-rise .5s var(--sr-ease) both;
}

@media (prefers-reduced-motion: reduce) {
  .analytics-container, .analytics-container * {
    animation-duration: .001s !important;
    transition-duration: .001s !important;
  }
}

@keyframes sr-rise {
  from { opacity: 0; transform: translateY(6px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ---------- TITLE ---------- */
.page-title {
  display: flex;
  align-items: center;
  gap: .55rem;
  font-size: 1.55rem;
  font-weight: 700;
  letter-spacing: -0.01em;
  margin-bottom: 1.1rem;
  background: linear-gradient(90deg, var(--sr-accent), var(--sr-accent-2) 70%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}
.page-title::after {
  content: "";
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--sr-accent);
  box-shadow: 0 0 0 0 color-mix(in srgb, var(--sr-accent) 55%, transparent);
  animation: sr-pulse 2.2s ease-in-out infinite;
  flex-shrink: 0;
}
@keyframes sr-pulse {
  0%   { box-shadow: 0 0 0 0 color-mix(in srgb, var(--sr-accent) 45%, transparent); }
  70%  { box-shadow: 0 0 0 9px transparent; }
  100% { box-shadow: 0 0 0 0 transparent; }
}

/* ---------- STAT CARDS ---------- */
.stats-row {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  position: relative;
  flex: 1;
  min-width: 170px;
  overflow: hidden;
  background:
    radial-gradient(120% 140% at 0% 0%, color-mix(in srgb, var(--sr-accent) 10%, transparent), transparent 60%),
    var(--sr-surface);
  border: 1px solid var(--sr-border);
  border-radius: var(--sr-radius-lg);
  text-align: center;
  padding: 1.15rem 1rem;
  backdrop-filter: blur(6px);
  box-shadow: 0 1px 0 color-mix(in srgb, var(--sr-text) 6%, transparent) inset,
              0 12px 28px -18px color-mix(in srgb, var(--sr-accent) 45%, transparent);
  transition: transform .35s var(--sr-ease), box-shadow .35s var(--sr-ease), border-color .35s;
}
.stat-card::before {
  content: "";
  position: absolute;
  inset: 0 0 auto 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--sr-accent), transparent);
  opacity: .8;
}
.stat-card:hover {
  transform: translateY(-3px);
  border-color: var(--sr-ring);
  box-shadow: 0 1px 0 color-mix(in srgb, var(--sr-text) 6%, transparent) inset,
              0 18px 36px -16px color-mix(in srgb, var(--sr-accent) 55%, transparent);
}
.stat-card h3 {
  color: var(--sr-text);
  font-size: 2.1rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  margin: 0;
}
.stat-card p {
  color: var(--sr-muted);
  margin: 4px 0 0;
  font-size: .82rem;
  text-transform: uppercase;
  letter-spacing: .08em;
}

/* ---------- CHART GRID ---------- */
.congestion-charts {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
  margin: 14px 0 18px;
}

.chart-lg { grid-column: 1 / -1; height: 340px; }
.chart-sm { height: 300px; }

.chart-card {
  position: relative;
  border-radius: var(--sr-radius-lg);
  border: 1px solid var(--sr-border);
  background: var(--sr-surface);
  backdrop-filter: blur(6px);
  padding: 14px 14px 10px;
  box-shadow: 0 10px 24px -20px color-mix(in srgb, var(--sr-accent) 40%, transparent);
  transition: transform .35s var(--sr-ease), box-shadow .35s var(--sr-ease), border-color .35s;
}
.chart-card:hover {
  transform: translateY(-2px);
  border-color: var(--sr-ring);
  box-shadow: 0 16px 34px -18px color-mix(in srgb, var(--sr-accent) 50%, transparent);
}

.chart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px dashed var(--sr-border);
}
.chart-header h4 {
  display: flex;
  align-items: center;
  gap: .5rem;
  margin: 0;
  font-size: .92rem;
  color: var(--sr-text);
  font-weight: 600;
  letter-spacing: .01em;
}
.chart-header h4::before {
  content: "";
  width: 7px;
  height: 7px;
  border-radius: 2px;
  background: var(--sr-accent);
  transform: rotate(45deg);
  flex-shrink: 0;
}

.chart-body { height: calc(100% - 38px); }
.chart-body canvas { width: 100% !important; height: 100% !important; }

@media (max-width: 900px) {
  .congestion-charts { grid-template-columns: 1fr; }
  .chart-lg { grid-column: auto; }
}
@media (max-width: 768px) {
  .chart-card { height: 260px; }
}

/* ---------- FORECAST CARD SECTION ---------- */
.card-section {
  margin-top: 1.5rem;
  padding: 1.1rem 1.15rem 1.3rem;
  border-radius: 20px;
  border: 1px solid var(--sr-border);
  background: linear-gradient(180deg, var(--sr-surface-2), transparent 40%), var(--sr-surface);
  backdrop-filter: blur(6px);
  box-shadow: 0 18px 40px -28px color-mix(in srgb, var(--sr-accent) 45%, transparent);
}

.section-title {
  display: flex;
  align-items: center;
  gap: .5rem;
  margin: 0 0 1rem;
  color: var(--sr-text);
  font-weight: 700;
  font-size: 1.05rem;
  padding-bottom: .7rem;
  border-bottom: 1px solid var(--sr-border);
}

/* ---------- CONTROLS ---------- */
.controls-row {
  display: flex;
  flex-wrap: wrap;
  gap: .75rem;
  align-items: end;
  margin-bottom: 1.1rem;
}

.control { min-width: 180px; flex: 1; }

.control-label {
  display: block;
  font-size: .74rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: .06em;
  color: var(--sr-muted);
  margin-bottom: .4rem;
}

.control-input {
  width: 100%;
  background: var(--sr-surface-2);
  border: 1px solid var(--sr-border);
  color: var(--sr-text);
  border-radius: 10px;
  padding: 9px 11px;
  outline: none;
  transition: border-color .2s, box-shadow .2s, background .2s;
}
.control-input:hover { border-color: color-mix(in srgb, var(--sr-accent) 40%, var(--sr-border)); }
.control-input:focus-visible {
  border-color: var(--sr-accent);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--sr-accent) 22%, transparent);
}

.btn-refresh {
  padding: 9px 18px;
  border-radius: 10px;
  border: 1px solid color-mix(in srgb, var(--sr-accent) 45%, var(--sr-border));
  background: linear-gradient(180deg, color-mix(in srgb, var(--sr-accent) 18%, transparent), color-mix(in srgb, var(--sr-accent) 6%, transparent));
  color: var(--sr-accent);
  font-weight: 600;
  cursor: pointer;
  transition: transform .18s var(--sr-ease), box-shadow .18s var(--sr-ease), background .18s;
}
.btn-refresh:hover {
  transform: translateY(-1px);
  box-shadow: 0 8px 18px -10px color-mix(in srgb, var(--sr-accent) 60%, transparent);
  background: linear-gradient(180deg, color-mix(in srgb, var(--sr-accent) 28%, transparent), color-mix(in srgb, var(--sr-accent) 10%, transparent));
}
.btn-refresh:active { transform: translateY(0); }

/* ---------- RISK SUMMARY GRID ---------- */
.risk-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(180px, 1fr));
  gap: .8rem;
  margin-bottom: 1.2rem;
}
@media (max-width: 1100px) { .risk-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 650px)  { .risk-grid { grid-template-columns: 1fr; } }

.risk-card {
  position: relative;
  background: var(--sr-surface-2);
  border: 1px solid var(--sr-border);
  border-radius: var(--sr-radius-md);
  padding: .95rem 1rem;
  transition: border-color .25s, transform .25s var(--sr-ease);
}
.risk-card:hover {
  border-color: var(--sr-ring);
  transform: translateY(-2px);
}

.risk-card-title {
  font-size: .78rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: .05em;
  color: var(--sr-muted);
  margin-bottom: .5rem;
}

.big-metric {
  font-size: 1.55rem;
  font-weight: 800;
  color: var(--sr-text);
  letter-spacing: -0.01em;
  margin-bottom: .5rem;
}

.muted-sm {
  font-size: .8rem;
  color: var(--sr-muted);
  margin-top: .4rem;
}

.progress {
  width: 100%;
  height: 8px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--sr-text) 10%, transparent);
  overflow: hidden;
}
.progress-bar {
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, var(--sr-accent), var(--sr-accent-2));
  box-shadow: 0 0 10px color-mix(in srgb, var(--sr-accent) 55%, transparent);
  transition: width .6s var(--sr-ease);
}
.progress-bar.warn {
  background: linear-gradient(90deg, #ffb020, #ff7a45);
  box-shadow: 0 0 10px rgba(255, 176, 32, .5);
}

/* ---------- RISK BADGES / PILLS ---------- */
.risk-badge, .risk-pill {
  display: inline-flex;
  align-items: center;
  gap: .4rem;
  font-weight: 700;
  letter-spacing: .03em;
}
.risk-badge::before, .risk-pill::before {
  content: "";
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

.risk-badge {
  padding: 6px 12px;
  border-radius: 999px;
  font-size: .82rem;
  margin-bottom: .5rem;
}
.risk-pill {
  padding: 5px 11px;
  border-radius: 999px;
  font-size: .76rem;
}

.low {
  background: color-mix(in srgb, var(--sr-low) 14%, transparent);
  color: var(--sr-low);
  border: 1px solid color-mix(in srgb, var(--sr-low) 30%, transparent);
}
.moderate {
  background: color-mix(in srgb, var(--sr-moderate) 14%, transparent);
  color: var(--sr-moderate);
  border: 1px solid color-mix(in srgb, var(--sr-moderate) 30%, transparent);
}
.high {
  background: color-mix(in srgb, var(--sr-high) 14%, transparent);
  color: var(--sr-high);
  border: 1px solid color-mix(in srgb, var(--sr-high) 30%, transparent);
  animation: sr-urgent 1.8s ease-in-out infinite;
}
.full {
  background: color-mix(in srgb, var(--sr-full) 16%, transparent);
  color: var(--sr-full);
  border: 1px solid color-mix(in srgb, var(--sr-full) 35%, transparent);
  animation: sr-urgent 1.2s ease-in-out infinite;
}
@keyframes sr-urgent {
  0%, 100% { filter: brightness(1); }
  50%      { filter: brightness(1.35); }
}

/* ---------- TABLE ---------- */
.table-wrap { margin-top: .9rem; }

.styled-scroll::-webkit-scrollbar { height: 6px; width: 6px; }
.styled-scroll::-webkit-scrollbar-thumb {
  background: color-mix(in srgb, var(--sr-accent) 35%, transparent);
  border-radius: 10px;
}
.styled-scroll::-webkit-scrollbar-track { background: transparent; }

.dark-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  color: var(--sr-text);
  border: 1px solid var(--sr-border);
  border-radius: var(--sr-radius-md);
  overflow: hidden;
  margin-top: .75rem;
}

.dark-table th {
  position: sticky;
  top: 0;
  z-index: 10;
  background: color-mix(in srgb, var(--sr-accent) 12%, var(--sr-surface));
  backdrop-filter: blur(6px);
  color: var(--sr-accent);
  padding: 11px 12px;
  font-size: .74rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .07em;
  border-bottom: 1px solid var(--sr-border);
  text-align: left;
}

.dark-table td {
  padding: 10px 12px;
  border-bottom: 1px solid var(--sr-border);
  font-size: .89rem;
}

.dark-table tbody tr { transition: background .15s; }
.dark-table tbody tr:nth-child(even) { background: color-mix(in srgb, var(--sr-text) 2.5%, transparent); }
.dark-table tbody tr:hover td { background: color-mix(in srgb, var(--sr-accent) 7%, transparent); }
.dark-table tbody tr:last-child td { border-bottom: none; }

.dark-table.compact th, .dark-table.compact td { padding: 10px 12px; }

.btn-mini {
  padding: 6px 12px;
  border-radius: 999px;
  border: 1px solid color-mix(in srgb, var(--sr-accent) 35%, var(--sr-border));
  background: transparent;
  color: var(--sr-accent);
  font-weight: 600;
  font-size: .8rem;
  cursor: pointer;
  transition: background .18s, transform .18s var(--sr-ease);
}
.btn-mini:hover {
  background: color-mix(in srgb, var(--sr-accent) 14%, transparent);
  transform: translateY(-1px);
}

/* ---------- PAGINATION ---------- */
.pagination-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1.1rem;
  flex-wrap: wrap;
  gap: 10px;
}

.pagination-info { font-size: .82rem; color: var(--sr-muted); }

.pagination-controls { display: flex; align-items: center; gap: 8px; }

.page-btn {
  padding: 7px 13px;
  border-radius: 999px;
  border: 1px solid var(--sr-border);
  background: var(--sr-surface-2);
  color: var(--sr-accent);
  font-weight: 600;
  cursor: pointer;
  transition: background .18s, border-color .18s, transform .18s var(--sr-ease);
}
.page-btn:hover:not(:disabled) {
  border-color: var(--sr-ring);
  background: color-mix(in srgb, var(--sr-accent) 10%, transparent);
  transform: translateY(-1px);
}
.page-btn:disabled { opacity: .35; cursor: not-allowed; }

.page-number { font-size: .82rem; color: var(--sr-text); font-weight: 600; }

.rows-select {
  background: var(--sr-surface-2);
  border: 1px solid var(--sr-border);
  color: var(--sr-text);
  border-radius: 999px;
  padding: 6px 10px;
}

/* ---------- Shared focus ring for a11y ---------- */
button:focus-visible, select:focus-visible, input:focus-visible {
  outline: 2px solid var(--sr-accent);
  outline-offset: 2px;
}

/* ---------- Loading text (kept, in case weather section is re-enabled) ---------- */
.loading-text { color: var(--sr-muted); padding: 1rem; text-align: center; }
</style>