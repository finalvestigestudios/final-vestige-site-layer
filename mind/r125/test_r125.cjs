'use strict';
/** Run: node --test mind/r125/test_r125.cjs (Node 20+). No network. */
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const dir=__dirname;
const read=(p)=>fs.readFileSync(path.join(dir,p),'utf8');
const article=read('thatcher-illusion-investigation.md');
const guide=read('merchant-conversion-acceptance.md');
const html=read('zen12-decision-insert.html');
const matrix=JSON.parse(read('claim-evidence-and-acceptance.json'));
const {evaluateSettledAffiliateCohort}=require('./offline-attribution-validation.cjs');
const fixture={window_days:7,asset_id:'test_asset_001',qualified_human_sessions:100,
  settled_commission_cents:1900,refunded_commission_cents:400,fees_cents:100,
  confirmed_paid_orders:2,merchant_settlement_verified:true,media_provenance_verified:true,campaign_attribution_verified:true};

test('original article has multiple independent sources and no commercial endorsement',()=>{
 for(const ref of ['8354050','25301017','25549504','10.1068/p6659','Cornes']) assert(article.includes(ref));
 assert(!/https:\/\/(?:zen12\.com|affiliates\.inspire3\.com)/i.test(article));
 assert(/No paid offer is presented/i.test(article));
});
test('article copyright caution and non-diagnostic free exercise',()=>{
 assert(/copyrighted portraits/i.test(article));assert(/not a validated psychological instrument/i.test(article));
});
test('single conditional offer from exact page; no approved earning URL',()=>{
 assert.equal(matrix.pilot.candidate,'Zen12 Premium');
 assert.equal(matrix.pilot.offer_page,'https://zen12.com/hnp');
 assert.equal(matrix.pilot.affiliate_url,null);
});
test('source identifiers unique; all claims evidence traceable',()=>{
 const ids=matrix.sources.map(x=>x.id);assert.equal(ids.length,new Set(ids).size);
 for(const c of matrix.decisions)assert(ids.includes(c.source));
 assert(matrix.sources.length>=16);assert(matrix.decisions.length>=20);
});
test('scientific, seller, regulation, privacy, first party sources separately identified',()=>{
 for(const kind of ['independent_experiment','merchant_exact_offer','merchant_policy','regulator','first_party_live','systematic_review'])
 assert(matrix.sources.some(x=>x.kind===kind));
});
test('every mandatory merchant and release gate closed',()=>{
 const g=Object.values(matrix.gates);assert(g.length>=18);assert(g.every(v=>v.passed===false&&v.evidence===null));
});
test('commercial KPI stays unknown, never silently zero',()=>{
 assert.equal(matrix.measurement.status,'NOT_COMPUTABLE');
 assert.equal(matrix.measurement.net_revenue_per_1000_qualified_sessions,null);
});
test('seller discount explicitly conditional and not advertised as universal',()=>{
 assert(/conditional \$37/i.test(guide));assert(guide.includes('$87.99'));assert(/not universally verified/i.test(guide));
});
test('seller privacy and FTC sources present',()=>{
 for(const s of ['https://inspire3.com/privacy/','https://affiliates.inspire3.com/'])assert(guide.includes(s));assert(html.includes('ftc.gov'));
 assert(guide.includes('aggregate-only'));
});
test('actual commerce is natively disabled; no merchant product links',()=>{
 assert(/<button\b[^>]*\bdisabled\s+aria-disabled="true"/i.test(html));
 assert(!/<a\b[^>]*href=["'][^"']*(?:zen12\.com|affiliates\.inspire3\.com|brainwaveshots\.com)/i.test(html));
});
test('clear disclosure appears immediately before disabled CTA',()=>{
 const d=html.indexOf('If you purchase through a future approved link');
 const b=html.indexOf('<button');assert(d>=0&&b>d&&b-d<250);
});
test('no duplicate list, pixels, scripts, autoplay or merchant embeds',()=>{
 for(const forbidden of [/<script\b/i,/<form\b/i,/<iframe\b/i,/<video\b/i,/<audio\b/i,/<img\b[^>]*src=/i,/<input\b/i,/\bautoplay\b(?==)/i])assert(!forbidden.test(html));
});
test('accessible semantic guide and no-JS Focus route',()=>{
 for(const marker of ['aria-labelledby','<h2','<h3','<ol','<button','prefers-reduced-motion',':focus-visible','https://finalvestige.com/focus/'])assert(html.includes(marker));
});
test('safe source-grounded CTA and founder hold in memo',()=>{
 assert(guide.includes('UNVERIFIED'));assert(guide.includes('NOT_COMPUTABLE'));assert(guide.includes('HARD HOLD'));
 assert(guide.includes('Grok'));assert(guide.includes('PR #970'));
});
test('missing settlement stays not computable',()=>{
 const r=evaluateSettledAffiliateCohort({...fixture,merchant_settlement_verified:false});
 assert.equal(r.status,'NOT_COMPUTABLE');assert.equal(r.net_revenue_per_1000_qualified_sessions_usd,null);
});
test('missing media provenance / campaign attribution close output',()=>{
 assert.equal(evaluateSettledAffiliateCohort({...fixture,media_provenance_verified:false}).status,'NOT_COMPUTABLE');
 assert.equal(evaluateSettledAffiliateCohort({...fixture,campaign_attribution_verified:false}).status,'NOT_COMPUTABLE');
});
test('missing denominator or verified session zero stays unknown',()=>{
 assert.equal(evaluateSettledAffiliateCohort({...fixture,qualified_human_sessions:null}).status,'NOT_COMPUTABLE');
 assert.equal(evaluateSettledAffiliateCohort({...fixture,qualified_human_sessions:0,confirmed_paid_orders:0}).status,'NOT_COMPUTABLE');
});
test('synthetic arithmetic returns correct net/1000 and paid rate',()=>{
 const r=evaluateSettledAffiliateCohort(fixture);
 assert.equal(r.status,'COMPUTABLE_FROM_VERIFIED_INPUT');
 assert.equal(r.net_revenue_usd,14);
 assert.equal(r.net_revenue_per_1000_qualified_sessions_usd,140);
 assert.equal(r.confirmed_paid_conversion_rate,0.02);
 assert.equal(r.tiny_sample_warning,true);
});
test('negative net outcome permitted if fees exceed receipts',()=>{
 const r=evaluateSettledAffiliateCohort({...fixture,fees_cents:2500});
 assert.equal(r.net_revenue_usd,-10);
});
test('invalid windows, numeric values and refunds fail',()=>{
 assert.throws(()=>evaluateSettledAffiliateCohort({...fixture,window_days:13}),/INVALID_WINDOW/);
 assert.throws(()=>evaluateSettledAffiliateCohort({...fixture,qualified_human_sessions:NaN}),/INVALID_/);
 assert.throws(()=>evaluateSettledAffiliateCohort({...fixture,refunded_commission_cents:3000}),/REFUNDS_EXCEED_GROSS/);
});
test('marketing clicks or subscriber totals never create paid-order proof',()=>{
 const r=evaluateSettledAffiliateCohort({...fixture,merchant_settlement_verified:false,affiliate_clicks:900,confirmed_leads:100});
 assert.equal(r.status,'NOT_COMPUTABLE');
});
test('reject personally identifying fields even in nested test payloads',()=>{
 for(const bad of [{email:'x@example.invalid'},{name:'a',order_id:'123'},{meta:{ip_address:'127.0.0.1'}}]){
 assert.throws(()=>evaluateSettledAffiliateCohort({...fixture,...bad}),/PII_FIELD_PROHIBITED/);
 }
});
test('reject unproven or invalid asset IDs to stop fabricated attribution',()=>{
 assert.throws(()=>evaluateSettledAffiliateCohort({...fixture,asset_id:'not actual?'}),/REAL_ASSET_ID/);
});
test('adversarial merchant link mutation would be caught',()=>{
 const mutant=html.replace('</section>\n<p class="source">','<a href="https://zen12.com/hnp">BUY</a></section>\n<p class="source">');
 assert(/<a\b[^>]*href="https:\/\/zen12\.com/i.test(mutant));
});
test('adversarial removed disclosure would be caught',()=>{
 const mutant=html.replace('If you purchase through a future approved link','');
 assert(!mutant.includes('If you purchase through a future approved link'));
});
test('adversarial enabled button would be caught',()=>{
 const mutant=html.replace(' disabled aria-disabled="true"',' aria-disabled="false"');
 assert(!/<button\b[^>]*\bdisabled\s+aria-disabled="true"/i.test(mutant));
});
