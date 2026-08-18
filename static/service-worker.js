// ═══════════════════════════════════════════════════════════════
// AAMUSTED GCC - Offline-First Service Worker v3
// Caches ALL navigation pages, static assets, and API responses.
// Shows proper offline page (never redirects to dashboard).
// ═══════════════════════════════════════════════════════════════

const CACHE_VERSION = 'aamusted-v4';
const STATIC_CACHE = `${CACHE_VERSION}-static`;
const PAGE_CACHE   = `${CACHE_VERSION}-pages`;
const API_CACHE    = `${CACHE_VERSION}-api`;

const STATIC_ASSETS = [
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

// ═══════════════════════════════════════════════════════════════
// INSTALL — cache static assets
// ═══════════════════════════════════════════════════════════════
self.addEventListener('install', event => {
  console.log('[SW] Installing...');
  event.waitUntil(
    caches.open(STATIC_CACHE).then(cache => {
      return cache.addAll(STATIC_ASSETS);
    }).then(() => self.skipWaiting())
  );
});

// ═══════════════════════════════════════════════════════════════
// ACTIVATE — clean old caches
// ═══════════════════════════════════════════════════════════════
self.addEventListener('activate', event => {
  console.log('[SW] Activating...');
  event.waitUntil(
    caches.keys().then(keys => {
      return Promise.all(
        keys.filter(k => !k.startsWith(CACHE_VERSION))
            .map(k => caches.delete(k))
      );
    }).then(() => self.clients.claim())
  );
});

// ═══════════════════════════════════════════════════════════════
// FETCH
// ═══════════════════════════════════════════════════════════════
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  // Mutations (POST/PUT/DELETE) — intercept and queue if offline
  if (request.method !== 'GET') {
    event.respondWith(handleMutation(request));
    return;
  }

  // Skip cross-origin
  if (url.origin !== self.location.origin) return;

  // Skip non-HTML, non-API, non-static
  const isNavigation = request.mode === 'navigate';
  const isAPI = url.pathname.startsWith('/api/') || url.pathname.startsWith('/sync/');
  const isStatic = url.pathname.startsWith('/static/') || url.pathname.includes('.');

  event.respondWith(
    (async () => {

      // ── API GET: network-first, cache fallback ──
      if (isAPI) {
        try {
          const resp = await fetch(request);
          if (resp.ok) {
            const cache = await caches.open(API_CACHE);
            cache.put(request, resp.clone());
          }
          return resp;
        } catch (e) {
          const cached = await caches.match(request);
          if (cached) return cached;
          return jsonOffline();
        }
      }

      // ── NAVIGATION: cache-first (instant from cache), then network ──
      if (isNavigation) {
        // Check page cache first (instant load)
        const cached = await caches.match(request);
        if (cached) {
          // Return cached immediately, but also refresh in background
          fetchAndCache(request);
          return cached;
        }

        // Not in cache — try network
        try {
          const resp = await fetch(request);
          if (resp.ok) {
            const cache = await caches.open(PAGE_CACHE);
            cache.put(request, resp.clone());
          }
          return resp;
        } catch (e) {
          // OFFLINE + NOT CACHED: show offline page (never redirect to dashboard)
          return offlinePage(request.url);
        }
      }

      // ── STATIC ASSETS: cache-first ──
      const cached = await caches.match(request);
      if (cached) return cached;

      try {
        const resp = await fetch(request);
        if (resp.ok) {
          const cache = await caches.open(STATIC_CACHE);
          cache.put(request, resp.clone());
        }
        return resp;
      } catch (e) {
        return new Response('', { status: 408 });
      }
    })()
  );
});

// Background refresh — update cache without blocking user
async function fetchAndCache(request) {
  try {
    const resp = await fetch(request);
    if (resp.ok) {
      const cache = await caches.open(PAGE_CACHE);
      cache.put(request, resp.clone());
    }
  } catch (e) { /* silent */ }
}

// ═══════════════════════════════════════════════════════════════
// MUTATIONS — queue offline POST/PUT/DELETE
// ═══════════════════════════════════════════════════════════════
async function handleMutation(request) {
  if (navigator.onLine) {
    try {
      return await fetch(request);
    } catch (e) {
      return queueAndRespond(request);
    }
  }
  return queueAndRespond(request);
}

async function queueAndRespond(request) {
  let body = null;
  try { body = await request.clone().text(); } catch (e) {}

  const clients = await self.clients.matchAll();
  for (const client of clients) {
    client.postMessage({
      type: 'QUEUE_MUTATION',
      url: request.url,
      method: request.method,
      body: body,
      timestamp: new Date().toISOString()
    });
  }

  return new Response(JSON.stringify({
    status: 'queued',
    message: 'Saved offline. Will sync when online.',
    offline: true
  }), {
    status: 200,
    headers: { 'Content-Type': 'application/json' }
  });
}

// ═══════════════════════════════════════════════════════════════
// MESSAGE — background sync trigger + page pre-cache
// ═══════════════════════════════════════════════════════════════
self.addEventListener('message', event => {
  const { type, pages } = event.data || {};

  if (type === 'TRIGGER_SYNC') {
    syncPendingChanges();
  }

  if (type === 'PRE_CACHE_PAGES' && Array.isArray(pages)) {
    preCachePages(pages);
  }
});

async function preCachePages(pages) {
  const cache = await caches.open(PAGE_CACHE);
  for (const url of pages) {
    try {
      const resp = await fetch(url);
      if (resp.ok) {
        await cache.put(url, resp);
        console.log('[SW] Cached:', url);
      }
    } catch (e) {
      console.log('[SW] Failed to cache:', url);
    }
  }
  // Notify client pre-caching is done
  const clients = await self.clients.matchAll();
  for (const client of clients) {
    client.postMessage({ type: 'PRE_CACHE_DONE', count: pages.length });
  }
}

async function syncPendingChanges() {
  const clients = await self.clients.matchAll();
  for (const client of clients) {
    client.postMessage({ type: 'REQUEST_SYNC' });
  }
}

// ═══════════════════════════════════════════════════════════════
// OFFLINE PAGE — shows which page wasn't cached, with links
// ═══════════════════════════════════════════════════════════════
function offlinePage(requestedUrl) {
  const path = new URL(requestedUrl, self.location.origin).pathname;
  const pageName = path.split('/').filter(Boolean).pop() || 'home';
  return new Response(`<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Offline - ${pageName}</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#0f172a;color:#e2e8f0;display:flex;align-items:center;justify-content:center;min-height:100vh;padding:20px}
.card{background:#1e293b;padding:36px;border-radius:16px;border:1px solid #334155;max-width:440px;width:100%;text-align:center}
.icon{font-size:2.5rem;margin-bottom:12px}
h2{font-size:1.2rem;margin-bottom:8px;color:#f8fafc}
p{color:#94a3b8;font-size:0.85rem;line-height:1.6;margin-bottom:20px}
.url{background:#0f172a;padding:8px 14px;border-radius:8px;font-family:monospace;font-size:0.75rem;color:#38bdf8;margin-bottom:20px;word-break:break-all}
.links{display:flex;flex-wrap:wrap;gap:8px;justify-content:center}
.links a{padding:8px 16px;border-radius:8px;background:#334155;color:#e2e8f0;text-decoration:none;font-size:0.8rem;font-weight:500;transition:all 0.2s}
.links a:hover{background:#475569}
.links a.primary{background:#800000;color:#fff}
.tip{margin-top:16px;padding:10px;background:rgba(255,193,7,0.1);border:1px solid rgba(255,193,7,0.2);border-radius:8px;font-size:0.75rem;color:#ffc107}
</style></head><body>
<div class="card">
  <div class="icon">📄</div>
  <h2>Page Not Cached Offline</h2>
  <p>This page hasn't been visited while online, so it's not available offline. Visit it once while connected and it will be available next time.</p>
  <div class="url">${path}</div>
  <div class="links">
    <a href="/dashboard" class="primary">Dashboard</a>
    <a href="/students">Clients</a>
    <a href="/appointments">Appointments</a>
    <a href="/admin/bookings">Bookings</a>
    <a href="/sessions">Sessions</a>
    <a href="/welcome">Login</a>
  </div>
  <div class="tip">Tip: Visit each page once while online to cache it for offline use.</div>
</div>
</body></html>`, {
    headers: { 'Content-Type': 'text/html' },
    status: 200
  });
}

function jsonOffline() {
  return new Response(JSON.stringify({ error: 'Offline', message: 'No network' }), {
    status: 503,
    headers: { 'Content-Type': 'application/json' }
  });
}
