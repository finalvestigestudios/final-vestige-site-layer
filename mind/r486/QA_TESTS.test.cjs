'use strict';
// Reproducible static-source regression tests for isolated Mind r486.
// Run from repository root: node --test mind/r486/QA_TESTS.test.cjs
// Requires Node >=18; built-in APIs only; no network, merchant API, browser or CMS calls.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const base = __dirname;
const text = f => fs.readFileSync(path.join(base,f),'utf8');
const A = text('ZEN12_A_TEXT_ONLY.html');
const B = text('ZEN12_B_OPTIONAL_42S_STORYBOARD.html');
const vtt = text('ZEN12_OPTIONAL_42S_CAPTIONS.vtt');
const article = text('THE_WHITE_BEAR_THAT_WOULD_NOT_LEAVE.md');
const hub = text('MIND_HUB_SOURCE_ONLY_GUTENBERG.html');
const matrix = JSON.parse(text('CLAIMS_SOURCES_PERMISSIONS_AND_RELEASE_GATES.json'));
const docket = text('OFFER_FUNNEL_CREATOR_CROSSWALK_AND_REVENUE_ACCEPTANCE.md');
const buyerCore = s => {const m=s.match(/<div id="buyer-core" data-buyer-core="zen12-independent-v1">([\s\S]*?)<\/div>/);assert.ok(m,'buyer core missing');return m[1]};
function rejectLiveMerchantAnchor(s){assert.doesNotMatch(s,/<a\b[^>]*href=["']https?:\/\/(?:www\.)?(?:inspire3|zen12)\.com/i)}
function disabledCTA(s){assert.match(s,/<button\b[^>]*\bdisabled\b[^>]*>Visit verified Zen12 offer/);assert.doesNotMatch(s,/<a\b[^>]*>\s*Visit verified Zen12 offer/)}
test('buyer core is exactly identical in A/B',()=>assert.equal(buyerCore(A),buyerCore(B)));
test('A is text-only; B is explicitly a storyboard rather than playable film',()=>{
 assert.doesNotMatch(A, /class="film"/);
 assert.match(B,/class="film"/);
 assert.match(B,/concept, not playable/i);
 assert.match(B,/<svg\b/);
 assert.match(B,/<title id="film-title">/);
 assert.match(B,/<desc id="film-desc">/);
 assert.doesNotMatch(B,/<video\b|<iframe\b|\sautoplay(?:\s|=|>)/i);
});
test('all buyer pages have natively disabled purchase control',()=>[A,B].forEach(disabledCTA));
test('no clickable merchant link or checkout on buyer pages',()=>[A,B].forEach(rejectLiveMerchantAnchor));
test('no Javascript, forms or remote resource requests in buyers',()=>[A,B].forEach(s=>assert.doesNotMatch(s,/<script\b|<form\b|<iframe\b|<img\b[^>]*src=|<link\b[^>]*href=/i)));
test('FTC material connection is adjacent to purchase control',()=>[A,B].forEach(s=>{
 const d=s.indexOf('Prospective affiliate disclosure:');
 const b=s.indexOf('Visit verified Zen12 offer');
 assert.ok(d>=0&&b>d&&b-d<650,'disclosure must sit near disabled purchase control');
 assert.match(s,/may earn a commission if you purchase/);
}));
test('independently useful free alternative remains available',()=>[A,B].forEach(s=>assert.match(s,/href="https:\/\/finalvestige.com\/focus\/"/)));
test('seller claim limitations and exact offer differentiation are present',()=>[A,B].forEach(s=>{
 for(const token of ['Beginner','Premium','Advanced','scientific','money-back','actual written policy','twelve-minute','no guaranteed price']) assert.ok(s.toLowerCase().includes(token.toLowerCase()),token);
}));
test('B transcript contains six 7-second intervals',()=>{
 assert.ok((B.match(/<strong>00:\d\d–00:\d\d/g)||[]).length===6);
 assert.ok(vtt.startsWith('WEBVTT\n'));
 assert.equal((vtt.match(/-->/g)||[]).length,6);
 assert.match(vtt,/00:00:35\.000 --> 00:00:42\.000/);
});
test('article has >=1800 words and source boundaries',()=>{
 assert.ok(article.trim().split(/\s+/).length>=1800);
 for(const token of ['Wegner','1993','2020','31 studies','Puységur','standardized experiment','affiliate purchase link','S10'])assert.ok(article.includes(token),token);
});
test('hub remains four-stream and links only to confirmed FV destinations',()=>{
 for(const token of ['Perception &amp; attention','History of suggestion','Practice &amp; reflection','Tools under review','https://finalvestige.com/focus/','/puysegurs-animal-magnetism-files/'])assert.ok(hub.includes(token),token);
 assert.doesNotMatch(hub,/<form\b|<script\b/i);
 assert.doesNotMatch(hub,/<a\b[^>]*href=["']https?:\/\/(?:www\.)?(?:zen12|inspire3)\.com/i);
});
test('matrix retains commercial gate and rejects efficacy guarantee',()=>{
 assert.ok(matrix.claims.length>=20);
 assert.ok(matrix.gates.length>=25);
 assert.equal(matrix.commercial_url,null);
 assert.notEqual(matrix.partner_approved,true);
 assert.ok(matrix.claims.some(x=>x.id==='zen12-equivalence'&&x.status.startsWith('REJECT')));
 assert.ok(matrix.gates.some(x=>x.id==='partner_named_approval'&&x.status==='hold'));
});
test('no invented revenue or published creator IDs',()=>{
 assert.match(docket,/NOT COMPUTABLE|not computable/i);
 assert.match(docket,/UNKNOWN — obtain from Grok/);
 assert.match(docket,/merchant_confirmed_purchase/);
 assert.match(docket,/settled_affiliate_commission/);
});
test('basic accessibility and no-JS contract survives',()=>{
 [A,B].forEach(s=>{assert.match(s,/<html lang="en">/);assert.match(s,/<meta name="viewport"/);assert.match(s,/:focus-visible/);assert.match(s,/prefers-reduced-motion/);assert.match(s,/<h1>/);assert.match(s,/name="robots" content="noindex,nofollow"/);});
});
