/* Apollo R313: first-party editorial URL continuity; no analytics, storage, or network requests.
 * Staging only: this enhancement must not ship without cache, consent, and owner review.
 * A cached HTML body remains identical for every visitor; values are read on ACTUAL click.
 */
(() => {
  'use strict';
  const FREE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
  const FIELDS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content'];
  const SOURCE_CODE = Object.freeze({youtube: 'yt', tiktok: 'tt', instagram: 'ig', facebook: 'fb'});
  const campaignFormat = /^apollo1_(?:pilot|longform|shorts)_20\d{2}_(?:0[1-9]|1[0-2])$/;
  // Grok may propose other IDs; they require a reviewed format change, not a silent fallback.
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
    if (!campaignFormat.test(values.utm_campaign)) return null;
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

  document.addEventListener('click', event => {
    // A real, user-initiated anchor click is the ONLY opportunity to add labels.
    if (!event.isTrusted || event.defaultPrevented) return;
    const link = intendedLink(event.target);
    if (!link) return;
    // Reset stale labels before each real activation, including an SPA URL change.
    link.href = FREE;
    const labels = verifiedLabels(window.location.search);
    if (!labels) return;
    const next = new URL(FREE);
    for (const field of FIELDS) next.searchParams.set(field, labels[field]);
    // Never echo source query or personal data. No network event is generated here.
    link.href = next.toString();
  }, true);
})();
