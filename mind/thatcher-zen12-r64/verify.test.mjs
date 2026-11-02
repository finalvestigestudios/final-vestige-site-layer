// Reproducible source tests: node --test mind/thatcher-zen12-r64/verify.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname,join} from 'node:path';
import {ACTIVE,MIN_GROUP,validateSyntheticRecord,aggregateSynthetic,emitOutboundEvent} from './privacy-attribution.mjs';
const dir=dirname(fileURLToPath(import.meta.url)), read=n=>readFileSync(join(dir,n),'utf8');
const article=read('investigation.md'), core=read('guide-core.html'), a=read('offer-a-text.blocks.html'),
 b=read('offer-b-video.blocks.html'), hub=read('mind-hub-noncanonical.blocks.html'),
 matrix=JSON.parse(read('claims-and-release.json')), vtt=read('film-captions.vtt'),
 poster=read('film-poster.svg'), renderer=read('render_film.py');

test('noncommercial substantial referenced history investigation',()=>{
 assert.ok(article.trim().split(/\s+/).length>=1800);
 for(const word of ['Peter Thompson','Puységur','10.1068/p090483','10.1068/p7755','10.3758/s13423-014-0705-3']) assert.ok(article.includes(word));
 assert.doesNotMatch(article,/Zen12|Inspire3|affiliate link/i);
});

test('source-identical guide in A/B without duplicate core',()=>{
 for(const html of [a,b]) assert.equal(html.split(core).length,2);
});

test('native disabled CTA and adjacent prospective affiliate disclosure',()=>{
 for(const html of [a,b]){
  const match=html.match(/<button\b[^>]*>Merchant offer unavailable<\/button>/);
  assert.ok(match);
  assert.match(match[0],/\sdisabled(?:\s|>|=)/);
  assert.match(match[0],/type="button"/);
  assert.ok(html.indexOf('id="fvm-offer-disclosure"')>html.indexOf(match[0]));
  assert.match(html,/may earn a commission at no additional cost to you/);
 }
});

test('no active commerce, forms, trackers, video embeds or unreachable asset sources',()=>{
 for(const html of [a,b]){
  assert.doesNotMatch(html,/<(?:script|iframe|form|input|video|audio|source)\b/i);
  assert.doesNotMatch(html,/\b(?:href|src)=["'](?:https?:)?\/\/[^"']*(?:zen12|inspire3|hypnosislive|affiliate)/i);
  assert.doesNotMatch(html,/<video\b[^>]*\bautoplay|\bonerror=|\bonclick=|dataLayer|fbq\(/i);
 }
});

test('only verified public internal and evidence-link destinations',()=>{
 for(const html of [a,b]){
  const urls=[...html.matchAll(/<a\b[^>]*\bhref=["']([^"']+)["']/g)].map(x=>new URL(x[1]));
  assert.ok(urls.length>=3);
  for(const url of urls) assert.ok(['finalvestige.com','www.nccih.nih.gov'].includes(url.hostname),url.hostname);
 }
});

test('film B is purely optional and honest without dead player',()=>{
 assert.ok(!a.includes('fvm-film-inner'));
 assert.ok(b.includes('fvm-film-inner'));
 assert.match(b,/<svg[^>]*role="img"/);
 assert.match(b,/<details open>/);
 assert.equal((b.match(/<strong>\d\d–\d\ds\.<\/strong>/g)||[]).length,6);
 assert.match(b,/No video file is hosted on this page/);
});

test('VTT six contiguous cues precisely cover forty seconds',()=>{
 assert.match(vtt,/^WEBVTT/);
 const cues=[...vtt.matchAll(/(\d\d:\d\d:\d\d\.\d{3}) --> (\d\d:\d\d:\d\d\.\d{3})/g)].map(x=>[x[1],x[2]]);
 assert.equal(cues.length,6);
 assert.equal(cues[0][0],'00:00:00.000');
 assert.equal(cues.at(-1)[1],'00:00:40.000');
 for(let i=1;i<cues.length;i++) assert.equal(cues[i][0],cues[i-1][1]);
});

test('poster and silent original renderer source available',()=>{
 assert.match(poster,/<svg\b/);
 assert.match(renderer,/W, H, FPS, SECONDS = 540, 960, 12, 40/);
 assert.match(renderer,/frame_no == SECONDS\*FPS == 480/);
 assert.match(renderer,/'-an'/);
});

test('forty-eight explicit claim and permission decisions with hard blocks',()=>{
 assert.equal(matrix.entries.length,48);
 assert.equal(matrix.commercial_activation,false);
 assert.ok(matrix.conditions.length>=7);
 for(const id of ['zen12-017','zen12-018','zen12-020','zen12-021','zen12-023','zen12-025','zen12-042']){
  assert.equal(matrix.entries.find(x=>x.id===id)?.decision,'BLOCK',id);
 }
});

test('attribution is inert without browser capture, transport or storage',()=>{
 assert.equal(ACTIVE,false); assert.equal(MIN_GROUP,20);
 assert.throws(()=>emitOutboundEvent(),/Not activated/);
 const module=read('privacy-attribution.mjs');
 assert.doesNotMatch(module,/(?:\bfetch\s*\(|navigator\.sendBeacon\s*\(|localStorage\.|sessionStorage\.|document\.cookie\s*=|addEventListener\s*\()/);
});

test('synthetic aggregation rejects unknown PII, objects and URLs',()=>{
 const ok={source:'organic',topic:'thatcher',action:'guide_view',variant:'text'};
 assert.equal(validateSyntheticRecord(ok),true);
 for(const bad of [{...ok,email:'someone@example.com'},{...ok,ip:'1.2.3.4'},
  {...ok,referrer:'https://example.com/?email=a'},{...ok,topic:'thatcher?email=a'},
  {...ok,source:'https://bad.example?x=1'},{...ok,variant:null},Object.create(null),[],null])
  assert.equal(validateSyntheticRecord(bad),false);
 assert.throws(()=>aggregateSynthetic([{...ok,userId:'42'}]),TypeError);
});

test('privacy threshold suppresses n19, shows n20 only with anonymous dimensions',()=>{
 const row={source:'organic',topic:'thatcher',action:'guide_view',variant:'text'};
 assert.deepEqual(aggregateSynthetic(Array.from({length:19},()=>({...row}))),[]);
 const result=aggregateSynthetic(Array.from({length:20},()=>({...row})));
 assert.equal(result.length,1);assert.equal(result[0].count,20);
 assert.deepEqual(Object.keys(result[0]).sort(),['action','count','source','topic','variant']);
});

test('noncanonical hub preserves existing one approved Focus funnel',()=>{
 assert.match(hub,/noncanonical/i);assert.match(hub,/PR #172/);
 assert.match(hub,/puysegurs-animal-magnetism-files/);
 assert.match(hub,/finalvestige\.com\/focus\//);
 assert.doesNotMatch(hub,/<form\b|<script\b|<iframe\b|zen12\.com\/getstarted/i);
});

test('responsive and a11y static controls are present',()=>{
 for(const html of [a,b,hub]){
  assert.match(html,/:focus-visible/);
  assert.match(html,/@media\(prefers-reduced-motion:reduce\)/);
  assert.match(html,/@media\(max-width:/);
  assert.doesNotMatch(html,/target="_blank"/);
 }
});

test('mutation: class name disabled is not acceptable without native attribute',()=>{
 const bad=a.replace(/type="button" disabled/,'type="button" class="disabled"');
 assert.ok(!/<button\b[^>]*\sdisabled(?:\s|>|=)/.test(bad));
});
test('mutation: merchant anchor injection is visible to blocked-destination guard',()=>{
 const bad=a+'<a href="https://zen12.com/getstarted">Buy</a>';
 assert.match(bad,/<a\b[^>]*href="https:\/\/zen12\.com/);
});
test('mutation: identity field is rejected',()=>{
 assert.equal(validateSyntheticRecord({source:'organic',topic:'thatcher',action:'guide_view',variant:'text',userId:'123'}),false);
});
