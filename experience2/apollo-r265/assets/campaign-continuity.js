/* Apollo R265: opt-in, staging-only internal campaign continuity. No events, cookies, network or storage. */
(() => {
  'use strict';
  const destination = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
  const sources = new Set(['youtube', 'tiktok', 'instagram', 'facebook', 'pinterest', 'x', 'bluesky']);
  const keys = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content'];
  const safeCampaign = /^[a-z0-9][a-z0-9_-]{2,63}$/;
  const safeAsset = /^[A-Za-z0-9_-]{3,80}$/;
  function validatedCampaign(search) {
    const input = new URLSearchParams(search);
    if ([...input.keys()].some(key => key.startsWith('utm_') && !keys.includes(key))) return null;
    if (keys.some(key => input.getAll(key).length !== 1)) return null;
    const source = input.get('utm_source');
    const medium = input.get('utm_medium');
    const campaign = input.get('utm_campaign');
    const asset = input.get('utm_content');
    if (!sources.has(source) || medium !== 'organic_social') return null;
    if (!safeCampaign.test(campaign) || !safeAsset.test(asset)) return null;
    return { utm_source: source, utm_medium: medium, utm_campaign: campaign, utm_content: asset };
  }
  function enhance() {
    try {
      const params = validatedCampaign(window.location.search);
      if (!params) return;
      const root = document.querySelector('.fv-apollo-atlas');
      if (!root || document.querySelectorAll('.fv-apollo-atlas').length !== 1) return;
      const links = [...root.querySelectorAll('a[href]')].filter(link => link.href === destination);
      if (links.length !== 1 || !links[0].closest('#fv-apollo-reading-bridge')) return;
      const url = new URL(destination);
      for (const key of keys) url.searchParams.set(key, params[key]);
      links[0].href = url.href;
    } catch (_) { /* Attribution fails open: the original free investigation link still works. */ }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', enhance, { once: true });
  else enhance();
})();
