/* Apollo R317: first-party editorial URL continuity; no analytics, storage, or network requests.
 * Staging only: this enhancement must not ship without cache, consent, and owner review.
 * A cached HTML body remains identical for every visitor; values are read on
 * trusted activation OR the opening of a native mouse/keyboard context menu.
 * This is a per-visitor navigation hint, NOT a confirmed session or sale.
 */
(() => {
  'use strict';
  const FREE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
  const FIELDS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content'];
  const SOURCE_CODE = Object.freeze({youtube: 'yt', tiktok: 'tt', instagram: 'ig', facebook: 'fb'});
  const campaignFormat = /^apollo1_(?:pilot|longform|shorts)_20\d{2}_(?:0[1-9]|1[0-2])$/;
  // TASK-008 (2026-11-03) defines <topic_cluster>_pilot_2026_11.
  // Permit ONLY its November 2026 History pilot in this Apollo-specific
  // staging adapter. Asset ids still MUST have the Apollo1+platform prefix.
  // This is a compatibility rule, NOT proof of a real published Grok asset.
  // Future months, other clusters and unrestricted asset names stay blocked.
  const reviewedHistoryPilot = 'history_pilot_2026_11';
  const contentFormat = /^apollo1_(yt|tt|ig|fb)_[a-z0-9]{3,24}$/;

  function verifiedLabels(search) {
    if (typeof search !== 'string' || search.length > 1200) return null;
    const params = new URLSearchParams(search);
    const values = {};
    for (const field of FIELDS) {
      const all = params.getAll(field);
      if (all.length !== 1 || all[0].length > 64) return null;
      values[field] = all[0];
    }
    if (!Object.hasOwn(SOURCE_CODE, values.utm_source)) return null;
    if (values.utm_medium !== 'organic_social') return null;
    if (!campaignFormat.test(values.utm_campaign) &&
        values.utm_campaign !== reviewedHistoryPilot) return null;
    const match = contentFormat.exec(values.utm_content);
    if (!match || match[1] !== SOURCE_CODE[values.utm_source]) return null;
    return values;
  }

  function intendedLink(target) {
    if (!(target instanceof Element)) return null;
    const link = target.closest('a[data-fv-cta="apollo-read-free-investigation"]');
    if (!link) return null;
    // A prior click may have annotated the same anchor in a long-lived page.
    // Accept only this exact editorial destination, never an arbitrary rewrite.
    let current;
    try { current = new URL(link.href, document.baseURI); } catch { return null; }
    if (current.origin + current.pathname !== FREE || current.hash) return null;
    const region = link.closest('section.fv-r281[data-fv-experience="apollo-1"]');
    if (!region || region.getAttribute('data-fv-client-campaign') !== 'staging-click-only') return null;
    return link;
  }

  function handleActivation(event) {
    // Browsers dispatch click for primary mouse, keyboard and touch activation,
    // auxclick for middle-button, contextmenu for right-click OR keyboard menu.
    // Reject synthetic, canceled, malformed and unrelated events. Never intercept navigation.
    if (!event.isTrusted || event.defaultPrevented) return;
    if (event.type === 'click' && event.button !== 0) return;
    if (event.type === 'auxclick' && event.button !== 1) return;
    // R316: Chromium emits trusted contextmenu with button=-1, buttons=0,
    // detail=0 on Shift+F10 and the dedicated ContextMenu key. R315 had
    // rejected this keyboard-only path, losing valid campaign continuity for
    // keyboard and assistive-technology users who open/copy the native link.
    // Keep mouse-right and keyboard-menu distinct; never intercept the menu.
    // A context menu is NOT a counted click, signup, checkout or purchase.
    if (event.type === 'contextmenu') {
      const mouseRight = event.button === 2;
      const keyboardMenu = event.button === -1 && event.buttons === 0 && event.detail === 0;
      if (!mouseRight && !keyboardMenu) return;
    }
    const link = intendedLink(event.target);
    if (!link) return;
    // Reset stale labels before each genuine activation, including SPA URL change.
    link.href = FREE;
    const labels = verifiedLabels(window.location.search);
    if (!labels) return;
    const next = new URL(FREE);
    for (const field of FIELDS) next.searchParams.set(field, labels[field]);
    // Never echo source query or personal data. No network event is generated here.
    link.href = next.toString();
  }

  document.addEventListener('click', handleActivation, true);
  document.addEventListener('auxclick', handleActivation, true);
  document.addEventListener('contextmenu', handleActivation, true);
})();
