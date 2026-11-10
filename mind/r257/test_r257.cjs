#!/usr/bin/env node
'use strict';
/** Mind R257: fail-closed source acceptance. Native: node mind/r257/test_r257.cjs
 * No network, no paid calls, no browser/CMS/merchant access.
 * Optional video check (after local render): R257_VIDEO=/path/to/preview.mp4 node ...
 */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=__dirname;
const read=n=>fs.readFileSync(path.join(root,n),'utf8');
const files={
article:read('TWELVE-MINUTES-AND-THE-FAIR-TEST-UNPUBLISHED.md'),
a:read('zen12-text-only-A-UNPUBLISHED.html'),
b:read('zen12-optional-film-B-UNPUBLISHED.html'),
hub:read('MIND-ARCHIVE-FOUR-STREAM-UNPUBLISHED-WP-PREVIEW.html'),
vtt:read('zen12_42s_preview.vtt'),
renderer:read('build_zen12_r257_preview.py'),
matrix:read('CLAIM-PROOF-OFFER-REVENUE-GATES.json'),
plan:read('REVENUE-FIRST-CREATOR-EXPERIMENT-RELEASE.md')
};
function validate(x){
 const m=JSON.parse(x.matrix), sourceIds=m.source_records.map(r=>r.id), gates=m.authorization_gates;
 assert.equal(m.status,'UNPUBLISHED_HARD_HOLD');
 assert.equal(m.commercial_activation,false);
 assert.equal(m.claims.length,33);
 assert.equal(m.source_records.length,15);
 assert.equal(gates.length,16);
 assert.equal(new Set(gates.map(g=>g.id)).size,16);
 assert.equal(new Set(sourceIds).size,15);
 assert.ok(gates.every(g=>g.status==='HARD_HOLD'));
 assert.equal(m.audit.gates_cleared,0);
 assert.ok(m.claims.every(c=>c.source_ids.length>0 && c.source_ids.every(id=>sourceIds.includes(id))));
 assert.ok(m.claims.some(c=>c.id==='C11'&&c.classification==='merchant_efficacy_unsubstantiated'));
 assert.ok(m.claims.some(c=>c.id==='C23'&&c.classification==='prohibited_false_inference'));
 for(const key of ['a','b','hub']){
  const h=x[key];
  assert.match(h,/<!doctype html>/i);
  assert.match(h,/<html lang="en">/);
  assert.match(h,/<meta name="viewport"/);
  assert.doesNotMatch(h,/<script\b|<iframe\b|<form\b|<input\b|<video\\b|onerror\s*=|onclick\s*=/i);
  assert.doesNotMatch(h,/href=["']https?:\/\/(?:www\.)?(?:zen12\.com|affiliates\.inspire3\.com|brainwaveshots\.com|hypnosislive\.com)/i);
  assert.doesNotMatch(h,/(?:pixel|doubleclick\.net|facebook\.net\/?en_US\/fbevents|gtag\s*\()/i);
  assert.match(h,/https:\/\/finalvestige\.com\/focus\//);
 }
 for(const key of ['a','b']){
  const h=x[key];
  assert.match(h,/<button[^>]*class="cta"[^>]*disabled\b[^>]*aria-describedby="hold disclosure"/);
  const i=h.indexOf('id="disclosure"'),j=h.indexOf('id="hold"');
  assert.ok(i>0 && j>0 && Math.abs(i-j)<800,'disclosure is adjacent to disabled CTA');
  assert.match(h,/may earn a commission at no additional cost to you/i);
  assert.match(h,/not an endorsement|not a product trial/i);
  assert.match(h,/2023 systematic review/i);
  assert.match(h,/not.*trial/i);
  assert.match(h,/seller.*promotional page/i);
 }
 assert.doesNotMatch(x.a,/<details class="film"/);
 assert.match(x.b,/<details class="film" id="optional-film">/);
 assert.match(x.b,/<summary>/);
 assert.match(x.b,/<svg[^>]*role="img"[^>]*aria-labelledby=/);
 assert.match(x.b,/<title id="poster-title">/);
 assert.match(x.b,/<desc id="poster-desc">/);
 assert.match(x.b,/No autoplay, scripts, remote media or tracking/i);
 const btext=x.b.replace(/<details class="film"[\s\S]*?<\/details>/,'').replace('OPTIONAL-FILM','TEXT-ONLY');
 assert.equal(btext,x.a,'all purchasing copy must be identical outside optional film');
 assert.equal((x.b.match(/<button/g)||[]).length,1);
 assert.equal((x.a.match(/<button/g)||[]).length,1);
 assert.match(x.hub,/Perception &amp; Attention/i);
 assert.match(x.hub,/HISTORY OF SUGGESTION/);
 assert.match(x.hub,/PRACTICE &amp; REFLECTION/);
 assert.match(x.hub,/TOOLS UNDER REVIEW/);
 assert.doesNotMatch(x.hub,/href=["'][^"']*puysegurs-animal-magnetism-files/);
 assert.match(x.article,/Puységur.*not.*verified destination/is);
 assert.match(x.article,/informal personal observation exercise/i);
 assert.match(x.article,/not a clinical trial/i);
 assert.match(x.plan,/Net revenue \/ 1,000/i);
 assert.match(x.plan,/asset_id/i);
 assert.match(x.plan,/Issue #820/);
 assert.match(x.plan,/Mind hub PR #172/);
 assert.match(x.renderer,/ffmpeg/);
 assert.match(x.renderer,/No consumer claims/);
 // The timecodes are all in strict VTT format HH:MM:SS.mmm and contiguous.
 const ranges=[...x.vtt.matchAll(/^(\d{2}):(\d{2}):(\d{2})\.(\d{3}) --> (\d{2}):(\d{2}):(\d{2})\.(\d{3})$/gm)];
 const clock=([h,m,s,ms])=>{assert.ok(+m<60&&+s<60&&+ms<1000);return +h*3600000+ +m*60000+ +s*1000+ +ms};
 assert.ok(x.vtt.startsWith('WEBVTT\n\n'));
 assert.equal(ranges.length,7);
 let edge=0;
 for(const r of ranges){
  const start=clock(r.slice(1,5)),end=clock(r.slice(5,9));
  assert.equal(start,edge);assert.equal(end-start,6000);edge=end;
 }
 assert.equal(edge,42000);
 assert.ok(!/HYPERLINK|COOKIE|MERCHANT_LINK_ACTIVE/.test(x.plan));
 return 'BASELINE PASS · 15 sources · 33 claims · 16 HARD_HOLD gates · 7 exact contiguous caption windows (42 seconds)';
}
console.log(validate(files));
const cases=[
 ['active merchant URL',o=>o.a=o.a.replace('href="https://finalvestige.com/focus/"','href="https://zen12.com/secret/"')],
 ['enabled checkout',o=>o.a=o.a.replace(' disabled aria-describedby',' aria-describedby')],
 ['remove disclosure',o=>o.a=o.a.replace('may earn a commission at no additional cost to you','benefits for everyone')],
 ['affiliate approval fabricated',o=>{let m=JSON.parse(o.matrix);m.authorization_gates[0].status='APPROVED';o.matrix=JSON.stringify(m)}],
 ['source provenance removed',o=>{let m=JSON.parse(o.matrix);m.claims[0].source_ids=['BOGUS'];o.matrix=JSON.stringify(m)}],
 ['duplicate commercial gate',o=>{let m=JSON.parse(o.matrix);m.authorization_gates[2].id=m.authorization_gates[1].id;o.matrix=JSON.stringify(m)}],
 ['evidence reclassified',o=>{let m=JSON.parse(o.matrix);m.claims.find(c=>c.id==='C11').classification='scientifically_proven';o.matrix=JSON.stringify(m)}],
 ['injected tracking',o=>o.b=o.b.replace('</body>','<script src="https://example.org/tracker.js"></script></body>')],
 ['new newsletter form',o=>o.hub=o.hub.replace('</body>','<form><input type="email"></form></body>')],
 ['forced playback',o=>o.b=o.b.replace('</body>','<video autoplay></video></body>')],
 ['hidden promo destination',o=>o.b=o.b.replace('href="https://finalvestige.com/focus/"','href="https://zen12.com/hnp"')],
 ['A/B copy changed',o=>o.b=o.b.replace('organized library','miracle library')],
 ['caption starts late',o=>o.vtt=o.vtt.replace('00:00:06.000 --> 00:00:12.000','00:00:06.100 --> 00:00:12.000')],
 ['caption malformed time',o=>o.vtt=o.vtt.replace('00:00:24.000 --> 00:00:30.000','00:00:65.000 --> 00:00:30.000')],
 ['caption shorter film',o=>o.vtt=o.vtt.replace('00:00:36.000 --> 00:00:42.000','00:00:36.000 --> 00:00:41.000')],
 ['false available Puységur link',o=>o.hub=o.hub.replace('Puységur\'s Animal Magnetism Files','<a href="https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/">Puységur\'s Animal Magnetism Files</a>')],
 ['false commercial activation',o=>{let m=JSON.parse(o.matrix);m.commercial_activation=true;o.matrix=JSON.stringify(m)}],
 ['missing source list',o=>{let m=JSON.parse(o.matrix);m.source_records=[];o.matrix=JSON.stringify(m)}],
 ['unlicensed outbound catalog CTA',o=>o.a=o.a.replace('href="https://finalvestige.com/focus/"','href="https://hypnosislive.com/"')],
 ['new pixel',o=>o.hub=o.hub.replace('</body>','<script>gtag("event","sale")</script></body>')]
];
let rejected=0;
for(const [name,mutate] of cases){
 const mutated={...files};mutate(mutated);
 try{validate(mutated);throw Error('UNREJECTED UNSAFE MUTATION: '+name)}
 catch(e){if(String(e.message).startsWith('UNREJECTED'))throw e;rejected++}
}
console.log(rejected+'/'+cases.length+' unsafe variants REJECTED');
if(process.env.R257_VIDEO){
 const cp=require('node:child_process');
 const info=JSON.parse(cp.execFileSync('ffprobe',['-v','error','-show_entries','format=duration:stream=width,height,codec_name','-of','json',process.env.R257_VIDEO],{encoding:'utf8'}));
 assert.equal(+info.format.duration,42);
 assert.ok(info.streams.some(s=>s.width===540 && s.height===960 && s.codec_name==='h264'));
 console.log('LOCAL MP4 PASS · 42.000 seconds · 540×960 H.264 (silent, not live)');
}
console.log('SOURCE TESTS ≠ browser a11y/WordPress/merchant checkout/paid commission confirmation.');
