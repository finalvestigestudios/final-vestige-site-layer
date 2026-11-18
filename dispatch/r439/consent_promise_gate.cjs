'use strict';
/* Offline, pure, read-only evaluator. No network, no WordPress writes, no sending. */
const assert = require('node:assert/strict');

function isNonempty(v) { return typeof v === 'string' && v.trim().length > 0; }
function safeRef(v) { return isNonempty(v) && /^[A-Za-z0-9_./#:-]{8,256}$/.test(v) && !/@|\?|&|email|token|secret|password|subscriber_id|ip_address/i.test(v); }
function evaluate(snapshot, proofs = {}) {
  const blockers = [];
  const errors = [];
  const s = snapshot || {};
  const c = s.newsletter || {};
  const f = s.followers || {};
  const sum = (arr) => arr.reduce((a,b) => a + b, 0);
  for (const k of ['total','confirmed','unconfirmed','suppressed']) {
    if (!Number.isInteger(c[k]) || c[k] < 0) errors.push(`invalid newsletter.${k}`);
  }
  if (Number.isInteger(c.total) && Number.isInteger(c.confirmed) && c.confirmed > c.total)
    errors.push('confirmed exceeds total');
  if (Number.isInteger(f.email) && f.email < 0 || Number.isInteger(f.reader) && f.reader < 0)
    errors.push('negative follower count');
  if (c.enabled !== true || c.email_new_posts_by_default !== false) blockers.push('newsletter settings drift: read current production');
  if (c.email_content_format !== 'full') blockers.push('email mode drift: inspect real preview');
  if (s.promise?.email_every_published_investigation === true && c.email_new_posts_by_default === false)
    blockers.push('public copy implies automatic dispatch for every publication while automatic sends are off');
  const eligible = proofs.email_eligible_count;
  const eligibleProof = safeRef(proofs.email_eligible_ref);
  if (!Number.isInteger(eligible) || eligible < 0 || eligibleProof !== true)
    blockers.push('unique email-eligible recipient count not provider witnessed');
  if (!safeRef(proofs.welcome_received_ref)) blockers.push('actual welcome + Fieldbook receipt unverified');
  if (!safeRef(proofs.preview_ref)) blockers.push('native Jetpack email preview not witnessed');
  if (!safeRef(proofs.valid_fv_postal_ref) || !safeRef(proofs.rendered_unsubscribe_ref))
    blockers.push('publisher physical mailing address and rendered unsubscribe not witnessed');
  const commercial = s.issue_mix?.editorial === 4 && s.issue_mix?.commercial === 2;
  if (!commercial) errors.push('4 editorial / 2 commercial allocation changed');
  const products = s.commercial_offers || [];
  if (!Array.isArray(products) || products.length !== 2) errors.push('exactly two commercial slots required');
  else for (const item of products) {
    if (![3,5].includes(item.issue)) errors.push('commercial slot must be issue 03 or 05');
    if ((item.issue === 3 && item.id !== 'zen12') || (item.issue === 5 && item.id !== 'hypnosis_live')) errors.push('canonical offer identity drift: Issue 03 Zen12 / Issue 05 Hypnosis Live');
    for (const field of ['email_permission_ref','approved_guide_ref','earning_url_ref','merchant_terms_ref','claim_review_ref'])
      if (!safeRef(proofs.offers?.[item.issue]?.[field])) blockers.push(`issue ${item.issue} missing ${field}`);
  }
  const providerConfirmed = proofs.confirmed_signup_event === true && safeRef(proofs.confirmed_signup_ref) && proofs.consent_scope === 'dispatch_newsletter';
  if (!providerConfirmed) blockers.push('confirmed_signup cannot be proven by click, URL parameter, PDF download or Reader follow');
  const auditedSessions = Number.isInteger(proofs.qualified_human_sessions) && proofs.qualified_human_sessions > 0 && safeRef(proofs.session_audit_ref);
  const paid = Number.isInteger(proofs.settled_orders) && proofs.settled_orders >= 0 && safeRef(proofs.merchant_settlement_ref) && safeRef(proofs.refunds_fees_ref);
  const validAmounts = ['gross','refunds','fees'].every(k => typeof proofs[k] === 'number' && Number.isFinite(proofs[k]) && proofs[k] >= 0);
  const netPerK = auditedSessions && paid && validAmounts ? 1000 * (proofs.gross - proofs.refunds - proofs.fees) / proofs.qualified_human_sessions : null;
  const readiness = { editorial_reviewable: errors.length === 0 && eligibleProof && Number.isInteger(eligible) && !!safeRef(proofs.preview_ref) && !!safeRef(proofs.valid_fv_postal_ref) && !!safeRef(proofs.rendered_unsubscribe_ref), commercial_reviewable: false, send_authorized: false };
  const types = { total: c.total ?? null, confirmed: c.confirmed ?? null, unconfirmed_excluded: c.unconfirmed ?? null, direct_email_followers: f.email ?? null, reader_followers: f.reader ?? null, eligible_inboxes: eligibleProof && Number.isInteger(eligible) ? eligible : null };
  return { errors, blockers, types, consent_status: providerConfirmed ? 'PROVIDER_EVENT_WITH_SCOPE' : 'UNVERIFIED', revenue_per_1000_qualified_humans: netPerK, readiness, note: 'No subject or HTML preview can override a missing legal, recipient, partner or founder release gate.' };
}
module.exports = { evaluate, safeRef };
