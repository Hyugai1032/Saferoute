<template>
  <div class="panel">
    <div class="report-container">
      <div class="report-header">
        <div>
          <h2 class="page-title">Affected Population Report</h2>
          <p class="page-subtitle">
            Inside evacuation center data only for now.
          </p>
        </div>

        <div class="header-actions">
          <div class="filter-group">
            <label class="filter-label">As of</label>
            <input
              v-model="asOfInput"
              type="datetime-local"
              class="filter-input"
            />
          </div>

          <button class="btn-primary" @click="loadReport" :disabled="loading">
            {{ loading ? 'Loading...' : 'Refresh' }}
          </button>

          <button class="btn-secondary" @click="exportToExcel" :disabled="!rows.length">
                Export to Excel
            </button>

            <button class="btn-secondary" @click="printReport" :disabled="!rows.length">
                Print
            </button>
        </div>
      </div>

      <div class="report-meta">
        <div><strong>Title:</strong> {{ report.title || 'Affected Population Report' }}</div>
        <div><strong>As of:</strong> {{ formattedAsOf }}</div>
      </div>

      <div v-if="error" class="error-box">
        {{ error }}
      </div>

      <div class="table-wrap styled-scroll" v-if="rows.length">
        <table class="report-table">
          <thead>
            <tr>
              <th rowspan="3">Province</th>
              <th rowspan="3">City / Municipality</th>
              <th rowspan="3">Barangay</th>

              <th colspan="3">No. of Affected</th>
              <th colspan="2">No. of ECs</th>
              <th colspan="4">Inside Evacuation Centers</th>
              <th colspan="4">Outside Evacuation Centers</th>
              <th colspan="4">Total Served (Current)</th>
            </tr>
            <tr>
              <th rowspan="2">Brgys.</th>
              <th rowspan="2">Families</th>
              <th rowspan="2">Persons</th>

              <th rowspan="2">CUM</th>
              <th rowspan="2">NOW</th>

              <th colspan="2">Families</th>
              <th colspan="2">Persons</th>

              <th colspan="2">Families</th>
              <th colspan="2">Persons</th>

              <th colspan="2">Families</th>
              <th colspan="2">Persons</th>
            </tr>
            <tr>
              <th>CUM</th>
              <th>NOW</th>
              <th>CUM</th>
              <th>NOW</th>

              <th>CUM</th>
              <th>NOW</th>
              <th>CUM</th>
              <th>NOW</th>

              <th>CUM</th>
              <th>NOW</th>
              <th>CUM</th>
              <th>NOW</th>
            </tr>
          </thead>

          <tbody>
            <tr
              v-for="(row, index) in rows"
              :key="index"
              :class="rowClass(row)"
            >
              <td>{{ row.province }}</td>
              <td>{{ row.municipality }}</td>
              <td>{{ row.barangay }}</td>

              <td>{{ num(row.affected_brgys) }}</td>
              <td>{{ num(row.affected_families) }}</td>
              <td>{{ num(row.affected_persons) }}</td>

              <td>{{ num(row.ecs_cum) }}</td>
              <td>{{ num(row.ecs_now) }}</td>

              <td>{{ num(row.inside_families_cum) }}</td>
              <td>{{ num(row.inside_families_now) }}</td>
              <td>{{ num(row.inside_persons_cum) }}</td>
              <td>{{ num(row.inside_persons_now) }}</td>

              <td>{{ num(row.outside_families_cum) }}</td>
              <td>{{ num(row.outside_families_now) }}</td>
              <td>{{ num(row.outside_persons_cum) }}</td>
              <td>{{ num(row.outside_persons_now) }}</td>

              <td>{{ num(row.total_families_cum) }}</td>
              <td>{{ num(row.total_families_now) }}</td>
              <td>{{ num(row.total_persons_cum) }}</td>
              <td>{{ num(row.total_persons_now) }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-else-if="!loading" class="empty-state">
        No report data found.
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import * as XLSX from 'xlsx'

const API_BASE = import.meta.env.VITE_API_BASE_URL

const loading = ref(false)
const error = ref('')
const report = ref({})
const rows = ref([])

const asOfInput = ref(getDefaultLocalDateTime())

function getDefaultLocalDateTime() {
  const now = new Date()
  const pad = (n) => String(n).padStart(2, '0')
  return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}T${pad(now.getHours())}:${pad(now.getMinutes())}`
}

const formattedAsOf = computed(() => {
  if (!report.value?.as_of) return '-'
  return new Date(report.value.as_of).toLocaleString()
})

function num(value) {
  return Number(value || 0).toLocaleString()
}

function rowClass(row) {
  if (row.row_type === 'grand_total') return 'row-grand-total'
  if (row.row_type === 'subtotal') return 'row-subtotal'
  return 'row-data'
}

async function loadReport() {
  loading.value = true
  error.value = ''

  try {
    const asOfIso = asOfInput.value ? new Date(asOfInput.value).toISOString() : ''
    const url = `${API_BASE}analytics/reports/affected-population/${asOfIso ? `?as_of=${encodeURIComponent(asOfIso)}` : ''}`

    const res = await fetch(url, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`
      }
    })

    if (!res.ok) {
      const text = await res.text()
      throw new Error(`Failed to load report (${res.status}): ${text}`)
    }

    const data = await res.json()
    report.value = data
    rows.value = data.rows || []
  } catch (err) {
    console.error(err)
    error.value = err.message || 'Failed to load affected population report.'
    report.value = {}
    rows.value = []
  } finally {
    loading.value = false
  }
}

function exportToExcel() {
  if (!rows.value.length) return

  const title = "EFFECTS OF SHEAR LINE"
  const subtitle = "AFFECTED POPULATION"
  const asOf = report.value?.as_of
    ? `As of ${new Date(report.value.as_of).toLocaleString()}`
    : ""

  // --- HEADER STRUCTURE ---
  const header1 = [
    "Province",
    "City / Municipality",
    "Barangay",
    "NO. OF AFFECTED", "", "",
    "NO. OF ECS", "",
    "INSIDE EVACUATION CENTERS", "", "", "",
    "OUTSIDE EVACUATION CENTERS", "", "", "",
    "TOTAL SERVED (CURRENT)", "", "", ""
  ]

  const header2 = [
    "", "", "",
    "Brgys.", "Families", "Persons",
    "CUM", "NOW",
    "Families", "", "Persons", "",
    "Families", "", "Persons", "",
    "Families", "", "Persons", ""
  ]

  const header3 = [
    "", "", "",
    "", "", "",
    "", "",
    "CUM", "NOW", "CUM", "NOW",
    "CUM", "NOW", "CUM", "NOW",
    "CUM", "NOW", "CUM", "NOW"
  ]

  // --- DATA ---
  const dataRows = rows.value.map(row => [
    row?.province ?? "",
    row?.municipality ?? "",
    row?.barangay ?? "",

    row?.affected_brgys ?? 0,
    row?.affected_families ?? 0,
    row?.affected_persons ?? 0,

    row?.ecs_cum ?? 0,
    row?.ecs_now ?? 0,

    row?.inside_families_cum ?? 0,
    row?.inside_families_now ?? 0,
    row?.inside_persons_cum ?? 0,
    row?.inside_persons_now ?? 0,

    row?.outside_families_cum ?? 0,
    row?.outside_families_now ?? 0,
    row?.outside_persons_cum ?? 0,
    row?.outside_persons_now ?? 0,

    row?.total_families_cum ?? 0,
    row?.total_families_now ?? 0,
    row?.total_persons_cum ?? 0,
    row?.total_persons_now ?? 0
  ])

  // --- COMBINE ---
  const sheetData = [
    [title],
    [subtitle],
    [asOf],
    [],
    header1,
    header2,
    header3,
    ...dataRows
  ]

  const ws = XLSX.utils.aoa_to_sheet(sheetData)

  // --- MERGES ---
  ws['!merges'] = [
    // Title merges
    { s: { r: 0, c: 0 }, e: { r: 0, c: 19 } },
    { s: { r: 1, c: 0 }, e: { r: 1, c: 19 } },
    { s: { r: 2, c: 0 }, e: { r: 2, c: 19 } },

    // Header group merges
    { s: { r: 4, c: 3 }, e: { r: 4, c: 5 } },
    { s: { r: 4, c: 6 }, e: { r: 4, c: 7 } },
    { s: { r: 4, c: 8 }, e: { r: 4, c: 11 } },
    { s: { r: 4, c: 12 }, e: { r: 4, c: 15 } },
    { s: { r: 4, c: 16 }, e: { r: 4, c: 19 } },

    // Sub-header merges
    { s: { r: 5, c: 8 }, e: { r: 5, c: 9 } },
    { s: { r: 5, c: 10 }, e: { r: 5, c: 11 } },
    { s: { r: 5, c: 12 }, e: { r: 5, c: 13 } },
    { s: { r: 5, c: 14 }, e: { r: 5, c: 15 } },
    { s: { r: 5, c: 16 }, e: { r: 5, c: 17 } },
    { s: { r: 5, c: 18 }, e: { r: 5, c: 19 } }
  ]

  // --- COLUMN WIDTHS ---
  ws['!cols'] = [
    { wch: 20 },
    { wch: 25 },
    { wch: 25 },
    ...Array(17).fill({ wch: 12 })
  ]

  // --- CREATE FILE ---
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, "Affected Population")

  XLSX.writeFile(wb, "affected_population_report.xlsx")
}

function printReport() {
  if (!rows.value.length) return
  window.print()
}

onMounted(() => {
  loadReport()
})
</script>

<style scoped>
.report-container {
  padding: 1.25rem;
  color: #e5e7eb;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: end;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
}

.page-title {
  margin: 0;
  font-size: 1.6rem;
  font-weight: 700;
}

.page-subtitle {
  margin: 0.35rem 0 0;
  color: #94a3b8;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
  align-items: end;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.filter-label {
  font-size: 0.85rem;
  color: #94a3b8;
}

.filter-input {
  background: #0f1a25;
  color: #e5e7eb;
  border: 1px solid rgba(0, 204, 255, 0.25);
  border-radius: 10px;
  padding: 0.65rem 0.8rem;
}

.btn-primary {
  background: linear-gradient(135deg, #00b4ff, #0088ff);
  color: white;
  border: none;
  border-radius: 10px;
  padding: 0.72rem 1rem;
  font-weight: 600;
  cursor: pointer;
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.report-meta {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
  padding: 0.9rem 1rem;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(0, 204, 255, 0.12);
}

.table-wrap {
  overflow: auto;
  border-radius: 14px;
  border: 1px solid rgba(0, 204, 255, 0.12);
  background: linear-gradient(145deg, #0f1a25, #0b121a);
}

.report-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 1600px;
}

.report-table th,
.report-table td {
  border: 1px solid rgba(255, 255, 255, 0.08);
  padding: 0.65rem 0.7rem;
  text-align: center;
  white-space: nowrap;
}

.report-table th {
  background: rgba(0, 180, 255, 0.14);
  color: #dbeafe;
  font-weight: 700;
  font-size: 0.9rem;
}

.report-table td:first-child,
.report-table td:nth-child(2),
.report-table td:nth-child(3) {
  text-align: left;
}

.row-data:hover {
  background: rgba(255, 255, 255, 0.03);
}

.row-subtotal {
  background: rgba(255, 221, 0, 0.18);
  font-weight: 700;
  color: #fff7bf;
}

.row-grand-total {
  background: rgba(96, 165, 250, 0.22);
  font-weight: 800;
  color: #dbeafe;
}

.error-box {
  margin-bottom: 1rem;
  padding: 0.9rem 1rem;
  border-radius: 10px;
  background: rgba(239, 68, 68, 0.14);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #fecaca;
}

.empty-state {
  padding: 1rem;
  color: #94a3b8;
}

.btn-secondary {
  background: transparent;
  color: #dbeafe;
  border: 1px solid rgba(0, 204, 255, 0.25);
  border-radius: 10px;
  padding: 0.72rem 1rem;
  font-weight: 600;
  cursor: pointer;
}

.btn-secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .report-container {
    padding: 0.9rem;
  }

  .page-title {
    font-size: 1.3rem;
  }
}

@media print {
  .panel,
  .report-container {
    padding: 0 !important;
    margin: 0 !important;
    background: white !important;
    color: black !important;
  }

  .header-actions,
  .page-subtitle {
    display: none !important;
  }

  .report-meta {
    border: 1px solid #ccc !important;
    background: white !important;
    color: black !important;
  }

  .table-wrap {
    overflow: visible !important;
    border: none !important;
    background: white !important;
  }

  .report-table {
    min-width: unset !important;
    width: 100% !important;
    font-size: 11px;
  }

  .report-table th,
  .report-table td {
    border: 1px solid #999 !important;
    color: black !important;
    background: white !important;
    padding: 4px 6px !important;
  }

  .row-subtotal td {
    background: #fff59d !important;
    color: black !important;
    font-weight: 700;
  }

  .row-grand-total td {
    background: #bbdefb !important;
    color: black !important;
    font-weight: 800;
  }

  .page-title {
    color: black !important;
    margin-bottom: 8px;
  }

  body {
    background: white !important;
  }
}
</style>