#!/usr/bin/env node
/**
 * Mind R317 static source validation. Run:
 *   node mind/r317/verify_r317.cjs
 * Built-in Node only, no network or credentials, no live CMS writes.
 * Not a replacement for native browser/WCAG, WordPress staging, payment or media QA.
 */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const root=__dirname;
const read=(name)=>fs.readFileSync(path.join(root,name),'utf8');
const a=read('ZEN12-A-TEXT-ONLY-REVIEW.html');
const b=read('ZEN12-B-OPTIONAL-42S-FILM-REVIEW.html');
const hub=read('MIND-FOUR-STREAM-WORDPRESS-REVIEW-ONLY.html');
const vtt=read('ORIGINAL-42S-CAPTIONS-CONCEPT.vtt');
const article=read('THE-INSTRUCTION-THAT-WORKED-WITHOUT-HYPNOSIS-UNPUBLISHED.md');
const dossier=read('ONE-OFFER-CREATOR-MEASUREMENT-AND-RELEASE-ACCEPTANCE.md');
const register=JSON.parse(read('CLAIM-SOURCE-PARTNER-AND-CONVERSION-HOLDS.json'));
const neutral=(html)=>html.match(/<article id="guide">([\s\S]*?)<\/article>/)?.[1]||'';
function safeHtml(h){
  if(!/^<!doctype html>/i.test(h))throw new Error('DOCTYPE missing');
  if(!/<html lang="en">/i.test(h))throw new Error('language missing');
  if(!/name="viewport"/i.test(h))throw new Error('mobile viewport missing');
  if(!/name="robots" content="noindex,nofollow"/i.test(h))throw new Error('review-only noindex missing');
  if(/<script\b|<iframe\b|<form\b|<video\b|<audio\b|<source\b/i.test(h))throw new Error('active executable/form/media forbidden');
  if(/https?:\/\/(?:affiliates\.inspire3\.com|www\.awin1\.com|click\.bank|bit\.ly|tinyurl\.com)/i.test(h))throw new Error('earning or cloaked URL forbidden');
  if(/utm_(source|campaign|medium)|fbclid|gclid|pixel|localStorage|document\.cookie/i.test(h))throw new Error('analytics pixel/query storage forbidden in prototype');
  if(/(?:guaranteed|cure[s]?|treats? (?:ADHD|anxiety)|brain reprogrammed|limitless concentration|never distracted again)/i.test(h))throw new Error('unsubstantiated benefit promise');
  if(!/If (?:a purchasing link is approved and later added here|an earning link is eventually added here), Final Vestige may earn a commission/i.test(h))throw new Error('clear adjacent prospective disclosure missing');
  if(!/<button\b[^>]*\bdisabled\b[^>]*aria-disabled="true"/i.test(h))throw new Error('merchant control not physically disabled');
  if(!/https:\/\/finalvestige\.com\/focus\//i.test(h))throw new Error('single existing Fieldbook route missing');
  if(/<a\b[^>]*href="https:\/\/(?:zen12|hypnosislive|brainwaveshots)\.com/i.test(h))throw new Error('product destination prematurely active');
  return true;
}
function assertSources(){
  assert.equal(register.release,'UNPUBLISHED_HARD_HOLD');
  assert.ok(register.sources.length>=15);
  assert.ok(register.claims.length>=25);
  assert.equal(register.commercial_holds.length,18);
  const src=new Set(register.sources.map(x=>x.id));
  assert.equal(src.size,register.sources.length);
  for(const s of register.sources){assert.ok(/^https:\/\//.test(s.url));assert.ok(s.scope?.length>5)}
  for(const c of register.claims){assert.ok(src.has(c.source_id)); assert.ok(c.disposition)}
  for(const g of register.commercial_holds){assert.equal(g.status,'HARD_HOLD');assert.ok(g.owner)}
  assert.ok(register.creator_candidate_fit.every(c=>c.grok_asset_id===null));
  assert.equal(register.kpi_status,'NOT_COMPUTABLE');
}
function check(){
  [a,b,hub].forEach(safeHtml);
  assert.equal(neutral(a),neutral(b),'A/B buyer content must be byte identical');
  assert.ok(b.includes('Optional original film concept'));
  assert.ok(!a.includes('Optional original film concept'));
  assert.ok(b.includes('Static SVG poster only.'));
  assert.ok(b.includes('Timecoded original narration'));
  assert.ok(b.includes('role="img"'));
  assert.ok(b.includes('<desc id="poster-desc">'));
  assert.ok(/^WEBVTT\s/m.test(vtt));
  assert.equal((vtt.match(/--> /g)||[]).length,6);
  assert.ok(vtt.includes('00:00:42.000'));
  assert.ok(article.length>7000);
  for(const url of ['pubmed.ncbi.nlm.nih.gov/12470132/','pubmed.ncbi.nlm.nih.gov/15994228/','pubmed.ncbi.nlm.nih.gov/39032268/'])assert.ok(article.includes(url));
  assert.ok(dossier.includes('NOT COMPUTABLE'));
  assert.ok(dossier.includes('Founder/Commerce'));
  assertSources();
}
check();
const attacks=[
  a.replace(' disabled aria-disabled="true"',' aria-disabled="true"'),
  a.replace(/If a purchasing link is approved and later added here, Final Vestige may earn a commission[^<]*/,''),
  a+'<script>fetch("https://tracker.example/x")</script>',
  a+'<form action="/subscribe"></form>',
  a+'<iframe src="https://seller.example/"></iframe>',
  a+'<video autoplay></video>',
  a.replaceAll('https://finalvestige.com/focus/','/new-duplicate-mailing-list'),
  a+'<a href="https://zen12.com/getstarted">buy</a>',
  a+'<a href="https://affiliates.inspire3.com/?id=unknown">affiliate</a>',
  a.replace('name="robots" content="noindex,nofollow"','name="robots" content="index"'),
  a.replace('lang="en"','lang=""'),
  a+'<span>guaranteed limitless concentration</span>',
  a+'<span>utm_campaign=private</span>',
  b.replace('disabled aria-disabled="true"','aria-disabled="true"'),
  hub.replace('disabled aria-disabled="true"','aria-disabled="true"')
];
let rejected=0;
for(const attack of attacks){
  try{safeHtml(attack)}catch{rejected++}
}
assert.equal(rejected,attacks.length,'All intentionally unsafe fixtures must be rejected');
console.log(JSON.stringify({baseline:'PASS',negative_rejected:rejected,negative_total:attacks.length,source_count:register.sources.length,claim_count:register.claims.length,commercial_holds:register.commercial_holds.length,mode:'native_node_required_for_this_script',commercial:'HARD_HOLD'},null,2));
