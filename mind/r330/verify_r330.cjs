'use strict';
/**
 * R330 safe source preflight. Run from repo root:
 * node mind/r330/verify_r330.cjs
 * This is not a replacement for real-browser a11y/CSP, WP sanitizer, merchant or transaction QA.
 */
const fs = require('node:fs');
const assert = require('node:assert/strict');
const path = require('node:path');
const root = __dirname;
const read = file => fs.readFileSync(path.join(root,file),'utf8');
const a = read('ZEN12-A-TEXT-EVIDENCE-GUIDE-REVIEW.html');
const b = read('ZEN12-B-OPTIONAL-42S-STORYBOARD-REVIEW.html');
const hub = read('MIND-FOUR-STREAM-WP-REVIEW-ONLY.html');
const vtt = read('ZEN12-42S-CAPTIONS.vtt');
const article = read('THE-CHOICE-YOU-NEVER-MADE-UNPUBLISHED.md');
const dossier = read('OFFER-FIRST-ATTRIBUTION-AND-RELEASE-DOSSIER.md');
const matrix = JSON.parse(read('SOURCE-CLAIM-PARTNER-COMMERCE-MATRIX.json'));

function noForbiddenMarkup(html) {
  assert(!/<script\b|<form\b|<iframe\b|<video\b|<audio\b/ig.test(html),'active script/form/embed forbidden');
  assert(!/<a[^>]+(?:zen12\.com|hypnosislive\.com|brainwaveshots\.com|affiliates\.inspire3\.com)/ig.test(html),'merchant href forbidden');
  assert(!/(?:onclick|onload|autoplay)\s*=/ig.test(html),'autoplay/inline handlers forbidden');
  assert(!/url\(\s*https?:\/\//ig.test(html),'remote CSS resource forbidden');
  assert(/<meta name="robots" content="noindex,nofollow">/.test(html),'noindex required');
  assert(/class="skip"/.test(html),'skip link required');
  assert(/:focus-visible/.test(html),'visible focus rule required');
  assert(/prefers-reduced-motion/.test(html),'reduced-motion rule required');
  assert(/<html lang="en">/.test(html),'document language required');
}
function commerce(html) {
  assert(/type="button" disabled aria-disabled="true"/.test(html),'purchase action must be disabled');
  const pos = html.indexOf('type="button" disabled');
  const disc = html.indexOf('Prospective affiliate disclosure:');
  assert(pos>=0 && disc>pos && disc-pos<1100,'near-button disclosure absent');
  assert(/No earning link is active/.test(html),'clear hold language absent');
  assert(/https:\/\/finalvestige\.com\/focus\//.test(html),'existing Focus route absent');
  assert(!/href="(?:https?:\/\/)?[^"]*inspire3\.com\//.test(html),'affiliate href blocked');
}
function substantivelySame(x,y) {
 const extract=h=>h.substring(h.indexOf('<section aria-labelledby="free">'),h.indexOf('</main>'));
 assert(extract(x).length>4000,'substantive copy missing');
 assert.equal(extract(x),extract(y),'A/B must differ only by optional film before shared copy');
}
function proveMatrix(m) {
 assert(m.sources.length>=18,'source inventory too small');
 assert(m.claims.length>=24,'claims inventory too small');
 assert.equal(m.gates.length,18,'18 authorization gates required');
 assert(m.gates.every(g=>g.status==='HOLD'&&g.pass_evidence===null),'all gates must remain held');
 assert.equal(m.affiliate_status.issued_earning_url,'NONE_VERIFIED','no earned link authorized');
 assert.equal(m.fv_product_status.mind_paid_sku,'UNVERIFIED','no authenticated paid SKU');
 const known=new Set(m.sources.map(s=>s.id));
 for(const c of m.claims) for(const id of c.source_ids) assert(known.has(id),'unknown source ID: '+id);
}
function run() {
 const tests=[
 ['A safe HTML',()=>noForbiddenMarkup(a)],
 ['B safe HTML',()=>noForbiddenMarkup(b)],
 ['hub safe HTML',()=>noForbiddenMarkup(hub)],
 ['A commerce held',()=>commerce(a)],
 ['B commerce held',()=>commerce(b)],
 ['A/B copy parity',()=>substantivelySame(a,b)],
 ['film is optional storyboard',()=>{assert(b.includes('42 seconds')&&b.includes('film')&&b.includes('details>'));assert(!a.includes('entire 42-second narration'));}],
 ['caption six cues',()=>assert.equal((vtt.match(/-->/g)||[]).length,6)],
 ['caption end 42s',()=>assert(vtt.includes('00:00:42.000'))],
 ['matrix proof',()=>proveMatrix(matrix)],
 ['investigation case title',()=>assert(article.includes('The Choice You Never Made'))],
 ['2005 source',()=>assert(article.includes('https://pubmed.ncbi.nlm.nih.gov/16210542/'))],
 ['2010 marketplace source',()=>assert(article.includes('https://pubmed.ncbi.nlm.nih.gov/20637455/'))],
 ['2013 Sweden source',()=>assert(article.includes('https://pubmed.ncbi.nlm.nih.gov/23593244/'))],
 ['2017 counter finding',()=>assert(article.includes('did not observe changes in voting intentions'))],
 ['2018 attitude source',()=>assert(article.includes('https://pubmed.ncbi.nlm.nih.gov/30148387/'))],
 ['historical bridge',()=>assert(article.includes('puysegurs-animal-magnetism-files'))],
 ['no brand proof implied',()=>assert(article.includes('do not demonstrate that a meditation recording'))],
 ['single existing Focus funnel',()=>assert(dossier.includes('existing Focus Fieldbook'))],
 ['qualified revenue definition',()=>assert(dossier.includes('1,000 × realized'))],
 ['responsibility separation',()=>assert(dossier.includes('Grok creates/posts'))],
 ['native buyer disclosure guidance',()=>assert(dossier.includes('FTC'))]
 ];
 for(const [name,fn] of tests){fn();process.stdout.write('PASS '+name+'\n');}
 const mutants=[
 ['script',s=>s.replace('</main>','<script src="/track.js"></script></main>'),noForbiddenMarkup],
 ['form',s=>s.replace('</main>','<form action="/subscribe"><input name="email"></form></main>'),noForbiddenMarkup],
 ['iframe',s=>s.replace('</main>','<iframe src="https://example.com"></iframe></main>'),noForbiddenMarkup],
 ['merchant href',s=>s.replace('</main>','<a href="https://zen12.com/getstarted">Buy</a></main>'),noForbiddenMarkup],
 ['autoplay',s=>s.replace('</main>','<audio autoplay></audio></main>'),noForbiddenMarkup],
 ['inline handler',s=>s.replace('</main>','<a onclick="send()" href="/x">X</a></main>'),noForbiddenMarkup],
 ['remote CSS',s=>s.replace('</style>','body{background:url(https://t.example/x)}</style>'),noForbiddenMarkup],
 ['missing disclosure',s=>s.replace('Prospective affiliate disclosure:','Disclosure removed:'),commerce],
 ['enabled purchase',s=>s.replace('type="button" disabled aria-disabled="true"','type="button"'),commerce],
 ['missing fieldbook',s=>s.replaceAll('https://finalvestige.com/focus/','/not-found/'),commerce],
 ['noindex removed',s=>s.replace('noindex,nofollow','index,follow'),noForbiddenMarkup],
 ['wrong A/B copy',s=>s.replace('What Zen12 actually sells','What Zen12 secretly sells'),x=>substantivelySame(a,x)]
 ];
 for (const [name,mutate,check] of mutants) {
   const altered=mutate(b); assert.notEqual(altered,b,'mutation ineffective: '+name);
   let rejected=false; try{check(altered);}catch(_){rejected=true;}
   assert(rejected,'unsafe mutation was not rejected: '+name);
   process.stdout.write('REJECTED '+name+'\n');
 }
 process.stdout.write('R330: '+tests.length+' baseline PASS, '+mutants.length+' unsafe mutants rejected; not browser/CI/merchant QA.\n');
}
if(require.main===module)run();
module.exports={noForbiddenMarkup,commerce,substantivelySame,proveMatrix};
