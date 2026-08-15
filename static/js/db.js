// AAMUSTED GCC - Offline IndexedDB Module
const DB_NAME = 'AAMUSTED GCC DB';
const DB_VERSION = 1;
let db;

function initDB() {
  return new Promise((resolve, reject) => {
    const r = indexedDB.open(DB_NAME, DB_VERSION);
    r.onupgradeneeded = e => {
      db = e.target.result;
      if (!db.objectStoreNames.contains('offline_sessions'))
        db.createObjectStore('offline_sessions', {keyPath: 'local_id', autoIncrement: true});
    };
    r.onsuccess = e => { db = e.target.result; resolve(db); };
    r.onerror = e => reject(e);
  });
}

async function saveOfflineSession(d) {
  if (!db) await initDB();
  return new Promise((res, rej) => {
    const tx = db.transaction('offline_sessions', 'readwrite');
    d.is_synced = false;
    d.saved_at = new Date().toISOString();
    tx.objectStore('offline_sessions').add(d);
    tx.oncomplete = () => res(true);
    tx.onerror = e => rej(e);
  });
}

async function getPending() {
  if (!db) await initDB();
  return new Promise((res, rej) => {
    const r = db.transaction('offline_sessions', 'readonly')
                .objectStore('offline_sessions').getAll();
    r.onsuccess = () => res(r.result || []);
    r.onerror = e => rej(e);
  });
}

async function clearSynced() {
  if (!db) await initDB();
  db.transaction('offline_sessions', 'readwrite')
    .objectStore('offline_sessions').clear();
}

function updateStatusBadge() {
  const b = document.getElementById('connection-badge');
  if (!b) return;
  if (navigator.online) {
    b.textContent = 'Online';
    b.style.background = '#28a745';
    b.style.color = '#fff';
  } else {
    b.textContent = 'Offline';
    b.style.background = '#ffc107';
    b.style.color = '#000';
  }
}

window.addEventListener('online', async () => {
  updateStatusBadge();
  const p = await getPending();
  if (p.length &gt; 0 && typeof supabaseClient !== 'undefined') {
    const { error } = await supabaseClient.from('sessions').upsert(p);
    if (!error) { await clearSynced(); alert('Synced ' + p.length + ' records'); }
  }
});
window.addEventListener('offline', updateStatusBadge);
window.addEventListener('load', () => {
  initDB();
  updateStatusBadge();
  if ('serviceWorker' in navigator)
    navigator.serviceWorker.register('/sw.js')
      .then(r => console.log('[PWA]', r.scope))
      .catch(console.error);
});
