// Portable read-only test suite. Run: node --test mind/r458/QA_GATES.test.mjs
// This suite is source-only. It cannot certify real browsers, legal permission, sales, or WordPress.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname,join} from 'node:path';
const d=dirname(fileURLToPath(import.meta.url));
const read=(x)=>readFileSync(join(d,x),'utf8');
const a=read('ZEN12_A_TEXT_ONLY.html'),b=read('ZEN12_B_OPTIONAL_42S_CONCEPT.html');
const hub=read('MIND_HUB_WP_SOURCE_ONLY.html');
const poster=read('ZEN12_42S_ORIGINAL_POSTER.svg'),vtt=read('ZEN12_42S_CAPTIONS.vtt');
const matrix=JSON.parse(read('CLAIM_SOURCE_MERCHANT_MATRIX.json'));
const plan=read('OFFER_FUNNEL_EXPERIMENT_ACCEPTANCE.md');
const article=read('THE_SECOND_TARGET_THAT_VANISHED.md');
const videoSection=/<section class="card" aria-labelledby="film">[\s\S]*?<\/section>/;
const prohibited=/<script\b|<iframe\b|<form\b|\son\w+\s*=|<video\b[^>]*autoplay|https?:\/\/(?:www\.)?(?:track|pixel)\./i;
for(const [name,html] of [['A',a],['B',b],['hub',hub]]){
 test(name+' valid document skeleton',()=>{assert.match(html,/^<!doctype html>/i);assert.match(html,/<html lang="en">/);assert.match(html,/<main id="main">/);assert.match(html,/<a class="skip" href="#main">/);});
 test(name+' zero tracking/form/autoplay',()=>assert.doesNotMatch(html,prohibited));
 test(name+' mobile + accessibility preflight syntax',()=>{assert.match(html,/name="viewport"/);assert.match(html,/focus-visible/);assert.match(html,/<h1>/);});
}
for(const [name,html] of [['A',a],['B',b]]){
 test(name+' disabled native CTA',()=>assert.match(html,/<button type="button" disabled aria-describedby="hold">/));
 test(name+' adjacent explicit commission disclosure',()=>{const disclosure=html.indexOf('may earn a commission');const button=html.indexOf('<button type="button" disabled');assert.ok(disclosure>0&&button>disclosure&&button-disclosure<700);});
 test(name+' no active merchant destination',()=>assert.doesNotMatch(html,/<a[^>]+href=["'][^"']*(?:zen12\.com|inspire3\.com|hypnosislive\.com|brainwaveshots\.com)/i));
 test(name+' free alternative and seller caution',()=>{assert.match(html,/finalvestige\.com\/focus\//);assert.match(html,/not established/i);});
}
test('B differs from A only by optional static video section',()=>assert.equal(b.replace(videoSection,''),a));
test('B has no video playback claim',()=>{assert.match(b,/Not.*embedded player|No embedded player/);assert.match(b,/42-second film concept/);});
test('poster self-contained SVG',()=>{assert.match(poster,/<svg[^>]+xmlns="http:\/\/www.w3.org\/2000\/svg"/);assert.doesNotMatch(poster,/<script|<image|<foreignObject|href\s*=|@import/i);});
test('captions exactly six cues through 42s',()=>{assert.equal((vtt.match(/-->/g)||[]).length,6);assert.match(vtt,/00:00:35\.000 --> 00:00:42\.000/);});
test('all merchant release gates held',()=>assert.ok(matrix.releaseGates.length>=25&&matrix.releaseGates.every(g=>g.status==='HOLD')));
test('no merchant approval is falsely represented',()=>assert.ok(matrix.claims.some(c=>c.id==='P-01'&&c.status==='UNVERIFIED')));
test('seller claims explicitly not supported',()=>assert.ok(matrix.claims.some(c=>c.id==='S-06'&&c.status.startsWith('NOT'))));
test('source matrix references FTC and independent research',()=>assert.ok(matrix.claims.some(c=>c.source?.includes('ftc.gov'))&&matrix.claims.some(c=>c.source?.includes('pubmed.ncbi.nlm.nih.gov'))));
test('article links primary sources and limits branded extrapolation',()=>{assert.match(article,/pubmed\.ncbi\.nlm\.nih\.gov\/1500880/);assert.match(article,/pubmed\.ncbi\.nlm\.nih\.gov\/17488185/);assert.match(article,/not a Zen12 trial/i);});
test('conversion plan distinguishes paid merchant evidence from clicks',()=>{assert.match(plan,/Click does not equal sale/i);assert.match(plan,/settled affiliate commission/);assert.match(plan,/NOT COMPUTABLE/i);});
test('no duplicate Jetpack list in hub',()=>{assert.match(hub,/One existing Jetpack\/Dispatch welcome route/);assert.doesNotMatch(hub,/<form\b/);});
test('no fabricated measurable social media IDs',()=>assert.match(plan,/UNKNOWN asset_id/));
test('preserves owner boundaries',()=>{assert.match(plan,/PR #49/);assert.match(plan,/PR #172/);assert.match(plan,/Issue #150/);});
