'use strict';
/** Native executable tests: node --test mind/r114/revenue-math.test.cjs
 * Pure offline synthetic fixtures. Successful tests do NOT constitute sales, visitor evidence or browser QA. */
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {validateSafeEvent,confirmedRevenue}=require('./revenue-math.cjs');
const d=__dirname,A=fs.readFileSync(path.join(d,'zen12-text-A.html'),'utf8'),B=fs.readFileSync(path.join(d,'zen12-film-B.html'),'utf8');
const GUIDE=fs.readFileSync(path.join(d,'zen12-canonical-decision-guide.md'),'utf8');
const VTT=fs.readFileSync(path.join(d,'film-40s.vtt'),'utf8');
const L=JSON.parse(fs.readFileSync(path.join(d,'evidence-claim-matrix.json'),'utf8'));
const filmStart=B.indexOf('<section aria-labelledby="film-title"'),filmEnd=B.indexOf('<section class="panel" aria-labelledby="limits">',filmStart);
test('R114 hard hold',()=>assert.equal(L.activation,'HARD_HOLD'));
test('not a verified affiliate',()=>assert.equal(L.partner_acceptance_verified,false));
test('no active commercial link',()=>assert.equal(L.affiliate_link_enabled,false));
test('no fake paid sales',()=>assert.equal(L.observed_outcomes.paid_orders,null));
test('no fake net',()=>assert.equal(L.observed_outcomes.net_revenue_per_1000_qualified_sessions,null));
test('no eligible owned SKU assumed',()=>assert.equal(L.owned_paid_sku_verified,false));
test('all commercial and release gates closed',()=>assert.ok(Object.values(L.gates).every(x=>x===false)));
test('seller price snapshot does not claim fixed checkout',()=>assert.equal(L.dated_offer_snapshot.assert_as_current_checkout_total,false));
test('rejected hour-equivalence claim documented',()=>assert.match(L.claim_decisions.find(x=>x.id==='C3').decision,/REJECT/));
test('distinct product terms not blended',()=>assert.match(L.claim_decisions.find(x=>x.id==='C16').decision,/REJECT/));
test('A/B share same copy except optional B film',()=>assert.equal(B.slice(0,filmStart)+B.slice(filmEnd),A));
for (const [tag,html] of [['A',A],['B',B]]){
 test(tag+' no merchant earning href',()=>assert.doesNotMatch(html,/<a[^>]+href=["']https?:\\/\\/(?:zen12|affiliates\.inspire3)[^"']*["']/i));
 test(tag+' disabled offer control',()=>assert.match(html,/<button[^>]+disabled\b/));
 test(tag+' near-button prospective disclosure',()=>assert.ok(html.includes('we may earn a commission when you buy')&&html.indexOf('we may earn a commission when you buy')<html.indexOf('Merchant link unavailable')));
 test(tag+' has no script/embed/form',()=>assert.doesNotMatch(html,/<script\b|<iframe\b|<form\b/));
 test(tag+' no autoplay media',()=>assert.doesNotMatch(html,/<video\b|autoplay\s*=/));
 test(tag+' noindex',()=>assert.match(html,/noindex,nofollow/));
 test(tag+' existing Focus route',()=>assert.ok(html.includes('https://finalvestige.com/focus/')));
 test(tag+' responsive and reduced motion',()=>{assert.match(html,/@media\(max-width:660px\)/);assert.match(html,/prefers-reduced-motion/);});
}
test('B storyboard is optional and no playback invented',()=>assert.ok(B.includes('data-film-status="storyboard-only"')&&B.includes('NOT been produced')));
test('captions six contiguous full-runtime segments',()=>{let p=0;const m=[...VTT.matchAll(/(\d\d):(\d\d):(\d\d)\.\d+ --> (\d\d):(\d\d):(\d\d)\.\d+/g)];assert.equal(m.length,6);for(const x of m){let a=3600*+x[1]+60*+x[2]+ +x[3],b=3600*+x[4]+60*+x[5]+ +x[6];assert.equal(a,p);assert.ok(b>a);p=b;}assert.equal(p,40);});
test('guide source manuscript substantial',()=>assert.ok(GUIDE.trim().split(/\s+/).length>1300));
test('guide research + free alternative',()=>assert.ok(GUIDE.includes('pubmed.ncbi.nlm.nih.gov/37205669')&&GUIDE.includes('finalvestige.com/focus/')));
test('no PII permitted in event schema',()=>assert.ok(['name','email','phone','IP'].every(x=>L.reporting_contract.prohibited.includes(x))));
test('valid minimal event accepted',()=>assert.ok(validateSafeEvent({event_name:'qualified_landing',utm_medium:'organic_social',utm_content_asset_id:'fvtest_123'})));
for(const bad of [{event_name:'affiliate_outbound_click',email:'person@example.com'},{event_name:'verified_merchant_order',merchant_customer_id:'abc'},{event_name:'qualified_landing',utm_content_asset_id:'bad space'},{event_name:'purchase',utm_source:'x'},{event_name:'qualified_landing',utm_medium:'paid_social'}]){
 test('unsafe or invented event rejected '+JSON.stringify(bad),()=>assert.equal(validateSafeEvent(bad),false));
}
const complete={source_proof:'merchant_reconciled_and_firstparty_qualified',attribution:'verified',cohort_days:7,owned_gross_settled_cents:2000,affiliate_commission_settled_cents:500,refunds_cents:250,chargebacks_cents:0,platform_fees_cents:100,confirmed_paid_orders:2,qualified_human_sessions:100};
test('synthetic merchant arithmetic net is 2150 cents',()=>assert.equal(confirmedRevenue(complete).net_settled_cents,2150));
test('synthetic per 1000 qualified sessions equals 21500 cents',()=>assert.equal(confirmedRevenue(complete).net_per_1000_cents,21500));
test('synthetic conversion count rate is distinct from clicks',()=>assert.equal(confirmedRevenue(complete).confirmed_paid_order_rate,.02));
test('small samples flagged',()=>assert.equal(confirmedRevenue(complete).small_sample_warning,true));
test('missing revenue components => NULL',()=>assert.equal(confirmedRevenue({...complete,refunds_cents:null}).net_per_1000_cents,null));
test('outbound click event alone cannot prove money',()=>assert.equal(confirmedRevenue({affiliate_outbound_click:1000}).net_per_1000_cents,null));
test('missing source proof => NULL',()=>assert.equal(confirmedRevenue({...complete,source_proof:'unverified'}).net_per_1000_cents,null));
test('wrong cohort => NULL',()=>assert.equal(confirmedRevenue({...complete,cohort_days:1}).net_per_1000_cents,null));
test('small private cohort suppressed',()=>assert.equal(confirmedRevenue({...complete,qualified_human_sessions:19}).status,'SUPPRESSED_SMALL_CELL'));
test('count anomaly fails closed',()=>assert.equal(confirmedRevenue({...complete,confirmed_paid_orders:200}).net_per_1000_cents,null));
test('explicitly unknown attribution fails closed',()=>assert.equal(confirmedRevenue({...complete,attribution:null}).net_per_1000_cents,null));
