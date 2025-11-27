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
        <div class="stat-card">
          <h3>{{ stats.activeCenters }}</h3>
          <p>Active Centers</p>
        </div>
        <div class="stat-card">
          <h3>{{ stats.predictedRisk }}%</h3>
          <p>Predicted Risk (48h)</p>
        </div>
      </div>

      <!-- Chart Toggle Buttons -->
      <div class="chart-controls">
        <button
          v-for="type in ['Evacuees', 'Supplies', 'Risk']"
          :key="type"
          @click="updateChart(type)"
          :class="{ active: currentChart === type }"
        >
          {{ type }}
        </button>
      </div>

      <!-- Chart Grid -->
      <div class="charts-grid">
        <div class="chart-card">
          <canvas id="barChart"></canvas>
        </div>
        <div class="chart-card">
          <canvas id="pieChart"></canvas>
        </div>
        <div class="chart-card full-width">
          <canvas id="lineChart"></canvas>
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

        <!-- Weather Line Chart -->
        <div class="chart-card full-width weather-chart-card">
          <canvas id="weatherChart"></canvas>
        </div>
      </div>

      <div v-else>
        <p class="loading-text">🔄 Fetching weather data...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { Chart, registerables } from 'chart.js'
Chart.register(...registerables)

// --- Reactive Data ---
const stats = ref({
  totalEvacuees: 315,
  activeCenters: 6,
  predictedRisk: 0  // Initial, will update from API
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
    const response = await fetch('http://127.0.0.1:8000/api/analytics/weather/predict/')  // Use relative URL for same-origin; adjust if needed
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

  // BAR CHART
  const barCtx = document.getElementById('barChart')
  barChart = new Chart(barCtx, {
    type: 'bar',
    data: {
      labels: ['Calapan', 'Naujan', 'Baco'],
      datasets: [
        {
          label: 'Evacuees',
          data: [50, 95, 80],
          backgroundColor: '#00b4ff',
          borderRadius: 8
        }
      ]
    },
    options: chartOptions()
  })

  // PIE CHART
  const pieCtx = document.getElementById('pieChart')
  pieChart = new Chart(pieCtx, {
    type: 'pie',
    data: {
      labels: ['Vacant', 'Nearly Full', 'Full'],
      datasets: [
        {
          data: [60, 25, 15],
          backgroundColor: ['#00ff7f', '#ffc107', '#ff4d4d'],
          borderWidth: 0
        }
      ]
    },
    options: chartOptions()
  })

  // LINE CHART
  const lineCtx = document.getElementById('lineChart')
  lineChart = new Chart(lineCtx, {
    type: 'line',
    data: {
      labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
      datasets: [
        {
          label: 'New Evacuees',
          data: [5, 15, 12, 20, 18, 30, 25],
          borderColor: '#4dc3ff',
          tension: 0.4,
          fill: true,
          backgroundColor: 'rgba(77,195,255,0.1)'
        }
      ]
    },
    options: chartOptions()
  })

  // Simulate live updates (existing)
  setInterval(() => {
    const randomChange = () => Math.floor(Math.random() * 10 - 5)
    barChart.data.datasets[0].data = barChart.data.datasets[0].data.map(v => v + randomChange())
    barChart.update()

    lineChart.data.datasets[0].data.push(Math.floor(Math.random() * 40))
    if (lineChart.data.datasets[0].data.length > 7) lineChart.data.datasets[0].data.shift()
    lineChart.update()
  }, 4000)
})

// Function to initialize weather line chart
function initWeatherChart() {
  const weatherCtx = document.getElementById('weatherChart')
  weatherChart = new Chart(weatherCtx, {
    type: 'line',
    data: {
      labels: weatherPredictions.value.map(pred => formatDate(pred.datetime)),
      datasets: [
        {
          label: 'Temperature (°C)',
          data: weatherPredictions.value.map(pred => pred.TAVG),
          borderColor: '#ff6384',
          tension: 0.1,
          yAxisID: 'y-temp'
        },
        {
          label: 'Precipitation (mm)',
          data: weatherPredictions.value.map(pred => pred.PRCP),
          borderColor: '#36a2eb',
          tension: 0.1,
          yAxisID: 'y-precip'
        }
      ]
    },
    options: {
      ...chartOptions(),
      scales: {
        'y-temp': {
          type: 'linear',
          position: 'left',
          title: { display: true, text: 'Temperature (°C)' }
        },
        'y-precip': {
          type: 'linear',
          position: 'right',
          title: { display: true, text: 'Precipitation (mm)' },
          grid: { drawOnChartArea: false }  // Avoid overlapping grids
        },
        x: {
          ticks: { autoSkip: true, maxTicksLimit: 12 }  // Limit labels for readability
        }
      }
    }
  })
}

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
</style>
