'use strict';
/* Run from any directory: node mind/r345/verify_r345.cjs
   No network, dependencies, environment secrets or production effects. */
const fs = require('node:fs');
const path = require('node:path');
const root = __dirname;
const names = [
  'THE_COMMAND_THAT_CHANGED_THE_COLOR.md',
  'ZEN12_A_TEXT_REVIEW.html',
  'ZEN12_B_OPTIONAL_FILM_REVIEW.html',
  'MIND_HUB_WORDPRESS_REVIEW_ONLY.html',
  'ZEN12_42S_CAPTIONS.vtt',
  'CLAIM_SOURCE_AUTHORIZATION_MATRIX.json',
  'CONVERSION_ACCEPTANCE.md'
];
const content = Object.fromEntries(names.map(name => [name, fs.readFileSync(path.join(root,name),'utf8')]));
const article = content[names[0]], A = content[names[1]], B = content[names[2]], hub = content[names[3]],
      vtt = content[names[4]], matrix = JSON.parse(content[names[5]]), plan = content[names[6]];
let checks = 0;
const assert = (condition, label) => { checks++; if (!condition) throw new Error('FAIL: '+label); };
const filmRE = /<section id="optional-film"[\s\S]*?<\/section>/g;
function safePage(s, label){
  assert(!/<script\b/i.test(s), label+': no JS script');
  assert(!/<form\b/i.test(s), label+': no duplicate signup');
  assert(!/<iframe\b/i.test(s), label+': no externally embedded frame');
  assert(!/<(?:video|audio)\b[^>]*\bautoplay\b/i.test(s),label+': no autoplay');
  assert(!/<a\b[^>]*href=["'](?:https?:\/\/)?(?:[^"']+\.)?(?:zen12\.com|hypnosislive\.com|brainwaveshots\.com|inspire3\.com)/i.test(s),label+': no active merchant URL');
  assert(/disabled[^>]*aria-disabled="true"/.test(s),label+': disabled button');
  const idx = s.indexOf('Affiliate disclosure:');
  assert(idx >= 0, label+': obvious disclosure');
  assert(s.indexOf('Merchant offer — awaiting verified approval',idx)>idx && s.indexOf('Merchant offer — awaiting verified approval',idx)-idx<800,label+': adjacent disclaimer');
  assert(/name="robots" content="noindex,nofollow"/.test(s),label+': noindex in review');
  assert(/skip.*href="#content"/.test(s),label+': keyboard skip link');
  assert(/prefers-reduced-motion/.test(s),label+': reduced motion');
}
safePage(A,'A');
safePage(B,'B');
assert(B.replace(filmRE,'')===A,'A/B strict copy parity with film section removed');
assert((B.match(/<section id="optional-film"/g)||[]).length===1,'optional film once');
assert(/<svg\b[^>]*role="img"[^>]*aria-labelledby/.test(B),'film poster accessible');
assert(/<details>[\s\S]*42 seconds/.test(B)===false,'nonmisleading film transcript metadata');
assert(/<summary>Read the complete film transcript/.test(B),'full transcript available');
assert(!/<video\b/i.test(B),'no fake playable asset');
assert((vtt.match(/-->/g)||[]).length===6,'six caption cues');
assert(/00:00:35\.000 --> 00:00:42\.000/.test(vtt),'captions end at exactly 42s');
assert(vtt.startsWith('WEBVTT'),'VTT valid header');
assert(/History of Suggestion/.test(hub)&&/Perception & Attention/.test(hub)&&/Practice & Reflection/.test(hub)&&/Tools Under Review/.test(hub),'four archive streams');
assert(!/<form\b|<script\b/i.test(hub),'hub no JS or new signup');
assert(/MIND_HUB_WORDPRESS_REVIEW_ONLY/.test(names[3]),'hub marked review');
assert(article.split(/\s+/).length >= 1700,'substantial original investigation');
for (const t of ['Stroop','Raz','Iani','Puységur','binaural','Zen12','Hypnosis Live','Brainwave Shots','limitations']) {
 assert(article.toLowerCase().includes(t.toLowerCase()),'article includes '+t);
}
assert(Object.keys(matrix.sources).length>=15,'source count >= 15');
assert(matrix.claims.length>=20,'claim count >= 20');
assert(matrix.authorization.length>=18,'commercial gates >= 18');
assert(matrix.authorization.every(x=>x.verified===false),'every commercial gate closed');
assert(matrix.policy.affiliate_url===null,'no affiliate link');
assert(matrix.policy.partner_approval===null,'no invented partner approval');
assert(matrix.policy.net_revenue===null,'no invented revenue');
assert(matrix.claims.every(x=>matrix.sources.some(y=>y.id===x.source_id)),'every claim maps to source');
assert(matrix.claims.some(x=>x.decision==='exclude_from_FV_performance_copy'),'seller outcomes excluded');
assert(plan.includes('NOT COMPUTABLE'),'no invented conversion KPI');
assert(plan.includes('UNKNOWN'),'unknown creator IDs held');
assert(plan.includes('HARD HOLD'),'release remains blocked');
assert(plan.includes('refund'),'payout net of refunds specified');
assert(!/href=["'][^"']*affiliates\.inspire3/.test(A+B),'no public active affiliate links');
const originals = checks;
const rejects = [];
function expectUnsafe(test, replacement, why){
 let ok=false;
 try{test(replacement);} catch(e){ok=true;}
 if(!ok) throw new Error('Mutation escaped: '+why);
 rejects.push(why);
}
expectUnsafe(s=>safePage(s,'A'),A.replace('disabled aria-disabled="true"','aria-disabled="true"'),'enabled buy CTA');
expectUnsafe(s=>safePage(s,'A'),A.replace('Affiliate disclosure:','Undisclosed:'),'removed commission disclosure');
expectUnsafe(s=>safePage(s,'A'),A.replace('</main>','<script src="track.js"></script></main>'),'new analytics script');
expectUnsafe(s=>safePage(s,'A'),A.replace('</main>','<form><input type="email"></form></main>'),'duplicate email intake');
expectUnsafe(s=>safePage(s,'A'),A.replace('</main>','<a href="https://zen12.com/">Buy now</a></main>'),'merchant checkout prematurely active');
expectUnsafe(s=>assert(s.authorization.every(x=>x.verified===false),'gates'),{...matrix,authorization:matrix.authorization.map((x,i)=>i===0?{...x,verified:true}:x)},'authorization falsely opened');
expectUnsafe(s=>assert(s.replace(filmRE,'')===A,'copy parity'),B.replace('Who might value this','Guaranteed results for every buyer'),'A/B guide copy mismatch');
expectUnsafe(s=>assert(/00:00:35\.000 --> 00:00:42\.000/.test(s),'caption duration'),vtt.replace('00:00:42.000','00:00:41.000'),'captions truncated');
console.log(JSON.stringify({status:'PASS',source_checks:originals,unsafe_mutations_rejected:rejects.length,files_read:names.length,publication:'NO',affiliate_activation:'NO',revenue:'NOT_COMPUTABLE'},null,2));