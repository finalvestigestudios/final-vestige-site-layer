// Run: node --test mind/r465/qa.test.cjs
// Static offline gates only; does not test real browsers, merchant systems or subscriptions.
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const load=n=>fs.readFileSync(path.join(__dirname,n),'utf8');
const A=load('ZEN12_A_BUYER_GUIDE.html'),B=load('ZEN12_B_OPTIONAL_FILM_GUIDE.html'),m=JSON.parse(load('CLAIM_SOURCE_PARTNER_MATRIX.json'));
test('both variants have inert purchase button and adjacent disclosure',()=>{for(const s of [A,B]){assert.match(s,/<button type="button" disabled/);let i=s.indexOf('Affiliate disclosure:'),j=s.indexOf('<button type="button" disabled');assert(i>0&&j>i&&j-i<700);assert.match(s,/No affiliate purchase link is active here/)}});
test('no remote scripts, third party embeds, live video, forced playback',()=>{for(const s of [A,B]){assert.doesNotMatch(s,/<script\b|<iframe\b|<video\b[^>]*src=|<form\b|autoplay\s*=/i);assert.match(s,/<html lang="en"/)}});
test('identical substantive guide content across A/B',()=>{for(const k of ['id="offer-facts"','id="free-trial"','id="questions"','id="limits"','id="decision"']){let sec=s=>s.match(new RegExp('<section '+k+'[\\s\\S]*?<\\/section>'))?.[0];assert(sec(A));assert.equal(sec(A),sec(B))}});
test('optional film is not misrepresented as working',()=>{assert.match(B,/storyboard, not a playable film/);assert.match(B,/<details>/);assert.match(B,/<svg/);assert.doesNotMatch(A,/<svg/)}});
test('caption cues are six through 42 seconds',()=>{const s=load('ZEN12_OPTIONAL_FILM_42S.vtt');assert(s.startsWith('WEBVTT'));assert.equal((s.match(/-->/g)||[]).length,6);assert.match(s,/00:00:42\.000/)});
test('all P0 merchant gates false',()=>{for(const k of ['named_publisher_approval','exact_sku_authorization','issued_earning_link','merchant_paid_order_receipt','qualified_human_sessions_verified'])assert.equal(m.release_gates[k],false)});
test('matrix provides seller vs independent and counters',()=>{assert(m.claims.length>=25);assert(m.claims.some(x=>x.id==='SCI-05'&&x.evidence_class==='COUNTEREVIDENCE'));assert(m.claims.some(x=>x.id==='ZEN-06'&&x.decision.startsWith('Exclude')))});
test('WP hub uses real existing sources with no duplicated signup',()=>{const h=load('MIND_HUB_WORDPRESS_SOURCE_ONLY.html');assert.match(h,/finalvestige.com\/focus\//);assert.match(h,/puysegurs-animal-magnetism-files/);assert.doesNotMatch(h,/<form\b|<script\b/i)});
test('investigation has primary links and uncertainty boundaries',()=>{const s=load('THE_WORD_YOU_SAW_TWICE.md');assert((s.match(/https:\/\/pubmed.nih.gov\//g)||[]).length>=7);assert.match(s,/Armstrong and Mewhort/);assert.match(s,/not a demonstration/);assert.match(s,/Puységur/)});
test('privacy plan separates affiliate click from verified order',()=>{const s=load('CREATOR_CONVERSION_ACCEPTANCE.md');for(const k of ['affiliate_click','merchant-reported confirmed order','NOT COMPUTABLE','utm_content','refunds/fees'])assert(s.includes(k))});
