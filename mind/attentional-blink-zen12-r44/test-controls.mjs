import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {sanitizeSyntheticRecord,summarizeSyntheticGroups} from './synthetic-attribution.mjs';
const read=n=>fs.readFileSync(new URL(n,import.meta.url),'utf8');
const a=read('zen12-guide-A.html'), b=read('zen12-guide-B.html'), art=read('article.html'), hub=read('mind-hub-alternative.html'), captions=read('film-captions.vtt');
const buyerCore=h=>{const s=h.indexOf('<section aria-labelledby="g0">'),e=h.indexOf('<aside class="hold"');return h.slice(s,e)};
for(const [variant,h] of [['A',a],['B',b]]){
 test(variant+' rejects active merchant destinations',()=>assert.doesNotMatch(h,/(href|src)=["']https?:\/\/(?:www\.)?(?:zen12|inspire3)\.com/i));
 test(variant+' contains no scripts forms iframe or video',()=>assert.doesNotMatch(h,/<(?:script|form|iframe|video)\b/i));
 test(variant+' has disclosure adjacent to disabled CTA',()=>assert.match(h,/may earn a commission[\s\S]{0,200}<\/p><p><button type="button" disabled/));
 test(variant+' has proper semantic headline',()=>assert.match(h,/<h1 id="zen44-title">/));
}
test('A and B share identical substantive guide core',()=>assert.equal(buyerCore(a),buyerCore(b)));
test('B has actual poster and honest no-video status',()=>{assert.match(b,/poster-title/);assert.match(b,/not a playable video/);assert.match(b,/transcript/);});
test('no vendor promotion inside independent article',()=>assert.doesNotMatch(art,/zen12|inspire3|affiliate|commission/i));
test('hub is read-only and links existing live routes',()=>{assert.match(hub,/puysegurs-animal-magnetism-files/);assert.match(hub,/finalvestige.com\/focus/);assert.doesNotMatch(hub,/<form\b/i)});
test('VTT proposes exactly six caption cues',()=>assert.equal((captions.match(/-->/g)||[]).length,6));
test('synthetic module refuses extra identifying keys',()=>assert.equal(sanitizeSyntheticRecord({variant:'text',topic:'attentional-blink',event:'guide_view',channel:'direct',email:'private@example.com'}),null));
test('synthetic module refuses invented sales event',()=>assert.equal(sanitizeSyntheticRecord({variant:'text',topic:'attentional-blink',event:'sale',channel:'direct'}),null));
test('groups under 20 suppressed',()=>{let record={variant:'film',topic:'attentional-blink',event:'guide_view',channel:'organic'};assert.equal(summarizeSyntheticGroups(Array(19).fill(record)).length,0);assert.equal(summarizeSyntheticGroups(Array(20).fill(record))[0].count,20)});
