// ═══════════════════════════════════════════════════════════════
// AAMUSTED GCC - Local-First IndexedDB Data Layer
// All data lives here. Syncs to cloud when online.
// ═══════════════════════════════════════════════════════════════

const DB_NAME = 'AAMUSTED_GCC_DB';
const DB_VERSION = 2;
let db = null;

// All tables that mirror the SQLite/PostgreSQL schema
const STORES = {
  Student:             { keyPath: 'id', indexes: ['global_id', 'index_number', 'case_number'] },
  Appointment:         { keyPath: 'id', indexes: ['global_id', 'student_id', 'booking_ref', 'status'] },
  BookingRequest:      { keyPath: 'id', indexes: ['global_id', 'reference', 'status', 'index_number'] },
  session:             { keyPath: 'id', indexes: ['global_id', 'appointment_id'] },
  Referral:            { keyPath: 'id', indexes: ['global_id', 'session_id'] },
  CaseManagement:      { keyPath: 'id', indexes: ['global_id', 'session_id'] },
  OutcomeQuestionnaire:{ keyPath: 'id', indexes: ['global_id', 'student_id'] },
  DASS21:              { keyPath: 'id', indexes: ['global_id', 'student_id'] },
  SessionIssue:        { keyPath: 'id', indexes: ['global_id', 'session_id'] },
  Feedback:            { keyPath: 'id', indexes: ['global_id', 'session_id'] },
  Notification:        { keyPath: 'id', indexes: ['global_id', 'user_id'] },
  app_settings:        { keyPath: 'id', indexes: ['global_id', 'setting_name'] },
  users:               { keyPath: 'id', indexes: ['username'] },
  audit_logs:          { keyPath: 'id', indexes: ['user_id'] },
  SMSQueue:            { keyPath: 'id', indexes: ['status'] },
  Counsellor:          { keyPath: 'id', indexes: [] },
  reports:             { keyPath: 'id', indexes: [] },
  // Sync queue: pending offline changes
  _sync_queue:         { keyPath: '_queue_id', indexes: ['table_name', 'record_id', 'sync_status'] },
  // Cached page responses for offline navigation
  _page_cache:         { keyPath: 'url' },
  // Local metadata
  _meta:               { keyPath: 'key' }
};

// ── INIT ──────────────────────────────────────────────────────
function initDB() {
  return new Promise((resolve, reject) => {
    if (db) { resolve(db); return; }
    const req = indexedDB.open(DB_NAME, DB_VERSION);

    req.onupgradeneeded = e => {
      const d = e.target.result;
      for (const [name, cfg] of Object.entries(STORES)) {
        if (!d.objectStoreNames.contains(name)) {
          const store = d.createObjectStore(name, { keyPath: cfg.keyPath, autoIncrement: cfg.keyPath === '_queue_id' });
          for (const idx of (cfg.indexes || [])) {
            store.createIndex(idx, idx, { unique: false });
          }
        }
      }
    };

    req.onsuccess = e => { db = e.target.result; resolve(db); };
    req.onerror = e => reject(e.target.error);
  });
}

// ── GENERIC CRUD ──────────────────────────────────────────────

async function dbGetAll(storeName) {
  await initDB();
  return new Promise((res, rej) => {
    const tx = db.transaction(storeName, 'readonly');
    const req = tx.objectStore(storeName).getAll();
    req.onsuccess = () => res(req.result || []);
    req.onerror = e => rej(e.target.error);
  });
}

async function dbGet(storeName, key) {
  await initDB();
  return new Promise((res, rej) => {
    const tx = db.transaction(storeName, 'readonly');
    const req = tx.objectStore(storeName).get(key);
    req.onsuccess = () => res(req.result);
    req.onerror = e => rej(e.target.error);
  });
}

async function dbGetByIndex(storeName, indexName, value) {
  await initDB();
  return new Promise((res, rej) => {
    const tx = db.transaction(storeName, 'readonly');
    const idx = tx.objectStore(storeName).index(indexName);
    const req = idx.getAll(value);
    req.onsuccess = () => res(req.result || []);
    req.onerror = e => rej(e.target.error);
  });
}

async function dbPut(storeName, record) {
  await initDB();
  return new Promise((res, rej) => {
    const tx = db.transaction(storeName, 'readwrite');
    tx.objectStore(storeName).put(record);
    tx.oncomplete = () => res(true);
    tx.onerror = e => rej(e.target.error);
  });
}

async function dbDelete(storeName, key) {
  await initDB();
  return new Promise((res, rej) => {
    const tx = db.transaction(storeName, 'readwrite');
    tx.objectStore(storeName).delete(key);
    tx.oncomplete = () => res(true);
    tx.onerror = e => rej(e.target.error);
  });
}

async function dbClear(storeName) {
  await initDB();
  return new Promise((res, rej) => {
    const tx = db.transaction(storeName, 'readwrite');
    tx.objectStore(storeName).clear();
    tx.oncomplete = () => res(true);
    tx.onerror = e => rej(e.target.error);
  });
}

async function dbCount(storeName) {
  await initDB();
  return new Promise((res, rej) => {
    const tx = db.transaction(storeName, 'readonly');
    const req = tx.objectStore(storeName).count();
    req.onsuccess = () => res(req.result);
    req.onerror = e => rej(e.target.error);
  });
}

// ── SYNC QUEUE ────────────────────────────────────────────────
// Every offline change goes here, then syncs when online

async function queueChange(tableName, recordId, operation, data) {
  await initDB();
  return new Promise((res, rej) => {
    const tx = db.transaction('_sync_queue', 'readwrite');
    tx.objectStore('_sync_queue').add({
      table_name: tableName,
      record_id: recordId,
      operation: operation,   // 'create', 'update', 'delete'
      data: data,
      sync_status: 'pending',
      created_at: new Date().toISOString(),
      retry_count: 0
    });
    tx.oncomplete = () => res(true);
    tx.onerror = e => rej(e.target.error);
  });
}

async function getPendingChanges() {
  await initDB();
  return new Promise((res, rej) => {
    const tx = db.transaction('_sync_queue', 'readonly');
    const idx = tx.objectStore('_sync_queue').index('sync_status');
    const req = idx.getAll('pending');
    req.onsuccess = () => res(req.result || []);
    req.onerror = e => rej(e.target.error);
  });
}

async function markSynced(queueId) {
  await initDB();
  return new Promise((res, rej) => {
    const tx = db.transaction('_sync_queue', 'readwrite');
    const store = tx.objectStore('_sync_queue');
    const req = store.get(queueId);
    req.onsuccess = () => {
      const item = req.result;
      if (item) {
        item.sync_status = 'synced';
        store.put(item);
      }
    };
    tx.oncomplete = () => res(true);
    tx.onerror = e => rej(e.target.error);
  });
}

async function markFailed(queueId) {
  await initDB();
  return new Promise((res, rej) => {
    const tx = db.transaction('_sync_queue', 'readwrite');
    const store = tx.objectStore('_sync_queue');
    const req = store.get(queueId);
    req.onsuccess = () => {
      const item = req.result;
      if (item) {
        item.retry_count = (item.retry_count || 0) + 1;
        item.sync_status = item.retry_count >= 5 ? 'failed' : 'pending';
        store.put(item);
      }
    };
    tx.oncomplete = () => res(true);
    tx.onerror = e => rej(e.target.error);
  });
}

async function clearSyncQueue() {
  await initDB();
  return new Promise((res, rej) => {
    const tx = db.transaction('_sync_queue', 'readwrite');
    tx.objectStore('_sync_queue').clear();
    tx.oncomplete = () => res(true);
    tx.onerror = e => rej(e.target.error);
  });
}

// ── HIGH-LEVEL SAVE (writes to IndexedDB + queues sync) ──────

async function saveRecord(tableName, record, operation) {
  const op = operation || (record.id ? 'update' : 'create');

  // Assign a local ID for creates if missing
  if (op === 'create' && !record.id) {
    record.id = Date.now() + Math.floor(Math.random() * 1000);
  }

  // Mark sync metadata
  record._sync_status = 'pending';
  record._local_updated_at = new Date().toISOString();

  // Write to IndexedDB store
  await dbPut(tableName, record);

  // Queue for cloud sync
  await queueChange(tableName, record.id, op, record);

  // If online, trigger immediate sync attempt
  if (navigator.onLine && typeof triggerBackgroundSync === 'function') {
    triggerBackgroundSync();
  }

  return record;
}

async function deleteRecord(tableName, recordId) {
  // Mark as deleted (soft delete for sync)
  try {
    const existing = await dbGet(tableName, recordId);
    if (existing) {
      existing.is_deleted = true;
      existing._sync_status = 'pending';
      existing._local_updated_at = new Date().toISOString();
      await dbPut(tableName, existing);
    }
  } catch (e) { /* record may not exist locally */ }

  // Queue for cloud sync
  await queueChange(tableName, recordId, 'delete', { id: recordId });

  if (navigator.onLine && typeof triggerBackgroundSync === 'function') {
    triggerBackgroundSync();
  }
}

// ── BULK SEED (pull from server) ─────────────────────────────

async function seedTable(tableName, records) {
  await initDB();
  return new Promise((res, rej) => {
    const tx = db.transaction(tableName, 'readwrite');
    const store = tx.objectStore(tableName);
    for (const rec of records) {
      rec._sync_status = 'synced';
      store.put(rec);
    }
    tx.oncomplete = () => res(records.length);
    tx.onerror = e => rej(e.target.error);
  });
}

// ── PAGE CACHE (for offline navigation) ───────────────────────

async function cachePage(url, html) {
  await initDB();
  return dbPut('_page_cache', { url, html, cached_at: new Date().toISOString() });
}

async function getCachedPage(url) {
  const result = await dbGet('_page_cache', url);
  return result ? result.html : null;
}

// ── SETTINGS CACHE ────────────────────────────────────────────

async function getSetting(name) {
  const rows = await dbGetByIndex('app_settings', 'setting_name', name);
  return rows.length > 0 ? rows[0].setting_value : null;
}

async function setSetting(name, value) {
  await dbPut('app_settings', { id: name, setting_name: name, setting_value: value, _sync_status: 'pending', _local_updated_at: new Date().toISOString() });
  await queueChange('app_settings', name, 'update', { setting_name: name, setting_value: value });
}

// ── METADATA ──────────────────────────────────────────────────

async function getMeta(key) {
  const r = await dbGet('_meta', key);
  return r ? r.value : null;
}

async function setMeta(key, value) {
  await dbPut('_meta', { key, value });
}

// ── CONNECTION STATUS ─────────────────────────────────────────

function updateStatusBadge() {
  const b = document.getElementById('connection-badge');
  if (!b) return;
  if (navigator.onLine) {
    b.textContent = 'Online';
    b.style.background = '#28a745';
    b.style.color = '#fff';
  } else {
    b.textContent = 'Offline';
    b.style.background = '#ffc107';
    b.style.color = '#000';
  }
}

// ── BOOTSTRAP ─────────────────────────────────────────────────

window.addEventListener('load', async () => {
  try {
    await initDB();
    console.log('[DB] IndexedDB initialized, stores:', Array.from(db.objectStoreNames).join(', '));
  } catch (e) {
    console.error('[DB] IndexedDB init failed:', e);
  }
  updateStatusBadge();
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js')
      .then(r => console.log('[PWA] Service worker registered:', r.scope))
      .catch(e => console.error('[PWA] SW registration failed:', e));
  }
});

window.addEventListener('online', () => {
  updateStatusBadge();
  if (typeof triggerBackgroundSync === 'function') triggerBackgroundSync();
});
window.addEventListener('offline', updateStatusBadge);
