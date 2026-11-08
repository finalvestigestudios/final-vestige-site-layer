import { test } from 'node:test';
import assert from 'node:assert/strict';
import { evaluateConfirmedSignup, aggregateConfirmedSignups } from './confirmed_signup.mjs';

const digest = (c='a') => 'h:' + c.repeat(64);
const valid = () => ({
  previous: { email_subscription: 'not_confirmed' },
  current: { email_subscription: 'subscribed', source:'native_jetpack_subscriber_filter' },
  consent: { kind:'explicit_site_newsletter_signup', site:'finalvestige.com', recorded_at:'2026-11-04T09:00:00Z', active:true },
  proof: { source:'native_jetpack_subscription_event', subscriber_digest: digest(), event_ref:'optin_001', method:'clicked_confirmation_link' },
  attribution: { origin:'verified_first_party_landing', human_evidence:true, utm_source:'youtube', utm_medium:'organic_social', utm_campaign:'mind_pilot_2026_11', utm_content:'grokasset_001',landing_path:'/focus/' }
});
const check = (name, mutate, reason) => test(name, () => { const v = valid(); mutate(v); assert.equal(evaluateConfirmedSignup(v).reason, reason); });

test('confirmed email route emits one event with safe attribution', () => {
  const r=evaluateConfirmedSignup(valid()); assert.equal(r.event.type,'confirmed_signup'); assert.equal(r.reason,'confirmed_platform_opt_in'); assert.equal(r.event.attribution.utm_content,'grokasset_001');
});
test('preverified WordPress-account route needs no confirmation email', () => {
  const v=valid(); v.previous.email_subscription='none'; v.proof.method='account_preverified'; v.proof.identity_kind='wordpress_account';
  assert.ok(evaluateConfirmedSignup(v).event);
});
check('preverified without native account proof', v=>{v.previous.email_subscription='none';v.proof.method='account_preverified';},'preverified_transition_absent');
check('preverified when pending confirmation is not new', v=>{v.proof.method='account_preverified';v.proof.identity_kind='wordpress_account';},'preverified_transition_absent');
check('confirmation click without pending state', v=>{v.previous.email_subscription='none';},'confirmation_transition_absent');
check('existing confirmed user must not be counted again', v=>{v.previous.email_subscription='subscribed';},'confirmation_transition_absent');
check('reader only excluded', v=>{v.current.email_subscription='not_subscribed';},'email_ineligible');
check('bounce excluded', v=>{v.current.email_subscription='bounced';},'email_ineligible');
check('paused excluded', v=>{v.current.email_subscription='emails_paused';},'email_ineligible');
check('not sending excluded', v=>{v.current.email_subscription='not_sending';},'email_ineligible');
check('unconfirmed excluded', v=>{v.current.email_subscription='not_confirmed';},'email_ineligible');
check('suppressed excluded', v=>{v.current.suppressed=true;},'email_ineligible');
check('removed excluded', v=>{v.current.removed=true;},'email_ineligible');
check('no native status', v=>{v.current.source='sdk_button';},'not_authoritative');
check('no event proof', v=>{v.proof.source='cta_click';},'not_authoritative');
check('raw email cannot be used as subscriber key', v=>{v.proof.subscriber_digest='somebody@example.com';},'unsafe_or_absent_identity');
check('bad unbounded digest', v=>{v.proof.subscriber_digest='h:1234';},'unsafe_or_absent_identity');
check('missing event id', v=>{v.proof.event_ref='';},'missing_event_ref');
check('email address in event id blocked', v=>{v.proof.event_ref='person@example.com';},'missing_event_ref');
check('consent not active', v=>{v.consent.active=false;},'consent_not_proven');
check('consent route unrelated to newsletter', v=>{v.consent.kind='download';},'consent_not_proven');
check('site mismatch', v=>{v.consent.site='other.example';},'consent_not_proven');
check('missing timestamp', v=>{v.consent.recorded_at='no-date';},'consent_not_proven');
check('an import is not a new opt-in', v=>{v.proof.is_imported=true;},'not_a_new_opt_in');
check('admin-created is not consent', v=>{v.proof.is_admin_created=true;},'not_a_new_opt_in');
check('unknown subscriber status', v=>{v.current.email_subscription='magic';},'unknown_status');
check('missing input is fail-closed', v=>{delete v.proof;},'insufficient_evidence');
check('unknown proof method is fail-closed', v=>{v.proof.method='button_click';},'confirmation_method_unverified');

test('already seen identity cannot be counted twice', () => {const v=valid();const key=`finalvestige.com:${digest()}`;assert.equal(evaluateConfirmedSignup(v,new Set([key])).reason,'duplicate_confirmation');});
test('unproven attribution MUST yield null, never a guessed source',()=>{const v=valid();v.attribution.origin='inferred_from_views';const r=evaluateConfirmedSignup(v);assert.ok(r.event);assert.equal(r.event.attribution,null);});
test('privacy violation in UTM content makes attribution unknown but not consent',()=>{const v=valid();v.attribution.utm_content='person@example.com';assert.equal(evaluateConfirmedSignup(v).event.attribution,null);});
test('unrecognized platform cannot be attributed',()=>{const v=valid();v.attribution.utm_source='reddit';assert.equal(evaluateConfirmedSignup(v).event.attribution,null);});
test('wrong campaign label cannot be attributed',()=>{const v=valid();v.attribution.utm_campaign='fake';assert.equal(evaluateConfirmedSignup(v).event.attribution,null);});
test('unverified human traffic cannot be attributed',()=>{const v=valid();v.attribution.human_evidence=false;assert.equal(evaluateConfirmedSignup(v).event.attribution,null);});
test('unapproved landing path cannot be attributed',()=>{const v=valid();v.attribution.landing_path='/cart/';assert.equal(evaluateConfirmedSignup(v).event.attribution,null);});
test('aggregate dedupes and keeps sales/revenue null',()=>{
 const a=valid(),b=valid(),c=valid();b.proof.event_ref='optin_002';c.proof.subscriber_digest=digest('b');c.proof.event_ref='optin_003';c.attribution=null;
 const s=aggregateConfirmedSignups([a,b,c]);assert.equal(s.confirmed_signup_events,2);assert.equal(s.attributable_opt_ins,1);assert.equal(s.source_unknown_opt_ins,1);assert.equal(s.excluded_reasons.duplicate_confirmation,1);assert.equal(s.paid_orders,null);assert.equal(s.net_revenue_per_1000,null);
});
test('empty list is NOT a zero-sales claim',()=>{const s=aggregateConfirmedSignups([]);assert.equal(s.paid_orders,null);assert.equal(s.email_reachable_subscriber_count,null);});
test('aggregate rejects non-array',()=>assert.throws(()=>aggregateConfirmedSignups({}),TypeError));
