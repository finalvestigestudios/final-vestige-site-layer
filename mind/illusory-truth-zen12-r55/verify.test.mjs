import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {ATTRIBUTION_ENABLED,measurementEnabled,validateSyntheticEvent,aggregateSyntheticRows} from './attribution.mjs';
const dir=path.dirname(fileURLToPath(import.meta.url));
const read=name=>fs.readFileSync(path.join(dir,name),'utf8');
const a=read('presell-a-text.html'),b=read('presell-b-film.html'),inv=read('investigation.md'),wpi=read('investigation.wp.html'),hub=read('mind-archive-noncanonical.html'),csv=read('claims-permissions.csv'),vtt=read('film.vtt'),sources=read('source-ledger.md');
const core=s=>s.match(/<section class="guide-core" id="guide-core">([\s\S]*?)<\/section>/)?.[1];
const clean=s=>{
 assert.doesNotMatch(s,/<(?:script|iframe|form)\b/i);
 assert.doesNotMatch(s,/<a\b[^>]*href=["']https?:\/\/(?:www\.)?(?:zen12\.com|inspire3\.com|affiliates\.inspire3\.com)/i);
 assert.doesNotMatch(s,/<video\b|autoplay|navigator\.sendBeacon|localStorage|document\.cookie|gclid|fbclid|utm_source/i);
};
test('A and B substantive guide core is byte-identical and substantial',()=>{
 assert.ok(core(a)&&core(a).length>12000);
 assert.equal(core(a),core(b));
});
test('both versions offer actual disabled button with nearby prospective commission notice',()=>{
 for(const page of [a,b]){
  const idx=page.lastIndexOf('may earn a commission');
  const btn=page.indexOf('<button type="button" disabled aria-disabled="true">');
  assert.ok(idx>=0 && btn>idx && btn-idx<380,'disclosure near disabled control');
  assert.match(page,/No earning link is currently active/);
 }
});
test('A/B contain no active merchant, script, embeds, signup or tracking',()=>[a,b].forEach(clean));
test('B has optional readable transcript with original labeled static poster; no fake video player',()=>{
 assert.match(b,/<svg[^>]*role="img"/);
 assert.match(b,/<details><summary>Read the complete 40-second video transcript<\/summary>/);
 assert.match(b,/0–6 seconds/);
 assert.doesNotMatch(b,/<video/);
});
test('film VTT is continuous and ends at forty seconds',()=>{
 assert.equal((vtt.match(/ --> /g)||[]).length,6);
 assert.match(vtt,/00:00:34\.000 --> 00:00:40\.000/);
});
test('research has no merchant product endorsement',()=>{
 assert.match(inv,/The Sentence That Became Familiar/);
 assert.doesNotMatch(inv,/Zen12|Inspire3|may earn a commission/i);
 assert.match(inv,/26301795/);
 assert.match(wpi,/The Sentence That Became Familiar/);
});
test('hub does not link unpublished pages and links the two published properties',()=>{
 clean(hub);
 assert.match(hub,/puysegurs-animal-magnetism-files/);
 assert.match(hub,/finalvestige.com\/focus\//);
 assert.doesNotMatch(hub,/href=["']\/mind\//);
});
test('matrix has at least 48 source decisions and all required statuses',()=>{
 assert.ok(csv.trim().split(/\n/).length>=49);
 for(const value of ['supported','seller_only','exclude','blocked','verify'])assert.ok(csv.includes(value));
 for(const id of ['P1','P2','P3','P4','P5','S4','S6','I2','G1','G2'])assert.ok(sources.includes('|'+id+'|'));
});
test('tracking default disabled and synthetic validation only',()=>{
 assert.equal(ATTRIBUTION_ENABLED,false);
 assert.equal(measurementEnabled(),false);
 const good={topic:'illusory-truth',channel:'organic',variant:'A',action:'guide_view'};
 assert.deepEqual(validateSyntheticEvent(good),good);
 for(const bad of [{...good,email:'buyer@example.com'},{...good,ip:'127.0.0.1'},{...good,phone:'12345'},{...good,utm:'x'},{...good,channel:'anything'},Object.assign(Object.create(null),good)])assert.equal(validateSyntheticEvent(bad),null);
});
test('synthetic small-group aggregation suppresses n19, permits n20',()=>{
 const e={topic:'illusory-truth',channel:'organic',variant:'A',action:'guide_view'};
 assert.deepEqual(aggregateSyntheticRows(Array(19).fill(e)),[]);
 assert.deepEqual(aggregateSyntheticRows(Array(20).fill(e)),[{group:'illusory-truth|organic|A|guide_view',count:20}]);
});
test('unsafe commerce and telemetry mutations are caught',()=>{
 for(const bad of ['<a href="https://zen12.com/getstarted">purchase</a>','<script>track()</script>','<form><input name="email"></form>','<video autoplay src="/v.mp4"></video>'])assert.throws(()=>clean(a+bad));
});
test('no new list and no active outbound link in the investigation',()=>{
 assert.doesNotMatch(wpi,/<form\b|subscribe now|<script\b/i);
 assert.doesNotMatch(a,/<a[^>]+href=["']https?:\/\/zen12/i);
});
