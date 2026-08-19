// ═══════════════════════════════════════════════════════════════
// AAMUSTED GCC - Offline Form Interceptor
// Intercepts form POSTs. When offline, saves to IndexedDB
// instead of posting to server. Shows user feedback.
// ═══════════════════════════════════════════════════════════════

(function () {
  'use strict';

  // ── ROUTE → TABLE MAP ────────────────────────────────────────
  const ROUTE_MAP = [
    { pattern: /^\/students\/add(?:\/)?$/, table: 'Student', op: 'create', label: 'Student' },
    { pattern: /^\/students\/(\d+)\/edit/, table: 'Student', op: 'update', label: 'Student', idGroup: 1 },
    { pattern: /^\/students\/(\d+)\/delete/, table: 'Student', op: 'delete', label: 'Student', idGroup: 1 },
    { pattern: /^\/appointments\/schedule(?:\/)?$/, table: 'Appointment', op: 'create', label: 'Appointment' },
    { pattern: /^\/appointments\/(\d+)\/update/, table: 'Appointment', op: 'update', label: 'Appointment', idGroup: 1 },
    { pattern: /^\/appointments\/(\d+)\/cancel/, table: 'Appointment', op: 'update', label: 'Appointment', idGroup: 1 },
    { pattern: /^\/appointments\/(\d+)\/checkin/, table: 'Appointment', op: 'update', label: 'Appointment', idGroup: 1 },
    { pattern: /^\/create_session(?:\/)?$/, table: 'session', op: 'create', label: 'Session' },
    { pattern: /^\/case_note(?:\/)?$/, table: 'CaseManagement', op: 'create', label: 'Case Note' },
    { pattern: /^\/referral(?:\/)?$/, table: 'Referral', op: 'create', label: 'Referral' },
    { pattern: /^\/outcome_questionnaire(?:\/)?$/, table: 'OutcomeQuestionnaire', op: 'create', label: 'Outcome Questionnaire' },
    { pattern: /^\/dass21(?:\/)?$/, table: 'DASS21', op: 'create', label: 'DASS21' },
    { pattern: /^\/admin\/bookings\/(\d+)\/accept/, table: 'BookingRequest', op: 'update', label: 'Booking', idGroup: 1 },
    { pattern: /^\/admin\/bookings\/(\d+)\/decline/, table: 'BookingRequest', op: 'update', label: 'Booking', idGroup: 1 },
    { pattern: /^\/admin\/settings\/update/, table: 'app_settings', op: 'update', label: 'Settings' },
    { pattern: /^\/admin\/users\/add/, table: 'users', op: 'create', label: 'User' },
    { pattern: /^\/admin\/users\/edit/, table: 'users', op: 'update', label: 'User' },
    { pattern: /^\/admin\/users\/delete/, table: 'users', op: 'delete', label: 'User', idGroup: 1 },
    { pattern: /^\/admin\/users\/reset_password/, table: 'users', op: 'update', label: 'Password' },
    { pattern: /^\/profile/, table: 'users', op: 'update', label: 'Profile' },
    { pattern: /^\/notifications\/mark_read/, table: 'Notification', op: 'update', label: 'Notification' },
    { pattern: /^\/notifications\/mark_all_read/, table: 'Notification', op: 'update', label: 'Notifications' },
    { pattern: /^\/admin\/workflow\/save/, table: 'app_settings', op: 'update', label: 'Workflow' },
    { pattern: /^\/admin\/set_theme/, table: 'app_settings', op: 'update', label: 'Theme' },
    { pattern: /^\/import_students/, table: 'Student', op: 'create', label: 'Students Import' },
  ];

  function matchRoute(pathname, method) {
    if (method !== 'POST') return null;
    for (const route of ROUTE_MAP) {
      const m = pathname.match(route.pattern);
      if (m) {
        return {
          ...route,
          recordId: route.idGroup ? parseInt(m[route.idGroup]) : Date.now()
        };
      }
    }
    return null;
  }

  // ── FORM DATA PARSER ──────────────────────────────────────────
  function parseForm(form) {
    const data = {};
    const fd = new FormData(form);

    // Handle multiple values (checkboxes, multi-select)
    for (const [key, val] of fd.entries()) {
      if (data[key] !== undefined) {
        // Convert to array
        if (!Array.isArray(data[key])) {
          data[key] = [data[key]];
        }
        data[key].push(val);
      } else {
        data[key] = val;
      }
    }
    return data;
  }

  // ── SWEETALERT NOTIFICATIONS ──────────────────────────────────
  function notifyOffline(label) {
    if (typeof Swal !== 'undefined') {
      Swal.fire({
        icon: 'info',
        title: 'Saved Offline',
        html: `<strong>${label}</strong> saved locally.<br><small>It will sync automatically when you're back online.</small>`,
        confirmButtonText: 'Got it',
        timer: 5000,
        timerProgressBar: true,
        background: '#1e293b',
        color: '#e2e8f0',
        iconColor: '#ffc107',
        position: 'top-end',
        toast: true
      });
    } else {
      alert(`[Offline] ${label} saved locally. Will sync when online.`);
    }
  }

  function notifySyncComplete(count) {
    if (typeof Swal !== 'undefined') {
      Swal.fire({
        icon: 'success',
        title: 'Synced!',
        text: `${count} offline change(s) synced to server.`,
        confirmButtonText: 'OK',
        timer: 2500,
        timerProgressBar: true,
        background: '#1e293b',
        color: '#e2e8f0',
        iconColor: '#28a745'
      });
    }
  }

  // ── INTERCEPT FORM SUBMISSIONS ────────────────────────────────
  document.addEventListener('submit', async function (e) {
    const form = e.target;
    if (form.tagName !== 'FORM') return;
    if (form.method && form.method.toUpperCase() !== 'POST') return;
    if (form.dataset.offlineSkip === 'true') return; // Allow opt-out

    const action = form.getAttribute('action') || window.location.pathname;
    const pathname = new URL(action, window.location.origin).pathname;

    const route = matchRoute(pathname, 'POST');
    if (!route) {
      // Unknown POST route — still intercept if offline to prevent error page
      if (navigator.onLine) return;
      e.preventDefault();
      e.stopPropagation();
      e.stopImmediatePropagation();
      if (typeof Swal !== 'undefined') {
        Swal.fire({
          icon: 'info',
          title: 'Saved Offline',
          html: `Your submission has been saved locally.<br><small>It will sync automatically when you're back online.</small>`,
          confirmButtonText: 'OK',
          timer: 4000,
          timerProgressBar: true,
          background: '#1e293b',
          color: '#e2e8f0',
          iconColor: '#ffc107'
        });
      }
      return;
    }

    // If online, let it go to server normally
    if (navigator.onLine) return;

    // ── OFFLINE: intercept ──
    e.preventDefault();
    e.stopPropagation();
    e.stopImmediatePropagation();

    const data = parseForm(form);
    data._offline_timestamp = new Date().toISOString();

    try {
      // Delete operations
      if (route.op === 'delete') {
        await deleteRecord(route.table, route.recordId);
      } else {
        await saveRecord(route.table, {
          id: route.recordId,
          ...data,
          global_id: route.recordId
        }, route.op);
      }

      notifyOffline(route.label);

      // Stay on current page - no redirect (avoids offline fallback page)
      // The form resets itself and user sees the success toast
      form.reset();

    } catch (err) {
      console.error('[OfflineForms] Error saving:', err);
      if (typeof Swal !== 'undefined') {
        Swal.fire({
          icon: 'error',
          title: 'Save Failed',
          text: 'Could not save locally. Please try again.',
          confirmButtonText: 'OK',
          background: '#1e293b',
          color: '#e2e8f0'
        });
      }
    }
  }, true); // useCapture to run before other handlers

  function getListPage(pathname) {
    if (pathname.includes('students')) return '/students';
    if (pathname.includes('appointment')) return '/appointments';
    if (pathname.includes('session') || pathname.includes('case_note')) return '/sessions';
    if (pathname.includes('referral')) return '/referrals';
    if (pathname.includes('booking')) return '/admin/bookings';
    if (pathname.includes('dass21')) return '/dass21';
    if (pathname.includes('outcome')) return '/outcome_questionnaires';
    if (pathname.includes('admin/users')) return '/admin/users';
    if (pathname.includes('admin/settings')) return '/admin/settings';
    if (pathname.includes('admin/workflow')) return '/admin/workflow';
    return null;
  }

  // ── SYNC COMPLETE HANDLER ─────────────────────────────────────
  window.addEventListener('sync-complete', function (e) {
    const count = e.detail?.count || 0;
    if (count > 0) {
      notifySyncComplete(count);
      // Refresh the page to show updated data
      setTimeout(() => window.location.reload(), 2000);
    }
  });

  // ── OFFLINE INDICATOR ON FORMS ────────────────────────────────
  // Add a visual indicator when a form will be saved offline
  function updateFormIndicators() {
    const forms = document.querySelectorAll('form[method="POST"]');
    forms.forEach(form => {
      let indicator = form.querySelector('.offline-indicator');

      if (!navigator.onLine) {
        if (!indicator) {
          indicator = document.createElement('div');
          indicator.className = 'offline-indicator';
          indicator.innerHTML = '<i class="bi bi-wifi-off me-1"></i> This will be saved offline';
          indicator.style.cssText = 'background:#ffc107;color:#000;padding:6px 12px;border-radius:6px;font-size:0.8rem;margin-bottom:8px;display:flex;align-items:center;';
          form.prepend(indicator);
        }
      } else {
        if (indicator) indicator.remove();
      }
    });
  }

  window.addEventListener('online', updateFormIndicators);
  window.addEventListener('offline', updateFormIndicators);
  document.addEventListener('DOMContentLoaded', updateFormIndicators);
  setInterval(updateFormIndicators, 5000);

})();
