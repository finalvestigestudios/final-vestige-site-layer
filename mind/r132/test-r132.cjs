'use strict';
/* Run locally after approved checkout of this PR:
   node --test mind/r132/test-r132.cjs
   All fixtures synthetic: no personal records and no web calls.
*/
const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const root=__dirname;
const read=x=>fs.readFileSync(path.join(root,x),'utf8');
const a=read('zen12-buyer-variant-a.html'),b=read('zen12-buyer-variant-b.html'),hub=read('mind-hub-custom-html-draft.html');
const guide=read('binaural-beats-buyer-evidence.md'),memo=read('commercial-proof-and-creator-routing.md'),ledger=JSON.parse(read('claims-and-gates.json'));
const {parseAggregate}=require('./conversion-metrics.cjs');
for(const [name,html] of [['A',a],['B',b]]){
 test(name+' has no commerce activation or runtime tracking',()=>{
  assert.match(html,/button type="button" disabled aria-disabled="true"/);
  assert.doesNotMatch(html,/<script\b|<iframe\b|\bautoplay\s*=|<form\b|<input\b|href="https?:\/\/(?:www\.)?(?:zen12|affiliates\.inspire3)/i);
 });
 test(name+' has near-button explicit earnings disclosure',()=>{
  const at=html.indexOf('class="disclosure"'),btn=html.indexOf('<button');
  assert(at>0&&btn>at&&btn-at<500);assert.match(html,/Final Vestige may earn a commission/);
 });
 test(name+' retains one native free route and keyboard contrast semantics',()=>{
  assert.match(html,/href="https:\/\/finalvestige\.com\/focus\/"/);
  assert.match(html,/:focus-visible/);assert.match(html,/prefers-reduced-motion/);
  assert.match(html,/aria-labelledby=/);assert.match(html,/max-width:390px/);
 });
}
test('Variant B contains original optional storyboard and transcript but no faux video',()=>{
 assert.match(b,/0–6s/);assert.match(b,/33–40s/);assert.match(b,/Full transcript/);
 assert.match(b,/storyboard only/);assert.doesNotMatch(b,/<video\b|\bautoplay\s*=|<iframe\b/i);
 assert.doesNotMatch(a,/Full transcript/);
});
test('A and B have identical central offer/merchant safeguards',()=>{
 for(const term of ['The sound between your ears','one-year guarantee','affiliate may receive','product-specific','Merchant purchase unavailable'])
  assert(a.includes(term)&&b.includes(term),term);
});
test('hub is editorial only and neither merchants nor duplicate forms appear',()=>{
 assert.match(hub,/The Mind &amp; Perception Archive/);
 assert.match(hub,/change-blindness/);assert.match(hub,/mesmerism/);assert.match(hub,/puysegurs/);
 assert.match(hub,/focus\//); assert.doesNotMatch(hub,/<form\b|<script\b|<iframe\b|href="https?:\/\/zen12/i);
});
test('guide sourced, cautious and not a first-person testimonial',()=>{
 for(const id of ['[S1]','[S2]','[S3]','[S4]','[S5]','[S6]','[S7]','[S8]','[S9]','[S10]'])assert(guide.includes(id),id);
 assert.match(guide,/does not.*substantiate|not a finding Final Vestige can substantiate/i);
 assert.match(guide,/not a clinical test/);
});
test('all legal and approval gates remain CLOSED',()=>{
 for(const [k,v] of Object.entries(ledger.gates)) assert.equal(v,'CLOSED',k);
 assert.equal(ledger.authorization,'UNVERIFIED');
 for(const c of ledger.claims)for(const id of c.sources) assert(ledger.sources.find(s=>s.id===id));
});
test('merchant URLs and rights restrictions are explicit',()=>{
 assert.match(memo,/named partner agreement/);
 assert.match(memo,/NO customer\/sale\/commission|not proof of rejection|no actual paid|No manufacturer/i);
 assert.match(memo,/NOT_COMPUTABLE/);
});
const good={cohort_days:7,qualified_human_sessions:100,attribution_evidence:'verified',merchant_report_complete:true,merchant_settlement_verified:true,attributable_orders:2,gross_commission_cents:1200,refunds_cents:200,fees_cents:100,report_period:'2026-11-01/2026-11-07',data_handling_approved:true};
test('a synthetic verified settlement computes net but warns small cohorts',()=>{
 const r=parseAggregate(good);assert.equal(r.status,'VERIFIED_AGGREGATE');
 assert.equal(r.net_revenue_cents,900);assert.equal(r.net_per_1000_qualified_human_sessions_cents,9000);
 assert.equal(r.warning,'TINY_SAMPLE_DO_NOT_INFER_CAUSALITY');
});
test('missing proof means NOT_COMPUTABLE, not zero',()=>{
 assert.equal(parseAggregate({...good,merchant_settlement_verified:false}).status,'NOT_COMPUTABLE');
 assert.equal(parseAggregate({...good,qualified_human_sessions:0}).status,'NOT_COMPUTABLE');
 assert.equal(parseAggregate({...good,attribution_evidence:'unknown'}).status,'NOT_COMPUTABLE');
});
test('visitor PII and invalid fields are blocked',()=>{
 assert.equal(parseAggregate({...good,customer_email:'private@example.com'}).status,'INVALID');
 assert.equal(parseAggregate({...good,qualified_human_sessions:-1}).status,'NOT_COMPUTABLE');
 assert.equal(parseAggregate({...good,refunds_cents:1300}).status,'INVALID');
});
test('intentional mutation of buying CTA is detectable',()=>{
 const unsafe=a.replace('button type="button" disabled aria-disabled="true"','button type="button"');
 assert.notEqual(unsafe,a);
 assert.doesNotMatch(unsafe,/button type="button" disabled aria-disabled="true"/);
});
test('intentional disclosure deletion is detectable',()=>{
 const unsafe=a.replace(/<p class="disclosure">[\s\S]*?<\/p>/,'');
 assert(!unsafe.includes('class="disclosure"'));
});
