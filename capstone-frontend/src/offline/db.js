// IndexedDB storage for offline use. IndexedDB (unlike localStorage) survives the
// localStorage.clear() that runs on a failed token refresh, holds far more data, and
// is the storage browsers keep for installed apps.
import { openDB } from 'idb'

const DB_NAME = 'saferoute-offline'
const DB_VERSION = 1

export const OUTBOX = 'evacueeOutbox' // records typed in offline, waiting to upload
const CACHE = 'cache'                  // last good copy of lists the forms need

let dbPromise = null

export function getDB() {
  if (!dbPromise) {
    dbPromise = openDB(DB_NAME, DB_VERSION, {
      upgrade(db) {
        if (!db.objectStoreNames.contains(OUTBOX)) {
          const store = db.createObjectStore(OUTBOX, { keyPath: 'client_id' })
          store.createIndex('owner', 'owner')
        }
        if (!db.objectStoreNames.contains(CACHE)) {
          db.createObjectStore(CACHE)
        }
      },
    })
  }
  return dbPromise
}

/** Who is signed in on this phone. Offline records belong to this account. */
export function currentOwner() {
  try {
    const user = JSON.parse(localStorage.getItem('userData') || '{}')
    return (user.email || '').trim().toLowerCase()
  } catch {
    return ''
  }
}

// Cached lists are kept per account so one user never sees another user's data.
const cacheKey = (name) => `${currentOwner() || 'anon'}:${name}`

/**
 * A plain copy of a value. Vue's reactive proxies can't be stored in IndexedDB
 * (DataCloneError), and everything cached here is JSON from the API anyway.
 */
export function plain(value) {
  return value === undefined ? undefined : JSON.parse(JSON.stringify(value))
}

export async function cacheSet(name, value) {
  try {
    const db = await getDB()
    await db.put(CACHE, { value: plain(value), savedAt: Date.now() }, cacheKey(name))
  } catch (err) {
    console.warn('Offline cache write failed:', err)
  }
}

/** Returns { value, savedAt } or null. */
export async function cacheGet(name) {
  try {
    const db = await getDB()
    return (await db.get(CACHE, cacheKey(name))) || null
  } catch {
    return null
  }
}

/** Ask the browser not to clear this app's data when the phone is low on space. */
export async function requestPersistentStorage() {
  try {
    if (navigator.storage?.persist && !(await navigator.storage.persisted())) {
      await navigator.storage.persist()
    }
  } catch {
    /* not supported: nothing to do */
  }
}