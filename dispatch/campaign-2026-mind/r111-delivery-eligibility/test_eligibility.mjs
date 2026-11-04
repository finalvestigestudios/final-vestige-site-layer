import test from 'node:test';
import assert from 'node:assert/strict';
import { reconcileNewsletter, evidenceReadiness, publicConsentScorecard } from './eligibility.mjs';
import { evaluateConfirmedSignup, aggregateConfirmedSignups } from '../r110-confirmed-signup/confirmed_signup.mjs';
const sample = () => ({
  status:{origin:'connected_wordpress_jetpack_newsletter_status',
    as_of:'2026-11-04T10:34:01Z',subscribers:{total:2, confirmed:2, unconfirmed:2,suppressed:0}},
  followers:{origin:'connected_wordpress_follower_summary',wordpress:2,email:0}
});
test('live 2 / 2 / 2 is not a fabricated four people', ()=>{
 const r=reconcileNewsletter(sample());
 assert.equal(r.newsletter_total,2);assert.equal(r.pending_unconfirmed,2);
 assert.equal(r.additive_subscriber_total,null);assert.equal(r.email_eligible_recipients,null);
 assert.equal(r.ready_to_send,false);assert.equal(r.followers.email_follower_summary,0);
});
test('no status is not evidence',()=>assert.equal(reconcileNewsletter().error,'no_authoritative_jetpack_snapshot'));
test('fake status origin rejected',()=>{const s=sample();s.status.origin='webpage_clicks';assert.ok(reconcileNewsletter(s).error);});
test('missing as-of rejected',()=>{const s=sample();s.status.as_of='yesterday';assert.ok(reconcileNewsletter(s).error);});
for(const field of ['total','confirmed','unconfirmed','suppressed']){
 test('invalid or absent '+field+' rejected',()=>{const s=sample();s.status.subscribers[field]=-1;assert.equal(reconcileNewsletter(s).eligibility,null);});
}
test('confirmed greater than total requires audit',()=>{const s=sample();s.status.subscribers.confirmed=5;assert.equal(reconcileNewsletter(s).error,'counts_require_native_review');});
test('suppressed greater than plausible population requires audit',()=>{const s=sample();s.status.subscribers.suppressed=20;assert.equal(reconcileNewsletter(s).error,'counts_require_native_review');});
test('follower summary not email eligibility',()=>{const s=sample();s.followers.email=100;const r=reconcileNewsletter(s);assert.equal(r.email_eligible_recipients,null);});
test('follower summary without authority omitted',()=>{const s=sample();s.followers.origin='anonymous';assert.equal(reconcileNewsletter(s).followers,null);});
test('unknown follower summary cannot block separate counts',()=>{const s=sample();delete s.followers;assert.equal(reconcileNewsletter(s).newsletter_total,2);});
test('never mark delivery from saved welcome setting',()=>assert.equal(reconcileNewsletter(sample()).welcome_delivered,null));
test('no evidence has all gates missing',()=>{const r=evidenceReadiness([]);assert.equal(r.missing_proof_kinds.length,8);assert.equal(r.sending_authorized,false);});
test('false proof cannot enable campaign',()=>{const r=evidenceReadiness([{proof_kind:'publisher_postal_address_approved',verified:true,evidence_ref:'bogus',source:'guess'}]);assert.equal(r.missing_proof_kinds.length,8);});
test('raw email evidence reference rejected',()=>{const r=evidenceReadiness([{proof_kind:'publisher_postal_address_approved',verified:true,evidence_ref:'person@example.com',source:'independent_authorized_review'}]);assert.equal(r.reviewed_proof_kinds.length,0);});
test('one properly scoped proof does not bypass other proofs',()=>{const r=evidenceReadiness([{proof_kind:'publisher_postal_address_approved',verified:true,evidence_ref:'evidence_postal_001',source:'independent_authorized_review'}]);assert.equal(r.reviewed_proof_kinds.length,1);assert.equal(r.sending_authorized,false);});
test('duplicates count once',()=>{const x={proof_kind:'publisher_postal_address_approved',verified:true,evidence_ref:'evidence_postal_001',source:'independent_authorized_review'};assert.equal(evidenceReadiness([x,x]).reviewed_proof_kinds.length,1);});
test('all synthetic attestations still fail closed; NOT authorization',()=>{const kinds=['existing_authorized_received_welcome_mime','first_party_pdf_open_verified','actual_received_commercial_footer','actual_received_unsubscribe_and_suppression','publisher_postal_address_approved','named_partner_email_channel_permission','approved_first_party_offer_guide','founder_exact_campaign_approval'];const r=evidenceReadiness(kinds.map(k=>({proof_kind:k,verified:true,evidence_ref:'evidence_test_123456',source:'independent_authorized_review'})));assert.equal(r.missing_proof_kinds.length,0);assert.equal(r.sending_authorized,false);});
test('any non-array proof invalid',()=>assert.throws(()=>evidenceReadiness({}),TypeError));
test('small cohort hides all identified leads',()=>{const r=publicConsentScorecard({confirmed_signup_events:2,attributable_opt_ins:1},2);assert.equal(r.status,'SMALL_COHORT_SUPPRESSED');assert.equal(r.confirmed_signups,null);});
test('threshold boundary 19 suppressed',()=>assert.equal(publicConsentScorecard({confirmed_signup_events:19,attributable_opt_ins:3},19).confirmed_signups,null));
test('threshold boundary 20 may show counts, still no orders',()=>{const r=publicConsentScorecard({confirmed_signup_events:20,attributable_opt_ins:3},20);assert.equal(r.confirmed_signups,20);assert.equal(r.orders,null);});
test('configured values cannot masquerade as paid orders',()=>{const r=publicConsentScorecard({confirmed_signup_events:21,attributable_opt_ins:6,orders:33,net_revenue:8000},22);assert.equal(r.orders,null);assert.equal(r.net_revenue,null);});
test('negative lead count rejected',()=>assert.equal(publicConsentScorecard({confirmed_signup_events:-1,attributable_opt_ins:0},20).status,'INVALID_OR_UNVERIFIED'));
test('attributable cannot exceed confirmed',()=>assert.equal(publicConsentScorecard({confirmed_signup_events:2,attributable_opt_ins:3},20).status,'INVALID_OR_UNVERIFIED'));
test('invalid k cannot expose tiny cohort',()=>assert.equal(publicConsentScorecard({confirmed_signup_events:2,attributable_opt_ins:1},2,2).status,'INVALID_OR_UNVERIFIED'));
test('R110 opt-in can be confirmed while reachability is UNKNOWN',()=>{
const proof={previous:{email_subscription:'not_confirmed'},current:{email_subscription:'subscribed',source:'native_jetpack_subscriber_filter'},consent:{kind:'explicit_site_newsletter_signup',site:'finalvestige.com',recorded_at:'2026-11-04T09:00:00Z',active:true},proof:{source:'native_jetpack_subscription_event',subscriber_digest:'h:'+'a'.repeat(64),event_ref:'optin_001',method:'clicked_confirmation_link'}};
const r=evaluateConfirmedSignup(proof);assert.equal(r.reason,'confirmed_platform_opt_in');assert.equal(r.reachable,null);
const a=aggregateConfirmedSignups([proof]);assert.equal(a.confirmed_signup_events,1);assert.equal(a.email_reachable_subscriber_count,null);
});
