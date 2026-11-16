/** R398: source-only consent QA. NOT connected to WordPress or a production collector. */
export const SITE_SIGNALS = Object.freeze(['subscribe_query', 'gift_visible', 'pdf_click', 'wordpress_reader_class', 'confirmation_email_seen']);
export const PROVIDER_OK = 'subscribed';

/** Public page interactions never verify a unique opted-in receiving inbox. */
export function classifyPageSignal(input = {}) {
  const observed = SITE_SIGNALS.filter((k) => Boolean(input[k]));
  return Object.freeze({event: null, confirmed_signup: false, status: 'NOT_CONFIRMED', observed, reason: 'Browser and download indicators are not authenticated Jetpack email eligibility records.'});
}

/**
 * Reviewer acceptance contract, NOT authentication. The only permitted caller is
 * a server-side adapter that has ALREADY authenticated a fresh Jetpack read.
 * source_verified must never be assigned from query params/client input.
 * Idempotent insert must be enforced durably by the owner analytics backend.
 */
export function evaluateProviderRead(proof = {}) {
  const failures = [];
  if (proof.source !== 'authenticated_jetpack_subscriber_read' || proof.source_verified !== true) failures.push('provider_authentication');
  if (proof.email_status !== PROVIDER_OK) failures.push('not_email_subscribed');
  if (proof.consent_scope !== 'dispatch_newsletter') failures.push('consent_scope');
  if (proof.email_delivery_preference !== 'on') failures.push('delivery_preference');
  if (typeof proof.opaque_provider_id !== 'string' || !/^[A-Za-z0-9_-]{8,128}$/.test(proof.opaque_provider_id)) failures.push('opaque_provider_id');
  if (typeof proof.confirmed_at !== 'string' || !Number.isFinite(Date.parse(proof.confirmed_at))) failures.push('confirmed_at');
  if (typeof proof.proof_ref !== 'string' || !/^[A-Za-z0-9_:\\/-]{8,160}$/.test(proof.proof_ref)) failures.push('private_proof_ref');
  if (proof.already_emitted === true) failures.push('deduplicated');
  if (proof.is_bounced === true || proof.email_paused === true || proof.is_suppressed === true) failures.push('email_ineligible');
  return Object.freeze({status: failures.length ? 'HOLD' : 'PROVIDER_PROOF_CANDIDATE', event: failures.length ? null : 'confirmed_signup_v1', failures, requires: 'transactional durable unique key and independently validated provider adapter before production'});
}

/** A frontend query string cannot provide partner EMAIL or product rights. */
export function evaluateCommercialRelease(p = {}) {
  const required = [
    'founder_campaign_approval', 'authorized_eligible_recipients', 'native_preview_inspected',
    'fv_physical_address_verified', 'functional_unsubscribe_verified', 'partner_fv_acceptance',
    'sku_scope_approved', 'merchant_email_permission', 'merchant_link_issued',
    'approved_guide_published', 'current_checkout_terms_verified', 'claims_disclosure_approved'
  ];
  const missing = required.filter((k) => p[k] !== true);
  if (p.has_live_vendor_url !== false) missing.push('premature_vendor_url');
  return Object.freeze({status: 'HOLD', ready_for_human_review_only: missing.length === 0, missing, can_send: false});
}
