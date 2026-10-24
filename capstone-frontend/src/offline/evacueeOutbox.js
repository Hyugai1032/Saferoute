// Offline-first evacuee registration.
//
// Every new evacuee is saved on the phone first (IndexedDB), then uploaded in small
// batches whenever there is a connection. Each record carries a UUID made on the phone,
// so a retry after a dropped connection never creates a duplicate on the server.
//
// Upload is attempted: right after saving, when the browser reports it is back online,
// when the app comes back to the foreground, every 30 seconds while records are waiting,
// and when staff tap "Sync now". (iPhones don't support Background Sync, so the app
// has to be opened for records to upload; Android behaves the same way here.)
import axios from 'axios'
import { reactive } from 'vue'
import { getDB, OUTBOX, currentOwner, requestPersistentStorage, plain } from './db'

const API_BASE = import.meta.env.VITE_API_BASE_URL
const SYNC_PATH = 'evac_centers/evacuees/sync/'
const BATCH_SIZE = 20          // server accepts up to 50; smaller batches suit weak signal
const REQUEST_TIMEOUT_MS = 30000
const RETRY_INTERVAL_MS = 30000

export const outboxState = reactive({
  online: typeof navigator === 'undefined' ? true : navigator.onLine,
  records: [],          // this account's records still on the phone (pending + needs attention)
  pendingCount: 0,
  failedCount: 0,
  otherAccountCount: 0, // records saved under a different login on this phone
  syncing: false,
  lastSyncAt: null,
  lastError: '',
  authRequired: false,  // the saved login expired; staff must sign in again to upload
  notices: [],          // e.g. "possible duplicate" warnings from the server
})

// A plain axios instance: unlike services/api.js it never redirects to the login page
// in the middle of a background upload. An expired login is shown in the banner instead.
const http = axios.create({ baseURL: API_BASE, timeout: REQUEST_TIMEOUT_MS })

function nowLocalIso() {
  // The server stores Asia/Manila local time (USE_TZ = False), so send the phone's
  // local wall-clock time without a timezone suffix.
  const d = new Date()
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}` +
    `T${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
}

function newId() {
  if (crypto?.randomUUID) return crypto.randomUUID()
  // Fallback for older browsers / non-HTTPS dev hosts
  const b = crypto.getRandomValues(new Uint8Array(16))
  b[6] = (b[6] & 0x0f) | 0x40
  b[8] = (b[8] & 0x3f) | 0x80
  const h = [...b].map((x) => x.toString(16).padStart(2, '0')).join('')
  return `${h.slice(0, 8)}-${h.slice(8, 12)}-${h.slice(12, 16)}-${h.slice(16, 20)}-${h.slice(20)}`
}

function notifyOtherTabs() {
  try {
    channel?.postMessage('changed')
  } catch { /* ignore */ }
}

const channel = typeof BroadcastChannel !== 'undefined'
  ? new BroadcastChannel('saferoute-evacuee-outbox')
  : null
if (channel) channel.onmessage = () => refreshOutbox()

/** Re-read the outbox from IndexedDB into outboxState. */
export async function refreshOutbox() {
  const db = await getDB()
  const all = await db.getAll(OUTBOX)
  const owner = currentOwner()
  const mine = all
    .filter((r) => r.owner === owner)
    .sort((a, b) => b.createdAt - a.createdAt)

  outboxState.records = mine
  outboxState.pendingCount = mine.filter((r) => r.status === 'pending').length
  outboxState.failedCount = mine.filter((r) => r.status === 'failed').length
  outboxState.otherAccountCount = all.length - mine.length
  return mine
}

/** Save a new evacuee on the phone. Returns the stored record. */
export async function queueEvacuee(payload) {
  const owner = currentOwner()
  if (!owner) throw new Error('Not signed in.')

  const client_id = newId()
  const record = {
    client_id,
    owner,
    status: 'pending',
    error: '',
    attempts: 0,
    createdAt: Date.now(),
    payload: { ...plain(payload), client_id, recorded_at: nowLocalIso() },
  }
  const db = await getDB()
  await db.put(OUTBOX, record)
  await refreshOutbox()
  notifyOtherTabs()
  return record
}

/** Edit a record that hasn't uploaded yet (also used to fix a record the server refused). */
export async function updateQueued(client_id, payload) {
  const db = await getDB()
  const record = await db.get(OUTBOX, client_id)
  if (!record) return null
  record.payload = { ...plain(payload), client_id, recorded_at: record.payload.recorded_at }
  record.status = 'pending'
  record.error = ''
  await db.put(OUTBOX, record)
  await refreshOutbox()
  notifyOtherTabs()
  return record
}

export async function discardQueued(client_id) {
  const db = await getDB()
  await db.delete(OUTBOX, client_id)
  await refreshOutbox()
  notifyOtherTabs()
}

export async function retryQueued(client_id) {
  const db = await getDB()
  const record = await db.get(OUTBOX, client_id)
  if (record) {
    record.status = 'pending'
    record.error = ''
    await db.put(OUTBOX, record)
  }
  await refreshOutbox()
  return syncNow()
}

function describeErrors(errors) {
  if (!errors) return 'The server could not accept this record.'
  if (typeof errors === 'string') return errors
  return Object.entries(errors)
    .map(([field, msgs]) => `${field.replace(/_/g, ' ')}: ${[].concat(msgs).join(' ')}`)
    .join('; ')
}

async function refreshAccessToken() {
  const refresh = localStorage.getItem('refresh_token')
  if (!refresh) return null
  try {
    const res = await http.post('auth/refresh/', { refresh })
    localStorage.setItem('access_token', res.data.access)
    return res.data.access
  } catch {
    return null
  }
}

async function postBatch(records) {
  const send = (token) => http.post(
    SYNC_PATH,
    { records: records.map((r) => r.payload) },
    { headers: token ? { Authorization: `Bearer ${token}` } : {} },
  )

  try {
    return await send(localStorage.getItem('access_token'))
  } catch (err) {
    if (err.response?.status !== 401) throw err
    const token = await refreshAccessToken()
    if (!token) {
      outboxState.authRequired = true
      throw err
    }
    return send(token)
  }
}

let syncPromise = null

/**
 * Upload this account's pending records. Safe to call any time and from several places;
 * overlapping calls share one run.
 */
export function syncNow() {
  if (!syncPromise) {
    syncPromise = runSync().finally(() => { syncPromise = null })
  }
  return syncPromise
}

async function runSync() {
  const owner = currentOwner()
  const hasLogin = localStorage.getItem('access_token') || localStorage.getItem('refresh_token')
  if (!owner || !hasLogin) {
    await refreshOutbox()
    return { uploaded: 0 }
  }

  // Only one tab uploads at a time (duplicates are prevented server-side anyway).
  if (navigator.locks?.request) {
    return navigator.locks.request('saferoute-evacuee-sync', { ifAvailable: true },
      (lock) => (lock ? uploadAll(owner) : { uploaded: 0 }))
  }
  return uploadAll(owner)
}

async function uploadAll(owner) {
  const db = await getDB()
  let uploaded = 0

  outboxState.syncing = true
  outboxState.authRequired = false
  try {
    // Keep going batch by batch until nothing is pending or the connection fails.
    for (;;) {
      const pending = (await db.getAllFromIndex(OUTBOX, 'owner', owner))
        .filter((r) => r.status === 'pending')
        .sort((a, b) => a.createdAt - b.createdAt)
        .slice(0, BATCH_SIZE)
      if (!pending.length) break

      let res
      try {
        res = await postBatch(pending)
      } catch (err) {
        for (const r of pending) {
          r.attempts += 1
          await db.put(OUTBOX, r)
        }
        outboxState.lastError = outboxState.authRequired
          ? 'Your sign-in has expired. Sign in again to upload saved records.'
          : err.response
            ? `Upload failed (server error ${err.response.status}). Will retry.`
            : 'No connection. Records are safe on this phone and will upload automatically.'
        break
      }

      const byId = new Map(pending.map((r) => [r.client_id, r]))
      for (const result of res.data?.results || []) {
        const record = byId.get(result.client_id)
        if (!record) continue
        byId.delete(result.client_id)

        if (result.status === 'created' || result.status === 'exists') {
          await db.delete(OUTBOX, record.client_id)
          uploaded += 1
          if (result.possible_duplicates?.length) {
            const p = record.payload
            outboxState.notices.unshift(
              `${p.last_name}, ${p.first_name} was uploaded, but someone with the same name is already registered at this center. Please check for a duplicate.`
            )
          }
        } else {
          record.status = 'failed'
          record.error = result.status === 'rejected'
            ? (result.detail || 'Not allowed for this account.')
            : describeErrors(result.errors)
          await db.put(OUTBOX, record)
        }
      }
      // Anything the server didn't report on stays pending for the next run.
      outboxState.lastError = ''
      outboxState.lastSyncAt = Date.now()
    }
  } finally {
    outboxState.syncing = false
    outboxState.notices = outboxState.notices.slice(0, 5)
    await refreshOutbox()
    if (uploaded) {
      notifyOtherTabs()
      window.dispatchEvent(new CustomEvent('outbox:uploaded', { detail: { uploaded } }))
    }
  }
  return { uploaded }
}

export function dismissNotice(index) {
  outboxState.notices.splice(index, 1)
}

/** Last-resort backup: download this account's unsent records as a CSV file. */
export function exportOutboxCsv(records = outboxState.records) {
  const columns = [
    'client_id', 'recorded_at', 'status', 'error', 'last_name', 'first_name', 'middle_name',
    'age', 'sex', 'contact_number', 'address', 'is_family_head', 'family_head_name',
    'reason_for_evacuation', 'is_child', 'is_senior', 'is_pwd', 'is_pregnant',
    'is_lactating', 'center', 'remarks',
  ]
  const cell = (v) => {
    const s = v == null ? '' : String(v)
    // Quote everything; prefix formula-like text so spreadsheets don't execute it.
    const safe = /^[=+\-@]/.test(s) ? `'${s}` : s
    return `"${safe.replace(/"/g, '""')}"`
  }
  const rows = records.map((r) => columns.map((c) => {
    if (c === 'status') return cell(r.status)
    if (c === 'error') return cell(r.error)
    return cell(r.payload[c])
  }).join(','))

  const blob = new Blob(['﻿' + [columns.join(','), ...rows].join('\r\n')], {
    type: 'text/csv;charset=utf-8',
  })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `unsent_evacuees_${nowLocalIso().slice(0, 16).replace(/[:T]/g, '-')}.csv`
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}

let started = false

/** Called once at app start. */
export function startOutboxAutoSync() {
  if (started || typeof window === 'undefined') return
  started = true

  requestPersistentStorage()

  window.addEventListener('online', () => {
    outboxState.online = true
    syncNow()
  })
  window.addEventListener('offline', () => {
    outboxState.online = false
  })
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') syncNow()
  })
  setInterval(() => {
    if (outboxState.pendingCount > 0 && document.visibilityState === 'visible') syncNow()
  }, RETRY_INTERVAL_MS)

  refreshOutbox().then(() => syncNow())
}