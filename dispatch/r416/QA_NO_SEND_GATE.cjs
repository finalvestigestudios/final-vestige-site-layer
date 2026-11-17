/* R416 no-send ledger conformance. Pure JS core; no network, sending, or site reads.
   Run: node dispatch/r416/QA_NO_SEND_GATE.cjs dispatch/r416/SOURCE_OF_TRUTH_HARD_HOLD_LEDGER.json
   This tests a SOURCE SNAPSHOT and schema; it cannot authenticate merchant contracts,
   subscriber inboxes, Jetpack preview, legal address, or paid settlement. */
'use strict';
const fs = require('node:fs');
const assert = require('node:assert/strict');
const PARTNER_HOSTS = ['zen12.com', 'hypnosislive.com', 'affiliates.inspire3.com'];
const EXPECTED_SLOTS = ['01','02','03','04','05','06'];

function audit(d) {
  const fails = [];
  const req = (ok, code) => { if (!ok) fails.push(code); };
  const byIssue = (d.slots || []).map(x => x.issue);
  req(d.version === 'r416.1', 'snapshot_version');
  req(d.governance?.issue === 174 && d.governance?.master_draft_pr === 175 && d.governance?.readiness_pr === 201, 'source_provenance');
  req(d.governance?.all_unsent === true && d.governance?.all_adoption === false && d.governance?.founder_final_approval === false, 'founder_hold');
  req(d.governance?.homepage_frozen_pr === 49, 'homepage_boundary');
  req(EXPECTED_SLOTS.join(',') === byIssue.join(','), 'six_ordered_slots');
  req(d.slots?.filter(s => s.type === 'editorial').length === 4, 'four_editorial');
  req(d.slots?.filter(s => s.type === 'commercial').length === 2, 'two_commercial');
  req(d.live_wordpress?.new_post_email_default === false, 'auto_email_must_remain_off');
  req(d.live_wordpress?.reply_to === 'no-reply', 'source_reply_to_drift');
  req(d.live_wordpress?.unique_eligible_inboxes === null, 'no_invented_recipients');
  req(d.live_wordpress?.dashboard?.total === 3 && d.live_wordpress?.dashboard?.confirmed === 3 && d.live_wordpress?.dashboard?.unconfirmed === 2, 'dashboard_snapshot_drift');
  req(d.live_wordpress?.follower_channels?.wpcom_reader === 3 && d.live_wordpress?.follower_channels?.direct_email === 0, 'follower_snapshot_drift');
  req(d.live_wordpress?.last_five_notification_statuses?.length === 5 && d.live_wordpress.last_five_notification_statuses.every(s => s === 'never_sent_opted_out'), 'unsent_post_notices');
  req(d.live_wordpress?.real_welcome_receipt_verified === false, 'welcome_unverified');
  req(d.live_wordpress?.publication_promise_alignment === 'NEEDS_FOUNDER_REVIEW', 'promise_not_yet_reconciled');
  req(d.release_proofs && Object.keys(d.release_proofs).length >= 12 && Object.values(d.release_proofs).every(v => v === false), 'missing_external_proofs_must_hold');
  for (const s of d.slots || []) {
    req(s.adopted === false, 'unapproved_adoption_' + s.issue);
    req(typeof s.subject === 'string' && s.subject.length > 15 && s.subject.length < 85, 'subject_length_' + s.issue);
    req(/^[0-9a-f]{40}$/.test(s.candidate_sha || ''), 'pinned_sha_' + s.issue);
    req(/^HOLD_/.test(s.send_status || ''), 'hold_' + s.issue);
    if (s.type === 'commercial') {
      req(s.cta === null && s.offer_email_permission === false && s.send_status === 'HOLD_MERCHANT', 'commercial_link_or_permission_' + s.issue);
    } else {
      req(/^https:\/\/finalvestige\.com\//.test(s.cta || '') && s.source_status === 'published' && Number.isInteger(s.wp_id), 'verified_first_party_destination_' + s.issue);
      try { const u = new URL(s.cta); req(!u.search && !PARTNER_HOSTS.includes(u.hostname) && !u.hash, 'unapproved_tracking_or_redirect_' + s.issue); }
      catch { req(false, 'malformed_url_' + s.issue); }
    }
  }
  req(d.proposed_utm_contract?.active === false, 'unapproved_link_attribution');
  req(d.event_truth?.confirmed_signup?.requires?.includes('authenticated_provider_confirmation') && d.event_truth.confirmed_signup.requires.includes('email_eligible') && d.event_truth.confirmed_signup.excludes.includes('URL_success_parameter'), 'provider_truth');
  req(d.event_truth?.settled_order?.requires?.includes('authenticated_paid_transaction') && d.event_truth.settled_order.requires.includes('net_of_refunds_and_fees') && d.event_truth.settled_order.excludes.includes('clicks'), 'merchant_settlement_truth');
  req(d.cohorts?.computed === false && d.cohorts?.net_revenue_per_1000_qualified_sessions === null && d.cohorts?.qualified_human_sessions === null && d.cohorts?.net_revenue === null, 'no_fake_revenue');
  const serialized = JSON.stringify(d);
  req(!/\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b/i.test(serialized), 'no_subscriber_email_in_public_snapshot');
  req(!/(?:access_token|api_key|secret_key|subscriber_email)\s*":/i.test(serialized), 'no_credential_or_personal_field');
  return {status: 'HOLD_UNSENT',pass:fails.length===0,assertions:fails.length?null:'source_conformance',failures:fails};
}
function test(d) {
  const positive = audit(d);
  assert.equal(positive.pass, true, 'unmodified HOLD must pass snapshot conformance: ' + positive.failures.join(','));
  const cases = [
    ['send_release', x => { x.governance.all_unsent = false; }],
    ['founder_forged', x => { x.governance.founder_final_approval = true; }],
    ['adoption_forged', x => { x.governance.all_adoption = true; }],
    ['switch_on_auto_email', x => { x.live_wordpress.new_post_email_default = true; }],
    ['reader_as_recipients', x => { x.live_wordpress.unique_eligible_inboxes = 3; }],
    ['sum_confirmed_unconfirmed', x => { x.live_wordpress.dashboard.total = 5; }],
    ['assume_welcome', x => { x.live_wordpress.real_welcome_receipt_verified = true; }],
    ['subscriber_claim_aligned', x => { x.live_wordpress.publication_promise_alignment = 'VERIFIED'; }],
    ['fake_native_preview', x => { x.release_proofs.native_jetpack_email_preview = true; }],
    ['fake_valid_postal_address', x => { x.release_proofs.valid_fv_postal_address_rendered = true; }],
    ['fake_unsubscribe', x => { x.release_proofs.functional_unsubscribe_verified = true; }],
    ['fake_email_permission', x => { x.release_proofs.zen12_specific_email_permission = true; }],
    ['affiliate_link_active', x => { x.slots[2].cta = 'https://zen12.com/about'; }],
    ['affiliate_approved', x => { x.slots[4].offer_email_permission = true; }],
    ['wrong_issue_allocation', x => { x.slots[2].type = 'editorial'; }],
    ['one_missing_slot', x => { x.slots.pop(); }],
    ['unapproved_tracking', x => { x.slots[0].cta += '?utm_content=secret'; }],
    ['unapproved_merchant_redirect', x => { x.slots[0].cta = 'https://zen12.com/about'; }],
    ['forged_qualified_sessions', x => { x.cohorts.qualified_human_sessions = 100; }],
    ['forged_net_revenue', x => { x.cohorts.net_revenue = 7; }],
    ['fake_revenue_ratio', x => { x.cohorts.net_revenue_per_1000_qualified_sessions = 100; }],
    ['fake_signup_truth', x => { x.event_truth.confirmed_signup.requires = ['URL_success_parameter']; }],
    ['fake_sale_from_click', x => { x.event_truth.settled_order.requires = ['clicks']; }],
    ['pii_leak', x => { x.subscriber_email = 'do-not-publish@example.org'; }],
    ['token_leak', x => { x.access_token = 'DO-NOT-PUBLISH'; }]
  ];
  for (const [name, mutate] of cases) {
    const x = JSON.parse(JSON.stringify(d));
    mutate(x);
    assert.equal(audit(x).pass, false, 'tampering should fail: ' + name);
  }
  return {positive:1,negative:cases.length,total:cases.length+1,verdict:'PASS',note:'source-conformance only; no external proof or native Jetpack witnessing'};
}
if (require.main === module) {
  const path = process.argv[2]; if (!path) throw new Error('Pass local R416 ledger JSON path');
  const d = JSON.parse(fs.readFileSync(path,'utf8'));
  process.stdout.write(JSON.stringify(test(d), null, 2) + '\n');
}
module.exports = {audit,test};
