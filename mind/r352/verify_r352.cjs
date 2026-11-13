#!/usr/bin/env node
// R352 isolated source safety and A/B parity checks. Run: node mind/r352/verify_r352.cjs
'use strict';
const fs=require('node:fs'),assert=require('node:assert/strict'),path=require('node:path');
const dir=__dirname;const a=fs.readFileSync(path.join(dir,'ZEN12_A_TEXT_REVIEW.html'),'utf8');
const b=fs.readFileSync(path.join(dir,'ZEN12_B_OPTIONAL_FILM_REVIEW.html'),'utf8');
const hub=fs.readFileSync(path.join(dir,'MIND_HUB_WORDPRESS_REVIEW_ONLY.html'),'utf8');
const matrix=JSON.parse(fs.readFileSync(path.join(dir,'PRODUCT_CLAIM_SOURCE_MATRIX.json'),'utf8'));
const vtt=fs.readFileSync(path.join(dir,'original_42s.vtt'),'utf8');
let count=0;
const check=(ok,msg)=>{assert.ok(ok,msg);count++};
for(const [name,html] of [['A',a],['B',b],['hub',hub]]){
  check(html.startsWith('<!doctype html>'),name+' doctype');check(html.includes('<html lang="en">'),name+' lang');
  check(html.includes('name="viewport"'),name+' responsive');
  check(!/<script\b/i.test(html),name+' no script');
  check(!/<form\b/i.test(html),name+' no extra email forms');
  check(!/<(?:video|audio)\b[^>]*\bautoplay\b/i.test(html),name+' no autoplay');
  check(!/https?:\/\/[^"' ]+\?(?:[^"' ]*affiliate|[^"' ]*ref=)/i.test(html),name+' no earning URL');
}
for(const [name,html] of [['A',a],['B',b]]){
  check(/<button[^>]+disabled[^>]*>/i.test(html),name+' disabled native commerce');
  check(html.includes('Prospective affiliate disclosure:'),name+' nearby disclosure');
  check(html.indexOf('Prospective affiliate disclosure:')>html.indexOf('id="decision"'),name+' disclosure in commerce region');
  check(html.includes('https://finalvestige.com/focus/'),name+' existing Focus route');
  check(html.includes('https://zen12.com/gift'),name+' separate merchant consent');
  check(html.includes('aria-disabled="true"'),name+' explicit disabled state');
  check(!/<iframe\b|<video\b/i.test(html),name+' no external embedded video');
}
const prefix='<section class="rule" aria-labelledby="film">';
check(!a.includes(prefix)&&b.includes(prefix),'film distinct B treatment');
check(b.replace(/<section class="rule" aria-labelledby="film">[\s\S]*?(?=<\/main>)/,'')===a.replace('Review B','Review A').replace('GUIDE B','GUIDE A').replace('Buyer Guide B','Buyer Guide A').replace('REVIEW B','REVIEW A').replace('Review Variant B','Review Variant A').replace(/Guide B \|/g,'Guide A |'),'substantive page parity'); // standalone variant-specific <title> normalized separately if necessary
check(b.includes('role="img"')&&b.includes('<figcaption>'),'SVG has readable alternative');
check(b.includes('<details>')&&b.includes('<summary>'),'optional transcript is user controlled');
check((vtt.match(/--> /g)||[]).length===6,'six caption cues');
check(vtt.includes('00:00:42.000'),'final 42 second cue');
check(matrix.claims.length>=30,'claim matrix substantive');
check(Object.keys(matrix.release_gates).length>=20,'release gates enumerated');
check(Object.values(matrix.release_gates).every(x=>x==='HOLD'),'all release gates held');
check(hub.includes('https://finalvestige.com/focus/')&&hub.includes('https://finalvestige.com/2026/11/02/mesmerism/'),'genuine live navigation');
check(hub.includes('not saved')||hub.includes('not create the /mind/ route'),'hub unpublished warning');
console.log('R352 source assertions passed:',count);
