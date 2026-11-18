'use strict';
/* node --test mind/r472/qa.test.cjs
 * Native Node v20+ required. No network, third-party packages, WordPress or merchant credentials.
 * These static regression checks do NOT substitute for actual WCAG/phone/hosted-video/checkout QA.
 */
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const root=__dirname;
const read=(name)=>fs.readFileSync(path.join(root,name),'utf8');
const A=read('ZEN12_A_TEXT_ONLY.html');
const B=read('ZEN12_B_OPTIONAL_FILM.html');
const hub=read('MIND_HUB_WP_SOURCE_ONLY.html');
const poster=read('ZEN12_POSTER_ORIGINAL.svg');
const vtt=read('ZEN12_FILM_42S_CAPTIONS.vtt');
const article=read('THE_GORILLA_YOU_WERE_NOT_LOOKING_FOR.md');
const matrix=JSON.parse(read('CLAIM_PRODUCT_PERMISSION_MATRIX.json'));
const spec=read('OFFER_TO_REALIZED_REVENUE_RUNBOOK.md');
const removeFilm=(html)=>html.replace(/<section class="panel" aria-labelledby="film-title"[\s\S]*?<\/section>/,'').replace(/\s+/g,' ').trim();
const unsafe=(html)=>/<script\b|<iframe\b|<form\b|<(?:video|audio)[^>]*\bautoplay\b|\bonclick=|\bonload=|http-equiv=["']refresh|<a[^>]*\bhref=["']https?:\/\/(?:affiliate\.example|tracking\.example|[^"']*refersion\.com)/i.test(html);
const missingDisclosedCTA=(html)=>{const offer=html.match(/<section class="panel offer"[\s\S]*?<\/section>/)?.[0]??'';return !/commission disclosure/i.test(offer)||!/<button\b[^>]*\sdisabled(?:\s|>|=)/i.test(offer)||offer.indexOf('commission disclosure')>offer.indexOf('<button');};
const safeGuide=(html)=>!unsafe(html)&&!missingDisclosedCTA(html);
const c=(id)=>matrix.claims.find(x=>x.id===id);

test('both buyer variants are standalone HTML, in English, with viewport metadata',()=>{
for(const html of [A,B]){assert.match(html,/<!doctype html>/i);assert.match(html,/<html lang="en">/);assert.match(html,/name="viewport"/);}
});
test('both guides specify noindex for source-only copies',()=>{for(const x of [A,B,hub])assert.match(x,/noindex,nofollow/);});
test('buyer guide text is identical apart from optional-film section',()=>assert.equal(removeFilm(A),removeFilm(B)));
test('optional film is native details, no autoplay or broken video source',()=>{
assert.match(B,/<details>/);assert.match(B,/<summary>/);assert.match(B,/Accessible transcript/);assert.match(B,/42-second/);assert.doesNotMatch(B,/<video\b/);
});
test('both guides have same disabled offered checkout',()=>{for(const x of [A,B]){assert.match(x,/<button\b[^>]*\sdisabled(?:\s|>|=)/);assert.match(x,/unavailable pending approval/);}});
test('nearby commission disclosure precedes disabled button',()=>{for(const x of [A,B])assert.equal(missingDisclosedCTA(x),false);});
test('guides avoid scripts, forms, autoplay, trackers and active earning links',()=>{for(const x of [A,B])assert.equal(unsafe(x),false);});
test('guide makes no invented merchant price or exact refund guarantee',()=>{
for(const x of [A,B]){assert.match(x,/No enduring, verified price/);assert.match(x,/no such figure is repeated/);assert.doesNotMatch(x,/(?:\$\s*\d{2,}|60%|EPC\s*\$)/);}
});
test('guide does not present seller benefit assertions as verified effect',()=>{for(const x of [A,B]){assert.match(x,/seller claims/i);assert.match(x,/did not test Zen12/);}});
test('guide provides free alternate route and no new subscription form',()=>{for(const x of [A,B]){assert.match(x,/https:\/\/finalvestige\.com\/focus\//);assert.doesNotMatch(x,/<form\b/i);}});
test('guides distinguish official standard and promo URLs',()=>{
for(const x of [A,B]){assert.match(x,/https:\/\/zen12\.com\/about/);assert.match(x,/https:\/\/zen12\.com\/secret\//);}
});
test('poster is original self-contained accessible SVG',()=>{
assert.match(poster,/<svg\b[^>]+xmlns="http:\/\/www\.w3\.org\/2000\/svg"/);assert.match(poster,/<title/);assert.match(poster,/<desc/);assert.doesNotMatch(poster,/<image\b|<script\b|(?:href|src)=["']https?:\/\//);
});
test('captions have WebVTT header, six sequential cues and end at 42 seconds',()=>{
assert.match(vtt,/^WEBVTT\n/);const cues=[...vtt.matchAll(/(\d\d:\d\d:\d\d\.\d{3}) --> (\d\d:\d\d:\d\d\.\d{3})/g)];assert.equal(cues.length,6);
assert.equal(cues[0][1],'00:00:00.000');assert.equal(cues.at(-1)[2],'00:00:42.000');for(let i=1;i<cues.length;i++)assert.equal(cues[i-1][2],cues[i][1]);
});
test('hub includes all four named research streams and only published live routes',()=>{
for(const s of ['Perception & attention','History of suggestion','Practice & reflection','Tools under review'])assert.ok(hub.includes(s));
assert.match(hub,/https:\/\/finalvestige\.com\/2026\/11\/02\/change-blindness\//);
assert.match(hub,/https:\/\/finalvestige\.com\/2026\/11\/02\/mesmerism\//);
assert.doesNotMatch(hub,/href="[^"]*mind\/r472/);
});
test('hub contains no email forms, buyer links, scripts or third-party embeds',()=>assert.equal(unsafe(hub),false));
test('article is long and contains primary source DOI links',()=>{
assert.ok(article.split(/\s+/).length>=2000);
for(const id of ['10.1068/p281059','10.1068/i0386','10.1177/0956797613479386','10.3758/s13423-023-02431-x'])assert.ok(article.includes(id));
});
test('article states limits and preserves Puységur evidence boundary',()=>{
assert.match(article,/does not mean attention is useless/);
assert.match(article,/not a study of inattentional blindness/);
assert.match(article,/no experimental bridge from missed basketball intruders/);
});
test('claim matrix contains 31 source-linked decisions',()=>{
assert.equal(matrix.claims.length,31);
assert.ok(matrix.claims.filter(x=>x.sources.length>0).length>=27);
});
test('matrix rejects unsupported medical and money outcomes',()=>{
for(const id of ['C07','C08','C15','C16','C19','C27'])assert.match(c(id).decision,/rejected/);
});
test('exact earning link, price and terms are null and activation false',()=>{
assert.equal(matrix.exact_offer.activation,false);
for(const f of ['approved_affiliate_link','approved_merchant_terms','verified_price','verified_refund_terms'])assert.equal(matrix.exact_offer[f],null);
});
test('all 38 release gates held, no false claim of approval',()=>{
assert.equal(matrix.gates.length,38);assert.ok(matrix.gates.every(g=>g.status==='HOLD'));
});
test('publisher approval is distinct from public affiliate program',()=>assert.match(c('C19').limitations,/named acceptance/));
test('owned product is not invented or conflated with the free Fieldbook',()=>{
assert.equal(matrix.fallback_owned_product.sku,null);
assert.equal(matrix.fallback_owned_product.verified_payable,false);
});
test('primary KPI is not computable without settled payment and sessions',()=>{
assert.equal(matrix.measurement.state,'NOT_COMPUTABLE');
assert.match(spec,/1000 \* \(G-R-F\)\/N/);
});
test('runbook matches exactly three creator-topic journeys and no fake asset IDs',()=>{
for(const t of ['Change blindness','Franklin & Mesmer','Invisible gorilla'])assert.ok(spec.includes(t));
assert.match(spec,/No existing matching Grok media IDs/);
});
test('no duplicate site analytics instrumentation was inserted',()=>{
for(const h of [A,B,hub]){assert.doesNotMatch(h,/<script/);assert.doesNotMatch(h,/google-analytics|gtag|analytics\.js|localStorage|document\.cookie/);}
});
test('regression: enabling offer button is rejected by policy',()=>{
assert.equal(safeGuide(A.replace('type="button" disabled','type="button"')),false);
});
test('regression: injected affiliate link is rejected',()=>{
assert.equal(safeGuide(A.replace('</main>','<a href="https://affiliate.example/approved">Buy now</a></main>')),false);
});
test('regression: removed adjacent disclosure is rejected',()=>{
assert.equal(safeGuide(A.replace('Potential commission disclosure','Commercial note')),false);
});
test('regression: added second form or tracking script is rejected',()=>{
assert.equal(safeGuide(A.replace('</main>','<form action="/subscribe"></form></main>')),false);
assert.equal(safeGuide(A.replace('</main>','<script>alert(1)</script></main>')),false);
});
