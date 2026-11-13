'use strict';
const assert = require('node:assert/strict');
const {test} = require('node:test');
const {countConfirmedSignup, classifyVisitorSignal, merchantRelease, netPerThousand} = require('./gate.cjs');
const valid = (o={}) => Object.assign({
  origin:'authenticated_jetpack_provider', site:'finalvestige.com',
  event_id:'event_identity_1234567', subscriber_key:'opaque_identity_1234567',
  observed_at:'2026-11-13T06:00:00Z', dispatch_consent:true,
  email_eligible:true, new_site_enrollment:true, was_preexisting:false,
  suppressed:false, route:'confirmed_email_link'
},o);
test('missing provider records are unknown, not zero',()=>assert.equal(countConfirmedSignup(null).count,null));
test('email confirmation qualifies only as synthetic candidate',()=>assert.equal(countConfirmedSignup([valid()]).count,1));
test('existing WordPress.com account can immediately enroll',()=>assert.equal(countConfirmedSignup([valid({route:'wpcom_immediate_active'})]).count,1));
test('preexisting follower is not new',()=>assert.equal(countConfirmedSignup([valid({was_preexisting:true})]).count,0));
test('Reader-only follow not qualified',()=>assert.equal(countConfirmedSignup([valid({route:'reader_follow'})]).count,0));
test('no consent not qualified',()=>assert.equal(countConfirmedSignup([valid({dispatch_consent:false})]).count,0));
test('not email eligible',()=>assert.equal(countConfirmedSignup([valid({email_eligible:false})]).count,0));
test('suppressed recipient refused',()=>assert.equal(countConfirmedSignup([valid({suppressed:true})]).count,0));
test('untrusted origin refused',()=>assert.equal(countConfirmedSignup([valid({origin:'browser'})]).count,0));
test('wrong Jetpack site refused',()=>assert.equal(countConfirmedSignup([valid({site:'merchant.com'})]).count,0));
test('missing event ID refused',()=>assert.equal(countConfirmedSignup([valid({event_id:''})]).count,0));
test('missing identity refused',()=>assert.equal(countConfirmedSignup([valid({subscriber_key:''})]).count,0));
test('invalid timestamp refused',()=>assert.equal(countConfirmedSignup([valid({observed_at:'not-a-date'})]).count,0));
test('duplicate event refused',()=>assert.equal(countConfirmedSignup([valid(),valid()]).count,1));
test('duplicate subscriber across methods refused',()=>assert.equal(countConfirmedSignup([valid(),valid({route:'wpcom_immediate_active',event_id:'second_event_123456'})]).count,1));
test('distinct confirmed identities count separately',()=>assert.equal(countConfirmedSignup([valid(),valid({event_id:'another_event_123456',subscriber_key:'different_identity_123456'})]).count,2));
test('Zen12 separate newsletter cannot count as FV lead',()=>assert.equal(classifyVisitorSignal({origin:'zen12.com',kind:'newsletter_signup'}),'MERCHANT_SEPARATE_LIST'));
test('free seller MP3 access cannot count as FV lead',()=>assert.equal(classifyVisitorSignal({origin:'zen12.com',kind:'download'}),'MERCHANT_SEPARATE_LIST'));
test('Focus download is not consent',()=>assert.equal(classifyVisitorSignal({kind:'download'}),'NOT_CONFIRMED'));
test('subscribe URL is not consent',()=>assert.equal(classifyVisitorSignal({kind:'query_parameter'}),'NOT_CONFIRMED'));
test('Reader follow is not email eligible',()=>assert.equal(classifyVisitorSignal({kind:'reader_follow'}),'NOT_EMAIL_ELIGIBILITY'));
test('provider candidate is not claimed as live count',()=>assert.equal(classifyVisitorSignal(valid()),'FV_CONFIRMED_CANDIDATE_ONLY'));
test('all merchant attestations false is HOLD',()=>assert.equal(merchantRelease({}).merchant_state,'HOLD_MERCHANT'));
test('ten merchant gates required',()=>assert.equal(merchantRelease({}).missing.length,10));
test('unattributed booleans do not satisfy gates',()=>assert.equal(merchantRelease({account_approved:true}).missing.length,10));
test('verified without evidence does not satisfy',()=>assert.equal(merchantRelease({account_approved:{verified:true,independent_reviewer:true}}).missing.length,10));
test('release stays HOLD_UNSENT even if hypothetical gates provided',()=>{
  const ok={verified:true,evidence_ref:'provider_record_123456',independent_reviewer:true};
  const all=Object.fromEntries(merchantRelease({}).missing.map(k=>[k,ok]));
  assert.equal(merchantRelease(all).state,'HOLD_UNSENT');
});
test('no unverified revenue denominator',()=>assert.equal(netPerThousand(null),null));
test('no fabricated zero on missing source proof',()=>assert.equal(netPerThousand({qualified_human_sessions:100,settled_gross:50,refunds:5,fees:2}),null));
test('zero denominator undefined',()=>assert.equal(netPerThousand({reconciled:true,sessions_origin_verified:true,settlements_origin_verified:true,qualified_human_sessions:0,settled_gross:0,refunds:0,fees:0}),null));
test('legitimately reconciled net per 1000',()=>assert.equal(netPerThousand({reconciled:true,sessions_origin_verified:true,settlements_origin_verified:true,qualified_human_sessions:250,settled_gross:80,refunds:10,fees:5}),260));
test('impossible refunds fail closed',()=>assert.equal(netPerThousand({reconciled:true,sessions_origin_verified:true,settlements_origin_verified:true,qualified_human_sessions:250,settled_gross:80,refunds:100,fees:5}),null));
