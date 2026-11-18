// Portable Node built-in tests; run node --test mind/r479/qa.test.cjs
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const read=n=>fs.readFileSync(path.join(__dirname,n),'utf8');
const a=read('ZEN12_A_TEXT_GUIDE.html'),b=read('ZEN12_B_OPTIONAL_FILM.html'),hub=read('MIND_HUB_SOURCE_ONLY.html'),article=read('THE_SECOND_THING_YOU_NEVER_SAW.md'),vtt=read('OPTIONAL_42_SECOND_CAPTIONS.vtt'),m=JSON.parse(read('SOURCE_CLAIM_PERMISSION_MATRIX.json'));
const body=s=>s.match(/<div id="buyer-copy">([\s\S]*?)<\/div>/)?.[1];
for(const [name,s] of [['A',a],['B',b]]) {
 test(name+' native disabled commercial button',()=>assert.match(s,/<button[^>]*\sdisabled\b/));
 test(name+' adjacent plain disclosure',()=>{const x=s.indexOf('id="affiliate-disclosure"'),y=s.indexOf('<button');assert(x>=0&&y>x&&y-x<500)});
 test(name+' no actual affiliate tracking',()=>assert.doesNotMatch(s,/affiliate_id=|aff_id=|refersion\.com\/r\//i));
 test(name+' no JS',()=>assert.doesNotMatch(s,/<script\b|onclick=|onload=/i));
 test(name+' no new signup form',()=>assert.doesNotMatch(s,/<form\b/i));
 test(name+' no autoplay attribute',()=>assert.doesNotMatch(s,/<video[^>]*\sautoplay(?:\s|=|>)/i));
 test(name+' responsive reduced motion',()=>{assert.match(s,/name="viewport"/);assert.match(s,/prefers-reduced-motion/);});
 test(name+' natural buyer qualifications',()=>{assert.match(s,/refund/i);assert.match(s,/price/i);assert.match(s,/seller/i);});
 test(name+' explicit free alternative',()=>assert.match(s,/Focus Fieldbook/));
 test(name+' no advertised numeric price',()=>assert.doesNotMatch(s,/\$[0-9]+/));
}
test('substantive buyer content identical',()=>assert.equal(body(a),body(b)));
test('film is only an optional concept',()=>{assert.match(b,/<details>/);assert.match(b,/storyboard only/);assert.doesNotMatch(b,/<video\b/);});
test('6 caption cues with 42s end',()=>{assert.equal((vtt.match(/-->/g)||[]).length,6);assert.match(vtt,/00:00:42\.000/);});
test('four archive streams',()=>['Perception & Attention','History of Suggestion','Practice & Reflection','Tools Under Review'].forEach(s=>assert.match(hub,new RegExp(s))));
test('hub existing URLs',()=>['change-blindness/','mesmerism/','/focus/','puysegurs-animal-magnetism-files/'].forEach(s=>assert.ok(hub.includes(s))));
test('hub no form or JS',()=>assert.doesNotMatch(hub,/<form\b|<script\b/));
test('21 commercial hard gates',()=>{assert.equal(m.gates.length,21);assert.ok(m.gates.every(g=>g.passed===false));});
test('unsupported claims not allowed',()=>m.claims.filter(c=>!c.may_publish).forEach(c=>assert.equal(c.may_publish,false)));
test('no earning URL',()=>assert.equal(m.authorization.affiliate_url,null));
test('source ledger integrity',()=>{const all=new Set(m.sources.map(s=>s.id));m.claims.forEach(c=>assert.ok(all.has(c.source)));});
test('article grounded attention studies',()=>['Raymond','Chun','Slagter','lag-1','Puységur'].forEach(s=>assert.ok(article.toLowerCase().includes(s.toLowerCase()))));
test('article separates study from product',()=>assert.match(article,/does not prove|does \*\*not\*\* show/i));
