// ═══════════════════════════════════════════════════════════════
// AAMUSTED GCC - Background Page Pre-Cache v2
// After login, quietly fetches and caches ALL important pages.
// Only caches HTML responses (skips redirects/errors).
// ═══════════════════════════════════════════════════════════════

(function () {
  'use strict';

  const PAGES_TO_CACHE = [
    '/dashboard',
    '/students',
    '/add_student',
    '/manage_appointments',
    '/intake',
    '/admin/bookings',
    '/admin/bookings?tab=recent',
    '/admin/bookings?tab=history',
    '/admin/bookings?tab=all',
    '/sessions',
    '/create_session',
    '/case_note',
    '/case_notes_list',
    '/referral',
    '/all_referrals',
    '/outcome_questionnaire',
    '/dass21',
    '/dass21_list',
    '/reports',
    '/statistics',
    '/my_cases',
    '/booking',
    '/admin/users',
    '/admin/settings',
    '/admin/workflow',
    '/admin/cloud_sync',
    '/admin/forms',
    '/profile',
    '/audit_logs',
    '/welcome'
  ];

  let _preCaching = false;
  let _done = false;

  async function preCacheAllPages() {
    if (_preCaching || _done || !navigator.onLine) return;

    // Don't pre-cache if not logged in
    if (!document.cookie.includes('session') && !window.location.pathname.includes('/login')) {
      return;
    }

    _preCaching = true;
    console.log('[PreCache] Starting background page cache...');

    try {
      const cache = await caches.open('aamusted-v8-pages');
      let cached = 0;
      let skipped = 0;

      for (const url of PAGES_TO_CACHE) {
        try {
          // Check if already cached
          const existing = await cache.match(url);
          if (existing) {
            skipped++;
            continue;
          }

          const resp = await fetch(url, {
            credentials: 'same-origin',
            redirect: 'follow',
            headers: { 'Accept': 'text/html' }
          });

          // Only cache successful HTML responses
          if (resp.ok) {
            const contentType = resp.headers.get('content-type') || '';
            const text = await resp.text();

            // Skip if it's not HTML (JSON, redirect page, etc.)
            if (!contentType.includes('text/html') && !text.includes('<!DOCTYPE html>') && !text.includes('<html')) {
              continue;
            }

            // Skip if it's a login redirect
            if (text.includes('window.location') && text.includes('login')) {
              continue;
            }

            // Cache the response
            const response = new Response(text, {
              headers: { 'Content-Type': 'text/html; charset=utf-8' },
              status: 200
            });
            await cache.put(url, response);
            cached++;
          }
        } catch (e) {
          // Skip failed pages
        }
      }

      console.log(`[PreCache] Done: ${cached} cached, ${skipped} already cached, ${PAGES_TO_CACHE.length - cached - skipped} skipped`);
      _done = true;

    } catch (e) {
      console.error('[PreCache] Error:', e);
    } finally {
      _preCaching = false;
    }
  }

  // Run after page load (don't block)
  if (navigator.onLine) {
    setTimeout(preCacheAllPages, 3000);
  }

  // Re-run when coming back online
  window.addEventListener('online', () => {
    _done = false;
    setTimeout(preCacheAllPages, 1500);
  });
})();
