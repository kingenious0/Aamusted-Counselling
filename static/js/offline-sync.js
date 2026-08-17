// ═══════════════════════════════════════════════════════════════
// AAMUSTED GCC - Background Sync Manager
// Pushes pending offline changes to server when online.
// Pulls latest data from server to keep IndexedDB fresh.
// ═══════════════════════════════════════════════════════════════

let _syncRunning = false;
let _syncInterval = null;

// ── TABLES TO SYNC ────────────────────────────────────────────
const SYNC_TABLES = [
  'Student', 'Appointment', 'BookingRequest', 'session',
  'Referral', 'CaseManagement', 'OutcomeQuestionnaire', 'DASS21',
  'SessionIssue', 'Feedback', 'Notification', 'app_settings',
  'Counsellor', 'users'
];

// ── PUSH PENDING CHANGES ─────────────────────────────────────
async function pushPendingChanges() {
  if (_syncRunning) return;
  _syncRunning = true;

  try {
    const pending = await getPendingChanges();
    if (pending.length === 0) {
      _syncRunning = false;
      return;
    }

    console.log(`[SYNC] Pushing ${pending.length} pending changes...`);
    updateSyncUI('syncing', pending.length);

    // Group by table
    const grouped = {};
    for (const item of pending) {
      if (!grouped[item.table_name]) grouped[item.table_name] = [];
      grouped[item.table_name].push(item);
    }

    // Push each table's changes
    for (const [tableName, items] of Object.entries(grouped)) {
      const records = items.map(item => {
        if (item.operation === 'delete') {
          return { id: item.record_id, is_deleted: true, _sync_status: 'synced' };
        }
        return { ...item.data, _sync_status: 'synced' };
      });

      try {
        const resp = await fetch('/api/offline/sync', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ changes: { [tableName]: records } })
        });

        if (resp.ok) {
          // Mark all as synced
          for (const item of items) {
            await markSynced(item._queue_id);
          }
          console.log(`[SYNC] Pushed ${records.length} ${tableName} records`);
        } else {
          console.error(`[SYNC] Push failed for ${tableName}:`, resp.status);
          for (const item of items) {
            await markFailed(item._queue_id);
          }
        }
      } catch (e) {
        console.error(`[SYNC] Network error pushing ${tableName}:`, e);
        // Leave as pending for next retry
      }
    }

    updateSyncUI('synced');
  } catch (e) {
    console.error('[SYNC] Push error:', e);
    updateSyncUI('error');
  } finally {
    _syncRunning = false;
  }
}

// ── PULL LATEST DATA ─────────────────────────────────────────
async function pullLatestData() {
  if (!navigator.onLine) return;

  try {
    const lastSync = await getMeta('last_pull_timestamp') || '1970-01-01 00:00:00';

    console.log('[SYNC] Pulling latest data from server...');
    updateSyncUI('pulling');

    const resp = await fetch('/api/offline/pull', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ last_sync_timestamp: lastSync })
    });

    if (!resp.ok) {
      console.error('[SYNC] Pull failed:', resp.status);
      return;
    }

    const data = await resp.json();
    const changes = data.changes || {};
    let totalSeeded = 0;

    for (const [tableName, records] of Object.entries(changes)) {
      if (SYNC_TABLES.includes(tableName) && records && records.length > 0) {
        // Only seed records that aren't locally pending
        const pending = await getPendingChanges();
        const pendingIds = new Set(
          pending.filter(p => p.table_name === tableName).map(p => p.record_id)
        );

        const toSeed = records.filter(r => !pendingIds.has(r.id));
        if (toSeed.length > 0) {
          await seedTable(tableName, toSeed);
          totalSeeded += toSeed.length;
        }
      }
    }

    // Update last pull timestamp
    await setMeta('last_pull_timestamp', data.server_time || new Date().toISOString());

    if (totalSeeded > 0) {
      console.log(`[SYNC] Pulled ${totalSeeded} records from server`);
      // Notify the page to refresh data
      window.dispatchEvent(new CustomEvent('sync-complete', { detail: { count: totalSeeded } }));
    }

    updateSyncUI('synced');
  } catch (e) {
    console.error('[SYNC] Pull error:', e);
    updateSyncUI('error');
  }
}

// ── FULL SYNC CYCLE ──────────────────────────────────────────
async function runSyncCycle() {
  if (!navigator.onLine) return;

  console.log('[SYNC] Starting sync cycle...');
  await pushPendingChanges();
  await pullLatestData();
  console.log('[SYNC] Sync cycle complete.');
}

// ── TRIGGER SYNC (called from SW message or online event) ────
function triggerBackgroundSync() {
  // Debounce: don't spam sync
  if (window._syncDebounce) clearTimeout(window._syncDebounce);
  window._syncDebounce = setTimeout(() => {
    runSyncCycle();
  }, 1000);
}

// ── LISTEN FOR SW MESSAGES ───────────────────────────────────
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.addEventListener('message', event => {
    const { type } = event.data;

    if (type === 'REQUEST_SYNC') {
      // Service worker asks us to push pending changes
      pushPendingChanges();
    }

    if (type === 'SYNC_START') {
      updateSyncUI('syncing');
    }

    if (type === 'QUEUE_MUTATION') {
      // SW intercepted an offline POST - store it
      handleOfflineMutation(event.data);
    }
  });
}

// ── HANDLE OFFLINE MUTATIONS FROM SW ─────────────────────────
async function handleOfflineMutation({ url, method, body, timestamp }) {
  try {
    // Parse the URL to determine table and operation
    const parsed = parseFlaskRoute(url, method);
    if (!parsed) {
      console.log('[SYNC] Could not parse offline mutation:', url);
      return;
    }

    const { table, recordId, operation } = parsed;
    let data = {};
    try { data = body ? JSON.parse(body) : {}; } catch (e) {
      // URL-encoded form data
      data = parseFormData(body);
    }

    await saveRecord(table, { id: recordId, ...data }, operation);
    console.log(`[SYNC] Queued offline ${operation} on ${table}:`, recordId);
  } catch (e) {
    console.error('[SYNC] Error handling offline mutation:', e);
  }
}

// ── PARSE FLASK ROUTES INTO TABLE + OPERATION ────────────────
function parseFlaskRoute(url, method) {
  const u = new URL(url, window.location.origin);
  const path = u.pathname;

  // /admin/bookings/<id>/accept → BookingRequest update
  if (path.match(/\/admin\/bookings\/\d+\/accept/)) {
    const id = parseInt(path.match(/\/(\d+)\//)[1]);
    return { table: 'BookingRequest', recordId: id, operation: 'update' };
  }

  // /admin/bookings/<id>/decline → BookingRequest update
  if (path.match(/\/admin\/bookings\/\d+\/decline/)) {
    const id = parseInt(path.match(/\/(\d+)\//)[1]);
    return { table: 'BookingRequest', recordId: id, operation: 'update' };
  }

  // /students/add → Student create
  if (path === '/students/add' && method === 'POST') {
    return { table: 'Student', recordId: Date.now(), operation: 'create' };
  }

  // /students/<id>/edit → Student update
  if (path.match(/\/students\/\d+\/edit/) && method === 'POST') {
    const id = parseInt(path.match(/\/students\/(\d+)/)[1]);
    return { table: 'Student', recordId: id, operation: 'update' };
  }

  // /appointments/schedule → Appointment create
  if (path === '/appointments/schedule' && method === 'POST') {
    return { table: 'Appointment', recordId: Date.now(), operation: 'create' };
  }

  // /appointments/<id>/update → Appointment update
  if (path.match(/\/appointments\/\d+\/update/) && method === 'POST') {
    const id = parseInt(path.match(/\/appointments\/(\d+)/)[1]);
    return { table: 'Appointment', recordId: id, operation: 'update' };
  }

  // /create_session → session create
  if (path === '/create_session' && method === 'POST') {
    return { table: 'session', recordId: Date.now(), operation: 'create' };
  }

  // /admin/settings → app_settings update
  if (path.match(/\/admin\/settings/) && method === 'POST') {
    return { table: 'app_settings', recordId: Date.now(), operation: 'update' };
  }

  // /notifications/mark_read/<id> → Notification update
  if (path.match(/\/notifications\/mark_read\/\d+/) && method === 'POST') {
    const id = parseInt(path.match(/\/(\d+)\/?$/)[1]);
    return { table: 'Notification', recordId: id, operation: 'update' };
  }

  // Generic fallback: try to extract table from URL
  if (path.startsWith('/api/')) return null;
  return { table: 'Unknown', recordId: Date.now(), operation: 'update' };
}

function parseFormData(body) {
  if (!body) return {};
  const data = {};
  const pairs = body.split('&');
  for (const pair of pairs) {
    const [key, val] = pair.split('=').map(decodeURIComponent);
    data[key] = val;
  }
  return data;
}

// ── UI STATUS UPDATES ────────────────────────────────────────
function updateSyncUI(status, count) {
  const badge = document.getElementById('sync-status-badge');
  if (!badge) return;

  switch (status) {
    case 'syncing':
    case 'pulling':
      badge.textContent = count ? `Syncing ${count}...` : 'Syncing...';
      badge.style.background = '#ffc107';
      badge.style.color = '#000';
      break;
    case 'synced':
      badge.textContent = 'Synced';
      badge.style.background = '#28a745';
      badge.style.color = '#fff';
      // Hide after 3 seconds
      setTimeout(() => { badge.style.display = 'none'; }, 3000);
      break;
    case 'error':
      badge.textContent = 'Sync Error';
      badge.style.background = '#dc3545';
      badge.style.color = '#fff';
      break;
  }
}

// ── AUTO-SYNC INTERVAL ───────────────────────────────────────
// Sync every 30 seconds when online
function startAutoSync() {
  if (_syncInterval) clearInterval(_syncInterval);
  _syncInterval = setInterval(() => {
    if (navigator.onLine) {
      runSyncCycle();
    }
  }, 30000);
}

// ── BOOTSTRAP ────────────────────────────────────────────────
window.addEventListener('load', () => {
  startAutoSync();
  // Initial sync after 5 seconds (let page load first)
  setTimeout(() => {
    if (navigator.onLine) runSyncCycle();
  }, 5000);
});

window.addEventListener('online', () => {
  console.log('[SYNC] Back online - triggering sync');
  setTimeout(runSyncCycle, 1000);
});
