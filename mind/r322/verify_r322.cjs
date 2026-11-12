#!/usr/bin/env node
'use strict';
/* Mind R322 deterministic STATIC source review, not browser, hosted CI or merchant proof.
 * Usage: node mind/r322/verify_r322.cjs
 * No network, API keys, PII, external packages, writes or tracking. */
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const root = __dirname;
const load = name => fs.readFileSync(path.join(root, name), 'utf8');
const a=load('ZEN12-A-TEXT-REVIEW.html');
const b=load('ZEN12-B-OPTIONAL-42S-REVIEW.html');
const hub=load('MIND-ARCHIVE-WP-REVIEW-ONLY.html');
const vtt=load('ORIGINAL-42S-CAPTIONS.vtt');
const article=load('THE-COLOR-THE-SCREEN-NEVER-HAD-UNPUBLISHED.md');
const raw=load('SOURCE-CLAIM-PRODUCT-AND-COMMERCIAL-GATES.json');
const matrix=JSON.parse(raw);
const proof=load('CONVERSION-EXPERIMENT-AND-RELEASE-ACCEPTANCE.md');
const filmSection=/<section class="section" aria-labelledby="film-title">[\s\S]*?<\/section>/;
const stripFilm=x=>x.replace(filmSection,'');
function guard(html){
 assert.match(html,/lang="en"/,'document language absent');
 assert.match(html,/name="viewport"/,'responsive viewport absent');
 assert.match(html,/noindex,nofollow/,'review prototype accidentally indexable');
 assert.match(html,/href="#main"/,'skip link absent');
 assert.match(html,/:focus-visible/,'visible keyboard focus missing');
 assert.match(html,/prefers-reduced-motion/,'reduced motion override missing');
 assert.doesNotMatch(html,/<script\b|\bon(?:load|click|error)=/i,'scripts/inline events prohibited');
 assert.doesNotMatch(html,/<form\b/i,'new/duplicated email form prohibited');
 assert.doesNotMatch(html,/<(?:audio|video)[^>]*\bautoplay\b/i,'autoplay prohibited');
 assert.doesNotMatch(html,/<(?:iframe|img)[^>]*src=["']https?:/i,'external media/embed prohibited');
 assert.doesNotMatch(html,/<a[^>]*href=["'][^"']*(?:affiliates?\.inspire3|inspire3\.com|zen12\.com|brainwaveshots\.com|hypnosislive\.com)/i,'merchant links remain withheld');
 assert.match(html,/<button\s+disabled\s+type="button"|<button\s+type="button"\s+disabled/,'disabled CTA required');
 assert.match(html,/(?:Prospective affiliate disclosure|Prospective commission disclosure)/,'clear commercial disclosure required');
 assert.match(html,/(?:may earn a commission|may receive a commission)/,'real-language commission disclosure missing');
 assert.match(html,/(?:no (?:affiliate|earning) link is active|None is active)/i,'non-activation must be explicit');
 assert.ok(html.indexOf('commission')<html.indexOf('<button'),'disclosure must precede CTA');
 assert.match(html,/href="\/focus\/"/,'original free resource preserved');
 assert.doesNotMatch(html,/guaranteed concentration|guarantees? (?:a|the) cure|proven (?:Zen12|concentration)|one hour of meditation in 12 minutes/i,'unsupported outcome promise');
 assert.doesNotMatch(html,/localStorage|sessionStorage|document\.cookie|fingerprint|pixel\.gif|analytics\.js/i,'unapproved instrumentation');
}
guard(a);guard(b);guard(hub);
assert.equal(stripFilm(b),a,'A/B should be identical outside optional original 42s storyboard');
assert.match(b,/role="img"/);assert.match(b,/<desc id="pd">/);assert.match(b,/<details>/);assert.match(b,/NOT playable/);
assert.equal((hub.match(/href="\/focus\/"/g)||[]).length,1,'hub should use one focus path');
assert.match(vtt,/^WEBVTT\s/);
assert.match(vtt,/00:00:00\.000 --> 00:00:07\.000/);
assert.match(vtt,/00:00:35\.000 --> 00:00:42\.000/);
assert.equal((vtt.match(/ --> /g)||[]).length,6,'6 narration caption segments');
assert.match(article,/eight highly hypnotizable/i);
assert.match(article,/\[P1\]/);assert.match(article,/\[H3\]/);
assert.match(article,/(?:not|None is) evidence that a particular consumer recording works/i);
assert.equal(matrix.gates.length,18);
assert.ok(matrix.gates.every(g=>g.status==='HOLD' && g.verified===false),'all authorization gates closed');
assert.equal(matrix.offer_fit.length,3);
assert.ok(matrix.offer_fit.every(v=>v.actual_grok_asset_id===null),'never invent Grok IDs');
assert.ok(matrix.vendor_products.every(v=>v.fv_earning_url===null),'never invent earning URLs');
assert.equal(matrix.realized_net_revenue_per_1000_qualified_sessions,null);
assert.ok(matrix.sources.length>=20);
assert.ok(matrix.claims.length>=25);
const ids=new Set(matrix.sources.map(x=>x.id));
assert.ok(matrix.claims.every(c=>c.source_ids.every(s=>ids.has(s))),'every claim source resolves');
assert.ok(matrix.claims.filter(x=>x.action==='REJECT').length>=8,'unsupported claims quarantined');
assert.match(proof,/merchant_confirmed_purchase/);assert.match(proof,/affiliate_outbound/);
assert.match(proof,/NET REVENUE/);assert.match(proof,/NOT COMPUTABLE/);
let negatives=0;
const unsafeMutations=[
 x=>x.replace('</body>','<script src="https://example.org/t.js"></script></body>'),
 x=>x.replace('</body>','<form><input type="email"></form></body>'),
 x=>x.replace('disabled type="button"','type="button"'),
 x=>x.replace('noindex,nofollow','index,follow'),
 x=>x.replace('href="/focus/"','href="https://zen12.com/getstarted"'),
 x=>x.replace(/<p class="disclosure">[\s\S]*?<\/p>/,''),
 x=>x.replace('may earn a commission','may get something'),
 x=>x.replace('No affiliate link is active','An earning link is active'),
 x=>x.replace('prefers-reduced-motion','prefers-normal-motion'),
 x=>x.replace(/:focus-visible/g,':hover'),
 x=>x.replace('href="#main"','href="#other"'),
 x=>x.replace('</main>','<iframe src="https://example.org/pixel"></iframe></main>'),
 x=>x.replace('</main>','<video autoplay></video></main>'),
 x=>x.replace('</main>','<img src="https://example.org/tracker.png"></main>'),
 x=>x.replace('</main>','<script>localStorage.setItem("v","1")</script></main>'),
 x=>x.replace('lang="en"','lang=""'),
 x=>x.replace('guaranteed concentration','guaranteed concentration'), // no-op negative excluded below
];
for(const [i,mutate] of unsafeMutations.entries()){
 if(i===16)continue;
 const bad=mutate(a);
 try{guard(bad)}catch{negatives++;continue;}
 throw new Error('Unsafe mutation unexpectedly accepted: '+i);
}
console.log('R322 static baseline PASS; claim/matrix checks PASS; unsafe mutations rejected '+negatives+'/16.');
console.log('LIMITS: Node source checks are not WCAG browser QA, WordPress sanitization, runnable video, authenticated merchant agreement or paid purchase proof.');
