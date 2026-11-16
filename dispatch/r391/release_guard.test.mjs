import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {inspectIssue05} from './release_guard.mjs';
const source = (path) => readFileSync(new URL(path, import.meta.url), 'utf8');
const base = {
  manifest:JSON.parse(source('../campaign-2026-mind/manifest.json')),
  evidence:JSON.parse(source('./CLAIM_PERMISSION_AND_PRICE_MATRIX.json')),
  html:source('./ISSUE05_TOTAL_FOCUS_OFFLINE.html'),
  plaintext:source('./ISSUE05_TOTAL_FOCUS_OFFLINE.txt')
};
const run = (patch={}) => inspectIssue05({...base,...patch});
const corrupt = (k, value) => run({[k]:value});
test('all source gates pass but release remains HOLD',()=>{
  const r=run(); assert.equal(r.passed,r.total,r.failures.join(','));
  assert.equal(r.release,'HOLD_UNSENT_NO_AUTOMATIC_OVERRIDE');
  assert.ok(r.total >= 15);
});
test('4 editorial, 2 commercial original issues are immutable',()=>assert.ok(run().checks.masterSixDrafts));
test('no original merchant URL is activated',()=>assert.ok(run().checks.originalUnmodified));
test('specific SKU issue allocation retained',()=>assert.ok(run().checks.issuerIs05));
test('named partner evidence remains explicitly false',()=>assert.ok(run().checks.permissionsAllUnverified));
test('unknown recipient count does not become a lead',()=>assert.ok(run().checks.actualSubscriberEligibilityNotAssumed));
test('one inert offer guide CTA is visibly blocked',()=>assert.ok(run().checks.oneDisabledPrimaryCta));
test('no hidden affiliate/UTM destination',()=>assert.ok(run().checks.noExposedAffiliateUrl));
test('commission disclosure sits by the disabled offer',()=>assert.ok(run().checks.proximateDisclosure));
test('seller claims are not upgraded to evidence',()=>assert.ok(run().checks.claimBoundaries));
test('historical, medical and merchant sources provided in both formats',()=>assert.ok(run().checks.directSources));
test('offline cannot impersonate actual inbox rendering',()=>assert.ok(run().checks.deliveryUnverifiedVisible));
test('address stays an explicit blocking placeholder',()=>assert.ok(run().checks.postalStillBlocked));
test('opt-out stays an explicit blocking placeholder',()=>assert.ok(run().checks.unsubscribeStillBlocked));
test('no tracking pixel, script or form',()=>assert.ok(run().checks.noActiveTrackingOrForm));
test('seller claims and general hypnosis research remain separate',()=>assert.ok(run().checks.sellerVsGeneralStudy));
test('no fixed checkout price in email',()=>assert.ok(run().checks.noOfferPriceInEmail));
test('unsafe real affiliate href fails',()=>{
 const html=base.html.replace('data-primary-cta="disabled"','data-primary-cta="disabled" href="https://example.com/?affiliate_id=123"');
 assert.equal(corrupt('html',html).checks.noExposedAffiliateUrl,false);
});
test('unsafe enabled CTA fails',()=>{
 const html=base.html.replace('data-primary-cta="disabled" aria-disabled="true"','data-primary-cta="enabled"');
 assert.equal(corrupt('html',html).checks.oneDisabledPrimaryCta,false);
});
test('unsafe deleted disclosure fails',()=>{
 const html=base.html.replace(/<p style="font-size:14px"><strong>Commercial disclosure[\s\S]*?<\/p>/,'');
 assert.equal(corrupt('html',html).checks.proximateDisclosure,false);
});
test('unsafe form or pixel fails',()=>{
 const html=base.html.replace('</body>','<img src="https://tracker.invalid/pixel"></body>');
 assert.equal(corrupt('html',html).checks.noActiveTrackingOrForm,false);
});
test('unsafe fabricated eligible inbox count fails',()=>{
 const e=structuredClone(base.evidence);
 e.last_authenticated_jetpack_snapshot.eligible_receiving_inboxes=3;
 assert.equal(corrupt('evidence',e).checks.actualSubscriberEligibilityNotAssumed,false);
});
test('unsafe merchant-permission assertion fails',()=>{
 const e=structuredClone(base.evidence);e.permissions.email_channel_authorized=true;
 assert.equal(corrupt('evidence',e).checks.permissionsAllUnverified,false);
});
test('unsafe remove postal block fails',()=>{
 const h=base.html.replace('[[VALID_POSTAL_ADDRESS_REQUIRED]]','address redacted');
 assert.equal(corrupt('html',h).checks.postalStillBlocked,false);
});
test('unsafe invented price fails',()=>{
 const h=base.html.replace('The seller currently','Only $15 today! The seller currently');
 assert.equal(corrupt('html',h).checks.noOfferPriceInEmail,false);
});
test('unsafe false preheader verification fails',()=>{
 const p=base.plaintext.replace('NOT VERIFIED IN JETPACK','VERIFIED IN JETPACK');
 assert.equal(corrupt('plaintext',p).checks.deliveryUnverifiedVisible,false);
});
test('unsafe unverified launch stage still cannot release',()=>{
 const e=structuredClone(base.evidence);
 Object.keys(e.permissions).forEach(k=>e.permissions[k]=true);
 assert.equal(corrupt('evidence',e).release,'HOLD_UNSENT_NO_AUTOMATIC_OVERRIDE');
});
