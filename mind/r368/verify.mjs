// Mind R368 source-only verifier. Run: node mind/r368/verify.mjs
// No network, merchant access, browser or CMS writes. Static source checks only.
import { readFileSync } from 'node:fs';
import assert from 'node:assert/strict';
const root = new URL('.', import.meta.url);
const read = n => readFileSync(new URL(n, root), 'utf8');
const article = read('THE_CHOICE_YOU_NEVER_MADE.md');
const a = read('ZEN12_A_TEXT_GUIDE.html');
const b = read('ZEN12_B_OPTIONAL_FILM_CONCEPT.html');
const hub = read('MIND_ARCHIVE_WORDPRESS_REVIEW_ONLY.html');
const vtt = read('ORIGINAL_42S_CAPTIONS.vtt');
const doc = read('CONVERSION_ACCEPTANCE_AND_ROUTING.md');
const mat = JSON.parse(read('CLAIM_SOURCE_AUTHORIZATION_MATRIX.json'));
let checks = 0;
function check(name, fn){try{fn(); checks++; process.stdout.write('PASS '+name+'\n');}catch(e){throw new Error('FAIL '+name+': '+e.message);}}
const main = s => (s.match(/<main id="guide" class="wrap">[\s\S]*?<\/main>/)||[])[0] || '';
function safeBuyer(s){
  assert.match(s,/lang="en"/);assert.match(s,/<meta name="robots" content="noindex,nofollow,noarchive">/);
  assert.match(s,/<main id="guide"/);assert.match(s,/<h1>/);assert.match(s,/<h2/);
  assert.match(s,/<div class="disclose" id="affiliate-disclosure">/);
  assert.match(s,/<button class="cta" type="button" disabled aria-describedby="affiliate-disclosure merchant-blocker">/);
  assert.match(s,/If a later approved earning link is enabled/);
  assert.match(s,/no active earning link here/i);
  assert.ok(s.indexOf('id="affiliate-disclosure"') < s.indexOf('disabled aria-describedby="affiliate-disclosure'));
  assert.ok(s.indexOf('disabled aria-describedby="affiliate-disclosure')-s.indexOf('id="affiliate-disclosure"') < 600);
  assert.doesNotMatch(s,/<a\s[^>]*href=["']https?:\/\/(?:www\.)?(?:zen12\.com|inspire3\.com|affiliates\.inspire3\.com|hypnosislive\.com|brainwaveshots\.com)/i);
  assert.doesNotMatch(s,/<script\b|<iframe\b|<form\b|<input\b|\bonclick\s*=|\bonload\s*=|autoplay\b/i);
  assert.match(s,/https:\/\/finalvestige\.com\/focus\//);
  assert.match(s,/One.year|one.year/i);
  assert.match(s,/not a demonstrated product.specific finding/i);
  assert.match(s,/\$87/);
  assert.match(s,/\$87\.99/);
}
function safeHub(s){
  for(const id of ['perception','history','practice','tools']) assert.ok(s.includes('id="'+id+'"'));
  assert.match(s,/noindex,nofollow,noarchive/);
  assert.doesNotMatch(s,/<script\b|<form\b|<iframe\b|\bonclick\s*=|autoplay\b/i);
  assert.doesNotMatch(s,/<a\s[^>]*href=["']https?:\/\/(?:www\.)?(?:zen12\.com|inspire3\.com|hypnosislive\.com|brainwaveshots\.com)/i);
  assert.match(s,/not a live/);
}
function safeMatrix(m){
 assert.equal(m.claim_count,39);assert.equal(m.release_gate_count,32);assert.equal(m.public_source_count,14);
 assert.equal(m.claims.length,39);assert.equal(m.release_gates.length,32);
 assert.ok(m.claims.every(c=>c.release_state==='HOLD'));
 assert.ok(m.release_gates.every(g=>g.status==='HOLD'));
 assert.equal(m.commercial_state,'HARD_HOLD');
 assert.ok(m.claims.some(c=>c.classification==='NOT_AUTHENTICATED'));
 assert.ok(m.claims.some(c=>c.classification==='EXCLUDE_UNSUBSTANTIATED'));
 assert.ok(m.sources.every(s=>/^https:\/\//.test(s.url)));
}
function safeCaps(s){
 const cues=[...s.matchAll(/(\d\d:\d\d:\d\d\.\d\d\d) --> (\d\d:\d\d:\d\d\.\d\d\d)/g)];
 assert.equal(cues.length,6);
 const toMs=t=>{const [h,m,sec]=t.split(':');return Math.round((Number(h)*3600+Number(m)*60+Number(sec))*1000);};
 assert.equal(toMs(cues[0][1]),0);
 for(let i=0;i<cues.length;i++){const [_,start,end]=cues[i];assert.ok(toMs(end)>toMs(start));if(i>0)assert.equal(toMs(start),toMs(cues[i-1][2]));}
 assert.equal(toMs(cues[5][2]),42000);
}
check('investigation primary evidence',()=>{for(const s of ['10.1126/science.1111709','10.1016/j.cognition.2010.06.010','10.1371/journal.pone.0060554','puysegurs-animal-magnetism-files','No purchase is requested'])assert.ok(article.includes(s));});
check('A buyer safety',()=>safeBuyer(a));
check('B buyer safety',()=>safeBuyer(b));
check('A/B identical substantive <main>',()=>assert.equal(main(a),main(b)));
check('B visual is conceptual not video playback',()=>{assert.match(b,/<svg /);assert.match(b,/42-second film treatment/);assert.match(b,/No hosted or playable video exists/);assert.doesNotMatch(b,/<video\b|<audio\b/);});
check('six caption cues exactly 42 seconds',()=>safeCaps(vtt));
check('source-only hub safety',()=>safeHub(hub));
check('commercial matrix release hold',()=>safeMatrix(mat));
check('measured revenue not click conversions',()=>{assert.match(doc,/NOT COMPUTABLE/);assert.match(doc,/affiliate_click/);assert.match(doc,/settled/i);assert.match(doc,/verified.*human/i);});
check('no additional signup or paid tool',()=>{for(const s of [a,b,hub])assert.doesNotMatch(s,/<form\b|<script\b/);assert.match(doc,/no new form/i);});
let mutants=0;
function reject(name, fn){let caught=false;try{fn();}catch(e){caught=true;}assert.ok(caught,'Unsafe mutation escaped: '+name);mutants++;process.stdout.write('REJECTED '+name+'\n');}
reject('enable buyer purchase button',()=>safeBuyer(a.replace('type="button" disabled aria-describedby','type="button" aria-describedby')));
reject('remove local disclosure',()=>safeBuyer(a.replace('<div class="disclose" id="affiliate-disclosure">','<div id="deleted-disclosure">')));
reject('active Zen12 merchant anchor',()=>safeBuyer(a.replace('</body>','<a href="https://zen12.com/">Buy here</a></body>')));
reject('injected tracking script',()=>safeBuyer(b.replace('</body>','<script src="https://tracker.example/m.js"></script></body>')));
reject('added signup form',()=>safeBuyer(a.replace('</main>','<form><input name="email"></form></main>')));
reject('false video playback claim',()=>assert.doesNotMatch(b.replace('No hosted or playable video exists','<video autoplay>play</video>'),/<video\b|autoplay\b/));
reject('caption ends early',()=>safeCaps(vtt.replace('00:00:42.000','00:00:41.000')));
reject('release gate opened',()=>safeMatrix({...mat,release_gates:mat.release_gates.map((x,i)=>i===0?{...x,status:'OPEN'}:x)}));
reject('unsubstantiated merchant claim in hub link',()=>safeHub(hub.replace('</body>','<a href="https://inspire3.com/">Merchant</a></body>')));
process.stdout.write('R368 static verification '+checks+'/'+checks+' PASS; '+mutants+'/'+mutants+' unsafe mutations rejected. NO browser/CMS/merchant validation.\n');
