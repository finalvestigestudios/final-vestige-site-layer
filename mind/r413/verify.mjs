// Mind R413 isolated static-source guard. Run: node mind/r413/verify.mjs
// No network, installs, credentials, live tracking or CMS writes. Not a substitute for browser/merchant QA.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
const root=dirname(fileURLToPath(import.meta.url));
const load=(name)=>readFileSync(join(root,name),'utf8');
const a=load('ZEN12_A_TEXT_ONLY.html');
const b=load('ZEN12_B_OPTIONAL_STORYBOARD.html');
const hub=load('MIND_HUB_FOUR_STREAM_SOURCE_ONLY.html');
const article=load('THATCHER_ILLUSION_SOURCED_INVESTIGATION.md');
const poster=load('ORIGINAL_POSTER.svg');
const vtt=load('ORIGINAL_42_SECONDS.vtt');
const matrix=JSON.parse(load('CLAIM_PROOF_PERMISSION_MATRIX.json'));
const acceptance=load('CONVERSION_ACCEPTANCE_AND_CREATOR_CROSSWALK.md');
let checks=0;
function check(ok,label){assert.ok(ok,label);checks++}
function safe(s){return !/<(?:script|iframe|form)\b/i.test(s)&& !/\bonclick\s*=/i.test(s)&& !/<meta[^>]+http-equiv=["']refresh/i.test(s)}
function idsUnique(html){const ids=[...html.matchAll(/\bid="([^"]+)"/g)].map(x=>x[1]);return ids.length===new Set(ids).size}
function held(html){return /<button\b[^>]*\bdisabled\b[^>]*>/i.test(html) && !/<a[^>]+href=["'][^"']*(?:zen12\.com\/secret|affiliates\.inspire3\.com|clickbank|hypnosislive\.com\/mental-skills|brainwaveshots\.com\/focus-shot)/i.test(html)}
function cleanHtml(html){return html.replace(/<section class="panel" aria-labelledby="storyboard">[\s\S]*?<\/section>/,'')}
function captionTimes(vtt){return [...vtt.matchAll(/(\d\d:\d\d:\d\d\.\d\d\d) --> (\d\d:\d\d:\d\d\.\d\d\d)/g)].map(m=>[m[1],m[2]])}
for(const [name,s] of [['A',a],['B',b],['hub',hub]]) {
 check(s.startsWith('<!doctype html>'),name+' HTML5');
 check(/<html lang="en">/.test(s),name+' language');
 check(/name="viewport"/.test(s),name+' viewport');
 check(/name="robots" content="noindex,nofollow"/.test(s),name+' unpublished');
 check(/class="skip" href="#main"/.test(s),name+' skip link');
 check(/id="main"/.test(s),name+' main target');
 check(/@media\(max-width:/.test(s),name+' responsive CSS');
 check(/prefers-reduced-motion/.test(s),name+' reduced motion');
 check(safe(s),name+' no tracking/scripts/forms/iframes');
 check(idsUnique(s),name+' ids unique');
}
for(const [name,s] of [['A',a],['B',b]]){
 check(held(s),name+' native disabled product control');
 check(s.includes('Prospective affiliate disclosure:'),name+' adjacent disclosure exists');
 check(s.includes('If you purchase through a future approved link, Final Vestige may earn a commission at no additional cost to you'),name+' exact plain-English disclosure');
 check(s.indexOf('Prospective affiliate disclosure:')>0 && s.indexOf('Prospective affiliate disclosure:')<s.indexOf('<button class="held"'),name+' disclosure precedes disabled offer');
 check(s.indexOf('<button class="held"')-s.indexOf('Prospective affiliate disclosure:')<500,name+' disclosure close to offer');
 check(s.includes('https://finalvestige.com/focus/'),name+' existing free path');
 check(s.includes('No one at Final Vestige claims to have used or tested Zen12'),name+' no invented experience');
 check(!/\<video\b/i.test(s),name+' no fake playable film');
 check(!/\b(?:\$|USD)\s*\d/.test(s),name+' no hardcoded price');
}
check(b.includes('ORIGINAL_POSTER.svg'),'B original poster');
check(b.includes('ORIGINAL_42_SECONDS.vtt'),'B caption production reference');
check(b.includes('Not playable yet'),'B honest storyboard label');
check(!a.includes('aria-labelledby="storyboard"'),'A text-only');
check(cleanHtml(b)===a,'variants share identical substantive copy');
check(poster.startsWith('<svg ') && poster.includes('xmlns="http://www.w3.org/2000/svg"'),'standalone SVG');
check(!/<(?:script|image|foreignObject)\b/i.test(poster),'poster no active/external markup');
check(vtt.startsWith('WEBVTT'),'caption syntax');
const times=captionTimes(vtt);
check(times.length===6,'six timed cues');
check(times[0][0]==='00:00:00.000' && times.at(-1)[1]==='00:00:42.000','42-second sequence');
check(times.every((t,i)=> i===0 || times[i-1][1]===t[0]),'captions contiguous');
check(article.split(/\s+/).length>=1800,'deep investigation');
for(const url of ['https://pubmed.ncbi.nlm.nih.gov/20942363/','https://pubmed.ncbi.nlm.nih.gov/25301017/','https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/'])check(article.includes(url),'article source '+url);
check(matrix.claims.length>=25,'claim matrix depth');
check(matrix.gates.length>=25,'release gate coverage');
check(matrix.gates.every(x=>x.status==='HOLD'&&x.proof===null),'all release gates fail closed');
check(matrix.affiliate_links_active===false && matrix.verified_partner_approval===false,'no affiliate activation');
check(matrix.claims.some(x=>x.id==='r413-012'&&x.status==='exclude_as_independent_fact'),'Zen12 hour equivalence excluded');
check(matrix.claims.some(x=>x.id==='r413-019'&&x.claim.includes('isochronic')),'modality distinction recorded');
check(matrix.claims.every(x=>Array.isArray(x.source)&&x.source.every(u=>Object.values(matrix.sources).includes(u))),'no unsourced external IDs');
check(hub.includes('Perception &amp; Attention') && hub.includes('History of Suggestion') && hub.includes('Practice &amp; Reflection') && hub.includes('Tools Under Review'),'four streams');
check(!hub.includes('href="/mind/"'),'no false live route');
check(acceptance.includes('NOT COMPUTABLE'),'missing financial proof stated');
check(acceptance.includes('Grok') && acceptance.includes('asset_id'),'creator audit contract');
check(acceptance.includes('merchant_settled_commission') && acceptance.includes('affiliate_click'),'separate sale and click');
function adversarial(html){return safe(html)&&held(html)&&html.includes('Prospective affiliate disclosure:')&&html.includes('If you purchase through a future approved link, Final Vestige may earn a commission at no additional cost to you')}
for(const evil of [a.replace('<button class="held" type="button" disabled','<button class="held" type="button"'),a.replace('Prospective affiliate disclosure:','No disclosure:'),a+'<script src="//tracker.example"></script>',a+'<form method="post"></form>',a.replace('If you purchase through a future approved link, Final Vestige may earn a commission at no additional cost to you',''),a+'<a href="https://zen12.com/secret/">Buy</a>'])check(!adversarial(evil),'unsafe mutation caught');
console.log('Mind R413 source guard PASS:',checks,'assertions including six unsafe mutations');
console.log('NOT TESTED: real-browser WCAG/CWV, WordPress sanitization, live provider confirmation, video encoding/playback, checkout, settlement, actual attribution');
