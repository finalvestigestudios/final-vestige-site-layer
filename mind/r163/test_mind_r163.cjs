/* R163 reproducible source and authorization invariants.
 * Run from repository root: node mind/r163/test_mind_r163.cjs
 * No network, no cookies, no emails, no merchant checkout and no CMS writes.
 * Does NOT substitute for hosted CI, browser a11y, actual transactions or consent.
 */
'use strict';
const fs = require('fs');
const assert = require('assert/strict');
const base = 'mind/r163/';
const read = name => fs.readFileSync(base + name, 'utf8');
const article = read('the-suggestion-is-not-the-evidence.md');
const html = read('total-focus-suggestion-presell-UNPUBLISHED.html');
const json = read('product-claims-permissions-revenue-gates.json');
const plan = read('one-offer-creator-to-purchase-and-test-contract.md');
const previous = fs.readFileSync('mind/r162/the-transfer-problem-meditation-evidence.md', 'utf8');
const data = JSON.parse(json);
let passed=0; function check(label, fn){fn();passed++;}
const rejects = (fn, label) => {let failed=false;try {fn();} catch(_) {failed=true;} assert.ok(failed, 'Mutation escaped: '+label);};
const assertPage = s => {
 assert.match(s,/<html lang="en">/i);
 assert.match(s,/<main id="main">/i);
 assert.match(s,/<a class="skip" href="#main">/i);
 assert.match(s,/<nav aria-label="Page navigation">/i);
 assert.match(s,/<button[^>]+\bdisabled\b[^>]*>/i);
 assert.match(s,/Purchase unavailable — review pending/);
 assert.match(s,/Affiliate disclosure:/i);
 assert.match(s,/may earn a commission at no additional cost to you/i);
 assert.match(s,/https:\/\/finalvestige\.com\/focus\//);
 assert.match(s,/<details>[\s\S]*?<summary>Optional 40-second video pilot/i);
 assert.match(s,/No video file currently exists/);
 assert.match(s,/@media\(max-width:790px\)/);
 assert.match(s,/@media\(max-width:380px\)/);
 assert.match(s, /prefers-reduced-motion:reduce/);
 assert.doesNotMatch(s,/<(form|iframe|script|video|audio)\b/i);
 assert.doesNotMatch(s, /<a[^>]+href=["'][^"']*(inspire3\.com|hypnosislive\.com|zen12\.com)/i);
 assert.doesNotMatch(s, /<a[^>]+href=["']https?:\/\/(?:bit\.ly|tinyurl\.com|t\.co)/i);
 assert.doesNotMatch(s,/<video[^>]*\\bautoplay\\b/i); // no video autoplay attribute
 assert.doesNotMatch(s,/<input[^>]+type=["']email/i);
 assert.doesNotMatch(s,/utm_source=|fbclid=|gclid=/i);
};
const assertEvidence = d => {
 assert.equal(d.activation,'HARD_HOLD');
 assert.equal(d.status,'UNPUBLISHED');
 assert.equal(d.product.verified_affiliate_status,null);
 assert.equal(d.product.earning_url,null);
 assert.equal(d.product.current_checkout_price,null);
 assert.equal(d.product.verified_paid_orders,null);
 assert.equal(d.product.verified_net_revenue,null);
 assert.ok(d.sources.length>=12);
 assert.ok(d.claims.length>=30);
 assert.ok(d.release_gates.length>=35);
 assert.ok(d.release_gates.every(g=>g.status==='CLOSED'));
 assert.ok(d.claims.some(c=>c.id==='c11'&&c.status==='unsubstantiated_product_outcome'));
 assert.ok(d.claims.some(c=>c.id==='c22'&&c.status==='supported'));
 assert.ok(d.hard_rules.some(x=>/merchant commissions are not inferred/i.test(x)));
};
check('original long-form editorial evidence',()=>{
 assert.ok(article.trim().split(/\s+/).length>1800);
 assert.match(article,/Puységur/);
 assert.match(article,/The recording problem/);
 assert.match(article,/not a defensible case for telling a reader/i);
 assert.match(article,/The ninety-second return/i);
 assert.match(article,/https:\/\/pubmed\.ncbi\.nlm\.nih\.gov\/39032268\//);
 assert.match(article,/https:\/\/pubmed\.ncbi\.nlm\.nih\.gov\/34358272\//);
});
check('product claims and source matrix schema',()=>assertEvidence(data));
check('exact product and non-transfer',()=>{
 assert.equal(data.product.seller_claimed_duration_minutes,33);
 assert.equal(data.product.seller_claimed_size_mb,47);
 assert.match(plan,/NONE VERIFIED|UNKNOWN|unverified/i);
 assert.match(plan,/Clinical|clinical|clinical intervention/i);
});
check('page semantics / no commercial link',()=>assertPage(html));
check('source-controlled independent funnel',()=>{
 assert.match(plan,/HARD HOLD/);
 assert.match(plan,/gross - refunds/i);
 assert.match(plan,/asset_id=NULL/);
 assert.match(plan,/7- and 30-day cohorts/);
 assert.match(plan,/A\/B experiment/);
 assert.match(plan,/PRAxxIS\/GROK/i);
 assert.match(plan,/No link tracking code is shipped/);
});
check('earlier bibliographic correction',()=>{
 assert.match(previous,/published online on 28 December 2023/i);
 assert.doesNotMatch(previous,/A 2024 report combining five studies/);
});
check('no seller engagement passed off as paid conversion',()=>{
 assert.doesNotMatch(html,/<a[^>]+href=["'][^"']*(?:hypnosislive|inspire3|zen12)[^"']*affiliate/i);
 assert.match(plan,/merchant_confirmed_paid_order/);
 assert.match(plan,/affiliate_confirmed_commission/);
 assert.match(plan,/NOT COMPUTABLE/);
});
const mutants=[
 ['stripped language',s=>s.replace('<html lang="en">','<html>')],
 ['broken skip',s=>s.replace('href="#main"','href="#gone"')], // asserts explicit skip target
 ['removed main',s=>s.replace('<main id="main">','<main>')],
 ['removed nav label',s=>s.replace('aria-label="Page navigation"','')],
 ['active buy button',s=>s.replace('type="button" disabled','type="button"')],
 ['removed purchase hold',s=>s.replace('Purchase unavailable — review pending','Buy now')],
 ['removed commission disclosure',s=>s.replace('Affiliate disclosure:','Advertisement:')],
 ['denied commission',s=>s.replace('may earn a commission at no additional cost to you','never earn any commission')],
 ['removed free destination',s=>s.replaceAll('https://finalvestige.com/focus/','https://invalid.example/')],
 ['lost video transcript',s=>s.replace('<details>','<section>')],
 ['false claim media exists',s=>s.replace('No video file currently exists','Video is fully produced')],
 ['deleted mobile 790 breakpoint',s=>s.replace('@media(max-width:790px)','@media(min-width:9999px)')],
 ['deleted small breakpoint',s=>s.replace('@media(max-width:380px)','@media(min-width:9999px)')],
 ['no reduced motion',s=>s.replace('prefers-reduced-motion:reduce','prefers-reduced-motion:ignore')],
 ['insert external script',s=>s.replace('</body>','<script src="https://tracker.example/a.js"></script></body>')],
 ['activated merchant referral',s=>s.replace('</body>','<a href="https://hypnosislive.com/mental-skills/total-focus?affid=123">Buy now</a></body>')],
 ['insert redirect cloak',s=>s.replace('</body>','<a href="https://bit.ly/redirect">Sale</a></body>')],
 ['insert email signup',s=>s.replace('</body>','<form><input type="email"></form></body>')],
 ['insert tracking query',s=>s.replace('</body>','utm_source=personal_email</body>')],
 ['add playable autoplay',s=>s.replace('</body>','<video autoplay src="/media.mp4"></video></body>')]
];
let mutations=0;
for(const [name, mutate] of mutants){
 const m=mutate(html);
 assert.notEqual(m,html,'Mutation did not change source: '+name);
 rejects(()=>assertPage(m),name);
 mutations++;
}
const evidenceMutants=[
 ['affiliate falsely approved',d=>{d.product.verified_affiliate_status='approved';}],
 ['earning URL leaked',d=>{d.product.earning_url='https://merchant.example/earn';}],
 ['imagined sales',d=>{d.product.verified_paid_orders=1;}],
 ['imagined net revenue',d=>{d.product.verified_net_revenue=32;}],
 ['gate opened',d=>{d.release_gates[0].status='OPEN';}],
 ['claims gutted',d=>{d.claims=[];}],
 ['sources gutted',d=>{d.sources=[];}],
 ['gate removed',d=>{d.release_gates=[];}],
 ['unsupported claim relabeled',d=>{d.claims.find(c=>c.id==='c11').status='supported';}],
 ['false launch state',d=>{d.activation='LIVE';}]
];
for(const [name, change] of evidenceMutants){
 const d=JSON.parse(json);change(d);
 rejects(()=>assertEvidence(d),name);mutations++;
}
console.log('PASS R163 source tests: '+passed+' top-level invariants, '+mutations+'/'+(mutants.length+evidenceMutants.length)+' deliberate unsafe mutations detected');
console.log('LIMITS: no hosted CI, device/browser WCAG, media, signup, affiliate acceptance or sale verification.');
