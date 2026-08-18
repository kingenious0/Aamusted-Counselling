// ═══════════════════════════════════════════════════════════════
// AAMUSTED GCC - Offline-First Service Worker v4
// ═══════════════════════════════════════════════════════════════

const CACHE_VERSION = 'aamusted-v6';
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
  '/static/js/precache.js',
  '/static/js/sweetalert2.all.min.js',
  '/static/js/jquery-3.6.0.min.js',
  '/static/js/flatpickr.min.js',
  '/static/js/chart.min.js',
  '/static/js/bootstrap.bundle.min.js',
  '/static/js/bootstrap.bundle2.min.js'
];

// ═══════════════════════════════════════════════════════════════
// INSTALL
// ═══════════════════════════════════════════════════════════════
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then(cache => cache.addAll(STATIC_ASSETS))
      .then(() => self.skipWaiting())
  );
});

// ═══════════════════════════════════════════════════════════════
// ACTIVATE
// ═══════════════════════════════════════════════════════════════
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => !k.startsWith(CACHE_VERSION)).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

// ═══════════════════════════════════════════════════════════════
// FETCH
// ═══════════════════════════════════════════════════════════════
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  if (url.origin !== self.location.origin) return;

  // POST/PUT/DELETE — queue if offline
  if (request.method !== 'GET') {
    event.respondWith(handleMutation(request));
    return;
  }

  const isNavigation = request.mode === 'navigate';
  const isAPI = url.pathname.startsWith('/api/') || url.pathname.startsWith('/sync/');
  const isStatic = url.pathname.startsWith('/static/');
  const isAction = /\/admin\/bookings\/\d+\/(register|accept|decline)/.test(url.pathname);

  event.respondWith((async () => {

    // ── ACTION ENDPOINTS: always network, never cache ──
    if (isAction) {
      return await fetch(request);
    }

    // ── API: network-first ──
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
        return cached || new Response('{"error":"Offline"}', {
          status: 503, headers: { 'Content-Type': 'application/json' }
        });
      }
    }

    // ── NAVIGATION: cache-first ──
    if (isNavigation) {
      const cached = await caches.match(request);
      if (cached) {
        fetchAndRefresh(request);
        return cached;
      }

      try {
        const resp = await fetch(request);
        if (resp.ok) {
          const ct = resp.headers.get('content-type') || '';
          if (ct.includes('text/html')) {
            const cache = await caches.open(PAGE_CACHE);
            cache.put(request, resp.clone());
          }
        }
        return resp;
      } catch (e) {
        return offlinePage(url.pathname);
      }
    }

    // ── STATIC: cache-first ──
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
  })());
});

async function fetchAndRefresh(request) {
  try {
    const resp = await fetch(request);
    if (resp.ok) {
      const cache = await caches.open(PAGE_CACHE);
      cache.put(request, resp.clone());
    }
  } catch (e) {}
}

// ═══════════════════════════════════════════════════════════════
// MUTATIONS — queue offline, never show raw JSON
// ═══════════════════════════════════════════════════════════════
async function handleMutation(request) {
  // Online: pass through
  if (navigator.onLine) {
    try { return await fetch(request); } catch (e) {}
  }

  // Offline: queue + return JSON (JS will handle it)
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
// MESSAGES
// ═══════════════════════════════════════════════════════════════
self.addEventListener('message', event => {
  const { type, pages } = event.data || {};
  if (type === 'TRIGGER_SYNC') {
    const clients = self.clients.matchAll().then(clients => {
      for (const c of clients) c.postMessage({ type: 'REQUEST_SYNC' });
    });
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
        const ct = resp.headers.get('content-type') || '';
        if (ct.includes('text/html')) {
          await cache.put(url, resp);
        }
      }
    } catch (e) {}
  }
  const clients = await self.clients.matchAll();
  for (const c of clients) c.postMessage({ type: 'PRE_CACHE_DONE', count: pages.length });
}

// ═══════════════════════════════════════════════════════════════
// OFFLINE PAGE — matches the app's sidebar + maroon theme
// ═══════════════════════════════════════════════════════════════
function offlinePage(pathname) {
  return new Response(`<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Offline - AAMUSTED GCC</title>
<link href="/static/css/bootstrap.min.css" rel="stylesheet">
<link rel="stylesheet" href="/static/css/bootstrap-icons.css">
<style>
  :root { --brand-primary: #800000; --brand-secondary: #FFD700; --sage-50:#f8faf6; --sage-100:#e8ede4; --sage-200:#d4dece; --sage-600:#4a7c3f; --sage-700:#3a6332; --sage-800:#2d4d27; --sage-900:#1a2e18; }
  * { box-sizing: border-box; }
  body { margin: 0; font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f1f5f9; display: flex; min-height: 100vh; }
  
  /* SIDEBAR */
  .sidebar { width: 260px; background: linear-gradient(180deg, #800000 0%, #5a0000 100%); color: #fff; padding: 20px 16px; flex-shrink: 0; display: flex; flex-direction: column; }
  .sidebar-logo { display: flex; align-items: center; gap: 10px; margin-bottom: 28px; padding: 0 8px; }
  .sidebar-logo .icon { width: 36px; height: 36px; background: rgba(255,255,255,0.15); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 18px; }
  .sidebar-logo .text { font-size: 1rem; font-weight: 700; letter-spacing: -0.02em; }
  .sidebar-section { font-size: 0.6rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; color: rgba(255,255,255,0.45); padding: 16px 8px 6px; }
  .sidebar-link { display: flex; align-items: center; gap: 10px; padding: 9px 12px; border-radius: 8px; color: rgba(255,255,255,0.7); text-decoration: none; font-size: 0.82rem; font-weight: 500; transition: all 0.2s; margin-bottom: 2px; }
  .sidebar-link:hover { background: rgba(255,255,255,0.1); color: #fff; }
  .sidebar-link.active { background: rgba(255,255,255,0.15); color: #fff; font-weight: 600; }
  .sidebar-link i { font-size: 1rem; width: 20px; text-align: center; }
  
  /* MAIN */
  .main { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 40px 20px; }
  .card-offline { background: #fff; border-radius: 16px; box-shadow: 0 4px 24px rgba(0,0,0,0.06); border: 1px solid #e2e8f0; padding: 48px 40px; max-width: 480px; width: 100%; text-align: center; }
  .card-offline .icon { font-size: 3rem; margin-bottom: 16px; }
  .card-offline h2 { font-size: 1.3rem; color: #1e293b; margin-bottom: 8px; }
  .card-offline p { color: #64748b; font-size: 0.85rem; line-height: 1.6; margin-bottom: 20px; }
  .card-offline .url-box { background: #f8fafc; border: 1px solid #e2e8f0; padding: 10px 16px; border-radius: 8px; font-family: monospace; font-size: 0.8rem; color: #800000; margin-bottom: 24px; word-break: break-all; }
  .nav-links { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; margin-bottom: 20px; }
  .nav-links a { padding: 8px 18px; border-radius: 8px; font-size: 0.8rem; font-weight: 500; text-decoration: none; transition: all 0.2s; border: 1px solid #e2e8f0; color: #475569; background: #fff; }
  .nav-links a:hover { background: #800000; color: #fff; border-color: #800000; }
  .nav-links a.primary { background: #800000; color: #fff; border-color: #800000; }
  .tip-box { background: #fffbeb; border: 1px solid #fde68a; border-radius: 8px; padding: 10px 14px; font-size: 0.75rem; color: #92400e; display: flex; align-items: center; gap: 8px; }
  .status-badge { display: inline-flex; align-items: center; gap: 5px; padding: 4px 12px; border-radius: 16px; font-size: 0.7rem; font-weight: 600; background: #ffc107; color: #000; position: fixed; bottom: 15px; right: 15px; z-index: 9999; }
</style>
</head>
<body>

<!-- SIDEBAR (matching app) -->
<nav class="sidebar">
  <div class="sidebar-logo">
    <div class="icon"><i class="bi bi-heart-pulse-fill"></i></div>
    <span class="text">USTED SYSTEM</span>
  </div>
  
  <div class="sidebar-section">Clients</div>
  <a href="/students" class="sidebar-link"><i class="bi bi-people"></i> Client Registry</a>
  <a href="/add_student" class="sidebar-link"><i class="bi bi-person-plus"></i> New Client Intake</a>
  
  <div class="sidebar-section">Appointments</div>
  <a href="/appointments" class="sidebar-link"><i class="bi bi-calendar-plus"></i> Schedule Appt.</a>
  <a href="/manage_appointments" class="sidebar-link"><i class="bi bi-calendar-check"></i> Manage Appts.</a>
  <a href="/admin/bookings" class="sidebar-link"><i class="bi bi-inbox"></i> Booking Requests</a>
  
  <div class="sidebar-section">Clinical</div>
  <a href="/sessions" class="sidebar-link"><i class="bi bi-journal-text"></i> Session Log</a>
  <a href="/case_notes_list" class="sidebar-link"><i class="bi bi-clipboard2-pulse"></i> Case Notes</a>
  <a href="/all_referrals" class="sidebar-link"><i class="bi bi-arrow-left-right"></i> Referrals</a>
  <a href="/dass21_list" class="sidebar-link"><i class="bi bi-clipboard-data"></i> DASS-21</a>
  
  <div class="sidebar-section">Reports</div>
  <a href="/reports" class="sidebar-link"><i class="bi bi-file-earmark-bar-graph"></i> Reports</a>
  <a href="/statistics" class="sidebar-link"><i class="bi bi-graph-up"></i> Statistics</a>
  
  <div style="flex:1"></div>
  <a href="/dashboard" class="sidebar-link" style="margin-top:auto;"><i class="bi bi-house"></i> Dashboard</a>
</nav>

<!-- MAIN CONTENT -->
<div class="main">
  <div class="card-offline">
    <div class="icon">📴</div>
    <h2>Page Not Available Offline</h2>
    <p>This page hasn't been cached yet. Visit it once while online and it will be available offline next time.</p>
    <div class="url-box">${pathname}</div>
    <div class="nav-links">
      <a href="/dashboard" class="primary">Dashboard</a>
      <a href="/students">Clients</a>
      <a href="/appointments">Appointments</a>
      <a href="/admin/bookings">Bookings</a>
      <a href="/sessions">Sessions</a>
      <a href="/case_notes_list">Case Notes</a>
      <a href="/dass21_list">DASS-21</a>
      <a href="/reports">Reports</a>
      <a href="/welcome">Login</a>
    </div>
    <div class="tip-box">
      <i class="bi bi-lightbulb"></i>
      Visit each page once while online to cache it for offline use.
    </div>
  </div>
</div>

<div class="status-badge">Offline</div>

</body>
</html>`, {
    headers: { 'Content-Type': 'text/html; charset=utf-8' },
    status: 200
  });
}
