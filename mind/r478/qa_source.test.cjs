/* R478 source-only QA. Execute after checkout: node mind/r478/qa_source.test.cjs
   No network, no credentials, no CMS changes, no assertions about real-world revenue. */
'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const base=__dirname;
const get=(name)=>fs.readFileSync(path.join(base,name),'utf8');
const A=get('ZEN12_GUIDE_A_TEXT_ONLY.html'),B=get('ZEN12_GUIDE_B_OPTIONAL_FILM.html');
const hub=get('MIND_ARCHIVE_WP_SOURCE_ONLY.html');
const poster=get('CHOICE_BLINDNESS_POSTER.svg'),vtt=get('CHOICE_BLINDNESS_42S.vtt');
const article=get('THE_CHOICE_YOU_NEVER_MADE.md');
const d=get('CREATOR_TO_NET_REVENUE_ACCEPTANCE.md');
const evidence=JSON.parse(get('PRODUCT_CLAIM_SOURCE_PERMISSION_MATRIX.json'));
const filmBlock=/<section class="study" aria-labelledby="film-title">[\s\S]*?<\/section>/;
const guard=(s)=> {
  assert.match(s,/\bdisabled\s+aria-describedby="merchant commission-note"/);
  assert.match(s,/<p class="disclosure" id="commission-note">/);
  assert.match(s,/<button\b[^>]*disabled/);
  assert.doesNotMatch(s,/<script\b/i);
  assert.doesNotMatch(s,/<form\b/i);
  assert.doesNotMatch(s,/<iframe\b/i);
  assert.doesNotMatch(s,/<a\b[^>]*href=["'][^"']*(ref=|affid=|affiliate_id=|clickbank|hop=)/i);
  assert.doesNotMatch(s,/<video\b[^>]*\bautoplay\b/i);
  assert.doesNotMatch(s,/(?:\bprice\s*:\s*\$\d+|coupon code\s+[A-Z0-9]{4,})/i);
  assert.match(s,/<meta name="robots" content="noindex,nofollow"/);
};
test('text guide holds commercial activation and has adjacent disclosure',()=>guard(A));
test('film guide holds commercial activation and has adjacent disclosure',()=>guard(B));
test('identical substantive copy across A/B; only optional film differs',()=> {
  assert.match(B,filmBlock);
  assert.equal(B.replace(filmBlock,''),A);
});
test('no broken player or forced playback; optional transcript works without scripts',()=> {
  assert.doesNotMatch(B,/<video\b/i);
  assert.match(B,/<details><summary>Read the complete 42-second transcript/);
  assert.match(B,/CHOICE_BLINDNESS_POSTER\.svg/);
  assert.doesNotMatch(B,/autoplay\s*=/i);
});
test('source poster contains title, desc, correct size',()=> {
  assert.match(poster,/<svg/);assert.match(poster,/<title/);assert.match(poster,/<desc/);
  assert.match(poster,/width="1280" height="720"/);
});
test('captions cover 42 seconds, six cues in order, no zero-duration cue',()=>{
  assert.match(vtt,/^WEBVTT/);
  const cues=[...vtt.matchAll(/(\d\d):(\d\d):(\d\d)\.(\d\d\d) --> (\d\d):(\d\d):(\d\d)\.(\d\d\d)/g)];
  assert.equal(cues.length,6);
  const ms=(m,i)=>Number(m[i])*3600000+Number(m[i+1])*60000+Number(m[i+2])*1000+Number(m[i+3]);
  cues.forEach((c,i)=>{assert.ok(ms(c,5)>ms(c,1));if(i)assert.equal(ms(c,1),ms(cues[i-1],5));});
  assert.equal(ms(cues[0],1),0);
  assert.equal(ms(cues[5],5),42000);
});
test('archive is WordPress source-only with four streams and existing free route',()=> {
  assert.match(hub,/UNPUBLISHED/i);assert.match(hub,/Perception &amp; Attention/);
  assert.match(hub,/History of Suggestion/);assert.match(hub,/Practice &amp; Reflection/);
  assert.match(hub,/Tools Under Review/);assert.match(hub,/finalvestige.com\/focus/);
  assert.doesNotMatch(hub,/<script\b|<form\b/i);
});
test('merchant and FTC bibliography exists in guides',()=> {
  for(const s of [A,B])for(const u of ['inspire3.com','zen12.com/about','zen12.com/secret/','ftc.gov','doi.org/10.1371/journal.pone.0286023'])assert.ok(s.includes(u),u);
});
test('release matrix every claim maps to a real source and every gate stays HOLD',()=>{
  assert.ok(evidence.claims.length>=20);assert.ok(evidence.sources.length>=12);
  const ids=new Set(evidence.sources.map(x=>x.id));for(const c of evidence.claims)assert.ok(ids.has(c.sourceId),c.id);
  assert.ok(evidence.releaseGates.length>=16);assert.ok(evidence.releaseGates.every(g=>g.status==='HOLD_NOT_VERIFIED'));
  assert.equal(evidence.activation,'HARD_HOLD');
});
test('scientific article keeps 2025 contradiction and source trail',()=>{
  for(const s of ['2025 challenge','Grassi','Johansson','Hall','Puységur','https://doi.org/10.3389/fpsyg.2025.1598254','not','https://finalvestige.com/focus/'])assert.ok(article.includes(s),s);
  assert.ok(article.split(/\s+/).length>=2000);
});
test('measurement spec prohibits click-as-sale and no unknown revenue arithmetic',()=>{
  assert.match(d,/NOT COMPUTABLE/);assert.match(d,/affiliate_outbound/);
  assert.match(d,/merchant_confirmed_order/);assert.match(d,/7\/30-day/);
  assert.match(d,/No synthetic asset IDs/);
});
test('mutation sentinels reject enabled link, deleted disclosure and injected script',()=>{
  assert.throws(()=>guard(A.replace(' disabled aria-describedby',' aria-describedby')));
  assert.throws(()=>guard(A.replace('<p class="disclosure"','<p class="unmarked"')));
  assert.throws(()=>guard(A.replace('</main>','<script src="https://tracker.example/x.js"></script></main>')));
  assert.throws(()=>guard(A.replace('href="https://zen12.com/about"','href="https://zen12.com/about?affid=GUESS"')));
  assert.throws(()=>guard(A.replace('</main>','<form><input type="email"/></form></main>')));
  assert.throws(()=>guard(A.replace('</main>','<video autoplay></video></main>')));
});