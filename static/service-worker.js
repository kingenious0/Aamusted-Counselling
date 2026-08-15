const CACHE_NAME = 'aamusted-counselling-v2';
const STATIC_ASSETS = [
  '/',
  '/static/manifest.json',
  '/static/css/modern_theme.css',
  '/static/css/bootstrap.min.css',
  '/static/css/bootstrap-icons.css',
  '/static/js/db.js',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png'
];

// 1. Install Event: Cache all critical UI and script assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[PWA] Caching offline app shell...');
      return cache.addAll(STATIC_ASSETS);
    })
  );
  self.skipWaiting();
});

// 2. Activate Event: Clean up legacy caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            console.log('[PWA] Removing old cache:', key);
            return caches.delete(key);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// 3. Fetch Event: Cache-first with navigation fallback for offline resilience
self.addEventListener('fetch', (event) => {
  // Only handle GET requests
  if (event.request.method !== 'GET') return;

  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      if (cachedResponse) {
        return cachedResponse;
      }
      return fetch(event.request)
        .then((networkResponse) => {
          // Cache newly fetched static assets dynamically
          if (networkResponse && networkResponse.status === 200 && networkResponse.type === 'basic') {
            const responseToCache = networkResponse.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(event.request, responseToCache);
            });
          }
          return networkResponse;
        })
        .catch(() => {
          // If offline and requesting a page route, return root index
          if (event.request.mode === 'navigate') {
            return caches.match('/');
          }
        });
    })
  );
});
