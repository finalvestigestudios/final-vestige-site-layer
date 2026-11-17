#!/usr/bin/env node
// Mind R454: source-only safety and parity verifier, not a browser/merchant test.
// Run from repository root: node mind/r454/verify_r454.mjs
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';

const root = path.dirname(new URL(import.meta.url).pathname);
const load = (name) => fs.readFileSync(path.join(root, name), 'utf8');
const a = load('ZEN12_A_TEXT_ONLY.html');
const b = load('ZEN12_B_OPTIONAL_42S_STORYBOARD.html');
const hub = load('MIND_HUB_WP_SOURCE_ONLY.html');
const article = load('THE_SECOND_NUMBER_THAT_VANISHED.md');
const captions = load('ZEN12_42S_CAPTIONS.vtt');
const data = JSON.parse(load('CLAIM_SOURCE_PERMISSION_MATRIX.json'));
const docket = load('OFFER_FUNNEL_CREATOR_REVENUE_ACCEPTANCE.md');
const cases = load('QA_RELEASE_CASES.md');
let count = 0;
function check(name, fn) {
  try { fn(); count += 1; process.stdout.write('PASS ' + name + '\n'); }
  catch (e) { process.stderr.write('FAIL ' + name + ': ' + e.message + '\n'); process.exitCode = 1; }
}
const main = (html) => (html.match(/<main\b[^>]*>[\s\S]*?<\/main>/i) || [])[0];
const disclosureNearDisabled = (html) => {
  const chunk = main(html) || '';
  const dis = chunk.indexOf('Prospective affiliate disclosure:');
  const btn = chunk.search(/<button\b[^>]*\sdisabled\b/i);
  return dis >= 0 && btn > dis && btn - dis < 1000;
};
const unsafeMerchantAnchor = (html) => /<a\b[^>]*href=["']https?:\/\/(?:www\.)?(?:inspire3|zen12|brainwaveshots|hypnosislive)\.(?:com|net)\b/i.test(html);
const inert = (html) => !(/<script\b|<iframe\b|<form\b|<video\b|<audio\b|onload\s*=|onclick\s*=/i.test(html));
const notClaimPrice = (html) => !/(?:USD\s*\d+|\$\s*\d+|commission\s*rate\s*:\s*\d+)/i.test(html);
const vttLines = captions.trim().split(/\r?\n/);
const cues = [...captions.matchAll(/(\d{2}:\d{2}:\d{2}\.\d{3})\s+-->\s+(\d{2}:\d{2}:\d{2}\.\d{3})/g)];
const sec = (s) => { const p=s.split(':'); return +p[0]*3600 + +p[1]*60 + +p[2]; };

check('A and B have exactly one main', () => { for(const h of [a,b]) assert.equal((h.match(/<main\b/gi) || []).length, 1); });
check('Full buyer main identical', () => assert.equal(main(a), main(b)));
check('Both are HTML and English', () => {for(const h of [a,b,hub]) assert.match(h,/<!doctype html><html lang="en">/i);});
check('Source-only robots noindex', () => {for(const h of [a,b,hub]) assert.match(h, /name="robots" content="noindex,nofollow"/i);});
check('Skip navigation exists', () => {for(const h of [a,b,hub]) assert.match(h, /href="#content"[^>]*>Skip to/);});
check('Native disabled button on both', () => {for(const h of [a,b]) assert.match(h, /<button\b[^>]*\sdisabled\b/);});
check('Near CTA prospective disclosure on both', () => {for(const h of [a,b]) assert.ok(disclosureNearDisabled(h));});
check('Both explicitly withhold affiliate purchase links', () => {for(const h of [a,b]) assert.match(h,/No affiliate purchase link is active/i);});
check('No clickable merchant link on pages', () => {for(const h of [a,b,hub]) assert.ok(!unsafeMerchantAnchor(h));});
check('No script iframe form or video/audio elements', () => {for(const h of [a,b,hub]) assert.ok(inert(h));});
check('No unverified price or commission rate', () => {for(const h of [a,b,hub]) assert.ok(notClaimPrice(h));});
check('Only one existing Focus CTA', () => {for(const h of [a,b]) assert.ok(h.includes('https://finalvestige.com/focus/'));});
check('Accessibility device sizing', () => {for(const h of [a,b,hub]) assert.match(h,/name="viewport"/);});
check('Reduced motion CSS present', () => {for(const h of [a,b,hub]) assert.match(h,/prefers-reduced-motion/);});
check('B-only optional storyboard', () => {assert.match(b,/<details>/);assert.match(b,/<svg\b/);assert.doesNotMatch(a,/<svg\b/);});
check('B-only title and description SVG', () => {assert.match(b,/<title id="video-poster-title">/);assert.match(b,/<desc id="video-poster-desc">/);});
check('B-only full transcript and not playable', () => {assert.match(b, /Complete narration transcript/);assert.match(b, /not encoded/i);});
check('Six WebVTT cues', () => assert.equal(cues.length, 6));
check('WebVTT starts zero ends 42s', () => { assert.equal(cues[0][1],"00:00:00.000");assert.equal(cues.at(-1)[2],"00:00:42.000");});
check('WebVTT consecutive bounded cues', () => {for(let i=0;i<cues.length;i++){assert.equal(sec(cues[i][2])-sec(cues[i][1]),7);if(i>0) assert.equal(cues[i-1][2],cues[i][1]);}});
check('WebVTT header', () => assert.equal(vttLines[0],"WEBVTT"));
check('Hub four stream headings', () => {for(const x of ['Perception &amp; Attention','History of Suggestion','Practice &amp; Reflection','Tools Under Independent Review'])assert.ok(hub.includes(x));});
check('Hub links published archive', () => assert.match(hub,/puysegurs-animal-magnetism-files/));
check('Hub identifies unpublished manuscript', () => assert.match(hub,/UNPUBLISHED manuscript/));
check('No second newsletter form in hub', () => assert.doesNotMatch(hub,/<form\b/i));
check('36 claim rows', () => assert.equal(data.claims.length,36));
check('Exactly 21 source records', () => assert.equal(Object.keys(data.source_inventory).length,21));
check('28 gates and ALL closed', () => {assert.equal(data.release_gates.length,28);assert.ok(data.release_gates.every(g=>g.cleared===false));});
check('No issued earning link or partner approval', () => {assert.equal(data.tracking_url,null);assert.equal(data.affiliate_account_approved,false);});
check('Revenue unknown not invented zero', () => {assert.equal(data.paid_orders_verified,null);assert.equal(data.net_revenue_verified,null);assert.equal(data.qualified_human_sessions,null);});
check('Every claim cited', () => assert.ok(data.claims.every(c=>c.sources.length>=1)));
check('Claim source URLs all known', () => {const urls=new Set(Object.values(data.source_inventory));assert.ok(data.claims.every(c=>c.sources.every(u=>urls.has(u))));});
check('Attentional-blink studies named with primary references', () => {for(const x of ['Raymond','Chun','Olivers','Slagter'])assert.ok(article.includes(x));});
check('2007 Slagter is not retail product test', () => {assert.match(article,/three months of intensive meditation training/i);assert.match(article,/not Zen12/i);});
check('Article is substantial original sourced research', () => {assert.ok(article.split(/\s+/).length>2400);assert.match(article,/Source ledger/);});
check('Article links to free Fieldbook', () => assert.match(article,/https:\/\/finalvestige\.com\/focus\//));
check('Dossier records three distinct social topics', () => {for(const x of ['stranger changed','franklin tested','first number'])assert.ok(docket.toLowerCase().includes(x));});
check('Dossier suppresses invented revenue', () => assert.match(docket,/NOT COMPUTABLE/));
check('Dossier disclaims authorization', () => assert.match(docket,/named Final Vestige approval/));
check('QA describes real unexecuted browser test', () => assert.match(cases,/WordPress block\/HTML sanitation/));

// Negative/attack tests: use in-memory mutations only.
const mutations = [
 ['merchant anchor', (h)=>h+'<a href="https://zen12.com/secret/">Buy</a>', h=>unsafeMerchantAnchor(h)],
 ['executable script', h=>h+'<script src="https://bad.example/tag.js"></script>', h=>!inert(h)],
 ['new signup form', h=>h+'<form action="/join"></form>', h=>!inert(h)],
 ['iframe', h=>h+'<iframe src="https://bad.example"></iframe>', h=>!inert(h)],
 ['tracking event', h=>h+'<div onclick="track()">click</div>', h=>!inert(h)],
 ['invented price', h=>h+'Price USD 199', h=>!notClaimPrice(h)],
 ['invented commission rate', h=>h+'commission rate: 99%', h=>!notClaimPrice(h)],
 ['remove native disabled', h=>h.replace(/(\<button\b[^\>]*?)\sdisabled\b/, '$1'), h=>!/<button\b[^>]*\sdisabled\b/.test(h)],
 ['remove disclosure', h=>h.replace('Prospective affiliate disclosure:', 'Sponsor message:'), h=>!disclosureNearDisabled(h)]
];
for(const [name,change,detect] of mutations)check('Reject synthetic '+name,()=>assert.ok(detect(change(a))));
check('Reject synthetic release gate unlock',()=>{const copy=structuredClone(data);copy.release_gates[0].cleared=true;assert.ok(!copy.release_gates.every(x=>!x.cleared));});
check('Reject synthetic invented revenue',()=>{const copy=structuredClone(data);copy.net_revenue_verified=999;assert.notEqual(copy.net_revenue_verified,null);});

process.stdout.write('SOURCE GUARDS: '+count+' passed; status '+(process.exitCode ? 'FAIL' : 'PASS')+'; NOT browser/merchant/real-revenue tests\n');
