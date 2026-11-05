'use strict';
/** Run: node --test experience2/apollo-creator-bridge/test_r129_creator_route_gate.cjs */
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {auditRoute,ALLOWED_EXTERNAL}=require('./r129_creator_route_gate.cjs');
const {audit}=require('./r127_source_role_crosswalk.cjs');
const apollo=fs.readFileSync(path.join(__dirname,'landing-preview.html'),'utf8');
function rejected(original,replacement,expected){
  const changed=apollo.replace(original,replacement);
  assert.notEqual(changed,apollo,'mutation must affect actual Apollo source');
  const result=auditRoute(changed);
  assert.equal(result.status,'FAIL');
  assert.ok(result.errors.some(e=>e.startsWith(expected)),JSON.stringify(result.errors));
}
test('exact Apollo staging source passes route/preflight, never merchant clearance',()=>{
  const report=auditRoute(apollo);
  assert.equal(report.status,'PASS',JSON.stringify(report.errors));
  assert.equal(report.link_count,36);
  assert.equal(report.nasa_link_count,22);
  assert.equal(report.external_link_count,23);
  assert.equal(report.primary_cta_count,1);
  assert.equal(report.commerce_status,'NO_VERIFIED_PAID_OFFER_OR_MERCHANT');
  assert.equal(report.attribution_status,'UNOBSERVABLE_NOT_A_SALE');
  assert.equal(ALLOWED_EXTERNAL.length,11);
});
test('unreviewed checkout cannot silently replace a source section',()=>rejected('href="#findings"','href="https://payhip.com/fake-checkout"','UNREVIEWED_LINK_'));
test('nonexistent section targets are not qualified engagement',()=>rejected('href="#findings"','href="#never-present"','BROKEN_FRAGMENT_'));
test('hidden classroom destination fails no-JS gate',()=>rejected('id="classroom-preview" tabindex','id="classroom-preview" hidden tabindex','NO_JS_CLASSROOM_DESTINATION_INVALID'));
test('a second primary CTA cannot be introduced accidentally',()=>rejected('</header>\n  <nav','<a href="#classroom-preview" data-fv-primary-cta>extra</a></header>\n  <nav','PRIMARY_CLASSROOM_ACTION_INVALID'));
test('unreviewed affiliate destination is rejected',()=>rejected('href="#findings"','href="https://aff.example/?tag=x"','UNREVIEWED_LINK_'));
test('invented on-domain paid route is rejected too',()=>rejected('href="#findings"','href="https://finalvestige.com/checkout/unverified"','UNREVIEWED_LINK_'));
test('javascript URL cannot masquerade as a legitimate action',()=>rejected('href="#findings"','href="javascript:alert(1)"','UNREVIEWED_LINK_'));
test('unapproved image binary fails even if sourced',()=>rejected('</main>','<img src="/nasa-uncleared.jpg"></main>','UNREVIEWED_MEDIA_OR_DATA_COLLECTION'));
test('a signup form requires separate owner approval',()=>rejected('</main>','<form><input type="email"></form></main>','UNREVIEWED_MEDIA_OR_DATA_COLLECTION'));
test('external analytics script fails pending review',()=>rejected('</head>','<script src="https://analytics.example/t.js"></script></head>','UNREVIEWED_EXTERNAL_ASSET'));
test('unexpected visitor storage fails',()=>rejected('</script>','localStorage.setItem("x","1");</script>','UNREVIEWED_TRACKING_OR_STORAGE'));
test('inline click handler requires review',()=>rejected('href="#findings"','href="#findings" onclick="spy()"','INLINE_LINK_HANDLER_'));
test('NASA source anchor must protect the referrer',()=>rejected('rel="noreferrer noopener">NASA crew training portrait','rel="noopener">NASA crew training portrait','NASA_REFERRER_PROTECTION_'));
test('student photo index cannot disappear',()=>rejected('data-fv-student-photo-index','data-fv-photo-index-gone','WORKSHEET_INTEGRITY_UNPROVEN'));
test('staging must remain noindexed',()=>rejected('content="noindex,nofollow"','content="index,follow"','STAGING_INDEX_BLOCK_REMOVED'));
test('Research Desk crosswalk propagates route violations without declaring a sale',()=>{
  const changed=apollo.replace('href="#findings"','href="https://payhip.com/unapproved"');
  const report=audit(changed,'<section>unreviewed Research Desk fixture</section>');
  assert.ok(report.integrity_errors.some(e=>e.startsWith('CREATOR_ROUTE_UNREVIEWED_LINK_')));
  assert.equal(report.release_status,'STAGING_HOLD');
  assert.equal(report.claims.merchant_paid_orders,'UNOBSERVABLE');
});
