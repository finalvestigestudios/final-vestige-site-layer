// Offline native Node verifier: node mind/r386/verify.mjs
// No network, no production writes. Run from repository root.
import fs from 'node:fs';
import assert from 'node:assert/strict';
const base='mind/r386/';
const a=fs.readFileSync(base+'ZEN12_A_GUIDE.html','utf8');
const b=fs.readFileSync(base+'ZEN12_B_STORYBOARD.html','utf8');
const hub=fs.readFileSync(base+'MIND_HUB_SOURCE_ONLY.html','utf8');
const svg=fs.readFileSync(base+'ZEN12_ORIGINAL_POSTER.svg','utf8');
const vtt=fs.readFileSync(base+'ZEN12_42S_CAPTIONS.vtt','utf8');
const matrix=JSON.parse(fs.readFileSync(base+'CLAIM_PROOF_AND_HOLDS.json','utf8'));
const article=fs.readFileSync(base+'STROOP_SUGGESTION_AND_THE_AUDIO_PROMISE.md','utf8');
let n=0;
function check(flag,description){assert.ok(flag,description);n++;}
for(const [name,html] of [['A',a],['B',b],['hub',hub]]){
 check(/<!doctype html>/i.test(html),name+' doctype');
 check(/<html lang="en"/.test(html),name+' lang');
 check(/<meta name="viewport"/.test(html),name+' viewport');
 check(/<meta name="robots" content="noindex,nofollow"/.test(html),name+' noindex');
 check((html.match(/<h1(?:\s|>)/g)||[]).length===1,name+' one h1');
 check(!/<script\b|<form\b|<iframe\b|\son(?:click|load|submit)\s*=|<video\b[^>]*autoplay/i.test(html),name+' no scripts/forms/iframe/handlers/autoplay');
 check(/prefers-reduced-motion/.test(html),name+' reduced-motion');
 check(/:focus-visible/.test(html),name+' focus style');
}
for(const [name,html] of [['A',a],['B',b]]){
 check(/<button[^>]*\sdisabled(?:\s|>)/i.test(html),name+' native disabled');
 check(/may earn a commission at no additional cost to you/i.test(html),name+' adjacent disclosure');
 check(/https:\/\/finalvestige.com\/focus\//.test(html),name+' existing Focus');
 check(!/<a\s[^>]*href=["']https?:\/\/(?:www\.)?(?:zen12\.com|inspire3\.com|hypnosislive\.com|brainwaveshots\.com|affiliates\.inspire3\.com)/i.test(html),name+' no merchant links');
 check(/$87\.99/.test(html),name+' dated seller displayed amount');
 check(/not independently authenticated referred checkout/i.test(html),name+' checkout caveat');
 check(/not.*independently established/i.test(html),name+' efficacy caveat');
 check(/Review the Zen12 offer — unavailable pending verification/.test(html),name+' disabled CTA text');
}
const start='<section aria-labelledby="story">',end='<section aria-labelledby="sources">';
function shared(h){return h.slice(h.indexOf(start),h.indexOf('</section>',h.indexOf(end)));}
check(shared(a)===shared(b),'shared buyer editorial body parity');
check(!a.includes('ZEN12_ORIGINAL_POSTER.svg'),'A no optional poster');
check(b.includes('ZEN12_ORIGINAL_POSTER.svg'),'B poster');
check(b.includes('<details>')&&b.includes('42-second narration'),'B transcript');
check(!/<video\b|<audio\b/i.test(b),'B not falsely playable');
check(/role="img"/.test(svg)&&/<title/.test(svg)&&/<desc/.test(svg),'SVG a11y');
check(!/<(?:image|script|foreignObject)\b|http:\/\//i.test(svg.replace('xmlns="http://www.w3.org/2000/svg"','')),'SVG no remote executable content');
check(vtt.startsWith('WEBVTT'),'VTT header');
check((vtt.match(/-->/g)||[]).length===6,'six VTT cues');
check(vtt.includes('00:00:42.000'),'42 second end');
check(matrix.release_gates.length===36,'36 release gates');
check(matrix.release_gates.every(g=>g.status==='HOLD'),'all gates held');
check(matrix.claims.length>=30,'substantive claim matrix');
check(matrix.sources.length>=15,'sourced');
check(matrix.economic_truth.net_revenue_per_1000_qualified_sessions===null,'no invented revenue');
check(article.includes('https://pubmed.ncbi.nlm.nih.gov/12470132/'),'study reference');
check(article.trim().split(/\s+/).length>1700,'deep original manuscript');
console.log('PASS '+n+' independent offline source assertions');
