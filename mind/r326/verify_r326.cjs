#!/usr/bin/env node
'use strict';
// FV Mind R326 source-only guard. Run: node mind/r326/verify_r326.cjs
// This script performs structural/source checks; it is NOT a browser, CI, payment, consent, or WP test.
const fs=require('node:fs');
const path=require('node:path');
const assert=require('node:assert/strict');
const dir=__dirname;
const read=n=>fs.readFileSync(path.join(dir,n),'utf8');
const a=read('ZEN12-A-TRUTHFUL-TEXT-REVIEW.html');
const b=read('ZEN12-B-OPTIONAL-42S-FILM-TREATMENT-REVIEW.html');
const hub=read('MIND-ARCHIVE-FOUR-STREAM-WP-REVIEW-ONLY.html');
const article=read('THE-WORD-NOBODY-SAID-UNPUBLISHED.md');
const matrix=JSON.parse(read('SOURCE-CLAIM-PARTNER-GATES-ATTRIBUTION.json'));
const vtt=read('ORIGINAL-42S-CAPTIONS.vtt');
let passed=0;
const test=(name,fn)=>{try{fn();passed++;console.log('PASS',name);}catch(e){console.error('FAIL',name,e.message);process.exitCode=1;}};
const video=/\<section class="film"[\s\S]*?<\/section>/;
function assertSafe(html){
 assert.match(html,/<!doctype html>/i);
 assert.match(html,/<html lang="en">/i);
 assert.match(html,/<meta name="viewport"/);
 assert.match(html,/<meta name="robots" content="noindex,nofollow"/);
 assert.match(html,/<button type="button" disabled aria-disabled="true">/);
 assert.match(html,/may earn a commission at no additional cost to you/i);
 assert.match(html,/there is no active earning link/i);
 assert.match(html,/https:\/\/finalvestige\.com\/focus\//);
 assert.doesNotMatch(html,/<(?:script|iframe|form|video)\b/i);
 assert.doesNotMatch(html,/<a\b[^>]*href=["']https?:\/\/(?:www\.)?(?:zen12\.com|inspire3\.com|hypnosislive\.com|brainwaveshots\.com)/i);
 assert.doesNotMatch(html,/(?:onclick\s*=|<link\b[^>]*rel=["'](?:preload|prefetch)|dataLayer|googletagmanager|fbq\s*\()/i);
 assert.doesNotMatch(html,/<a\b[^>]*href=["']javascript:/i);
 const disclosure=html.indexOf('may earn a commission');
 const button=html.indexOf('<button type="button" disabled');
 assert.ok(disclosure>0&&button>disclosure&&button-disclosure<320,'disclosure is adjacent to disabled CTA');
}
test('text buyer safety',()=>assertSafe(a));
test('film buyer safety',()=>assertSafe(b));
test('B equals A aside from one accessible optional film',()=>{
 assert.equal((b.match(video)||[]).length,1);
 assert.equal(b.replace(video,''),a);
 assert.match(b,/<details><summary>/);assert.match(b,/not an encoded or playable video/i);
});
test('unpublished no-JS WordPress hub',()=>{
 assert.match(hub,/Perception &amp; Attention/);assert.match(hub,/History of Suggestion/);
 assert.match(hub,/Practice &amp; Reflection/);assert.match(hub,/Tools Under Review/);
 assert.doesNotMatch(hub,/<(?:script|form|iframe|video)\b/i);
 assert.doesNotMatch(hub,/<a\b[^>]*href=["']https?:\/\/(?:zen12\.com|inspire3\.com)/i);
 assert.match(hub,/noindex,nofollow/);assert.match(hub,/WP|WordPress/);
});
test('original sourced investigation and boundaries',()=>{
 assert.ok(article.trim().split(/\s+/).length>=1700);
 for(const x of ['Roediger','McDermott','Deese','Freyd','Puységur','1995','1996','2024','not a','https://doi.org/10.1037/0278-7393.21.4.803']) assert.ok(article.includes(x),x);
});
test('matrix integrity and all commerce closed',()=>{
 assert.ok(matrix.sources.length>=15&&matrix.claims.length>=30);
 assert.equal(matrix.authorization_gates.length,18);
 assert.ok(matrix.authorization_gates.every(x=>x.status==='HARD_HOLD'));
 assert.ok(matrix.claims.every(c=>c.source_ids.every(id=>matrix.sources.some(s=>s.id===id))));
 assert.ok(matrix.creator_to_purchase_candidate.every(c=>c.actual_asset_id===null));
 assert.match(matrix.attribution_contract.kpi,/NOT COMPUTABLE/);
});
test('caption concept covers 42 seconds',()=>{
 assert.ok(vtt.startsWith('WEBVTT'));
 assert.equal((vtt.match(/-->/g)||[]).length,6);
 assert.match(vtt,/00:00:42\.000/);
});
const mutations=[
 ['active product href',x=>x.replace('<button type="button" disabled','<a href="https://zen12.com/getstarted">Buy</a><button type="button" disabled')],
 ['missing disclosure',x=>x.replace('may earn a commission at no additional cost to you','no earnings mention')],
 ['enabled button',x=>x.replace('disabled aria-disabled="true"','')],
 ['script injection',x=>x.replace('</main>','<script src="//external.test/a.js"></script></main>')],
 ['new signup form',x=>x.replace('</main>','<form><input name="email"></form></main>')],
 ['JS click-tracker',x=>x.replace('</main>','<a onclick="track()">Visit</a></main>')],
 ['merchant as source link',x=>x.replace('</main>','<a href="https://brainwaveshots.com/focus-shot">Seller</a></main>')],
 ['missing focus route',x=>x.replaceAll('https://finalvestige.com/focus/','https://example.invalid/')],
];
test('adversarial commerce mutations rejected',()=>{
 for(const [name,mutate] of mutations){let bad=mutate(a), caught=false;
  try{assertSafe(bad);if(name==='missing focus route')assert.match(bad,/https:\/\/finalvestige\.com\/focus\//);}catch(e){caught=true;}
  assert.ok(caught,'unsafe mutation accepted: '+name);
 }
});
console.log('TOTAL',passed,'of 8 suites; source-only. Browser, Node compatibility, WCAG and merchant settlement require independent QA.');
if(process.exitCode)process.exit(process.exitCode);
