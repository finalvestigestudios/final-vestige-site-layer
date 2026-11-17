// R450 reproducible source-level guard. Run from repository: node mind/r450/check_r450.mjs
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
const root=dirname(fileURLToPath(import.meta.url));const read=n=>readFileSync(join(root,n),'utf8');
const article=read('THE_STRANGER_THROUGH_THE_DOOR.md'),a=read('ZEN12_A_TEXT.html'),b=read('ZEN12_B_FILM_CONCEPT.html'),hub=read('MIND_HUB_WORDPRESS_SOURCE_ONLY.html'),poster=read('ZEN12_42S_POSTER.svg'),vtt=read('ZEN12_42S_CAPTIONS.vtt'),matrix=JSON.parse(read('CLAIM_SOURCE_PERMISSION_MATRIX.json')),plan=read('OFFER_CREATOR_REVENUE_ACCEPTANCE.md');
let count=0;function test(name,fn){fn();++count;console.log('PASS '+count+' '+name)}
const body=x=>x.slice(x.indexOf('<main id="content"'),x.indexOf('</main>')+7);
for(const [name,html] of [['A',a],['B',b],['hub',hub]]){
 test(name+' html',()=>assert.match(html,/^<!doctype html>/i));
 test(name+' language',()=>assert.match(html,/<html lang="en"/));
 test(name+' viewport',()=>assert.match(html,/name="viewport"/));
 test(name+' one main',()=>assert.equal((html.match(/<main\b/g)||[]).length,1));
 test(name+' no JS forms external trackers',()=>assert.doesNotMatch(html,/<script\b|<iframe\b|<form\b|<input\b|<img[^>]+src=["']https?:|onload\s*=|onclick\s*=|googletagmanager|facebook\.com\/tr\//i));
 test(name+' keyboard focus',()=>assert.match(html,/:focus-visible/));
 test(name+' responsive',()=>assert.match(html,/@media\(max-width:/));
 test(name+' reduced motion',()=>assert.match(html,/prefers-reduced-motion/));
 test(name+' not indexable as live',()=>assert.match(html,/noindex,nofollow/));
}
for(const [name,html] of [['A',a],['B',b]]){
 test(name+' native disabled',()=>assert.match(html,/<button\b[^>]*\sdisabled(?:\s|=|>)/i));
 test(name+' no merchant affiliate href',()=>assert.doesNotMatch(html,/<a\b[^>]*href=["']https?:\/\/(?:www\.)?(?:affiliates\.inspire3|inspire3|zen12|hypnosislive|brainwaveshots)\.[^"']*(?:ref=|aff=|affiliate=|utm_)/i));
 test(name+' exact near-link disclosure',()=>{const x=html.indexOf('Potential affiliate disclosure:');const y=html.indexOf('<button',x);assert.ok(x>0&&y>x&&y-x<650)});
 test(name+' none of the unsupported advertised outcomes',()=>assert.doesNotMatch(html,/guaranteed (?:wealth|healing|brain rewiring)|12 minutes equals an hour of meditation/i));
 test(name+' no forced media playback',()=>assert.doesNotMatch(html,/<video\b|<audio\b|\bautoplay\b/i));
 test(name+' free Focus',()=>assert.match(html,/https:\/\/finalvestige\.com\/focus\//));
}
test('identical substantive buyer guide',()=>assert.equal(body(a),body(b)));
test('A no film concept',()=>assert.doesNotMatch(a,/id="film-concept"/));
test('B optional film',()=>assert.match(b,/id="film-concept"/));
test('B local poster',()=>assert.match(b,/src="\.\/ZEN12_42S_POSTER\.svg"/));
test('B full transcript',()=>assert.match(b,/full 42-second spoken transcript/));
test('SVG inert and accessible',()=>{assert.match(poster,/<title id="title">/);assert.doesNotMatch(poster,/<script|<foreignObject|onload=|xlink:href|<image\b/i)});
test('VTT six timings',()=>{assert.match(vtt,/^WEBVTT/);assert.equal((vtt.match(/-->/g)||[]).length,6);assert.match(vtt,/00:00:42\.000/)});
test('hub four named streams',()=>['Perception & Attention','History of Suggestion','Practice & Reflection','Tools Under Review'].forEach(s=>assert.ok(hub.includes(s),s)));
test('hub warns unpublished routes',()=>assert.match(hub,/no invented live URL/));
test('primary article research DOI links',()=>['10.3758/BF03208840','10.1111/j.1467-9280.1997.tb00427.x','10.1068/p3104'].forEach(s=>assert.ok(article.includes(s),s)));
test('article source-limits and historical bridge',()=>{assert.match(article,/Puységur/);assert.match(article,/not evidence that Puységur/);assert.match(article,/not a product efficacy trial/i)});
test('claims and counts',()=>{assert.equal(matrix.claim_count,matrix.claims.length);assert.equal(matrix.release_gate_count,matrix.release_gates.length)});
test('claim IDs unique and sources mapped',()=>{const ids=new Set(matrix.sources.map(s=>s.id));assert.equal(new Set(matrix.claims.map(x=>x.id)).size,matrix.claim_count);matrix.claims.forEach(c=>c.source_ids.forEach(id=>assert.ok(ids.has(id),id)))});
test('28 closed gates',()=>{assert.equal(matrix.release_gates.length,28);assert.ok(matrix.release_gates.every(x=>x.passed===false))});
test('no commercial activation',()=>['affiliate_approval_verified','owned_paid_mind_sku_verified','paid_transaction_evidence','qualified_human_denominator_verified','referral_url_activated'].forEach(k=>assert.equal(matrix[k],false)));
test('plan financial distinction',()=>{assert.match(plan,/affiliate_click/);assert.match(plan,/merchant_confirmed_paid_order/);assert.match(plan,/net_per_1000_qualified_sessions/);assert.match(plan,/NOT COMPUTABLE/)});
test('plan publisher ownership',()=>{assert.match(plan,/Grok/);assert.match(plan,/Jetpack/);assert.match(plan,/founder authorization/i)});
console.log('PASS ALL '+count+' source-only checks; browser/CI/WordPress/merchant tests NOT RUN');