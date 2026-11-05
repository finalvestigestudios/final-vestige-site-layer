"use strict";
/**
 * Run: node mind/r146/test-r146.cjs (from repository root)
 * Offline structural and controlled mutation tests only.
 * Does NOT claim browser, WP, Lighthouse, native merchant, consent or revenue verification.
 */
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '../..');
const read = rel => fs.readFileSync(path.join(root, rel), 'utf8');
const article = read('mind/r146/twelve-minute-meditation-independent-buyer-investigation.md');
const page = read('mind/r146/zen12-premium-high-intent-presell-review-only.html');
const plan = read('mind/r146/one-offer-to-settled-revenue-contract.md');
const ledger = JSON.parse(read('mind/r146/claim-evidence-commerce-gates.json'));
const a = read('mind/r145/zen12-premium-presell-a-review-only.html');
const b = read('mind/r145/zen12-premium-presell-b-review-only.html');
const hub = read('mind/r144/mind-hub-wp-draft.html');
let passed = 0;
const test = (name, fn) => { fn(); passed++; process.stdout.write('PASS ' + name + '\n'); };
const assertCommercialClosed = html => {
 assert.match(html,/data-fv-state="REVIEW_ONLY"|data-release="HARD_HOLD"/);
 assert.match(html,/\bdisabled\b/);
 assert.doesNotMatch(html,/<script\b|<iframe\b|<form\b|<video\b/i);
 assert.doesNotMatch(html,/https?:\/\/[^"' ]*(ref=|aff_id=|hop=|clickbank|utm_content=mock)/i);
};
const assertDisclosure = html => {
 assert.match(html,/If you buy through (this|a) link.*may earn a commission/is);
 assert.ok(html.indexOf('may earn a commission') < html.lastIndexOf('disabled'), 'disclosure precedes closed control');
};
const assertSources = text => {
 for (const s of ['https://doi.org/10.1016/j.bbr.2018.08.023','https://doi.org/10.1371/journal.pone.0286023','https://zen12.com/hnp','https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking'])
 assert.ok(text.includes(s),'missing: '+s);
};
const assertAllGatesClosed = data => {
 assert.equal(data.release,'HARD_HOLD');
 assert.equal(data.commercial_activation_allowed,false);
 assert.ok(data.gates.length>=20);
 assert.ok(data.gates.every(g=>g.verified===false && g.activation_blocking===true));
};
test('article long-form source-led original',()=>assert.ok(article.split(/\s+/).length>=1600));
test('article exact Basso trial and 8-not-4 caveat',()=>{assert.match(article,/thirteen.minute/i);assert.match(article,/eight weeks/i);assert.match(article,/not after four weeks/i)});
test('article contains explicit product-evidence boundary',()=>assert.match(article,/did not test the Zen12 Premium audio files/));
test('article merchant price presented as observed not final',()=>{assert.match(article,/\$87\.99/);assert.match(article,/not a verified checkout total/);});
test('article independent sources',()=>assertSources(article));
test('article free noncommercial Focus destination',()=>assert.match(article,/https:\/\/finalvestige\.com\/focus\//));
test('article merchant free newsletter separate from FV',()=>assert.match(article,/merchant.s newsletter/i));
test('article safety and no medical guarantee',()=>assert.match(article,/adverse experiences/));
test('article historical Puységur bridge',()=>assert.match(article,/puysegurs-animal-magnetism-files/));
test('article rejects invented firsthand endorsement',()=>assert.match(article,/has not tested or purchased/));
test('exact SKU title and merchant reference',()=>{assert.match(page,/Zen12 <em>Premium<\/em>/);assertSources(page);});
test('R146 page structurally closed',()=>assertCommercialClosed(page));
test('R146 near-CTA disclosure',()=>assertDisclosure(page));
test('R146 working free CTA has no tracking param',()=>assert.match(page,/href="https:\/\/finalvestige\.com\/focus\/"/));
test('R146 no external media/assets',()=>assert.doesNotMatch(page,/<img\b|<source\b|<audio\b|<video\b|@import|url\(/i));
test('R146 keyboard focus and responsive style',()=>{assert.match(page,/:focus-visible/);assert.match(page,/@media\(min-width:780px\)/);assert.match(page,/@media\(prefers-reduced-motion:reduce\)/);});
test('R146 semantic headings and accessible details',()=>{assert.match(page,/<h1\s+id="fv-r146-h1">/);assert.match(page,/<details><summary>/);});
test('R146 unique declared HTML IDs',()=>{let x=[...page.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]);assert.equal(new Set(x).size,x.length);});
test('R146 displays no personal signup duplication',()=>assert.doesNotMatch(page,/<input\b|<form\b/i));
test('R146 contrasts product price with unverified checkout',()=>assert.match(page,/actual checkout total.*not authenticated/i));
test('R146 includes source-supported adverse experience caveat',()=>assert.match(page,/not Zen12-specific/i));
test('R146 commercial control actually disabled',()=>assert.match(page,/<button type="button" disabled>/));
test('ledger JSON has adequate sources/claim decisions',()=>{assert.ok(ledger.source_evidence.length>=16);assert.ok(ledger.claim_decisions.length>=25)});
test('ledger source URLs all distinct and HTTPS',()=>{const s=ledger.source_evidence;assert.equal(new Set(s.map(x=>x.url)).size,s.length);assert.ok(s.every(x=>x.url.startsWith('https://')));});
test('ledger source references resolve locally',()=>{const ids=new Set(ledger.source_evidence.map(x=>x.id));assert.ok(ledger.claim_decisions.every(d=>d.source_ids.length && d.source_ids.every(id=>ids.has(id))));});
test('ledger commercial release gates hard false',()=>assertAllGatesClosed(ledger));
test('ledger excludes 12 minutes=hour seller promise',()=>assert.ok(ledger.claim_decisions.some(x=>x.id==='d03'&&x.status==='EXCLUDE_SELLER_CLAIM')));
test('ledger does not infer commission from click',()=>assert.ok(ledger.claim_decisions.some(x=>x.id==='d23'&&x.status==='FALSE_EXCLUDE')));
test('ledger records merchant newsletter consent',()=>assert.ok(ledger.claim_decisions.some(x=>x.id==='d13')));
test('ledger requires named affiliate approval',()=>assert.ok(ledger.gates.some(x=>x.id==='named_partner_acceptance'&& !x.verified)));
test('ledger requires actual paid order reconciliation',()=>assert.ok(ledger.gates.some(x=>x.id==='merchant_paid_order_reconciliation' && !x.verified)));
test('plan includes qualified human session denominator',()=>assert.match(plan,/qualified_human_sessions/));
test('plan separates paid event from affiliate click',()=>{assert.match(plan,/order_paid_verified/);assert.match(plan,/affiliate_click/);});
test('plan returns NOT COMPUTABLE when denominator absent',()=>assert.match(plan,/NOT COMPUTABLE/));
test('plan includes explicit refund and fee arithmetic',()=>assert.match(plan,/refunds - chargebacks - merchant_fees/));
test('plan names 7 and 30 day cohorts',()=>assert.match(plan,/Seven- and thirty-day cohort/));
test('plan defers Grok asset ID rather than making one up',()=>assert.match(plan,/Actual creator IDs/));
test('plan leaves paid SKU unauthenticated',()=>assert.match(plan,/rights-cleared Mind SKU/));
test('plan assigns release approval to founder',()=>assert.match(plan,/founder signs release/));
test('plan denies duplicate scripts',()=>assert.match(plan,/no duplicate scripts/i));
test('R145 inherited A/B remain hard hold and script free',()=>{assertCommercialClosed(a);assertCommercialClosed(b)});
test('R145 inherited A/B both have disclosure',()=>{assert.match(a,/may earn a commission/);assert.match(b,/may earn a commission/);});
test('R145 B video is only storyboarding',()=>{assert.match(b,/storyboard only/i);assert.match(b,/00:34–00:40/);assert.doesNotMatch(b,/<video\b|<iframe\b/i)});
test('R145 A has no film storyboard',()=>assert.doesNotMatch(a,/<section class="film"/i));
test('canonical unpublished R144 /mind/ hub has published Focus link',()=>{assert.match(hub,/finalvestige\.com\/focus\//);assert.match(hub,/UNPUBLISHED/);});
const shouldFail=(label,fn)=>{assert.throws(fn);passed++;process.stdout.write('PASS intentional negative '+label+'\n');};
shouldFail('affiliate control enabled',()=>assertCommercialClosed(page.replace(/<button type="button" disabled>/,'<button type="button">').replace('data-fv-state="REVIEW_ONLY"','data-fv-state="ACTIVE"')));
shouldFail('disclosure removed',()=>assertDisclosure(page.replace('If you buy through a link on this guide, Final Vestige may earn a commission at no additional cost to you.','Editorial note only.')));
shouldFail('injected tracking script',()=>assertCommercialClosed(page+'<script src="https://tracking.example/x.js"></script>'));
shouldFail('injected duplicate signup form',()=>assertCommercialClosed(page+'<form action="/subscribe"><input name="email"></form>'));
shouldFail('injected earnings URL',()=>assertCommercialClosed(page+'<a href="https://affiliate.example/?ref=fake">buy</a>'));
shouldFail('merchant approval gate falsely opened',()=>assertAllGatesClosed({...ledger,gates:ledger.gates.map((g,i)=>i===0?{...g,verified:true}:g)}));
shouldFail('priced claim without citation',()=>assertSources(article.replaceAll('https://zen12.com/hnp','MISSING_OFFICIAL_LINK')));
process.stdout.write('TOTAL '+passed+' PASS (offline structural and intentional negative assertions)\n');
