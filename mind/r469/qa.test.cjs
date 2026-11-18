// Run from the repository checkout: node --test mind/r469/qa.test.cjs
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const read = name => fs.readFileSync(path.join(__dirname,name),'utf8');
const a=read('ZEN12_A_TEXT_GUIDE.html'), b=read('ZEN12_B_OPTIONAL_42S_GUIDE.html');
const hub=read('MIND_ARCHIVE_WP_SOURCE_ONLY.html'),article=read('THE_HALF_SECOND_AFTER_FIRST_THING.md');
const matrix=JSON.parse(read('CLAIM_MERCHANT_MATRIX.json'));
const vtt=read('ZEN12_FILM_CAPTIONS.vtt'),poster=read('ZEN12_FILM_POSTER.svg');
const pages=[a,b,hub];

test('A and B have disabled CTA, clear prospective commission disclosure and no seller earning link',()=>{
  for(const html of[a,b]){
    assert.match(html,/disabled aria-disabled="true"/);
    assert.match(html,/Prospective affiliate disclosure/);
    assert.match(html,/No such affiliate link is active/i);
    assert.doesNotMatch(html,/href="https:\/\/(?:zen12|inspire3|affiliates\.inspire3)\.com/i);
    assert.doesNotMatch(html,/<form\b/i);
  }
});
test('disclosure appears immediately before commercial control',()=>{
  for(const html of[a,b]){
    const i=html.indexOf('Prospective affiliate disclosure'),j=html.indexOf('<button type="button" disabled');
    assert.ok(i>0&&j>i&&j-i<600);
  }
});
test('buyer substance identical except optional film and HTML title',()=>{
  const normalize=s=>s.replace(/<section class="film"[\s\S]*?<\/section>/,'').replace(/<title>[^<]*<\/title>/,'').replace(/\s+/g,' ');
  assert.equal(normalize(a),normalize(b));
});
test('B represents an unembedded optional video concept and complete transcript',()=>{
  assert.match(b,/No playback is embedded/);
  assert.match(b,/Read the complete video transcript/);
  assert.doesNotMatch(b,/<video\b/);
});
test('six exact nonoverlapping caption intervals total 42 seconds',()=>{
  const intervals=[...vtt.matchAll(/(\d\d):(\d\d):(\d\d)\.\d+ --> (\d\d):(\d\d):(\d\d)\.\d+/g)]
     .map(m=>[Number(m[1])*3600+Number(m[2])*60+Number(m[3]),Number(m[4])*3600+Number(m[5])*60+Number(m[6])]);
  assert.equal(intervals.length,6);
  intervals.forEach((x,i)=>assert.deepEqual(x,[7*i,7*(i+1)]));
});
test('original SVG has a human-readable title and description',()=>{
  assert.match(poster,/<title id="title">/);
  assert.match(poster,/<desc id="desc">/);
});
test('hub has four streams, real published destinations and no duplicate tracking/opt in',()=>{
  for(const id of['attention','suggestion','practice','tools']) assert.ok(hub.includes('id="'+id+'"'));
  assert.match(hub,/https:\/\/finalvestige\.com\/focus\//);
  assert.match(hub,/https:\/\/finalvestige\.com\/2026\/11\/02\/mesmerism\//);
  assert.doesNotMatch(hub,/<script\b|<form\b/i);
});
test('article cites primary data, limitations and editorial firewall',()=>{
  assert.match(article,/lag-1 sparing/);
  assert.match(article,/10,704/);
  assert.match(article,/2007/);
  assert.match(article,/no commission-bearing URL/);
  assert.match(article,/pubmed\.ncbi\.nlm\.nih\.gov\/1500880/);
});
test('matrix never converts a candidate product into live merchant approval',()=>{
  assert.ok(matrix.claim_decisions.length>=30);
  assert.ok(matrix.release_gates.length>=30);
  assert.ok(matrix.release_gates.every(g=>g.status==='HOLD'&&!g.passed));
  assert.equal(matrix.commercial.active_affiliate_links,0);
  assert.equal(matrix.commercial.realized_net_revenue_per_1000_qualified_sessions,null);
});
test('no added client trackers and no autoplaying video',()=>{
  for(const html of pages){
    assert.doesNotMatch(html,/<script\b|<iframe\b|<video\b[^>]*autoplay/i);
  }
});
test('responsive, semantic, accessible static HTML shell',()=>{
  for(const html of pages){
    assert.match(html,/<html lang="en">/);
    assert.match(html,/name="viewport"/);
    assert.match(html,/<main\b/);
    assert.match(html,/@media/);
  }
});
test('FTC and original research sources remain present',()=>{
  const urls=Object.values(matrix.sources);
  assert.ok(urls.some(x=>x.includes('ftc.gov')));
  assert.ok(urls.some(x=>x.includes('37205669')));
  assert.ok(urls.some(x=>x.includes('1500880')));
});
