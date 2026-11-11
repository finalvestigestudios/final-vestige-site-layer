'use strict';
// Pure, read-only review checks. NOT a delivery authorization engine.
// Source values originate in the separately dated evidence snapshot; it cannot authenticate them.
function scope(t) {
  const s = typeof t === 'string' ? t.replace(/<[^>]*>/g,' ').toLowerCase() : '';
  return {
    names_dispatch: /\bthe dispatch\b/.test(s),
    expectation_of_emails: /\b(email|emails|you.ll hear|subscribe|subscribing)\b/.test(s),
    commission_expectation: /\b(commission|affiliate|earn us a commission|may earn)\b/.test(s),
    opt_out_promised: /\b(unsubscribe|opt.out)\b/.test(s)
  };
}
function review(e) {
  if (!e || typeof e !== 'object' || !e.surfaces || !e.newsletter || !e.merchant)
    throw new TypeError('dated source snapshot required');
  const slots = ['focus','dispatch','welcome'];
  const consent = Object.fromEntries(slots.map(k => {
    if (!e.surfaces[k] || typeof e.surfaces[k].text !== 'string')
      throw new TypeError('missing surface: ' + k);
    return [k, scope(e.surfaces[k].text)];
  }));
  const mix = { editorial:4, commercial:2, ids:[1,2,3,4,5,6], commercial_ids:[3,5] };
  const blockers = [];
  if (!consent.dispatch.commission_expectation)
    blockers.push('DISPATCH_SIGNUP_EXPECTATION_GAP');
  if (!consent.welcome.commission_expectation)
    blockers.push('CONFIGURED_WELCOME_EXPECTATION_GAP');
  if (!consent.focus.commission_expectation)
    blockers.push('FOCUS_SIGNUP_EXPECTATION_GAP');
  if (e.newsletter.eligible_recipient_count === null)
    blockers.push('ACTUAL_EMAIL_ELIGIBILITY_UNKNOWN');
  if (e.newsletter.welcome_received !== true)
    blockers.push('RECEIVED_WELCOME_NOT_AUTHENTICATED');
  if (e.actual_received_jetpack_footer !== true)
    blockers.push('RENDERED_POSTAL_UNSUB_NOT_AUTHENTICATED');
  const m = e.merchant;
  if (m.affiliate_acceptance !== true || m.email_promo_permission !== true ||
      typeof m.earning_url !== 'string' || !/^https:\/\//.test(m.earning_url) ||
      m.approved_live_guide !== true)
    blockers.push('COMMERCIAL_OFFERS_NOT_AUTHORIZED');
  if (e.founder_final_send_approval !== true)
    blockers.push('FINAL_CAMPAIGN_APPROVAL_ABSENT');
  if (e.verified_paid_orders === null || e.realized_net_revenue_per_1000_qualified_sessions === null)
    blockers.push('REALIZED_NET_REVENUE_NOT_COMPUTABLE');
  // Never infer authorization from external caller-supplied attestation flags.
  // Founder approval and delivery authorization are separate out-of-band processes.
  return Object.freeze({state:'HOLD_UNSENT', mix, consent, blockers,
    real_revenue:null, can_send:false, authorization_mechanism:'OUT_OF_BAND_NOT_IMPLEMENTED'});
}
module.exports = {scope, review};
