/* Apollo R265: STAGING ONLY — validated DOM handoff hints, no internal UTM links or analytics. */
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
      // Never add UTMs to internal navigation: event-scoped attribution could be distorted.
      const link = links[0];
      if (Object.keys(link.dataset).some(key => key.startsWith('fvApolloCampaign'))) return;
      link.dataset.fvApolloCampaignSource = params.utm_source;
      link.dataset.fvApolloCampaignMedium = params.utm_medium;
      link.dataset.fvApolloCampaignName = params.utm_campaign;
      link.dataset.fvApolloCampaignAsset = params.utm_content;
      link.dataset.fvApolloCampaignStatus = 'unverified';
    } catch (_) { /* The original free investigation link is always unchanged. */ }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', enhance, { once: true });
  else enhance();
})();
