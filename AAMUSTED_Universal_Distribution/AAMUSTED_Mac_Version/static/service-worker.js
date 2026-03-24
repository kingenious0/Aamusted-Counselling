const CACHE_NAME = 'usted-v1';
const ASSETS = [
    '/static/icon.png',
    '/static/manifest.json',
    '/static/css/bootstrap.min.css',
    '/static/css/bootstrap-icons.css'
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS))
    );
});

self.addEventListener('fetch', (event) => {
    // Skip non-GET requests
    if (event.request.method !== 'GET') return;

    // Strategy: Network First for all HTML pages, Cache First for static assets
    const url = new URL(event.request.url);
    
    // For static files in /static/, use Cache First
    if (url.pathname.startsWith('/static/')) {
        event.respondWith(
            caches.match(event.request).then((cachedResponse) => {
                if (cachedResponse) return cachedResponse;
                return fetch(event.request).then((networkResponse) => {
                    return caches.open(CACHE_NAME).then((cache) => {
                        cache.put(event.request, networkResponse.clone());
                        return networkResponse;
                    });
                });
            })
        );
    } else {
        // For everything else (HTML pages), use Network First
        event.respondWith(
            fetch(event.request).catch(() => {
                return caches.match(event.request);
            })
        );
    }
});
