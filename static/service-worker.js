// ═══════════════════════════════════════════════════════════════
// AAMUSTED GCC - Offline-First Service Worker v2
// Caches ALL pages + static assets. Serves offline fallback.
// Intercepts POST/PUT/DELETE and queues for sync.
// ═══════════════════════════════════════════════════════════════

const CACHE_VERSION = 'aamusted-v3';
const STATIC_CACHE = `${CACHE_VERSION}-static`;
const PAGE_CACHE   = `${CACHE_VERSION}-pages`;
const API_CACHE    = `${CACHE_VERSION}-api`;

const STATIC_ASSETS = [
  '/',
  '/static/manifest.json',
  '/static/css/modern_theme.css',
  '/static/css/bootstrap.min.css',
  '/static/css/bootstrap-icons.css',
  '/static/js/db.js',
  '/static/js/offline-sync.js',
  '/static/js/offline-forms.js',
  '/static/js/sweetalert2.all.min.js',
  '/static/js/jquery-3.6.0.min.js',
  '/static/js/flatpickr.min.js',
  '/static/js/chart.min.js',
  '/static/js/bootstrap.bundle.min.js',
  '/static/js/bootstrap.bundle2.min.js'
];

// Pages to pre-cache on install (the most common navigation targets)
const PRECACHE_PAGES = [
  '/dashboard',
  '/welcome',
  '/admin/bookings',
  '/students',
  '/appointments',
  '/admin/users'
];

// ── INSTALL ───────────────────────────────────────────────────
self.addEventListener('install', event => {
  console.log('[SW] Installing...');
  event.waitUntil(
    caches.open(STATIC_CACHE).then(cache => {
      console.log('[SW] Caching static assets');
      return cache.addAll(STATIC_ASSETS);
    }).then(() => self.skipWaiting())
  );
});

// ── ACTIVATE ──────────────────────────────────────────────────
self.addEventListener('activate', event => {
  console.log('[SW] Activating...');
  event.waitUntil(
    caches.keys().then(keys => {
      return Promise.all(
        keys.filter(k => !k.startsWith(CACHE_VERSION))
            .map(k => { console.log('[SW] Deleting old cache:', k); return caches.delete(k); })
      );
    }).then(() => self.clients.claim())
  );
});

// ── FETCH ─────────────────────────────────────────────────────
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET for cache strategy (but intercept POST for offline queue)
  if (request.method === 'POST' || request.method === 'PUT' || request.method === 'DELETE') {
    event.respondWith(handleMutation(request));
    return;
  }

  // Only handle same-origin
  if (url.origin !== self.location.origin) return;

  event.respondWith(
    (async () => {
      // 1. Try network first for API calls (GET)
      if (url.pathname.startsWith('/api/') || url.pathname.startsWith('/sync/')) {
        try {
          const networkResponse = await fetch(request);
          // Cache successful API GET responses
          if (networkResponse.ok) {
            const cache = await caches.open(API_CACHE);
            cache.put(request, networkResponse.clone());
          }
          return networkResponse;
        } catch (e) {
          // Offline: try API cache
          const cached = await caches.match(request);
          if (cached) return cached;
          return new Response(JSON.stringify({ error: 'Offline', message: 'No network connection' }), {
            status: 503,
            headers: { 'Content-Type': 'application/json' }
          });
        }
      }

      // 2. For page navigation: network first, fall back to cache, then offline page
      if (request.mode === 'navigate') {
        try {
          const networkResponse = await fetch(request);
          // Cache the page for offline use
          if (networkResponse.ok) {
            const cache = await caches.open(PAGE_CACHE);
            cache.put(request, networkResponse.clone());
          }
          return networkResponse;
        } catch (e) {
          // Offline: serve from page cache
          const cached = await caches.match(request);
          if (cached) return cached;

          // Last resort: serve cached dashboard or offline shell
          const fallback = await caches.match('/dashboard') || await caches.match('/');
          if (fallback) return fallback;

          return new Response(offlineHTML(), {
            headers: { 'Content-Type': 'text/html' }
          });
        }
      }

      // 3. Static assets: cache first, then network
      const cached = await caches.match(request);
      if (cached) return cached;

      try {
        const networkResponse = await fetch(request);
        if (networkResponse.ok) {
          const cache = await caches.open(STATIC_CACHE);
          cache.put(request, networkResponse.clone());
        }
        return networkResponse;
      } catch (e) {
        return new Response('', { status: 408 });
      }
    })()
  );
});

// ── HANDLE MUTATIONS (POST/PUT/DELETE) WHEN OFFLINE ──────────
async function handleMutation(request) {
  // If online, pass through normally
  if (navigator.onLine) {
    try {
      return await fetch(request);
    } catch (e) {
      // Network failed even though online - queue it
      return queueAndRespond(request);
    }
  }

  // OFFLINE: Queue the request and return a success response
  return queueAndRespond(request);
}

async function queueAndRespond(request) {
  const url = request.url;
  const method = request.method;
  let body = null;

  try {
    body = await request.clone().text();
  } catch (e) { /* body may be empty */ }

  // Store in IndexedDB sync queue via a message to the client
  const clients = await self.clients.matchAll();
  for (const client of clients) {
    client.postMessage({
      type: 'QUEUE_MUTATION',
      url: url,
      method: method,
      body: body,
      timestamp: new Date().toISOString()
    });
  }

  // Return a fake success so the UI doesn't show an error
  return new Response(JSON.stringify({
    status: 'queued',
    message: 'Change saved offline. Will sync when online.',
    offline: true
  }), {
    status: 200,
    headers: { 'Content-Type': 'application/json' }
  });
}

// ── BACKGROUND SYNC ──────────────────────────────────────────
self.addEventListener('sync', event => {
  if (event.tag === 'aamusted-sync') {
    event.waitUntil(syncPendingChanges());
  }
});

self.addEventListener('message', event => {
  if (event.data && event.data.type === 'TRIGGER_SYNC') {
    syncPendingChanges();
  }
});

async function syncPendingChanges() {
  // Notify client that sync is starting
  const clients = await self.clients.matchAll();
  for (const client of clients) {
    client.postMessage({ type: 'SYNC_START' });
  }

  try {
    // We can't access IndexedDB directly from SW in all browsers,
    // so we ask the client to send us the pending changes
    for (const client of clients) {
      client.postMessage({ type: 'REQUEST_SYNC' });
    }
  } catch (e) {
    console.error('[SW] Sync error:', e);
  }
}

// ── OFFLINE HTML FALLBACK ────────────────────────────────────
function offlineHTML() {
  return `<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Offline - AAMUSTED GCC</title>
<style>
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;background:#0f172a;color:#fff;text-align:center;padding:20px;}
.card{background:#1e293b;padding:40px;border-radius:16px;border:1px solid #334155;max-width:420px;width:100%;}
h1{font-size:1.5rem;margin:16px 0 8px;}
p{color:#94a3b8;line-height:1.6;font-size:0.9rem;}
.icon{font-size:3rem;}
.badge{display:inline-block;padding:6px 14px;border-radius:20px;font-weight:bold;background:#ffc107;color:#000;font-size:0.8rem;margin-top:12px;}
</style></head>
<body>
<div class="card">
<div class="icon">📴</div>
<h1>You're Offline</h1>
<p>Your changes are being saved locally and will sync automatically when your connection is restored.</p>
<span class="badge">Saved Locally</span>
<p style="margin-top:16px;font-size:0.75rem;color:#64748b;">AAMUSTED Guidance & Counselling System</p>
</div>
</body></html>`;
}
