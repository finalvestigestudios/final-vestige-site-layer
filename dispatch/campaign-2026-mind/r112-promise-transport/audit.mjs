/**
 * R112: non-sending, privacy-minimal review of the public signup promise,
 * actual Jetpack transport configuration and first-party campaign routes.
 * NO network, email, WP writes, subscriber export, analytics emitter or sends.
 */
const CURRENT_ORIGIN = 'connected_wordpress_jetpack_newsletter_status';
const SETTINGS_ORIGIN = 'connected_wordpress_jetpack_newsletter_settings';
const PUBLIC_ORIGIN = 'connected_wordpress_published_content';
const LIVE_ORIGIN = 'connected_wordpress_published_destination';
const N = value => Number.isSafeInteger(value) && value >= 0;
const CANONICAL = new Set([1,2,3,4,5,6]);
const COMMERCIAL = new Set([3,5]);
const EXPECTED_DESTINATIONS = Object.freeze({
  1:'https://finalvestige.com/the-missing-caption/',
  2:'https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/',
  4:'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/',
  6:'https://finalvestige.com/focus/'
});
const DATE = x => typeof x === 'string' && !Number.isNaN(Date.parse(x)) && /^20\d{2}-\d{2}-\d{2}T/.test(x);
const limit = (s, n = 10000) => typeof s === 'string' && s.length <= n;
const canonicalURL = raw => {
  try {
    const u = new URL(raw);
    if (u.protocol !== 'https:' || u.hostname !== 'finalvestige.com' || u.username || u.password || u.hash) return null;
    const safe = new URL('https://finalvestige.com' + u.pathname);
    if (u.search) return null; // Reviewed editorial destinations are path-only.
    return safe.toString();
  } catch (_) { return null; }
};

export function reviewSubscriberPromise({status,settings,pages,received}={}) {
  if (!status || status.origin !== CURRENT_ORIGIN || !DATE(status.as_of) ||
      !settings || settings.origin !== SETTINGS_ORIGIN || !DATE(settings.as_of) ||
      !pages || pages.origin !== PUBLIC_ORIGIN ||
      !limit(pages.focus) || !limit(pages.dispatch) || !limit(settings.welcome_message,5000)) {
    return {state:'INVALID_EVIDENCE', blockers:['missing_authoritative_read_only_snapshots'], sending_authorized:false};
  }
  const s=status.subscribers;
  if (!s || !['total','confirmed','unconfirmed','suppressed'].every(k=>N(s[k])) ||
      s.confirmed > s.total) {
    return {state:'INVALID_EVIDENCE',blockers:['invalid_subscriber_aggregates'],sending_authorized:false};
  }
  const messages=Array.isArray(status.recent_sends) ? status.recent_sends : [];
  const recentDispatched=messages.some(m=>m && m.dispatched_at && ['sent','completed','delivered'].includes(m.status));
  const automaticNewPosts=settings.email_new_posts_by_default;
  const explicitPromise=/when (?:we|there(?:'s| is)).{0,60}(?:publish|new.*investigation)/i.test(pages.dispatch+' '+settings.welcome_message);
  const commercialConsentFocus=/commission|affiliate recommendation|earning link/i.test(pages.focus);
  const commercialConsentDispatch=/commission|affiliate recommendation|earning link/i.test(pages.dispatch);
  const receivedWelcome = received && received.origin === 'independent_authorized_mime_review' &&
    received.kind === 'fieldbook_welcome' && received.result === 'received_with_pdf_link_and_download_verified';
  const blockers = [];
  if (automaticNewPosts !== false) blockers.push('automatic_new_post_default_not_proven_off');
  if (settings.email_content_format !== 'excerpt') blockers.push('native_transport_contract_changed_review_again');
  if (explicitPromise && automaticNewPosts === false) blockers.push('publisher_promise_needs_manual_send_expectation_review');
  if (!commercialConsentDispatch && commercialConsentFocus) blockers.push('dispatch_focus_commercial_consent_copy_mismatch');
  if (!receivedWelcome) blockers.push('no_authorized_received_welcome_and_pdf_proof');
  blockers.push('native_recipient_email_eligibility_unverified');
  blockers.push('commercial_postal_address_and_functional_optout_unverified');
  blockers.push('native_preheader_and_excerpt_received_rendering_unverified');
  return {
    state:'REVIEW_REQUIRED_HOLD_UNSENT', transport:'jetpack_native_excerpt',
    automatic_new_posts:automaticNewPosts, recent_send_recorded:recentDispatched,
    note:recentDispatched ? 'some_recent_dispatch_recorded_not_proof_of_inbox_delivery' : 'none_of_checked_recent_sends_prove_dispatch',
    counts:{newsletter_total:s.total,confirmed:s.confirmed,unconfirmed_excluded:s.unconfirmed},
    email_reachable:null, welcome_delivered:receivedWelcome ? true : null,
    consent_parity:commercialConsentDispatch ? 'matched_or_requires_manual_review' : 'dispatch_copy_not_equivalent',
    blockers:[...new Set(blockers)], sending_authorized:false, revenue_verified:null
  };
}

/** Validate exact original 4:2 scheme and four verified *published* CTA routes.
 * Never infer merchant permission from a vendor URL, vendor policy or a guide draft. */
export function verifyOriginalCampaign(manifest,publishedDestinations=[]) {
  const fail=(reason)=>({valid:false,reason,issue_readiness:[],sending_authorized:false});
  if (!manifest || manifest.status!=='DRAFT_UNSENT_NO_SCHEDULING' ||
      !Array.isArray(manifest.issues) || manifest.issues.length!==6 ||
      !Array.isArray(publishedDestinations)) return fail('invalid_master_manifest');
  const identifiers=manifest.issues.map(x=>x?.number);
  if (!identifiers.every((x,i)=>CANONICAL.has(x) && x===i+1)) return fail('edition_number_drift');
  const evidence=new Map();
  for (const item of publishedDestinations) {
    if (!item || !Number.isInteger(item.edition) || !item.url ||
        item.source!==LIVE_ORIGIN || item.status!=='publish' ||
        canonicalURL(item.url)!==item.url) continue;
    evidence.set(item.edition,item.url);
  }
  const rows=[];
  for (const entry of manifest.issues) {
    const commercial=COMMERCIAL.has(entry.number);
    if ((entry.kind==='commercial-review-pending')!==commercial ||
        entry.publish_state!=='hold' || entry.merchant_affiliate_url!==null) return fail('campaign_allocation_or_activation_drift');
    if (commercial) rows.push({edition:entry.number,kind:'commercial',verified_cta:false,
      reason:'partner_approval_and_live_guide_unverified',state:'HOLD_MERCHANT'});
    else {
      const actual=EXPECTED_DESTINATIONS[entry.number];
      const matching=entry.editorial_cta===actual && evidence.get(entry.number)===actual;
      rows.push({edition:entry.number,kind:'editorial',verified_cta:matching,
        reason:matching?'first_party_published_destination_verified':'first_party_destination_not_verified',state:'HOLD_UNSENT'});
    }
  }
  return {valid:true,allocation:{editorial:4,commercial_reserved:2},
    issue_readiness:rows,sending_authorized:false,paid_sales_verified:null};
}

/** Optional first-party URL tag contract only; *not* a live tracking script.
 * A URL with valid tags is not evidence that a human clicked or purchased. */
export function draftEmailAttribution({edition,destination,campaign}={}) {
  if (!Number.isInteger(edition) || !CANONICAL.has(edition) ||
      !limit(campaign,80) || !/^dispatch_pilot_20\d{2}_\d{2}$/.test(campaign)) {
    return {status:'REJECTED',url:null,event:null};
  }
  if (!EXPECTED_DESTINATIONS[edition] || destination!==EXPECTED_DESTINATIONS[edition]) {
    return {status:'REJECTED',url:null,event:null};
  }
  const u=new URL(destination);
  u.searchParams.set('utm_source','dispatch');
  u.searchParams.set('utm_medium','email');
  u.searchParams.set('utm_campaign',campaign);
  u.searchParams.set('utm_content','issue'+String(edition).padStart(2,'0'));
  return {status:'UNSENT_ATTRIBUTION_DRAFT_ONLY',url:u.toString(),
    event:null,clicked:null,confirmed_signup:null,paid_order:null,net_revenue:null};
}
