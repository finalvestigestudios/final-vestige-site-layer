'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {auditLanding,evaluate,cohort,approvedEvidence,required}=require('./r129_educator_offer_gate.cjs');
const manifest=JSON.parse(fs.readFileSync(path.join(__dirname,'r129_offer_manifest.json'),'utf8'));
const html='<section id="classroom-preview"><article data-fv-student-print></article></section>'+
  '<a href="#classroom-preview" data-fv-primary-cta>Free classroom evidence exercise</a>'+
  '<p>Apollo 204 Review Board / photograph reuse 0/6</p>';
const clone=x=>JSON.parse(JSON.stringify(x));
const evidence={verified:true,evidence_ref:'read-only-verified-merchant-record',reviewed_by:'human-reviewer',reviewed_on:'2026-11-04'};
test('unverified status stays held, never sells a fictional product',()=>{
 const result=evaluate(manifest,html);
 assert.equal(result.readiness,'STAGING_HOLD');
 assert.ok(result.blockers.length>=required.length);
 assert.equal(result.permitted_commerce_cta,'NONE_UNTIL_SEPARATE_RELEASE_AUTHORIZATION');
 assert.equal(result.verified_sku_in_this_report,false);
});
test('manifest and HTML content have zero active checkout or collection',()=>{
 assert.deepEqual(auditLanding(html),[]);
 assert.ok(auditLanding(html+'<form></form>').includes('UNAPPROVED_LEAD_CAPTURE_FORM'));
 assert.ok(auditLanding(html+'<a href="https://payhip.com/b/demo">BUY</a>').includes('UNVERIFIED_COMMERCE_LINK_PRESENT'));
 assert.ok(auditLanding(html+'<img src="nasa.jpg">').includes('UNREVIEWED_MEDIA_EMBED'));
});
test('fail-open free CTA, no-JS worksheet, and rights warnings all required',()=>{
 assert.ok(auditLanding(html.replace('data-fv-primary-cta','data-disabled')).includes('FREE_CLASSROOM_ACTION_MISSING_OR_DUPLICATED'));
 assert.ok(auditLanding(html+ '<a href="#classroom-preview" data-fv-primary-cta>duplicate</a>').includes('FREE_CLASSROOM_ACTION_MISSING_OR_DUPLICATED'));
 assert.ok(auditLanding(html.replace('data-fv-student-print','data-none')).includes('NO_JS_CLASSROOM_EXERCISE_MISSING'));
 assert.ok(auditLanding(html.replace('0/6','six')).includes('PRIMARY_SOURCE_OR_REUSE_WARNING_MISSING'));
});
test('one self-declared flag without provenance cannot unblock offer',()=>{
 const m=clone(manifest);m.merchant.existing_sku_verified={verified:true};
 assert.ok(evaluate(m,html).blockers.includes('EXISTING_SELLABLE_SKU_NOT_VERIFIED'));
});
test('merchant URL requires direct HTTPS product, not redirect or lookalike',()=>{
 for(const bad of ['http://payhip.com/b/x','https://payhip.com.evil.net/b/x','https://payhip.com/','https://payhip.com/b/x?utm_source=fake', 'not a url']){
  const m=clone(manifest);m.merchant.listing_url=bad;
  const codes=evaluate(m,html).blockers;
  assert.ok(codes.includes('LISTING_URL_NOT_DIRECT_PAYHIP_PRODUCT')||codes.includes('LISTING_URL_INVALID'),bad);
 }
});
test('even complete independently referenced manifest only enters human review',()=>{
 const m=clone(manifest);m.merchant.listing_url='https://payhip.com/b/approved';
 for(const [p] of required){let node=m;const keys=p.split('.');for(const k of keys.slice(0,-1))node=node[k];node[keys.at(-1)]=evidence;}
 assert.equal(evaluate(m,html).readiness,'HUMAN_REVIEW_REQUIRED');
 assert.equal(evaluate(m,html).verified_sku_in_this_report,false);
});
test('no cohort arithmetic from unverified sessions, clicks or orders',()=>{
 assert.equal(cohort(null).status,'NOT_COMPUTABLE');
 assert.equal(cohort({qualified_human_sessions:100,paid_orders:2,gross_minor:2000,refunds_minor:0,fees_minor:100}).status,'NOT_COMPUTABLE');
});
test('cohort zero denominator and inconsistent refund amounts fail closed',()=>{
 const verified={window:'7d',qualified_human_sessions_verified:true,merchant_orders_reconciled:true,asset_to_order_join_verified:true,
 qualified_human_sessions:0,paid_orders:0,gross_minor:0,refunds_minor:0,fees_minor:0};
 assert.equal(cohort(verified).status,'NOT_COMPUTABLE');
 verified.qualified_human_sessions=10;verified.refunds_minor=1;
 assert.equal(cohort(verified).status,'NOT_COMPUTABLE');
});
test('synthetic verified aggregate demonstrates transparent formula only',()=>{
 const demo={window:'30d',qualified_human_sessions_verified:true,merchant_orders_reconciled:true,asset_to_order_join_verified:true,
 qualified_human_sessions:200,paid_orders:2,gross_minor:4000,refunds_minor:500,fees_minor:300};
 const out=cohort(demo);
 assert.equal(out.status,'AGGREGATE_COMPUTABLE_NOT_CAUSAL_PROOF');
 assert.equal(out.realized_net_minor,3200);
 assert.equal(out.net_revenue_per_1000_minor,16000);
 assert.equal(out.paid_conversion_rate,0.01);
 assert.equal(out.small_sample_warning,true);
});
test('evidence requires review date, reference and named independent reviewer',()=>{
 assert.equal(approvedEvidence(evidence),true);
 for(const bad of [{verified:true},{...evidence,evidence_ref:'x'},{...evidence,reviewed_on:'soon'},{...evidence,reviewed_by:'x'}])
  assert.equal(approvedEvidence(bad),false);
});
