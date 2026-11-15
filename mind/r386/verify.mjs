// Native offline Node verifier. Run: node mind/r386/verify.mjs
// Read-only. No network requests, production edits, event tracking or affiliate activation.
import fs from 'node:fs';
import assert from 'node:assert/strict';
const base='mind/r386/';
const read=n=>fs.readFileSync(base+n,'utf8');
const a=read('ZEN12_A_GUIDE.html'), b=read('ZEN12_B_STORYBOARD.html');
const hub=read('MIND_HUB_SOURCE_ONLY.html'), svg=read('ZEN12_ORIGINAL_POSTER.svg');
const vtt=read('ZEN12_42S_CAPTIONS.vtt'), article=read('STROOP_SUGGESTION_AND_THE_AUDIO_PROMISE.md');
const matrix=JSON.parse(read('CLAIM_PROOF_AND_HOLDS.json'));
let count=0;
function check(value,description){assert.ok(value,description);count++;}
const plain=h=>h.replace(/<[^>]*>/g,' ').replace(/\s+/g,' ');
for(const [name,h] of [['A',a],['B',b],['hub',hub]]){
 check(/<!doctype html>/i.test(h),name+' doctype');
 check(/<html lang="en"/.test(h),name+' lang');
 check(/<meta name="viewport"/.test(h),name+' viewport');
 check(/<meta name="robots" content="noindex,nofollow"/.test(h),name+' noindex');
 check((h.match(/<h1(?:\s|>)/g)||[]).length===1,name+' one h1');
 check(!/<script\b|<form\b|<iframe\b|\son(?:click|load|submit)\s*=|<video\b[^>]*autoplay/i.test(h),name+' no scripts/forms/iframe/handlers/autoplay');
 check(/prefers-reduced-motion/.test(h),name+' reduced motion');
 check(/:focus-visible/.test(h),name+' keyboard focus');
}
for(const [name,h] of [['A',a],['B',b]]){
 check(/<button[^>]*\sdisabled(?:\s|>)/i.test(h),name+' native disabled');
 check(plain(h).includes('may earn a commission at no additional cost to you'),name+' nearby disclosure');
 check(h.includes('https://finalvestige.com/focus/'),name+' existing Focus route');
 check(!/<a\s[^>]*href=["']https?:\/\/(?:www\.)?(?:zen12\.com|inspire3\.com|hypnosislive\.com|brainwaveshots\.com|affiliates\.inspire3\.com)/i.test(h),name+' no seller links');
 check(/\$87\.99/.test(h),name+' dated seller display price');
 check(plain(h).includes('not an independently authenticated referred checkout'),name+' checkout caveat');
 check(plain(h).includes('not been independently established'),name+' health/efficacy limit');
 check(h.includes('Review the Zen12 offer — unavailable pending verification'),name+' CTA text');
}
const buyerStart='<section aria-labelledby="story">';
check(a.includes(buyerStart)&&b.includes(buyerStart),'buyer content present');
check(a.slice(a.indexOf(buyerStart))===b.slice(b.indexOf(buyerStart)),'identical buyer body A/B');
check(!a.includes('ZEN12_ORIGINAL_POSTER.svg'),'A no media poster');
check(b.includes('ZEN12_ORIGINAL_POSTER.svg'),'B original poster');
check(b.includes('<details>')&&b.includes('42-second narration'),'B transcript');
check(!/<video\b|<audio\b/i.test(b),'B not falsely playable');
check(/role="img"/.test(svg)&&/<title/.test(svg)&&/<desc/.test(svg),'SVG accessibility');
check(!/<(?:image|script|foreignObject)\b/i.test(svg),'SVG no scripts or external images');
check(vtt.startsWith('WEBVTT'),'VTT header');
check((vtt.match(/-->/g)||[]).length===6,'six timed cues');
check(vtt.includes('00:00:42.000'),'42-second storyboard end');
check(matrix.sources.length===16,'16 source entries');
check(matrix.claims.length===36,'36 claim decisions');
check(matrix.release_gates.length===36,'36 commercial release gates');
check(matrix.release_gates.every(g=>g.status==='HOLD'),'all release gates held');
check(matrix.economic_truth.net_revenue_per_1000_qualified_sessions===null,'no invented net revenue');
check(article.includes('https://pubmed.ncbi.nlm.nih.gov/12470132/'),'primary research cited');
check(article.trim().split(/\s+/).length>2000,'substantive source manuscript');
console.log('PASS '+count+' native offline source assertions');
