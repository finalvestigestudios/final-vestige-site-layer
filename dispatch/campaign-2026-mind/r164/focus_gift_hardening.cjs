'use strict';
/**
 * Draft, offline-only Gutenberg source transformer for Focus page #1579.
 * This code does not connect to WordPress, email, analytics, or a subscriber list.
 * Claude/Site QA must review before any live edit.
 */
const EXPECTED_PDF = 'https://finalvestige.com/wp-content/uploads/2026/10/Final_Vestige_Seven_Day_Focus_Fieldbook_Complete_Edition.pdf';
const OLD_SCRIPT = /<!-- wp:html -->\s*<script id="fvf-gift-v2">([\s\S]*?)<\/script>\s*<!-- \/wp:html -->/g;
const OLD_PANEL = /<div id="fvf-gift" class="fvf-gift" hidden role="status">([\s\S]*?)<\/div>/g;
const SUBSCRIPTION_BLOCK = /<!-- wp:jetpack\/subscriptions\s/gi;
const ABSOLUTE_DOWNLOAD = /href="(https:\/\/[^"\s]+\.pdf)"/g;
function count(source, re) {return [...source.matchAll(re)].length;}
function hardenFocusSource(raw) {
  if (typeof raw !== 'string' || !raw) throw new TypeError('Expected nonempty Gutenberg markup string');
  if (count(raw, OLD_SCRIPT) !== 1) throw new Error('Fail-closed: expected exactly one canonical fvf-gift-v2 script block');
  if (count(raw, OLD_PANEL) !== 1) throw new Error('Fail-closed: expected exactly one canonical hidden gift panel');
  if (count(raw, SUBSCRIPTION_BLOCK) !== 1) throw new Error('Fail-closed: expected exactly one existing Jetpack subscription block');
  const panel = raw.match(OLD_PANEL)[0];
  if (!panel.includes(`href="${EXPECTED_PDF}"`)) throw new Error('Fail-closed: unexpected Fieldbook media URL');
  if (!panel.includes('data-fv-event="focus_pdf_click"') || !panel.includes('data-fv-location="after_signup"')) throw new Error('Fail-closed: gift tracking selectors drifted');
  const script = raw.match(OLD_SCRIPT)[0];
  if (!script.includes("get('subscribe')") || !script.includes('is-subscriber') || !script.includes('g.hidden=false')) throw new Error('Fail-closed: source script has changed; re-audit manually');
  const safePanel = `<div id="fvf-gift" class="fvf-gift" role="region" aria-label="Free Focus Fieldbook download">
    <p class="fvf-gift-title">The free Fieldbook is available here.</p>
    <a class="fvf-btn" href="${EXPECTED_PDF}" data-fv-event="focus_pdf_click" data-fv-location="public_fieldbook">Download the Seven Day Focus Fieldbook</a>
    <p class="fvf-micro">The download is free whether or not you subscribe. Downloading does not subscribe you to The Dispatch. If you entered your email above and WordPress asks you to confirm, use the link in its confirmation message; the welcome email also includes this PDF.</p>
  </div>`;
  const updated = raw.replace(OLD_PANEL, safePanel).replace(OLD_SCRIPT, '<!-- Removed URL/CSS-based fvf-gift-v2 success detector. No client-side subscription verification. -->');
  if (updated === raw || updated.includes('id="fvf-gift-v2"') || updated.includes('data-fv-location="after_signup"')) throw new Error('Unsafe transformation result');
  if (count(updated, SUBSCRIPTION_BLOCK) !== 1 || count(updated, /id="fvf-gift"/g) !== 1) throw new Error('Subscription or panel duplication');
  if (updated.split(EXPECTED_PDF).length !== raw.split(EXPECTED_PDF).length) throw new Error('Fieldbook media link count drift');
  return Object.freeze({updated, summary:Object.freeze({wordpressPageId:1579, change:'REVIEW_ONLY_NO_WORDPRESS_WRITE', oldScriptRemoved:true, publicDownloadClarified:true, confirmedSignupProof:'NONE_FROM_CLIENT', automaticEmailChanges:false, subscriberListChanges:false})});
}
module.exports = { hardenFocusSource, EXPECTED_PDF };
