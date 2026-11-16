#!/usr/bin/env node
/* Final Vestige Mind R421: reproducible offline source preflight. Node >=18, no npm, no network.
   Run: node mind/r421/verify-r421.cjs
   This does NOT qualify browser, WP, merchant, media playback, consent or paid outcomes. */
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const root = __dirname;
const read = file => fs.readFileSync(path.join(root,file),'utf8');
const A = read('ZEN12_A_TEXT.html');
const B = read('ZEN12_B_OPTIONAL_STORYBOARD.html');
const H = read('MIND_HUB_SOURCE_ONLY.html');
const P = read('ZEN12_FILM_POSTER.svg');
const V = read('ZEN12_FILM_CAPTIONS.vtt');
const ARTICLE = read('THE_GORILLA_WAS_NOT_A_DEFECT.md');
const M = JSON.parse(read('CLAIM_PERMISSION_MATRIX.json'));
const DOSSIER = read('CONVERSION_ACCEPTANCE_AND_GROK_CROSSWALK.md');
const checks = [];
const check = (description,run)=>{run();checks.push(description);};
const contains = (s,re,msg)=>assert.match(s,re,msg);
const denies = (s,re,msg)=>assert.doesNotMatch(s,re,msg);
const sellerLink = /<a\b[^>]*\bhref\s*=\s*["']https?:\/\/(?:www\.)?(?:zen12\.com|inspire3\.com|affiliates\.inspire3\.com|hypnosislive\.com|brainwaveshots\.com|go\.inspire3\.com)(?:[\/?:"']|$)/i;
const badExternal = /(?:utm_[a-z]+|clickid|subid|affid|hoplink)\s*=/i;
function pageSafety(s) {
  assert.match(s,/<html\b[^>]*lang="en"/i);
  assert.match(s,/<meta name="viewport"/i);
  assert.match(s,/<meta name="robots" content="noindex,nofollow"/i);
  assert.match(s,/<a class="skip" href="#main">/i);
  assert.match(s,/<main id="main">/i);
  assert.match(s,/:focus-visible/);
  assert.match(s, /prefers-reduced-motion/);
  assert.match(s, /Purchase link unavailable — approval pending/);
  assert.match(s, /<button[^>]*\bdisabled\b[^>]*>Purchase link unavailable/);
  assert.match(s, /aria-disabled="true"/);
  assert.match(s, /If you purchase through a future earning link on this page, Final Vestige may earn a commission at no additional cost to you\./);
  assert.match(s, /We have not verified named publisher acceptance/);
  assert.match(s, /no additional email form/i);
  denies(s,sellerLink);
  denies(s,/<script\b|<iframe\b|<form\b|<input\b/i);
  denies(s,/<(?:video|audio)\b[^>]*\bautoplay\b|\bonclick\s*=|\bonload\s*=/i);
  denies(s,/\bhref\s*=\s*["'](?:javascript|data):/i);
  denies(s,/<a\b[^>]*\bdownload\b/i);
  denies(s,/<video\b|<audio\b/i); // placeholder cannot masquerade as playable
  denies(s,/<img\b[^>]*\bsrc\s*=\s*["']https?:/i); // no remote trackers
  denies(s,badExternal);
  return true;
}
function hubSafety(s) {
  contains(s,/<html\b[^>]*lang="en"/i);
  contains(s,/<main id="main">/);
  contains(s,/<meta name="robots" content="noindex,nofollow"/);
  contains(s,/Stream 01/);
  contains(s,/Stream 02/);
  contains(s,/Stream 03/);
  contains(s,/Stream 04/);
  contains(s,/https:\/\/finalvestige.com\/focus\//);
  contains(s,/https:\/\/finalvestige.com\/2026\/11\/02\/mesmerism\//);
  contains(s,/https:\/\/finalvestige.com\/free-resources\/puysegurs-animal-magnetism-files\//);
  denies(s,/<script\b|<iframe\b|<form\b|<input\b/i);
  denies(s, sellerLink);
  denies(s,/<video\b[^>]*autoplay/);
  return true;
}
function matrixSafety(m) {
  assert.equal(m.no_commercial_activation,true);
  assert.equal(m.claims.length,35);
  assert.equal(m.release_gates.length,28);
  assert.equal(Object.keys(m.sources).length,21);
  assert.equal(m.release_gates.every(g=>g.status==='HOLD'&&g.verified===false),true);
  assert.equal(new Set(m.release_gates.map(g=>g.id)).size,m.release_gates.length);
  assert.equal(new Set(m.claims.map(c=>c.id)).size,m.claims.length);
  for(const c of m.claims){
    assert.equal(c.publish_as_benefit,false);
    for(const id of c.source_ids)assert.ok(m.sources[id], 'missing source '+id+' on '+c.id);
    assert.ok(c.limit.length>10);
  }
  for(const s of Object.values(m.sources))assert.match(s.url,/^https:\/\//);
  assert.equal(m.metric_contract.net_per_1000.includes('NOT_COMPUTABLE'),true);
  assert.equal(m.metric_contract.affiliate_click.includes('not a sale'),true);
  return true;
}
function parseVtt(text){
  assert.match(text,/^WEBVTT\r?\n/);
  const mm = [...text.matchAll(/(\d\d):(\d\d):(\d\d)\.(\d\d\d) --> (\d\d):(\d\d):(\d\d)\.(\d\d\d)/g)];
  const toMs=x=>((+x[1]*60 + +x[2])*60 + +x[3])*1000 + +x[4];
  const spans = mm.map(x=>({start:toMs([null,...x.slice(1,5)]),end:toMs([null,...x.slice(5,9)])}));
  assert.equal(spans.length,6);
  assert.equal(spans[0].start,0);
  assert.equal(spans[5].end,42000);
  for(let i=0;i<spans.length;i++){
    assert.ok(spans[i].end>spans[i].start);
    if(i)assert.equal(spans[i].start,spans[i-1].end);
  }
  return spans;
}
check('Buyer A explicit no-JS/no-authorized-link safety',()=>assert.equal(pageSafety(A),true));
check('Buyer B explicit no-JS/no-authorized-link safety',()=>assert.equal(pageSafety(B),true));
check('Hub four-stream no-JS no-merchant safety',()=>assert.equal(hubSafety(H),true));
check('Matrix 35 claims / 28 held gates with resolved provenance',()=>assert.equal(matrixSafety(M),true));
const start = '<section class="reading" aria-labelledby="problem">';
check('Identical substantive core buyer copy across variants',()=>assert.equal(A.slice(A.indexOf(start),A.indexOf('</main>')),B.slice(B.indexOf(start),B.indexOf('</main>'))));
check('Original poster SVG accessible without remote assets',()=>{contains(P,/<svg\b/);contains(P,/<title id="t">/);contains(P,/<desc id="d">/);denies(P,/<script\b|<foreignObject\b|<image\b|<animate\b/i);denies(P,/<image\b|<script\b/i);});
check('Six contiguous caption cues total 42 seconds',()=>assert.equal(parseVtt(V).length,6));
check('Storyboard reports NOT playable instead of fake media',()=>{contains(B,/not an encoded or playable film/i);contains(B, /Read the complete film transcript/i);contains(B,/ZEN12_FILM_POSTER.svg/);contains(B,/ZEN12_FILM_CAPTIONS.vtt/);});
check('Original source-led manuscript',()=>{assert.ok(ARTICLE.split(/\s+/).length>=2200);for(const u of ['10.1068/p281059','PMC3563049','PMC3964612','2214930120','puysegurs-animal-magnetism-files','finalvestige.com/focus/'])contains(ARTICLE,new RegExp(u));});
check('Dossier requires actual settled net and founder approval',()=>{for(const u of ['NOT COMPUTABLE','Founder','HARD HOLD','refund','Grok','consent','no additional','A/B','UNPUBLISHED','28'])contains(DOSSIER,new RegExp(u,'i'));});
check('Research/buyer copy separates science from merchant promises',()=>{contains(ARTICLE,/None of those sources demonstrates/i);contains(A,/seller claims/i);contains(A,/no cited study/i);});
check('Commercial disclosure precedes native-disabled CTA',()=>{for(const s of [A,B])assert.ok(s.indexOf('If you purchase through a future earning link')<s.indexOf('<button type="button" class="locked" disabled'));});
const unsafe=[
 ['enable real button',s=>s.replace('class="locked" disabled','class="locked"'),false],
 ['remove aria disabled',s=>s.replace('aria-disabled="true"','aria-disabled="false"'),false],
 ['remove disclosure',s=>s.replace('If you purchase through a future earning link on this page, Final Vestige may earn a commission at no additional cost to you.',''),false],
 ['add merchant anchor',s=>s.replace('</body>','<a href="https://zen12.com/order">Buy</a></body>'),false],
 ['add partner referral',s=>s.replace('</body>','<a href="https://affiliates.inspire3.com/?affid=abc">Tracked</a></body>'),false],
 ['inject form',s=>s.replace('</body>','<form><input type="email"></form></body>'),false],
 ['inject tracking pixel',s=>s.replace('</body>','<img src="https://tracker.example/1"></body>'),false],
 ['inject remote script',s=>s.replace('</body>','<script src="https://example.org/p.js"></script></body>'),false],
 ['inject autoplay film',s=>s.replace('</body>','<video autoplay controls></video></body>'),false],
 ['inject javascript link',s=>s.replace('</body>','<a href="javascript:alert(1)">Open</a></body>'),false],
 ['insert URL campaign ID',s=>s.replace('</body>','<p>utm_content=hidden-user-id</p></body>'),false],
 ['remove publisher hold',s=>s.replace('We have not verified named publisher acceptance','Partner verified'),false]
];
let rejected=0;
for(const [name,mutate] of unsafe){
  check('Mutation rejected: '+name,()=>{assert.throws(()=>pageSafety(mutate(A)));rejected++;});
}
const matrixBad=structuredClone(M);matrixBad.release_gates[0].verified=true;
check('Mutation rejected: counterfeit publisher approval',()=>assert.throws(()=>matrixSafety(matrixBad)));
const matrixBad2=structuredClone(M);matrixBad2.claims[0].source_ids=['FAKE'];
check('Mutation rejected: invented claim source',()=>assert.throws(()=>matrixSafety(matrixBad2)));
const matrixBad3=structuredClone(M);matrixBad3.release_gates.pop();
check('Mutation rejected: missing commercial authorization gate',()=>assert.throws(()=>matrixSafety(matrixBad3)));
const capBad=V.replace('00:00:42.000','00:00:43.000');
check('Mutation rejected: caption exceeds 42 seconds',()=>assert.throws(()=>parseVtt(capBad)));
const hubBad=H.replace('Stream 03','Stream 33');
check('Mutation rejected: missing practice stream',()=>assert.throws(()=>hubSafety(hubBad)));
console.log('R421 PASS: '+checks.length+'/'+checks.length+' assertions; '+(rejected+5)+'/'+(rejected+5)+' deliberately unsafe synthetic mutations rejected.');
console.log('No browser/WP/merchant/video/Jetpack/transaction tests were executed by this script.');
