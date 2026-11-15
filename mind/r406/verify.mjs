#!/usr/bin/env node
import { readFileSync } from 'node:fs';
import assert from 'node:assert/strict';

const read=(name)=>readFileSync(new URL(name,import.meta.url),'utf8');
const A=read('ZEN12_A_TEXT.html');
const B=read('ZEN12_B_OPTIONAL_VISUAL.html');
const hub=read('MIND_HUB_SOURCE_ONLY.html');
const article=read('INDEPENDENT_BUYERS_FIELD_GUIDE.md');
const vtt=read('ZEN12_42S.vtt');
const plan=read('CONVERSION_ACCEPTANCE.md');
const matrix=JSON.parse(read('CLAIM_SOURCE_PERMISSION_MATRIX.json'));
let count=0;
const check=(label,fn)=>{ fn(); count++; console.log('PASS '+label); };
const withoutFilm=(s)=>s.replace(/<section aria-labelledby="film-heading">[\s\S]*?<\/section>/,'').replace(/Variant [AB]/,'Variant X');
check('A/B common buyer copy identical',()=>assert.equal(withoutFilm(A),withoutFilm(B)));
for (const [name,html] of [['A',A],['B',B]]){
  check(name+' valid document skeleton',()=>{assert.match(html,/^<!doctype html><html lang="en">/);assert.match(html,/<main class="page" id="main">/);});
  check(name+' native-disabled merchant button',()=>assert.match(html,/<button type="button" disabled aria-describedby="earn-disclosure">/));
  check(name+' adjacent commission disclosure',()=>{const i=html.indexOf('id="earn-disclosure"'),j=html.indexOf('<button type="button" disabled');assert.ok(i>=0&&j>i&&j-i<650);assert.match(html,/may earn a commission/);});
  check(name+' one existing Focus destination',()=>assert.match(html,/href="https:\/\/finalvestige.com\/focus\/"/));
  check(name+' no merchant checkout anchors',()=>assert.doesNotMatch(html,/<a[^>]+href="https?:\/\/(?:www\.)?(?:zen12|inspire3|hypnosislive|brainwaveshots)\.com/i));
  check(name+' no form, script, onclick or autoplay',()=>assert.doesNotMatch(html,/<form\b|<script\b|\bonclick\s*=|\bonload\s*=|\bautoplay\b/i));
  check(name+' responsive and motion preference',()=>{assert.match(html,/name="viewport"/);assert.match(html,/prefers-reduced-motion/);});
  check(name+' noindex preproduction',()=>assert.match(html,/name="robots" content="noindex,nofollow"/));
}
check('B original and optional not falsely called playable video',()=>{assert.match(B,/<details class="film"><summary>/);assert.match(B,/<svg/);assert.match(B,/NOT a playable encoded video/);});
check('A has no B panel',()=>assert.doesNotMatch(A,/<details class="film">/));
check('VTT six contiguous cues exactly 42 seconds',()=>{const t=[...vtt.matchAll(/(\d\d:\d\d:\d\d\.\d\d\d) --> (\d\d:\d\d:\d\d\.\d\d\d)/g)];assert.equal(t.length,6);assert.equal(t[0][1],'00:00:00.000');assert.equal(t.at(-1)[2],'00:00:42.000');for(let i=1;i<t.length;i++)assert.equal(t[i][1],t[i-1][2]);});
check('VTT transcript parity B',()=>{const t=vtt.replace(/^WEBVTT\s*/,'').replace(/\d\d:\d\d:\d\d\.\d\d\d --> \d\d:\d\d:\d\d\.\d\d\d/g,'').replace(/\s+/g,' ').trim();const b=B.match(/<h3>Complete written transcript<\/h3><p>(.*?)<\/p>/)?.[1];assert.ok(b);assert.equal(t,b.replace(/\s+/g,' ').trim());});
check('hub four editorial streams and no active products',()=>{for(const s of ['Perception & attention','History of suggestion','Practice & reflection','Tools under review'])assert.ok(hub.includes(s));assert.doesNotMatch(hub,/<form\b|<script\b/i);});
check('hub only canonical live content',()=>{for(const s of ['change-blindness/','mesmerism/','puysegurs-animal-magnetism-files/','/focus/'])assert.ok(hub.includes(s));});
check('matrix source references resolved',()=>{const sourceIds=new Set(matrix.sources.map(x=>x.id));assert.ok(matrix.claims.every(x=>sourceIds.has(x.source_id)));});
check('matrix release gates fail closed',()=>{assert.equal(matrix.sources.length,16);assert.equal(matrix.claims.length,28);assert.equal(matrix.gates.length,29);assert.ok(matrix.gates.every(x=>x.state==='HOLD'&&x.evidence===null));});
check('substantive guide seller/research/history mix',()=>{for(const s of ['Zen12','Total Focus','Focus Shot','Puységur','10.1016/j.concog.2024.103730','10.1016/j.concog.2025.103948'])assert.ok(article.includes(s));});
check('conversion reporting segregates funnel events',()=>{for(const s of ['affiliate_click','merchant_confirmed_paid_conversion','NOT COMPUTABLE','ut m_source'.replace(' ',''),'refunds'])assert.ok(plan.includes(s));});
check('no product efficacy borrowed from old research',()=>assert.ok(matrix.claims.filter(x=>x.decision==='EXCLUDE').length>=10));
console.log(count+' source-only checks PASS. NOT a browser, CMS, consumer checkout, affiliate acceptance or merchant revenue test.');
