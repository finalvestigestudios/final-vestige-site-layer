'use strict';
// Reproducible offline validation: node mind/r122/verify-r122.cjs
// Unit tests and structural assertions only. Not a real browser, native WordPress, CI or merchant validation.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const root = __dirname;
const read = f => fs.readFileSync(path.join(root,f),'utf8');
const A = read('zen12-buyer-variant-a-text.html');
const B = read('zen12-buyer-variant-b-storyboard.html');
const article = read('when-meditation-isnt-calm-investigation.md');
const plan = read('one-offer-conversion-acceptance.md');
const ledger = JSON.parse(read('merchant-claims-evidence-2026-11-04.json'));
const { evaluateCohort } = require('./cohort-proof.cjs');
let passes=0;
function test(name, fn) { fn(); passes++; console.log('PASS', passes, name); }
const badMerchantAnchor = /href\s*=\s*["']https?:\/\/(?:www\.)?(?:zen12\.com|affiliates\.inspire3\.com|inspire3\.com|hypnosislive\.com|brainwaveshots\.com)\//i;
const unsafeScript = /<script\b|<form\b|\bautoplay\s*=/i;
const filmed = /<section id="film"[\s\S]*?<\/section>/;
const removeFilm = html => html.replace(filmed,'');
const quoteMoney = /\$87\.99/;
const fixture = () => ({
  campaign_id:'mind_audio_pilot_2026_11',cohort_start:'2026-11-04',
  cohort_days:7,qualified_human_sessions:2000,qualified_session_method:'human_filter_v1',
  merchant:'inspire3_partner',merchant_report_reference:'synthetic_fixture_only',
  merchant_report_confirmed:true,attribution_join_verified:true,fully_settled:true,
  confirmed_paid_orders:20,confirmed_customers:19,gross_settled_revenue:100,
  refunds:10,merchant_fees:5,chargebacks:0
});
test('ledger dated',()=>assert.equal(ledger.date,'2026-11-04'));
test('eighteen source links',()=>assert.equal(ledger.verified_observations.length,18));
test('nineteen claim decisions',()=>assert.equal(ledger.claims.length,19));
test('merchant product exact URL present',()=>assert(ledger.verified_observations.some(x=>x.url==='https://zen12.com/hnp')));
test('official privacy source present',()=>assert(ledger.verified_observations.some(x=>x.url==='https://inspire3.com/privacy/')));
test('independent adverse-effect reviews present',()=>assert(ledger.verified_observations.some(x=>x.url.includes('acps.13225')) && ledger.verified_observations.some(x=>x.url.includes('s12671'))));
test('product equivalence excluded',()=>assert(ledger.claims.some(x=>x.claim.includes('60 minutes') && x.decision.startsWith('EXCLUDE'))));
test('universal price excluded',()=>assert(ledger.claims.some(x=>x.claim.includes('$87.99') && x.decision.startsWith('REJECT'))));
test('product specific adverse rate excluded',()=>assert(ledger.claims.some(x=>x.claim.includes('8.3%') && x.decision.startsWith('EXCLUDE'))));
test('partner approval closed',()=>assert.equal(ledger.permissions.named_affiliate_approval,false));
test('all seventeen permissions closed',()=>assert.equal(Object.values(ledger.permissions).filter(v=>v===false).length,17));
test('all release gates remain closed',()=>assert.equal(ledger.gates.live_affiliate_CTA,'CLOSED'));
test('no pretend source sales',()=>assert.equal(ledger.quantitative_status.real_transactions,null));
test('A/B parity exactly apart from film',()=>assert.equal(removeFilm(B),A));
test('optional storyboard appears only in B',()=>assert(!filmed.test(A)&&filmed.test(B)));
test('B includes 40 second storyboard',()=>assert(B.includes('00:35–00:40')&&B.includes('00:00–00:07')));
test('B has six timed caption intervals',()=>assert.equal((B.match(/<li><strong>00:/g)||[]).length,6));
test('B clearly not playable',()=>assert(/NOT PLAYABLE/.test(B) && /STORYBOARD ONLY/.test(B)));
test('no active merchant anchor',()=>assert(!badMerchantAnchor.test(A+B)));
test('no forms scripts or autoplay',()=>assert(!unsafeScript.test(A+B)));
test('no video or iframe remote request',()=>assert(!/<video\b|<iframe\b|<track\b/i.test(A+B)));
test('A html disabled button natively',()=>assert(/<button[^>]*\sdisabled\b[^>]*>/.test(A)));
test('B html disabled button natively',()=>assert(/<button[^>]*\sdisabled\b[^>]*>/.test(B)));
test('affiliate explanation close to button',()=>{
  for(const h of [A,B]) {
    const pos=h.indexOf('may earn a commission');
    const btn=h.indexOf('<button class="cta"');
    assert(pos>0 && btn>pos && btn-pos<750);
  }
});
test('one existing Focus CTA each',()=>assert.equal((A.match(/href="https:\/\/finalvestige\.com\/focus\/"/g)||[]).length,1));
test('no added lead form',()=>assert(!/<form\b/i.test(A+B)));
test('English language and mobile viewport',()=>assert([A,B].every(h=>h.includes('<html lang="en">')&&h.includes('name="viewport"'))));
test('skip link main target',()=>assert([A,B].every(h=>h.includes('href="#content"')&&h.includes('id="content"'))));
test('reduced motion and responsive layout',()=>assert([A,B].every(h=>h.includes('prefers-reduced-motion')&&h.includes('max-width:760px'))));
test('noindex on draft',()=>assert([A,B].every(h=>h.includes('noindex,nofollow'))));
test('buyer offer is dated and non-checkout',()=>assert([A,B].every(h=>quoteMoney.test(h)&&h.includes('not confirmed buyer checkout prices'))));
test('seller buyer privacy concern shown',()=>assert([A,B].every(h=>h.includes('purchase details with affiliates'))));
test('article contains no affiliate selling',()=>assert(!badMerchantAnchor.test(article)));
test('article does not claim product-specific adverse rate',()=>assert(/not a prospective safety trial of Zen12/.test(article)));
test('historical archive link in article',()=>assert(article.includes('puysegurs-animal-magnetism-files')));
test('article has formal source trail',()=>assert(article.includes('### Evidence register / references')));
test('plan maps three video destinations',()=>assert(plan.includes('Change Blindness')&&plan.includes('Puységur')&&plan.includes('mind-wandering')));
test('plan distinguishes asset IDs from assumption',()=>assert(plan.includes('actual immutable Grok asset_id')));
test('plan prioritizes settled merchant evidence',()=>assert(plan.includes('settled, attributable paid receipts')));
test('plan protects other branches and issue owners',()=>assert(plan.includes('PR #172')&&plan.includes('homepage flagship #49')));
test('cohort calculator denies missing evidence',()=>assert.equal(evaluateCohort({campaign_id:'x'}).status,'NOT_COMPUTABLE'));
test('cohort calculator denies PII keys',()=>assert.throws(()=>evaluateCohort({...fixture(),buyer_email:'a@example.com'})));
test('cohort calculator denies nested PII',()=>assert.throws(()=>evaluateCohort({...fixture(),aux:{ip_address:'127.0.0.1'}})));
test('cohort calculator denies visitor IDs',()=>assert.throws(()=>evaluateCohort({...fixture(),visitor_id:'xyz'})));
test('cohort calculator denies unverified partner report',()=>assert.equal(evaluateCohort({...fixture(),merchant_report_confirmed:false}).status,'NOT_COMPUTABLE'));
test('cohort calculator denies missing attribution',()=>assert.equal(evaluateCohort({...fixture(),attribution_join_verified:false}).status,'NOT_COMPUTABLE'));
test('cohort calculator denies pending settlement',()=>assert.equal(evaluateCohort({...fixture(),fully_settled:false}).status,'NOT_COMPUTABLE'));
test('cohort calculator denies zero denominator',()=>assert.equal(evaluateCohort({...fixture(),qualified_human_sessions:0}).status,'NOT_COMPUTABLE'));
test('cohort calculator denies NaN',()=>assert.equal(evaluateCohort({...fixture(),gross_settled_revenue:NaN}).status,'INVALID'));
test('cohort calculator denies negative prices',()=>assert.equal(evaluateCohort({...fixture(),merchant_fees:-1}).status,'INVALID'));
test('cohort calculator denies impossible customers',()=>assert.equal(evaluateCohort({...fixture(),confirmed_customers:21}).status,'INVALID'));
test('cohort calculator allows 30-day cohorts',()=>assert(evaluateCohort({...fixture(),cohort_days:30}).status.startsWith('COMPUTABLE_')));
test('cohort synthetic arithmetic is correct',()=>{
  const r=evaluateCohort(fixture());
  assert.equal(r.net_revenue,85);
  assert.equal(r.net_revenue_per_1000_qualified_sessions,42.5);
  assert.equal(r.paid_order_rate,0.01);
  assert.equal(r.tiny_sample_warning,true);
  assert(/NOT_INDEPENDENTLY_VERIFIED/.test(r.status));
});
test('no claims of verified real sales in guide',()=>assert(/no authorized earning link/.test(A)&&/No live merchant offer/.test(A)));
console.log('FINISHED',passes,'source-level tests; no native browser/checkout/merchant verification inferred.');
