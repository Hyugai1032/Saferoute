// Backend runs with USE_TZ=False, so timestamps arrive with no offset and are
// Asia/Manila local time. Parse and display them consistently everywhere.
const TZ = 'Asia/Manila'

export function parseServerDate(value) {
  if (!value) return null
  if (value instanceof Date) return isNaN(value) ? null : value
  let s = String(value).trim().replace(' ', 'T')
  if (/^\d{4}-\d{2}-\d{2}$/.test(s)) s += 'T00:00:00'
  s = s.replace(/(\.\d{3})\d+/, '$1')                 // trim microseconds (Safari)
  if (!/(Z|[+-]\d{2}:?\d{2})$/.test(s)) s += '+08:00' // naive -> Manila
  const d = new Date(s)
  return isNaN(d) ? null : d
}

export function formatDateTime(value, { seconds = false } = {}) {
  const d = parseServerDate(value)
  if (!d) return '—'
  return d.toLocaleString('en-PH', {
    timeZone: TZ, year: 'numeric', month: 'short', day: 'numeric',
    hour: 'numeric', minute: '2-digit', ...(seconds ? { second: '2-digit' } : {}),
  })
}

export function formatDate(value) {
  const d = parseServerDate(value)
  if (!d) return '—'
  return d.toLocaleDateString('en-PH', { timeZone: TZ, year: 'numeric', month: 'short', day: 'numeric' })
}

export function hoursSince(value) {
  const d = parseServerDate(value)
  return d ? (Date.now() - d.getTime()) / 3600000 : null
}

export function timeAgo(value) {
  const d = parseServerDate(value)
  if (!d) return null
  const mins = Math.round((Date.now() - d.getTime()) / 60000)
  if (mins < 1) return 'just now'
  if (mins < 60) return `${mins} min ago`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `${hrs} hr ago`
  const days = Math.floor(hrs / 24)
  return `${days} day${days === 1 ? '' : 's'} ago`
}