import test from 'node:test';
import assert from 'node:assert/strict';
import {focusGiftSurface, providerConfirmedSignup, PILOT_RELEASE} from './consent_truth_gate.mjs';
const valid = () => ({provenance:'authenticated_provider_export',provider:'jetpack',subscriptionStatus:'confirmed',scope:'dispatch_newsletter',suppressed:false,unsubscribed:false,providerAttested:true,eventKey:'jetpack:synthetic_001'});
for (const [query,shown] of [['',false],['?subscribe=success',true],['?subscribe=anything',true],['?subscribe=invalid_email',false],['?subscribe=error',false],['?subscribe=blocked',false],['?subscribe=opted_out',false],['?subscribe=blocked_email',false]]) {
  test('FOCUS UI surface: '+(query||'empty'),()=>{const r=focusGiftSurface({search:query});assert.equal(r.giftVisible,shown);assert.equal(r.confirmedSignup,false);});
}
test('existing subscriber CSS class can expose gift without provider proof',()=>{let r=focusGiftSurface({className:'x is-subscriber y'});assert.equal(r.giftVisible,true);assert.equal(r.confirmedSignup,false);});
test('invalid CSS class not subscriber',()=>assert.equal(focusGiftSurface({className:'is-subscriberish'}).giftVisible,false));
test('synthetic provider witness models conditional eligibility only',()=>{const r=providerConfirmedSignup(valid());assert.equal(r.status,'ELIGIBLE_FOR_ONE_EVENT');assert.equal(r.eventName,'confirmed_signup');assert.match(r.caveat,/SYNTHETIC/);});
const invalid=[
  ['no provider record',null,'NO_PROVIDER_RECORD'],
  ['browser-only confirmation',{...valid(),provenance:'browser_redirect'},'UNAUTHENTICATED_PROVENANCE'],
  ['wrong provider',{...valid(),provider:'unknown'},'UNRECOGNIZED_PROVIDER'],
  ['unconfirmed',{...valid(),subscriptionStatus:'pending'},'NOT_CONFIRMED'],
  ['unrelated consent',{...valid(),scope:'download_only'},'WRONG_CONSENT_SCOPE'],
  ['suppressed',{...valid(),suppressed:true},'NOT_MAIL_ELIGIBLE'],
  ['opted out',{...valid(),unsubscribed:true},'NOT_MAIL_ELIGIBLE'],
  ['self-attested',{...valid(),providerAttested:false},'NO_PROVIDER_ATTESTATION'],
  ['email instead of opaque ID',{...valid(),eventKey:'foo@example.com'},'INVALID_OPAQUE_KEY'],
  ['PII field supplied',{...valid(),email:'private@example.com'},'PII_NOT_ACCEPTED'],
  ['too-short event key',{...valid(),eventKey:'tiny'},'INVALID_OPAQUE_KEY']
];
for (const [label,input,reason] of invalid) test('reject '+label,()=>{let r=providerConfirmedSignup(input);assert.equal(r.status,'HOLD');assert.equal(r.reason,reason);});
test('deduplicate by opaque event key',()=>{let v=valid();assert.equal(providerConfirmedSignup(v,[v.eventKey]).status,'NO_NEW_EVENT');});
test('reject non-array dedup context',()=>assert.equal(providerConfirmedSignup(valid(),new Set()).reason,'UNSAFE_DEDUP_CONTEXT'));
test('original 4:2 pilot and hard hold unchanged',()=>{assert.equal(PILOT_RELEASE.editorial.length,4);assert.equal(PILOT_RELEASE.commercial.length,2);assert.equal(PILOT_RELEASE.all,'HOLD_UNSENT');});
