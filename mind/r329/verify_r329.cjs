// R329 reproducible Node source-level safety checks; run from repository root:
// node mind/r329/verify_r329.cjs
const fs=require('node:fs'); const path=require('node:path'); const assert=require('node:assert/strict');
const here=__dirname; const read=f=>fs.readFileSync(path.join(here,f),'utf8');
const a=read('ZEN12-A-TEXT-ONLY-REVIEW.html'), b=read('ZEN12-B-OPTIONAL-FILM-REVIEW.html');
const hub=read('MIND-FOUR-STREAM-REVIEW-ONLY.html'), article=read('WHEN-HYPNOSIS-MADE-THE-LECTURE-HARDER.md');
const matrix=JSON.parse(read('SOURCE-CLAIM-COMMERCE-MATRIX.json')); const captions=read('ZEN12-42S-CAPTIONS.vtt');
const checks=[
['A and B have identical substantive core',()=>assert.equal(a.split('<!-- CORE START -->')[1].split('<!-- CORE END -->')[0],b.split('<!-- CORE START -->')[1].split('<!-- CORE END -->')[0])],
['A and B disabled merchant CTA',()=>{for(const h of [a,b])assert.match(h,/<button[^>]*disabled/)}],
['No merchant href in either variant',()=>{for(const h of [a,b])assert.doesNotMatch(h,/<a[^>]+href=["'][^"']*(zen12|hypnosislive|brainwaveshots|inspire3|affiliates)/i)}],
['No forms scripts or iframes in buyer variants',()=>{for(const h of [a,b])assert.doesNotMatch(h,/<(form|script|iframe)\b/i)}],
['No autoplay or remote media in variants',()=>{for(const h of [a,b])assert.doesNotMatch(h,/(autoplay|<video|<audio|googletagmanager|doubleclick)/i)}],
['Disclosure appears next to commerce control',()=>{for(const h of [a,b])assert.match(h,/<p class="disclosure">[\s\S]{0,450}<\/p><button[^>]*disabled/)}],
['Existing Focus route only',()=>{for(const h of [a,b,hub])assert.ok(h.includes('https://finalvestige.com/focus/'))}],
['B optional film is clearly NOT playable',()=>{assert.match(b,/static video-production treatment/);assert.match(b,/<details>/);assert.match(b,/Original, static/i)}],
['B local poster no external image',()=>assert.match(b,/src="ZEN12-42S-POSTER.svg"/)],
['VTT ends at 42 seconds',()=>{assert.ok(captions.startsWith('WEBVTT'));assert.ok(captions.includes('00:00:42.000'))}],
['No claims of affiliate approval',()=>{for(const h of [a,b])assert.match(h,/No earning link is active here/)}],
['No permanent price promises',()=>{for(const h of [a,b])assert.match(h,/historical context, not a live quote/)}],
['Article acknowledges original negative-result study',()=>assert.ok(article.includes('worse'))],
['Article includes opposite-sign study',()=>assert.ok(article.includes('23 volunteers'))],
['Article contains Puységur bridge',()=>assert.ok(article.includes('Puységur'))],
['Independent research never marked product-specific',()=>assert.ok(matrix.independent_research.every(c=>c.product_specific===false))],
['Commercial holds closed',()=>assert.equal(matrix.holds.length,18)],
['Revenue KPI has no invented data',()=>assert.equal(matrix.revenue_per_1000_qualified_sessions,null)],
['Hub is marked noindex and unpublished',()=>{assert.match(hub,/noindex/);assert.match(hub,/REVIEW ONLY/)}],
['Article includes original source URLs',()=>{assert.ok(article.includes('https://pubmed.ncbi.nlm.nih.gov/23724570/'));assert.ok(article.includes('https://pubmed.ncbi.nlm.nih.gov/26894423/'))}],
['No fake GitHub or user attribution',()=>assert.ok(matrix.offer_funnel_blocker_owner.length===6)]
];
let passed=0; for(const [name,fn] of checks){fn(); passed++; console.log('PASS',name);} console.log('R329',passed,'/',checks.length,'source-level checks PASS');