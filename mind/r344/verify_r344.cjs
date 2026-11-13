'use strict';
/** Node 18+. Reproducible static guard; executes read-only. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const here=__dirname;
const read=p=>fs.readFileSync(path.join(here,p),'utf8');
const A=read('ZEN12_A_TEXT_REVIEW.html'),B=read('ZEN12_B_FILM_REVIEW.html');
const article=read('THE_EXPLANATION_TRAP.md'),hub=read('MIND_HUB_WP_REVIEW_ONLY.html');
const matrix=JSON.parse(read('CLAIM_SOURCE_AUTHORIZATION_MATRIX.json'));
const acceptance=read('CONVERSION_ACCEPTANCE.md'),captions=read('ZEN12_42S_CAPTIONS.vtt');
let count=0;
const test=(name,fn)=>{fn();count++;console.log('PASS',name)};
test('article full independently cited',()=>{assert(article.length>7000);for(const word of ['Rozenblit','Weisberg','Ingendoh','Puységur','not independently'])assert(article.includes(word));});
test('all gates false',()=>{assert.equal(matrix.all_commerce_releases_blocked,true);assert.equal(Object.keys(matrix.commercial_gates).length,20);assert(Object.values(matrix.commercial_gates).every(v=>v===false));});
for(const [label,html] of [['A',A],['B',B]]){
test(label+' HTML responsive',()=>{assert(html.includes('name="viewport"'));assert(html.includes('max-width:720px'));assert(html.includes('prefers-reduced-motion:reduce'));});
test(label+' linkless purchase',()=>{assert(/<button[^>]*disabled[^>]*>Merchant option unavailable/.test(html));assert(!/<a[^>]*href="https?:\/\/(?:zen12|affiliates\.inspire3)/i.test(html));});
test(label+' no activation',()=>{assert(!/<(?:script|form|iframe|video|audio)\b/i.test(html));assert(!/\bautoplay\s*=/i.test(html));});
test(label+' disclosure visible',()=>{assert(html.includes('Final Vestige may earn a commission at no additional cost to you.'));assert(html.indexOf('Final Vestige may earn a commission')<html.indexOf('Merchant option unavailable'));});
test(label+' content commitments',()=>{for(const s of ['Premium','twelve levels and 48 MP3','seller\'s newsletter','Seven Day Focus Fieldbook','no verified'])assert(html.includes(s));});
}
test('A B base content same',()=>{const marker='<section class="panel" aria-label="Optional forty-two-second visual explanation">';assert(B.includes(marker));const stop='<section class="panel" aria-labelledby="proof">';const pos=B.indexOf(marker),end=B.indexOf(stop,pos);assert.equal(B.slice(0,pos)+B.slice(end),A);});
test('B semantic poster & transcript',()=>{for(const s of ['<svg','role="img"','<title','<desc','<figcaption','<details','Read the full 42-second film transcript'])assert(B.includes(s));});
test('VTT six cues and 42 sec end',()=>{assert.equal((captions.match(/-->/g)||[]).length,6);assert(captions.includes('00:00:42.000'));});
test('hub protects ownership',()=>{assert(hub.includes('not saved in WordPress'));assert(hub.includes('PR #172'));});
test('not revenue from clicks',()=>{assert(acceptance.includes('NOT COMPUTABLE'));assert(acceptance.includes('paid_affiliate_order'));assert(acceptance.includes('refund'));});
console.log('TOTAL',count);
