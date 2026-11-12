'use strict';
// Reproducible source-level safety suite. Run: node verify_r331.cjs from this folder.
const fs=require('node:fs'), assert=require('node:assert/strict');
const A=fs.readFileSync('ZEN12-A-TEXT-REVIEW.html','utf8');
const B=fs.readFileSync('ZEN12-B-OPTIONAL-FILM-REVIEW.html','utf8');
const V=fs.readFileSync('ZEN12-42S.vtt','utf8');
const G=fs.readFileSync('MIND-HUB-WP-REVIEW-ONLY.html','utf8');
const M=JSON.parse(fs.readFileSync('SOURCE-CLAIM-COMMERCE-MATRIX.json','utf8'));
let n=0;
const pass=(ok,name)=>{assert.ok(ok,name);n++;};
const extract=h=>h.match(/<section id="guide" data-buyer-copy="r331">[\s\S]*?<\/section>/)?.[0];
for(const [k,h] of [['A',A],['B',B]]){
pass(h.startsWith('<!doctype html>'),'doctype '+k);
pass(/<html lang="en">/.test(h),'lang '+k);
pass(/name="viewport"/.test(h),'viewport '+k);
pass(/name="robots" content="noindex,nofollow"/.test(h),'noindex '+k);
pass(/disabled aria-disabled="true"/.test(h),'disabled '+k);
pass(/Potential affiliate relationship:[\s\S]{0,230}may earn a commission/.test(h),'near affiliate disclosure '+k);
pass(h.includes('https://finalvestige.com/focus/'),'existing Focus '+k);
pass(!/<script\b|<iframe\b|<form\b|<(?:video|audio)[^>]*\sautoplay(?:\s|=|>)/i.test(h),'no forms scripts autoplay '+k);
pass(!/href="https?:\/\/(?:zen12|inspire3|affiliates\.inspire3|hypnosislive|brainwaveshots)\.com/i.test(h),'no merchant links '+k);
}
pass(extract(A)===extract(B),'substantive A/B parity');
pass(B.includes('Optional 42-second film')&&B.includes('not yet playable'),'B labeled unencoded');
pass(!A.includes('Optional 42-second film'),'A has no film');
pass((V.match(/-->/g)||[]).length===6,'six WebVTT cues');
pass(V.includes('00:00:42.000'),'42s complete');
pass(G.includes('Perception & Attention')&&G.includes('History of Suggestion')&&G.includes('Tools Under Review'),'hub streams');
pass(!/<form\b|<script\b/i.test(G),'hub no extra forms/scripts');
pass(Object.keys(M.release_gates).length===18,'18 explicit gates');
pass(Object.values(M.release_gates).every(x=>x==='HOLD'),'no approved commercial gate');
pass(M.claims.some(c=>c.id==='Z06'&&!c.eligible_for_buyer_copy),'efficacy excluded');
pass(M.metrics.net_revenue_per_1000_qualified_human_sessions===null,'no invented revenue');
for(const mutation of [
h=>h.replace('disabled aria-disabled="true"',''),
h=>h.replace('If we are approved','We are approved'),
h=>h.replace('Potential affiliate relationship:','Purchase now:'),
h=>h.replace('</main>','<form action="/subscribe"></form></main>'),
h=>h.replace('</main>','<script src="https://tracker.invalid/x.js"></script></main>'),
h=>h.replace('</main>','<a href="https://zen12.com/">Buy now</a></main>'),
h=>h.replace('</main>','<video autoplay src="demo.mp4"></video></main>')
]){
const bad=mutation(A);
const safe=/disabled aria-disabled="true"/.test(bad)&&/Potential affiliate relationship:[\s\S]{0,230}may earn a commission/.test(bad)&&!/<form\b|<script\b|<(?:video|audio)[^>]*\sautoplay(?:\s|=|>)|tracker\.invalid/i.test(bad)&&!/href="https:\/\/zen12\.com\//.test(bad)&&bad.includes('If we are approved');
assert.equal(safe,false,'unsafe mutation escaped');n++;
}
console.log('R331 source baseline and seven negative mutations: '+n+'/'+n+' PASS (source-level); no browser/WP/payment checks performed');
