'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {audit,RECORDS}=require('./r132_research_desk_source_role_gate.cjs');
const source=fs.readFileSync(path.join(__dirname,'r132_research_desk_source_role_review.html'),'utf8');
const fail=(name,html,expected)=>test(name,()=>{
 const result=audit(html);
 assert.equal(result.status,'FAIL');
 assert.ok(result.errors.some(error=>error.startsWith(expected)),JSON.stringify(result.errors));
});
test('R132 exact candidate passes source/rights/route preflight but NEVER counts as LIVE',()=>{
 const result=audit(source);
 assert.equal(result.status,'PASS',JSON.stringify(result.errors));
 assert.equal(result.reviewed_records,6);
 assert.equal(result.photo_links,6);
 assert.equal(result.rights,'0_OF_6_CLEARED');
 assert.equal(result.release,'STAGING_HOLD');
 assert.equal(result.browser_acceptance,'NOT_ESTABLISHED');
 assert.equal(result.revenue,'NO_VERIFIED_OFFER_OR_CONFIRMED_PURCHASE');
});
test('Each of six photographic source roles and exact dates appears once',()=>{
 for(const [id,url,date,role] of RECORDS){
  assert.match(source,new RegExp('id="fv-ex2-ledger-apollo1-record-'+id+'"'));
  assert.ok(source.includes('data-fv-r132-photo-role="'+role+'"'));
  assert.ok(source.includes('data-fv-r132-photo-date="'+date+'"'));
  assert.ok(source.includes('href="'+url+'"'));
 }
});
fail('A promoted portrait catalog claim fails',source.replace('S67-19766 unverified','S67-19766 certified'),'UNVERIFIED_PORTRAIT_ID');
fail('A 2017 exhibit substituted with a 1967 date fails',source.replace('data-fv-r132-photo-date="2017-01-24"','data-fv-r132-photo-date="1967-01-24"'),'PHOTO_DATE_OR_ROLE_DRIFT');
fail('A NASA photographic link substitution fails',source.replace('https://www.nasa.gov/image-detail/amf-s67-21294/','https://untrusted.example/photo'),'UNAPPROVED_DESTINATION');
fail('A new unverified Payhip merchant CTA fails',source+'<a href="https://payhip.com/b/invented">Buy now</a>','UNAPPROVED_DESTINATION');
fail('Replacing the original-article CTA with checkout fails',source.replace('href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/"','href="https://payhip.com/b/invented"'),'UNAPPROVED_DESTINATION');
fail('An embedded unreviewed image fails',source+'<img src="/foo.jpg" alt="">','UNREVIEWED_MEDIA_OR_COLLECTION');
fail('An injected external collection form fails',source+'<form action="https://example.com"><input name="email"></form>','UNREVIEWED_MEDIA_OR_COLLECTION');
fail('Removing rights notice fails',source.replace('All six photographs require individual reuse review','All rights certified'),'MISSING_RIGHTS_BOUNDARY');
fail('Removing source classification fails',source.replace('data-fv-r132-photo-role="PHOTO_CONTEXT_NOT_TELEMETRY"','data-broken-role="unknown"'),'PHOTO_DATE_OR_ROLE_DRIFT');
fail('Unhiding controls without JS fails',source.replace('data-fvx-tools hidden','data-fvx-tools'),'NO_JS_FAIL_OPEN_UNPROVEN');
fail('Adding a duplicate photographic record fails',source.replace('</section>',source.match(/<article class="fv-ex2-ledger__card"[\\s\\S]*?<\\/article>/)[0]+'</section>'),'SIX_CARD_COUNT_MISMATCH');
test('A changed upstream Research Desk source must fail strict pinned-blob verification',()=>{
 const result=audit(source,'modified PR158 template');
 assert.equal(result.status,'FAIL');
 assert.ok(result.errors.includes('UPSTREAM_PR158_SOURCE_DRIFT'));
});
