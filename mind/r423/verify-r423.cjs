'use strict';
/* Execute from this directory: node verify-r423.cjs
 * Static source safety assertions. This DOES NOT replace browser, CMS, media, merchant or consent QA.
 */
const fs = require('node:fs');
const assert = require('node:assert/strict');
const path = require('node:path');
const get = name => fs.readFileSync(path.join(__dirname,name),'utf8');
const a=get('ZEN12_A_TEXT_ONLY.html'), b=get('ZEN12_B_OPTIONAL_VIDEO.html'),
 hub=get('MIND_HUB_WP_SOURCE_ONLY.html'), poster=get('ZEN12_R423_POSTER.svg'),
 vtt=get('ZEN12_R423_42S.vtt'), investigation=get('THE_VOICE_IS_NOT_THE_EVIDENCE.md'),
 dossier=get('CONVERSION_ACCEPTANCE_AND_CREATOR_CROSSWALK.md'),
 ledger=JSON.parse(get('CLAIM_SOURCE_PERMISSION_MATRIX.json'));
let passed=0;
function test(name,fn){try{fn();passed++;process.stdout.write('PASS '+name+'\n')}catch(e){process.stderr.write('FAIL '+name+': '+e.message+'\n');process.exitCode=1}}
function safeHtml(h){
 assert.match(h,/<html lang="en">/);
 assert.match(h,/name="viewport"/);
 assert.match(h,/<a class="skip"/);
 assert.match(h,/prefers-reduced-motion/);
 assert.match(h,/noindex,nofollow/);
 assert.doesNotMatch(h,/<script\b|<iframe\b|autoplay\s*=|<form\b|on(?:click|load|error)\s*=|javascript:/i);
 assert.doesNotMatch(h,/<a\b[^>]*href=["'][^"']*(zen12\.com|inspire3\.com|hypnosislive\.com|brainwaveshots\.com)/i);
}
test('A strict HTML/document fallback',()=>safeHtml(a));
test('B strict HTML/document fallback',()=>safeHtml(b));
test('Hub strict HTML/document fallback',()=>safeHtml(hub));
for(const [tag,html] of [['A',a],['B',b]]){
 test(tag+' native disabled merchant control',()=>{assert.match(html,/<button\s+class="button"\s+disabled\s+type="button"\s+aria-disabled="true">/);assert.match(html,/unavailable pending approval/);});
 test(tag+' nearby unambiguous disclosure',()=>{let disclosure=html.indexOf('may earn a commission');let button=html.indexOf('View verified Zen12 offer');assert.ok(disclosure>=0&&button>disclosure&&button-disclosure<600);});
 test(tag+' existing Focus no duplicated opt-in',()=>{assert.match(html,/https:\/\/finalvestige\.com\/focus\//);assert.doesNotMatch(html,/<input\b|type="email"|mailchimp|convertkit|activecampaign/i);});
 test(tag+' no marketing guarantee or merchant price',()=>{assert.doesNotMatch(html,/(?:\$|USD)\s*[0-9]+|guaranteed (?:cure|focus|success)|only \d+ left/i);});
 test(tag+' independent research vs seller separation',()=>{assert.match(html,/seller's format description/);assert.match(html,/Neither tests Zen12/);});
}
test('Buyer copy is byte-identical after B-only film',()=>{
 let marker='<section aria-labelledby="need">';
 assert.equal(a.slice(a.indexOf(marker),a.indexOf('</main>')),b.slice(b.indexOf(marker),b.indexOf('</main>')));
});
test('B only has optional storyboard with transcript',()=>{assert.doesNotMatch(a,/id="film"/);assert.match(b,/id="film"/);assert.match(b,/Read the full 42-second narration/);assert.match(b,/ZEN12_R423_42S.vtt/);});
test('B poster is static with intrinsic dimensions and lazy-load',()=>{assert.match(b,/<img class="poster"[^>]+alt="[^"]+"[^>]+width="1280" height="720" loading="lazy"/);});
test('Poster is original scalable art not third-party pixels',()=>{assert.match(poster,/<svg/);assert.match(poster,/<title/);assert.match(poster,/<desc/);assert.doesNotMatch(poster,/<image\b|xlink:href=|<script/);});
test('Six contiguous caption cues span 42 seconds',()=>{
 let lines=[...vtt.matchAll(/(\d\d):(\d\d):(\d\d)\.\d\d\d --> (\d\d):(\d\d):(\d\d)\.\d\d\d/g)];
 assert.equal(lines.length,6);
 let prev=0;for(const m of lines){const start=+m[1]*3600+ +m[2]*60+ +m[3];const end=+m[4]*3600+ +m[5]*60+ +m[6];assert.equal(start,prev);assert.ok(end>start);prev=end;}assert.equal(prev,42);
});
test('Ledger has exactly 28 all-HOLD gates',()=>{assert.equal(Object.keys(ledger.release_gates).length,28);assert.ok(Object.values(ledger.release_gates).every(v=>v.verified===false&&v.status==='HOLD'));});
test('Ledger claims source keys resolve',()=>{const refs=new Set(ledger.sources.map(s=>s.id));assert.ok(ledger.claims.length>=30);assert.ok(ledger.claims.every(c=>c.sources.every(r=>refs.has(r))));});
test('No payout, success or publication asserted',()=>{assert.equal(ledger.status,'DRAFT_UNPUBLISHED_COMMERCE_HARD_HOLD');assert.match(dossier,/NOT COMPUTABLE/);assert.match(dossier,/No WordPress CMS draft has been saved/);});
test('Article has thorough primary sources and no merchant URL',()=>{assert.ok(investigation.trim().split(/\s+/).length>1800);for(const url of ['41217756','10.1002/ejp.70369','37399315','puysegurs-animal-magnetism'])assert.ok(investigation.includes(url));assert.doesNotMatch(investigation,/https?:\/\/(?:affiliates\.inspire3|hop\.clickbank)/i);});
test('Creator IDs remain unverified and no sales implied',()=>{assert.match(dossier,/NOT VERIFIED/);assert.match(dossier,/commission_settled/);assert.match(dossier,/affiliate_click/);});
process.stdout.write('Static source verifier: '+passed+' tests; '+(process.exitCode?'FAIL':'PASS')+'. NOT browser, WordPress, affiliate or media testing.\n');
if(process.exitCode)process.exit(process.exitCode);