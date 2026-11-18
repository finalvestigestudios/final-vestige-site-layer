// Portable native Node source tests; authored for CI but DO NOT claim executed unless a Node runner records exit 0.
// Usage from repository root: node --test mind/r457/RELEASE_GATES.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
const root = new URL('.', import.meta.url);
const get = name => readFileSync(new URL(name,root),'utf8');
const a=get('ZEN12_A_TEXT.html'), b=get('ZEN12_B_OPTIONAL_42S.html');
const matrix=JSON.parse(get('CLAIM_SOURCE_PARTNER_MATRIX.json'));
const guide = s => s.match(/<section id="buyer-guide"[\s\S]*?<\/section>/)?.[0];
test('identical substantive buyer copy',()=>assert.equal(guide(a),guide(b)));
for(const [label,s] of [['A',a],['B',b]]){
 test(label+' native disabled merchant button',()=>assert.match(s,/<button\s+type="button"\s+disabled\s+aria-describedby="notavailable">/));
 test(label+' disclosure in same offer block',()=>assert.match(s,/<div class="offer"[\s\S]*?<p class="disclosure"[\s\S]*?may earn a commission[\s\S]*?<button/));
 test(label+' no scripts forms tracking pixels or affiliate URLs',()=>{assert.doesNotMatch(s,/<script|<form|<iframe|<video|<audio|dataLayer|gtag\(|fbq\(|rel="sponsored"|href="https:\/\/affiliates\.inspire3\.com/i);});
 test(label+' pages are noindex',()=>assert.match(s,/name="robots" content="noindex,nofollow"/));
}
test('B contains original poster and explanation concept',()=>{assert.match(b,/ZEN12_42S_POSTER.svg/);assert.match(b,/No video file is embedded or autoplayed/);});
test('caption file full 42s',()=>{const v=get('ZEN12_42S_CAPTIONS.vtt');assert.match(v,/WEBVTT/);assert.equal((v.match(/ --> /g)||[]).length,6);assert.match(v,/00:00:35.000 --> 00:00:42.000/);});
test('poster has no foreign resources or script',()=>{const v=get('ZEN12_42S_POSTER.svg');assert.match(v,/<svg/);assert.doesNotMatch(v,/<script|<foreignObject|<image|https?:\/\//i);});
test('all release gates explicitly HOLD',()=>{assert.ok(matrix.release_gates.length>=25);assert.ok(matrix.release_gates.every(g=>g.status==='HOLD'));assert.equal(matrix.partner_acceptance_verified,false);assert.equal(matrix.authorized_tracking_url,null);});
test('research not represented as product efficacy',()=>{assert.ok(matrix.claims.some(c=>c.id==='C19' && c.treatment==='exclude'));});
test('one existing Focus route, no second form in hub',()=>{const h=get('MIND_HUB_WP_SOURCE_ONLY.html');assert.match(h,/https:\/\/finalvestige\.com\/focus\//);assert.doesNotMatch(h,/<form|<script|<iframe/);});
test('core editorial sources and disclosure references present',()=>{const s=get('THE_CHOICE_YOU_NEVER_MADE.md');assert.match(s,/16210542/);assert.match(s,/20637455/);assert.match(s,/4033137/);assert.match(s,/Puységur/);});
test('do not treat missing revenue as zero',()=>{const p=get('CONVERSION_AND_ATTRIBUTION_ACCEPTANCE.md');assert.match(p,/UNKNOWN/,);assert.match(p,/not zero/);});
