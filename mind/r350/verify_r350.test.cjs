// node --test mind/r350/verify_r350.test.cjs
// Static source-acceptance checks only. No browser, WP, merchant, or efficacy testing.
'use strict';
const test=require('node:test');const assert=require('node:assert/strict');const fs=require('node:fs');const path=require('node:path');
const root=__dirname,read=n=>fs.readFileSync(path.join(root,n),'utf8');
const a=read('ZEN12_A_TEXT_ONLY.html'),b=read('ZEN12_B_OPTIONAL_42S.html'),hub=read('MIND_HUB_WP_SOURCE_ONLY.html'),film=read('42S_CAPTIONS_CONCEPT.vtt');
const claims=JSON.parse(read('CLAIM_SOURCE_AUTHORIZATION_MATRIX.json'));
function compact(s){return s.replace(/\s+/g,' ').trim()}
function withoutOptional(s){return s.replace(/<section class="panel" id="optional-film"[\s\S]*?<\/section>/,'')}
test('evidence matrix has 30 independently classified source claims',()=>{assert.equal(claims.claims.length,30);assert.ok(Object.keys(claims.sources).length>=16);for(const c of claims.claims){assert.ok(c.claim);assert.ok(c.source_ids.every(id=>claims.sources[id]))}});
test('all 30 release gates held',()=>{assert.equal(Object.keys(claims.release_gates).length,30);assert.ok(Object.values(claims.release_gates).every(x=>x==='HOLD'))});
for(const [name,html] of [['A',a],['B',b]]) {
 test(name+' fixed-content disclosure immediately before disabled CTA',()=>{const d=html.indexOf('Affiliate disclosure for any future earning link');const btn=html.indexOf('disabled aria-disabled="true"');assert.ok(d>0&&btn>d&&btn-d<700)});
 test(name+' no active merchant purchase link',()=>{assert.doesNotMatch(html,/<a[^>]+href="(?:https?:\/\/)?(?:www\.)?(?:zen12\.com\/checkout|affiliates\.inspire3\.com\/click|hop\.clickbank\.net)/i);assert.match(html,/Merchant offer unavailable — approval required/)});
 test(name+' no JS, form or autoplay',()=>{assert.doesNotMatch(html,/<script\b|<form\b|<iframe\b/i);assert.doesNotMatch(html,/<(?:video|audio)\b[^>]*\bautoplay\b/i)});
 test(name+' no unsubstantiated efficacy endorsement',()=>{assert.match(html,/not found independently verified product-specific evidence/);assert.match(html,/neither choice requires believing|No checkout or affiliate link is active/i)});
 test(name+' preserves one live Focus path and separate merchant newsletter',()=>{assert.match(html,/https:\/\/finalvestige\.com\/focus\//);assert.match(html,/merchant's newsletter/)});
 test(name+' basic accessibility',()=>{assert.match(html,/<html lang="en"/);assert.match(html,/<meta name="viewport"/);assert.match(html,/:focus-visible/);assert.match(html,/@media\(prefers-reduced-motion:reduce\)/);assert.match(html,/aria-disabled="true"/)});
}
test('text/video variants share identical original buyer copy',()=>assert.equal(compact(withoutOptional(b)),compact(a)));
test('film is voluntary, textual and no remote media',()=>{assert.match(b,/id="optional-film"/);assert.match(b,/<details>/);assert.doesNotMatch(b,/<video\b|<iframe\b|<audio\b/i)});
test('VTT six monotonic cues ending 42 seconds',()=>{assert.match(film,/^WEBVTT/);const m=[...film.matchAll(/\d\d:\d\d:\d\d\.\d{3} --> \d\d:\d\d:\d\d\.\d{3}/g)];assert.equal(m.length,6);assert.match(film,/00:00:35.000 --> 00:00:42.000/)});
test('hub includes four streams and published not imaginary links',()=>{for(const t of ['Perception &amp; Attention','History of Suggestion','Practice &amp; Reflection','Tools Under Review'])assert.ok(hub.includes(t));assert.doesNotMatch(hub,/<script\b|<form\b/i);assert.match(hub,/not published/)});
test('no manufactured revenue or live activation',()=>{const m=read('CONVERSION_ACCEPTANCE.md');assert.match(m,/NOT COMPUTABLE/);assert.match(m,/HARD HOLD/);assert.match(m,/qualified_human_sessions/);assert.match(m,/no login|no login/i)});
