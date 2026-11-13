'use strict';
// Source-only advisory; never calls WordPress, subscribers, an email API or an earning URL.
const ID = 'fv-dispatch-mind-launch-2026-10-30';
const EDITORIAL = new Set([1, 2, 4, 6]);
const COMMERCIAL = new Set([3, 5]);
const GATES = ['final_campaign_approval','affiliate_permission_verified','first_party_guides_live_verified','confirmed_eligible_recipients_verified','postal_address_verified','unsubscribe_received_tested','recipient_welcome_received_verified','settled_sale_evidence_verified'];
function review(master, ledger) {
  const problems = [], improvements = [], limitations = [];
  const issues = Array.isArray(master?.issues) ? master.issues : [];
  const rows = Array.isArray(ledger?.issues) ? ledger.issues : [];
  if (master?.id !== ID) problems.push('original_master_identity_invalid');
  if (ledger?.original_master_sha !== 'd57ccdba3aee8f065e143e101c2945f4f3d01647') problems.push('original_commit_identity_invalid');
  if (master?.status !== 'DRAFT_UNSENT_NO_SCHEDULING') problems.push('master_not_draft_unsent');
  if (issues.length !== 6 || rows.length !== 6) problems.push('campaign_must_have_six');
  if (master?.mix?.editorial !== 4 || master?.mix?.commercial_review_pending !== 2) problems.push('original_mix_must_be_four_two');
  const seen = new Set();
  for (const issue of issues) {
    if (!Number.isInteger(issue?.number) || seen.has(issue.number) || !EDITORIAL.has(issue.number) && !COMMERCIAL.has(issue.number)) {
      problems.push('duplicate_or_unexpected_issue'); continue;
    }
    seen.add(issue.number);
    const row = rows.find(r => r?.number === issue.number);
    if (!row) { problems.push('missing_decision_row_'+issue.number); continue; }
    const kind = EDITORIAL.has(issue.number) ? 'editorial' : 'commercial-review-pending';
    if (issue.kind !== kind || row.kind !== kind) problems.push('allocation_drift_'+issue.number);
    if (issue.subject !== row.subject || issue.editorial_cta !== row.original_cta) problems.push('source_drift_'+issue.number);
    if (issue.publish_state !== 'hold') problems.push('active_publication_'+issue.number);
    if (issue.merchant_affiliate_url != null) problems.push('unexpected_merchant_link_'+issue.number);
    if (row.alternative_status !== 'NOT_ADOPTED') problems.push('unapproved_alternative_'+issue.number);
    if (COMMERCIAL.has(issue.number)) {
      if (!/^\[\[APPROVED_[A-Z0-9_]+_URL_REQUIRED\]\]$/.test(issue.editorial_cta || '')) problems.push('offer_guide_not_safely_placeholder_'+issue.number);
      if (row.issue_state !== 'HOLD_MERCHANT') problems.push('merchant_hold_missing_'+issue.number);
    } else {
      if (!/^https:\/\/finalvestige\.com\//.test(issue.editorial_cta || '')) problems.push('editorial_cta_not_first_party_'+issue.number);
      if (row.issue_state !== 'HOLD_UNSENT') problems.push('editorial_hold_missing_'+issue.number);
    }
  }
  if (seen.size !== 6) problems.push('missing_or_duplicate_issue_numbers');
  if (issues.find(i=>i.number===1)?.editorial_cta === issues.find(i=>i.number===2)?.editorial_cta) improvements.push('01_02_same_destination');
  if (issues.find(i=>i.number===6)?.editorial_cta === 'https://finalvestige.com/focus/') improvements.push('06_repeats_acquisition_cta');
  if (/Fourteen seconds/.test(issues.find(i=>i.number===4)?.subject || '')) improvements.push('04_define_clock_endpoints_before_subject');
  if (issues.find(i=>i.number===5)?.subject === 'Before you press play on a hypnosis audio') improvements.push('05_identify_specific_total_focus_offer');
  const policy = ledger?.policy || {};
  if (policy.send_allowed !== false || policy.auto_email_new_posts !== false) problems.push('send_flag_not_explicit_hold');
  for (const gate of GATES) if (policy[gate] !== false) problems.push('unattested_or_unsafe_flag_'+gate);
  const audience = ledger?.audience || {};
  if (audience.eligible_recipients !== null || audience.welcome_delivered !== null || audience.confirmed_new_signups_attributed !== null) problems.push('fabricated_recipient_truth');
  if (Number.isFinite(audience.newsletter_total) && Number.isFinite(audience.newsletter_confirmed) && Number.isFinite(audience.newsletter_unconfirmed) && audience.newsletter_confirmed+audience.newsletter_unconfirmed>audience.newsletter_total) limitations.push('newsletter_status_counts_overlap');
  if (audience.followers_email === 0 && audience.followers_wpcom === 3) limitations.push('follower_channels_do_not_establish_eligible_recipients');
  if (ledger?.realized_net_revenue_per_1000_qualified_sessions !== null) problems.push('fabricated_revenue_metric');
  return Object.freeze({
    release_status:'HOLD_UNSENT', send_allowed:false,
    editorial_slots:4, commercial_slots:2,
    independently_verified_eligible_audience:null,
    realized_net_revenue_per_1000_qualified_sessions:null,
    problems:[...new Set(problems)], improvements, limitations,
    next_decision:problems.length ? 'REPAIR_SOURCE_OR_UNVERIFIED_DATA' : 'FOUNDER_EDITORIAL_SELECTION_THEN_SEPARATE_REAL_WORLD_ATTESTATION'
  });
}
module.exports = { review, GATES };
