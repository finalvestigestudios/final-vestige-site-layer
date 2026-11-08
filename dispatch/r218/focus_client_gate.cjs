'use strict';
// Offline representation of the exact gift-visibility conditions observed in
// WordPress page 1579 on 2026-11-08. Never emits analytics or email.
const BAD = new Set(['invalid_email','error','blocked_email','opted_out','blocked']);
function liveGiftVisible({subscribeQuery=null, containerClasses=''}={}) {
  const queryTriggered = typeof subscribeQuery === 'string' &&
    subscribeQuery.length > 0 && !BAD.has(subscribeQuery);
  const classTriggered = /\bis-subscriber\b/.test(String(containerClasses));
  return queryTriggered || classTriggered;
}
function interpretBrowserState(input={}) {
  const visible = liveGiftVisible(input);
  return Object.freeze({
    giftVisibleInBrowser: visible,
    confirmedSignup: null,
    providerProof: 'NOT_OBSERVED',
    analyticsInstruction: 'DO_NOT_EMIT_CONFIRMED_SIGNUP',
    note: 'Gift visibility is client-side presentation, not proof of double opt-in.'
  });
}
function classifyProviderRecord(record) {
  // This only checks shape. Authentication and provenance must be independently
  // established by the authorized provider connector; this is not a signature check.
  if (!record || record.provider !== 'jetpack' ||
      record.record_type !== 'subscription_confirmation' ||
      record.status !== 'confirmed' ||
      !/^[-a-zA-Z0-9_:]{8,128}$/.test(String(record.provider_event_id || '')) ||
      !/^[0-9a-f]{64}$/.test(String(record.anonymous_subject_digest || '')) ||
      record.source_verified !== true) return 'INSUFFICIENT_PROVIDER_EVIDENCE';
  return 'STRUCTURALLY_ELIGIBLE_AWAIT_AUTHENTICATED_PROVENANCE';
}
function dedupeConfirmedEvents(records) {
  const seen = new Set();
  let structurallyEligible = 0, duplicates = 0, rejected = 0;
  for (const r of records) {
    if (classifyProviderRecord(r) !== 'STRUCTURALLY_ELIGIBLE_AWAIT_AUTHENTICATED_PROVENANCE') {rejected++; continue;}
    const id = r.provider + ':' + r.provider_event_id;
    if (seen.has(id)) { duplicates++; continue; }
    seen.add(id); structurallyEligible++;
  }
  return Object.freeze({structurallyEligible,duplicates,rejected,
    confirmedLeads: null, reason:'Connector authenticity and recipient email eligibility not established.'});
}
function releaseStatus() { return Object.freeze({allSix:'HOLD_UNSENT',commercial03And05:'HOLD_MERCHANT',
  authorizedToPublish:false, authorizedToSend:false, mailListMutation:false}); }
module.exports = {BAD, liveGiftVisible, interpretBrowserState, classifyProviderRecord,
  dedupeConfirmedEvents, releaseStatus};
