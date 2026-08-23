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

          <button class="btn-secondary" @click="exportToExcel(report, rows, { leftLogoUrl, rightLogoUrl })" :disabled="!rows.length">
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
import ExcelJS from 'exceljs'
import { saveAs } from 'file-saver'
import { computed, onMounted, ref } from 'vue'
import leftLogoUrl from '@/assets/orminlogo.png'
import rightLogoUrl from '@/assets/pdrrmo.png'

const API_BASE = import.meta.env.VITE_API_BASE_URL

const loading = ref(false)
const error = ref('')
const report = ref({})
const rows = ref([])

const asOfInput = ref(getDefaultLocalDateTime())
function getDefaultLocalDateTime() {
  const now = new Date()
  const pad = (n) => String(n).padStart(2, '0')

  return (
    `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}` +
    `T${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`
  )
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
    const asOf = asOfInput.value || ''
    const url = `${API_BASE}analytics/reports/affected-population/${asOf ? `?as_of=${encodeURIComponent(asOf)}` : ''}`

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

// ---- style constants pulled from the sample sheet ----
const FILL_HEADER = 'FFE2EFDA'   // pale green — header block
const FILL_DATA = 'FFE2EFDA'     // pale green — data rows
const FILL_SUBTOTAL = 'FFFFFF00' // yellow
const FILL_TOTAL = 'FFBDD7EE'    // light blue
const FILL_WHITE = 'FFFFFFFF'
 
const THIN_BORDER = {
  top: { style: 'thin', color: { argb: 'FF000000' } },
  left: { style: 'thin', color: { argb: 'FF000000' } },
  bottom: { style: 'thin', color: { argb: 'FF000000' } },
  right: { style: 'thin', color: { argb: 'FF000000' } },
}
 
const TEAL_BORDER = {
  top: { style: 'medium', color: { argb: 'FF008080' } },
  left: { style: 'medium', color: { argb: 'FF008080' } },
  bottom: { style: 'medium', color: { argb: 'FF008080' } },
  right: { style: 'medium', color: { argb: 'FF008080' } },
}
 
const TOTAL_COLS = 20 // A..T
const LAST_COL_LETTER = 'T'
 
const HEADER_FONT = 'Arial Narrow'
 
function applyFillBorder(cell, fillArgb, opts = {}) {
  cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: fillArgb } }
  cell.border = opts.border || THIN_BORDER
  cell.alignment = {
    vertical: 'middle',
    horizontal: opts.align || 'center',
    wrapText: !!opts.wrap,
  }
  if (opts.bold || opts.fontName) {
    cell.font = { ...(cell.font || {}), ...(opts.bold ? { bold: true } : {}), ...(opts.fontName ? { name: opts.fontName } : {}) }
  }
}
 
async function loadImage(url) {
  const res = await fetch(url)
  if (!res.ok) throw new Error(`Failed to fetch logo at ${url} (status ${res.status})`)
  const buffer = await res.arrayBuffer()
 
  // ExcelJS only accepts 'png' | 'jpeg' | 'gif' — detect from content-type first,
  // fall back to the URL's file extension. A mismatch here is the #1 reason a
  // logo silently fails to render in Excel even though the export succeeds.
  const contentType = res.headers.get('content-type') || ''
  let extension = null
  if (contentType.includes('png')) extension = 'png'
  else if (contentType.includes('jpeg') || contentType.includes('jpg')) extension = 'jpeg'
  else if (contentType.includes('gif')) extension = 'gif'
 
  if (!extension) {
    const match = url.match(/\.(png|jpe?g|gif)(\?|#|$)/i)
    if (match) extension = match[1].toLowerCase() === 'jpg' ? 'jpeg' : match[1].toLowerCase()
  }
 
  if (!extension) {
    throw new Error(
      `Could not determine image type for ${url} — ExcelJS only supports png/jpeg/gif (not svg/webp).`
    )
  }
 
  return { buffer, extension }
}
 
// row where the title block ("SITREP No. 8") starts — letterhead occupies rows 1..(TITLE_START-1)
const TITLE_START = 9
 
async function exportToExcel(report, rows, logos = {}) {
  if (!rows?.length) return
 
  const { leftLogoUrl, rightLogoUrl } = logos
  console.log('[exportToExcel] logos received:', { leftLogoUrl, rightLogoUrl })
 
  const asOfText = report?.as_of
    ? `As of ${new Date(report.as_of).toLocaleString('en-US', {
        month: 'long',
        day: '2-digit',
        year: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        hour12: true,
      })}`
    : ''
 
  const wb = new ExcelJS.Workbook()
  const ws = wb.addWorksheet('Affected Population', {
    views: [{ state: 'frozen', ySplit: TITLE_START + 8 }], // freeze under the full header block
  })
 
  // ---------- LETTERHEAD (rows 1-8) ----------
  ws.mergeCells(`A2:${LAST_COL_LETTER}2`)
  ws.getCell('A2').value = 'Republic of the Philippines'
  ws.getCell('A2').font = { italic: true, size: 10, name: HEADER_FONT }
  ws.getCell('A2').alignment = { horizontal: 'center' }
 
  ws.mergeCells(`A3:${LAST_COL_LETTER}3`)
  ws.getCell('A3').value = 'PROVINCE OF ORIENTAL MINDORO'
  ws.getCell('A3').font = { bold: true, size: 13, name: HEADER_FONT }
  ws.getCell('A3').alignment = { horizontal: 'center' }
 
  ws.mergeCells(`A5:${LAST_COL_LETTER}5`)
  ws.getCell('A5').value = 'PROVINCIAL DISASTER RISK REDUCTION AND MANAGEMENT OFFICE'
  ws.getCell('A5').font = { bold: true, size: 11, name: HEADER_FONT }
  ws.getCell('A5').alignment = { horizontal: 'center' }
 
  ws.mergeCells(`A7:${LAST_COL_LETTER}7`)
  ws.getCell('A7').value =
    'Provincial Capitol Complex, Barangay Camilmil, Calapan City 5200, Oriental Mindoro'
  ws.getCell('A7').font = { italic: true, size: 9, name: HEADER_FONT }
  ws.getCell('A7').alignment = { horizontal: 'center' }
 
  // thick rule under the letterhead, spanning the full width
  ws.mergeCells(`A8:${LAST_COL_LETTER}8`)
  ws.getCell('A8').border = { bottom: { style: 'medium', color: { argb: 'FF000000' } } }
 
  for (let r = 1; r <= 8; r++) ws.getRow(r).height = r === 1 || r === 8 ? 6 : 14
 
  // logos — anchored top-left, floating over the letterhead rows (0-indexed col/row)
  if (leftLogoUrl) {
    try {
      console.log('[exportToExcel] fetching left logo:', leftLogoUrl)
      const { buffer, extension } = await loadImage(leftLogoUrl)
      const id = wb.addImage({ buffer, extension })
      ws.addImage(id, { tl: { col: 0.15, row: 0.15 }, ext: { width: 65, height: 65 } })
      console.log('[exportToExcel] left logo embedded, extension:', extension)
    } catch (err) {
      console.warn('[exportToExcel] left logo not embedded:', err.message)
    }
  } else {
    console.warn('[exportToExcel] no leftLogoUrl provided — skipping left logo entirely')
  }
  if (rightLogoUrl) {
    try {
      console.log('[exportToExcel] fetching right logo:', rightLogoUrl)
      const { buffer, extension } = await loadImage(rightLogoUrl)
      const id = wb.addImage({ buffer, extension })
      ws.addImage(id, { tl: { col: 18.6, row: 0.15 }, ext: { width: 65, height: 65 } })
      console.log('[exportToExcel] right logo embedded, extension:', extension)
    } catch (err) {
      console.warn('[exportToExcel] right logo not embedded:', err.message)
    }
  } else {
    console.warn('[exportToExcel] no rightLogoUrl provided — skipping right logo entirely')
  }
 
  ws.columns = [
    { width: 16 }, // Province
    { width: 16 }, // City/Municipality
    { width: 16 }, // Barangay
    { width: 8 },  // Brgys
    { width: 9 },  // Families (affected)
    { width: 9 },  // Persons (affected)
    { width: 7 },  // CUM (ecs)
    { width: 7 },  // NOW (ecs)
    { width: 8 },  // Inside Families CUM
    { width: 8 },  // Inside Families NOW
    { width: 8 },  // Inside Persons CUM
    { width: 8 },  // Inside Persons NOW
    { width: 8 },  // Outside Families CUM
    { width: 8 },  // Outside Families NOW
    { width: 8 },  // Outside Persons CUM
    { width: 8 },  // Outside Persons NOW
    { width: 9 },  // Total Families CUM
    { width: 9 },  // Total Families NOW
    { width: 9 },  // Total Persons CUM
    { width: 9 },  // Total Persons NOW
  ]
 
  // ---------- TITLE BLOCK ----------
  const T1 = TITLE_START       // SITREP No. 8
  const T2 = TITLE_START + 1   // EFFECTS OF SHEAR LINE
  const T3 = TITLE_START + 2   // AFFECTED POPULATION
  const T4 = TITLE_START + 3   // As of ...
  const SPACER = TITLE_START + 4
 
  ws.mergeCells(`A${T1}:${LAST_COL_LETTER}${T1}`)
  ws.getCell(`A${T1}`).value = 'SITREP No. 8'
  ws.getCell(`A${T1}`).alignment = { horizontal: 'left', vertical: 'middle' }
  ws.getCell(`A${T1}`).font = { bold: true } // keep default font here — explicitly excluded from Arial Narrow
 
  ws.mergeCells(`A${T2}:${LAST_COL_LETTER}${T2}`)
  ws.getCell(`A${T2}`).value = 'EFFECTS OF SHEAR LINE'
  ws.getCell(`A${T2}`).alignment = { horizontal: 'center', vertical: 'middle' }
  ws.getCell(`A${T2}`).font = { bold: true, size: 13, name: HEADER_FONT }
 
  ws.mergeCells(`A${T3}:${LAST_COL_LETTER}${T3}`)
  ws.getCell(`A${T3}`).value = 'AFFECTED POPULATION'
  ws.getCell(`A${T3}`).alignment = { horizontal: 'center', vertical: 'middle' }
  ws.getCell(`A${T3}`).font = { bold: true, size: 13, name: HEADER_FONT }
 
  ws.mergeCells(`A${T4}:${LAST_COL_LETTER}${T4}`)
  ws.getCell(`A${T4}`).value = asOfText
  ws.getCell(`A${T4}`).alignment = { horizontal: 'center', vertical: 'middle' }
  ws.getCell(`A${T4}`).font = { bold: true, name: HEADER_FONT }
 
  for (let r = T1; r <= T4; r++) {
    for (let c = 1; c <= TOTAL_COLS; c++) {
      const cell = ws.getRow(r).getCell(c)
      cell.border = {
        top: r === T1 ? TEAL_BORDER.top : undefined,
        left: c === 1 ? TEAL_BORDER.left : undefined,
        bottom: r === T4 ? TEAL_BORDER.bottom : undefined,
        right: c === TOTAL_COLS ? TEAL_BORDER.right : undefined,
      }
    }
  }
  ws.getRow(SPACER).height = 6 // spacer row
 
  // ---------- HEADER BLOCK ----------
  const HR1 = SPACER + 1, HR2 = SPACER + 2, HR3 = SPACER + 3, HR4 = SPACER + 4
 
  // vertical merges for Province / City-Municipality / Barangay
  ws.mergeCells(`A${HR1}:A${HR4}`)
  ws.mergeCells(`B${HR1}:B${HR4}`)
  ws.mergeCells(`C${HR1}:C${HR4}`)
  ws.getCell(`A${HR1}`).value = 'Province'
  ws.getCell(`B${HR1}`).value = 'City / Municipality'
  ws.getCell(`C${HR1}`).value = 'Barangay'
 
  // group headers row (HR1)
  ws.mergeCells(`D${HR1}:F${HR1}`)
  ws.getCell(`D${HR1}`).value = 'NO. OF AFFECTED'
 
  ws.mergeCells(`G${HR1}:H${HR1}`)
  ws.getCell(`G${HR1}`).value = 'NO. OF ECS'
 
  ws.mergeCells(`I${HR1}:L${HR1}`)
  ws.getCell(`I${HR1}`).value = 'INSIDE EVACUATION CENTERS'
 
  ws.mergeCells(`M${HR1}:P${HR1}`)
  ws.getCell(`M${HR1}`).value = 'OUTSIDE EVACUATION CENTERS'
 
  ws.mergeCells(`Q${HR1}:T${HR1}`)
  ws.getCell(`Q${HR1}`).value = 'TOTAL SERVED (CURRENT)'
 
  // sub-label row for TOTAL SERVED
  ws.mergeCells(`Q${HR2}:T${HR2}`)
  ws.getCell(`Q${HR2}`).value = '(Inside + Outside)'
 
  // Families / Persons row (HR3) for Inside / Outside / Total blocks
  ws.mergeCells(`I${HR3}:J${HR3}`)
  ws.getCell(`I${HR3}`).value = 'Families'
  ws.mergeCells(`K${HR3}:L${HR3}`)
  ws.getCell(`K${HR3}`).value = 'Persons'
 
  ws.mergeCells(`M${HR3}:N${HR3}`)
  ws.getCell(`M${HR3}`).value = 'Families'
  ws.mergeCells(`O${HR3}:P${HR3}`)
  ws.getCell(`O${HR3}`).value = 'Persons'
 
  ws.mergeCells(`Q${HR3}:R${HR3}`)
  ws.getCell(`Q${HR3}`).value = 'Families'
  ws.mergeCells(`S${HR3}:T${HR3}`)
  ws.getCell(`S${HR3}`).value = 'Persons'
 
  // final row (HR4): CUM / NOW labels + Brgys/Families/Persons for affected block
  ws.getCell(`D${HR4}`).value = 'Brgys.'
  ws.getCell(`E${HR4}`).value = 'Families'
  ws.getCell(`F${HR4}`).value = 'Persons'
  ws.getCell(`G${HR4}`).value = 'CUM'
  ws.getCell(`H${HR4}`).value = 'NOW'
  ;['I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T'].forEach((col, i) => {
    ws.getCell(`${col}${HR4}`).value = i % 2 === 0 ? 'CUM' : 'NOW'
  })
 
  // style every cell in the header block
  for (let r = HR1; r <= HR4; r++) {
    for (let c = 1; c <= TOTAL_COLS; c++) {
      const cell = ws.getRow(r).getCell(c)
      applyFillBorder(cell, FILL_HEADER, { bold: true, wrap: true, fontName: HEADER_FONT })
    }
  }
  ws.getRow(HR1).height = 18
  ws.getRow(HR4).height = 16
 
  // ---------- DATA ROWS ----------
  let currentRow = HR4 + 1
  const numericFields = [
    'affected_brgys', 'affected_families', 'affected_persons',
    'ecs_cum', 'ecs_now',
    'inside_families_cum', 'inside_families_now', 'inside_persons_cum', 'inside_persons_now',
    'outside_families_cum', 'outside_families_now', 'outside_persons_cum', 'outside_persons_now',
    'total_families_cum', 'total_families_now', 'total_persons_cum', 'total_persons_now',
  ]
 
  for (const row of rows) {
    const isSubtotal = row.row_type === 'subtotal'
    const isGrandTotal = row.row_type === 'grand_total'
    const fill = isGrandTotal ? FILL_TOTAL : isSubtotal ? FILL_SUBTOTAL : FILL_DATA
 
    const excelRow = ws.getRow(currentRow)
    excelRow.getCell(1).value = isGrandTotal ? '' : row.province || ''
    excelRow.getCell(2).value = isGrandTotal ? '' : row.municipality || ''
    excelRow.getCell(3).value = isGrandTotal ? 'Total' : row.barangay || ''
 
    numericFields.forEach((field, idx) => {
      const col = idx + 4 // starts at column D
      const val = row[field]
      // leave blank (not 0) when the source row never populated this location (pure barangay stub)
      excelRow.getCell(col).value = val === undefined || val === null ? '' : Number(val)
    })
 
    for (let c = 1; c <= TOTAL_COLS; c++) {
      const cell = excelRow.getCell(c)
      applyFillBorder(cell, fill, {
        align: c <= 3 ? 'left' : 'center',
        bold: isSubtotal || isGrandTotal,
      })
      if (typeof cell.value === 'number') {
        cell.numFmt = '#,##0'
      }
    }
 
    currentRow++
  }
 
  // ---------- DOWNLOAD ----------
  const buffer = await wb.xlsx.writeBuffer()
  const blob = new Blob([buffer], {
    type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  })
  saveAs(blob, 'affected_population_report.xlsx')
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
  padding: 1.75rem;
  color: #e5e7eb;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: end;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 1.25rem;
}

.page-title {
  margin: 0;
  padding-left: 0.85rem;
  border-left: 4px solid #00b4ff;
  font-size: 1.7rem;
  font-weight: 800;
  letter-spacing: 0.01em;
}

.page-subtitle {
  margin: 0.4rem 0 0 1.05rem;
  color: #94a3b8;
  font-size: 0.92rem;
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
  font-weight: 600;
}

.filter-input {
  background: #0f1a25;
  color: #e5e7eb;
  border: 1px solid rgba(0, 204, 255, 0.25);
  border-radius: 10px;
  padding: 0.65rem 0.8rem;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.filter-input:focus {
  outline: none;
  border-color: rgba(0, 204, 255, 0.6);
  box-shadow: 0 0 0 3px rgba(0, 180, 255, 0.18);
}

.btn-primary {
  background: linear-gradient(135deg, #00c2ff, #0080ff);
  color: white;
  border: none;
  border-radius: 10px;
  padding: 0.72rem 1.1rem;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 6px 16px rgba(0, 136, 255, 0.3);
  transition: transform 0.15s ease, box-shadow 0.15s ease, opacity 0.15s ease;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 22px rgba(0, 136, 255, 0.4);
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  box-shadow: none;
  transform: none;
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.03);
  color: #dbeafe;
  border: 1px solid rgba(0, 204, 255, 0.3);
  border-radius: 10px;
  padding: 0.72rem 1.1rem;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.15s ease, transform 0.15s ease, border-color 0.15s ease;
}

.btn-secondary:hover:not(:disabled) {
  background: rgba(0, 180, 255, 0.12);
  border-color: rgba(0, 204, 255, 0.55);
  transform: translateY(-2px);
}

.btn-secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.report-meta {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
  margin-bottom: 1.25rem;
  padding: 1rem 1.2rem;
  border-radius: 14px;
  background: linear-gradient(135deg, rgba(0, 180, 255, 0.08), rgba(255, 255, 255, 0.02));
  border: 1px solid rgba(0, 204, 255, 0.18);
}

.table-wrap {
  overflow: auto;
  border-radius: 16px;
  border: 1px solid rgba(0, 204, 255, 0.14);
  box-shadow: 0 14px 34px rgba(0, 0, 0, 0.35), 0 2px 6px rgba(0, 0, 0, 0.25);
  max-height: 72vh;
}

.report-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 1600px;
}

.report-table th,
.report-table td {
  border: 1px solid rgba(255, 255, 255, 0.07);
  padding: 0.75rem 0.8rem;
  text-align: center;
  white-space: nowrap;
}

.report-table thead th {
  position: sticky;
  top: 0;
  z-index: 2;
  font-weight: 800 !important;
  font-size: 0.88rem;
  letter-spacing: 0.02em;
  text-transform: uppercase;
  box-shadow: inset 0 -1px 0 rgba(0, 0, 0, 0.25);
}

/* base identity columns (Province / City / Barangay) — solid, theme-proof */
.report-table thead th:nth-child(-n+3) {
  background: #101c2b !important;
  color: #a8c5e0 !important;
}

/* --- Group header row (row 1): solid, dark shade, white text --- */
.report-table thead tr:nth-child(1) th:nth-child(4) {
  background: #b45309 !important;
  color: #ffffff !important;
}
.report-table thead tr:nth-child(1) th:nth-child(5) {
  background: #7e22ce !important;
  color: #ffffff !important;
}
.report-table thead tr:nth-child(1) th:nth-child(6) {
  background: #0e7490 !important;
  color: #ffffff !important;
}
.report-table thead tr:nth-child(1) th:nth-child(7) {
  background: #be185d !important;
  color: #ffffff !important;
}
.report-table thead tr:nth-child(1) th:nth-child(8) {
  background: #15803d !important;
  color: #ffffff !important;
}

/* --- Sub-header row (row 2): solid, medium shade, white text --- */
.report-table thead tr:nth-child(2) th:nth-child(-n+3) {
  background: #d97706 !important;
  color: #ffffff !important;
}
.report-table thead tr:nth-child(2) th:nth-child(n+4):nth-child(-n+5) {
  background: #9333ea !important;
  color: #ffffff !important;
}
.report-table thead tr:nth-child(2) th:nth-child(n+6):nth-child(-n+7) {
  background: #0891b2 !important;
  color: #ffffff !important;
}
.report-table thead tr:nth-child(2) th:nth-child(n+8):nth-child(-n+9) {
  background: #db2777 !important;
  color: #ffffff !important;
}
.report-table thead tr:nth-child(2) th:nth-child(n+10) {
  background: #16a34a !important;
  color: #ffffff !important;
}

/* --- CUM / NOW row (row 3): solid, light shade, dark text for contrast --- */
.report-table thead tr:nth-child(3) th:nth-child(-n+4) {
  background: #fbbf24 !important;
  color: #1c1300 !important;
}
.report-table thead tr:nth-child(3) th:nth-child(n+5):nth-child(-n+8) {
  background: #f0abfc !important;
  color: #2e0a35 !important;
}
.report-table thead tr:nth-child(3) th:nth-child(n+9) {
  background: #6ee7b7 !important;
  color: #032116 !important;
}

/* --- Body columns tinted subtly to match their section --- */
.row-data td:nth-child(-n+3) {
  text-align: left;
  font-weight: 600;
}
.row-data td:nth-child(n+4):nth-child(-n+6) {
  background: rgba(217, 119, 6, 0.06) !important;
}
.row-data td:nth-child(n+7):nth-child(-n+8) {
  background: rgba(147, 51, 234, 0.06) !important;
}
.row-data td:nth-child(n+9):nth-child(-n+12) {
  background: rgba(8, 145, 178, 0.06) !important;
}
.row-data td:nth-child(n+13):nth-child(-n+16) {
  background: rgba(219, 39, 119, 0.06) !important;
}
.row-data td:nth-child(n+17) {
  background: rgba(22, 163, 74, 0.07) !important;
  font-weight: 600;
}

.report-table td:first-child,
.report-table td:nth-child(2),
.report-table td:nth-child(3) {
  text-align: left;
}

.row-data:hover td {
  background: rgba(0, 180, 255, 0.09) !important;
}

/* Subtotal / Grand total — swapped from yellow to indigo / sky blue.
   Raised specificity + !important to beat the pre-existing global class rules. */
.report-table tbody tr.row-subtotal,
.report-table tbody tr.row-subtotal td {
  background: rgba(129, 140, 248, 0.22) !important;
  font-weight: 700;
}

.report-table tbody tr.row-grand-total,
.report-table tbody tr.row-grand-total td {
  background: rgba(56, 189, 248, 0.22) !important;
  font-weight: 800;
}

.error-box {
  margin-bottom: 1rem;
  padding: 0.9rem 1rem;
  border-radius: 12px;
  background: rgba(239, 68, 68, 0.14);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #fecaca;
}

.empty-state {
  padding: 1rem;
  color: #94a3b8;
}

@media (max-width: 768px) {
  .report-container {
    padding: 1rem;
  }

  .page-title {
    font-size: 1.35rem;
  }
}

@media print {
  @page {
    size: landscape;
    margin: 8mm;
  }

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

  .page-title {
    border-left: none !important;
    padding-left: 0 !important;
    color: black !important;
    margin-bottom: 8px;
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
    box-shadow: none !important;
    max-height: none !important;
  }

  .report-table {
    min-width: unset !important;
    width: 100% !important;
    table-layout: fixed !important;
    font-size: 8.5px;
  }

  .report-table th,
  .report-table td {
    border: 1px solid #999 !important;
    color: black !important;
    background: white !important;
    padding: 3px 4px !important;
    white-space: normal !important;
    word-break: break-word;
  }

  .report-table thead th {
    position: static !important;
    box-shadow: none !important;
  }

  /* Force plain black-on-white for print — matching the SAME specificity
     as the colored header rules above so they actually win in the cascade. */
  .report-table thead th:nth-child(-n+3),
  .report-table thead tr:nth-child(1) th:nth-child(4),
  .report-table thead tr:nth-child(1) th:nth-child(5),
  .report-table thead tr:nth-child(1) th:nth-child(6),
  .report-table thead tr:nth-child(1) th:nth-child(7),
  .report-table thead tr:nth-child(1) th:nth-child(8),
  .report-table thead tr:nth-child(2) th:nth-child(-n+3),
  .report-table thead tr:nth-child(2) th:nth-child(n+4):nth-child(-n+5),
  .report-table thead tr:nth-child(2) th:nth-child(n+6):nth-child(-n+7),
  .report-table thead tr:nth-child(2) th:nth-child(n+8):nth-child(-n+9),
  .report-table thead tr:nth-child(2) th:nth-child(n+10),
  .report-table thead tr:nth-child(3) th:nth-child(-n+4),
  .report-table thead tr:nth-child(3) th:nth-child(n+5):nth-child(-n+8),
  .report-table thead tr:nth-child(3) th:nth-child(n+9) {
    background: white !important;
    color: black !important;
  }

  .row-data td:nth-child(-n+3),
  .row-data td:nth-child(n+4):nth-child(-n+6),
  .row-data td:nth-child(n+7):nth-child(-n+8),
  .row-data td:nth-child(n+9):nth-child(-n+12),
  .row-data td:nth-child(n+13):nth-child(-n+16),
  .row-data td:nth-child(n+17) {
    background: white !important;
    color: black !important;
    font-weight: normal !important;
  }

  tr {
    page-break-inside: avoid;
  }

  .report-table tbody tr.row-subtotal,
  .report-table tbody tr.row-subtotal td {
    background: #fff59d !important;
    color: black !important;
    font-weight: 700;
  }

  .report-table tbody tr.row-grand-total,
  .report-table tbody tr.row-grand-total td {
    background: #bbdefb !important;
    color: black !important;
    font-weight: 800;
  }

  body {
    background: white !important;
  }
}
</style>