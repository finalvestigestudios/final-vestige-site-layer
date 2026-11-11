/**
 * R286 review-only contract, NOT a production analytics implementation.
 * UI state (including query strings or Jetpack CSS) is never consent evidence.
 * Only a provider-authenticated positive subscription state can propose a lead.
 * Requires upstream access control, provenance and durable idempotency in production.
 */
const VERIFIED = 'provider-confirmed';
export function assessSignup(record, prior = new Set()) {
  const blockers = [];
  if (!record || typeof record !== 'object' || Array.isArray(record)) return { ok: false, blockers: ['missing_record'] };
  if (record.provenance !== VERIFIED) blockers.push('unverified_provenance');
  if (record.subscription !== 'active') blockers.push('not_active');
  if (record.emailPermission !== true) blockers.push('missing_email_permission');
  if (record.suppressed === true || record.unsubscribed === true) blockers.push('suppressed_or_unsubscribed');
  if (record.confirmedAt == null || !/^\d{4}-\d\d-\d\dT/.test(String(record.confirmedAt))) blockers.push('missing_confirmation_time');
  if (typeof record.opaqueSubscriptionId !== 'string' || !/^[a-zA-Z0-9_-]{8,90}$/.test(record.opaqueSubscriptionId)) blockers.push('invalid_opaque_subscription_id');
  if (typeof record.lifecycleId !== 'string' || !/^[a-zA-Z0-9_-]{8,90}$/.test(record.lifecycleId)) blockers.push('invalid_lifecycle_id');
  if ('email' in record || 'ip' in record || 'fullName' in record || 'phone' in record) blockers.push('pii_in_analytics_candidate');
  if (record.clientSuccess === true || record.urlSubscribe != null || record.jetpackCssClass != null || record.pdfDownloaded != null) blockers.push('client_ui_not_provider_evidence');
  const key = typeof record.opaqueSubscriptionId === 'string' && typeof record.lifecycleId === 'string' ? record.opaqueSubscriptionId + ':' + record.lifecycleId : '';
  if (prior.has(key)) blockers.push('already_recorded');
  if (blockers.length) return { ok: false, blockers };
  return { ok: true, event: 'confirmed_signup', dedupeKey: key };
}

export function assessPaidConversion(record) {
  const blockers = [];
  if (!record || typeof record !== 'object') return { ok: false, blockers: ['missing_order'] };
  if (record.source !== 'authenticated_merchant_settlement' && record.source !== 'authenticated_owned_order') blockers.push('no_independent_order_evidence');
  if (record.status !== 'settled') blockers.push('not_settled');
  if (record.orderId == null || !/^[a-zA-Z0-9_-]{8,90}$/.test(String(record.orderId))) blockers.push('missing_order_id');
  if (![record.grossCents,record.refundCents,record.feeCents].every(n=>Number.isSafeInteger(n)&&n>=0)) blockers.push('invalid_financial_fields');
  if (record.affiliateClick === true && record.source !== 'authenticated_merchant_settlement') blockers.push('click_not_sale');
  if (blockers.length) return { ok: false, blockers };
  const netCents = record.grossCents - record.refundCents - record.feeCents;
  if (netCents < 0) return { ok: false, blockers: ['negative_net_needs_reconciliation'] };
  return { ok: true, netCents };
}
