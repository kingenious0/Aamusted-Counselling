// ═══════════════════════════════════════════════════════════════
// AAMUSTED GCC - Background Page Pre-Cache
// After login, quietly fetches and caches all important pages
// so they're available offline immediately.
// ═══════════════════════════════════════════════════════════════

(function () {
  'use strict';

  const PAGES_TO_CACHE = [
    '/dashboard',
    '/students',
    '/add_student',
    '/appointments',
    '/admin/bookings',
    '/admin/bookings?tab=recent',
    '/admin/bookings?tab=history',
    '/admin/bookings?tab=all',
    '/sessions',
    '/create_session',
    '/case_note',
    '/referral',
    '/outcome_questionnaire',
    '/dass21',
    '/admin/users',
    '/admin/settings',
    '/admin/workflow',
    '/admin/cloud_sync',
    '/reports',
    '/profile',
    '/notifications'
  ];

  let _preCaching = false;

  async function preCacheAllPages() {
    if (_preCaching || !navigator.onLine) return;
    _preCaching = true;

    // Check if SW is ready
    if (!navigator.serviceWorker.controller) {
      // Wait for SW to be active
      navigator.serviceWorker.ready.then(() => doPreCache());
      return;
    }
    doPreCache();
  }

  async function doPreCache() {
    try {
      // Ask SW to pre-cache pages
      navigator.serviceWorker.controller.postMessage({
        type: 'PRE_CACHE_PAGES',
        pages: PAGES_TO_CACHE
      });

      // Also cache via IndexedDB page cache as backup
      let cached = 0;
      for (const url of PAGES_TO_CACHE) {
        try {
          const resp = await fetch(url, { credentials: 'same-origin' });
          if (resp.ok) {
            const html = await resp.text();
            if (typeof cachePage === 'function') {
              await cachePage(url, html);
            }
            cached++;
          }
        } catch (e) {
          // Skip failed pages silently
        }
      }
      console.log(`[PreCache] Cached ${cached}/${PAGES_TO_CACHE.length} pages`);
    } catch (e) {
      console.error('[PreCache] Error:', e);
    } finally {
      _preCaching = false;
    }
  }

  // Listen for SW confirmation
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.addEventListener('message', event => {
      if (event.data.type === 'PRE_CACHE_DONE') {
        console.log(`[PreCache] SW cached ${event.data.count} pages`);
      }
    });
  }

  // Run on page load if online and logged in
  if (navigator.onLine && document.cookie.includes('session')) {
    // Delay 2 seconds to not block page load
    setTimeout(preCacheAllPages, 2000);
  }

  // Also pre-cache when coming back online
  window.addEventListener('online', () => {
    setTimeout(preCacheAllPages, 1000);
  });
})();
