'use strict';
/**
 * Read-only laboratory rendering telemetry for the media browser probe.
 * Observer injected BEFORE navigation; no DOM text, image URLs, cookies,
 * credentials or third-party binaries collected.
 * Scripted full-page scrolling is NOT equivalent to real-user CWV.
 */
const DOCUMENT_START_SCRIPT = String.raw`(() => {
  if (window.__fvMediaVisualLabV1) return;
  const state = {
    version: 1,
    layout_shift_supported: false,
    largest_contentful_paint_supported: false,
    layout_shift_score: null,
    max_session_window_shift_score: null,
    session_start_ms: null,
    session_previous_ms: null,
    session_score: 0,
    qualifying_layout_shift_events: 0,
    excluded_recent_input_events: 0,
    largest_contentful_paint: null,
    layout_shift_samples: [],
    observers: []
  };
  Object.defineProperty(window, '__fvMediaVisualLabV1', {
    value: state, writable: false, configurable: false
  });
  if (typeof PerformanceObserver !== 'function') return;
  try {
    const layout = new PerformanceObserver(list => {
      for (const entry of list.getEntries()) {
        if (!Number.isFinite(entry.value) || entry.value < 0 ||
            !Number.isFinite(entry.startTime) || entry.startTime < 0) continue;
        if (entry.hadRecentInput === true) {
          state.excluded_recent_input_events++;
          continue;
        }
        state.layout_shift_score += entry.value;
        // CLS-style lab diagnostic: largest session window, with max 1s
        // gap and max 5s duration (not field / 75th-percentile CLS).
        if (state.session_start_ms === null ||
            entry.startTime - state.session_previous_ms > 1000 ||
            entry.startTime - state.session_start_ms > 5000) {
          state.session_start_ms = entry.startTime;
          state.session_score = 0;
        }
        state.session_previous_ms = entry.startTime;
        state.session_score += entry.value;
        state.max_session_window_shift_score =
          Math.max(state.max_session_window_shift_score, state.session_score);
        state.qualifying_layout_shift_events++;
        if (state.layout_shift_samples.length < 20) {
          state.layout_shift_samples.push({
            start_time_ms: Math.round(entry.startTime),
            score: Math.round(entry.value * 1000000) / 1000000,
            affected_element_tags: (entry.sources || []).slice(0, 5).map(s =>
              String(s.node && s.node.tagName || 'unknown').toLowerCase()
            )
          });
        }
      }
    });
    layout.observe({ type: 'layout-shift', buffered: true });
    state.layout_shift_supported = true;
    state.layout_shift_score = 0;
    state.max_session_window_shift_score = 0;
    state.observers.push(layout);
  } catch (_) { /* Unsupported LayoutShift: do not invent a zero. */ }
  try {
    const lcp = new PerformanceObserver(list => {
      for (const entry of list.getEntries()) {
        if (!Number.isFinite(entry.startTime) || entry.startTime < 0) continue;
        const tag = String(entry.element && entry.element.tagName || 'unknown').toLowerCase();
        state.largest_contentful_paint = {
          start_time_ms: Math.round(entry.startTime),
          size_px2: Number.isFinite(entry.size) && entry.size >= 0 ? Math.round(entry.size) : null,
          element_tag: tag,
          element_is_image: tag === 'img'
        };
      }
    });
    lcp.observe({ type: 'largest-contentful-paint', buffered: true });
    state.largest_contentful_paint_supported = true;
    state.observers.push(lcp);
  } catch (_) { /* Unsupported LCP: do not claim one. */ }
})();`;

const READ_EXPRESSION = String.raw`(() => {
  const s = window.__fvMediaVisualLabV1;
  if (!s || s.version !== 1) return null;
  return {
    version: 1,
    layout_shift_supported: s.layout_shift_supported === true,
    largest_contentful_paint_supported: s.largest_contentful_paint_supported === true,
    layout_shift_score: s.layout_shift_supported === true ?
      Math.round(s.layout_shift_score * 1000000) / 1000000 : null,
    max_session_window_shift_score: s.layout_shift_supported === true ?
      Math.round(s.max_session_window_shift_score * 1000000) / 1000000 : null,
    qualifying_layout_shift_events: s.qualifying_layout_shift_events,
    excluded_recent_input_events: s.excluded_recent_input_events,
    largest_contentful_paint: s.largest_contentful_paint || null,
    layout_shift_samples: s.layout_shift_samples.slice()
  };
})()`;

function interpretVisualLab(initial,afterScroll,documentVerified) {
  const usable = x => x && x.version === 1 &&
    typeof x.layout_shift_supported === 'boolean' &&
    typeof x.largest_contentful_paint_supported === 'boolean';
  if (documentVerified !== true || !usable(initial) || !usable(afterScroll)) {
    return {
      state: 'UNVERIFIED', after_navigation: null, after_automated_scroll: null,
      field_cwv_claim_permitted: false, reasons: ['missing_verified_document_or_document_start_observer']
    };
  }
  return {
    state: 'LAB_OBSERVED_NOT_FIELD_CWV',
    after_navigation: initial,
    after_automated_scroll: afterScroll,
    field_cwv_claim_permitted: false,
    reasons: [
      'scripted_scroll_is_not_real_user_interaction',
      'no_field_distribution_or_cwv_75th_percentile',
      'missing_layout_shift_or_lcp_observer_must_remain_null'
    ]
  };
}
module.exports = { DOCUMENT_START_SCRIPT, READ_EXPRESSION, interpretVisualLab };
