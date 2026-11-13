'use strict';
// Run from repository root: node mind/r351/verify_r351.cjs
// This is a deterministic source guard, NOT a substitute for browser, WordPress, merchant, or payout QA.
const fs = require('node:fs');
const path = require('node:path');
const root = __dirname;
const read = name => fs.readFileSync(path.join(root, name), 'utf8');
function check(files) {
  const {article,a,b,hub,matrix,poster,captions,dossier} = files;
  let passed = 0;
  const assert = (condition, explanation) => {if (!condition) throw Error('FAIL: '+explanation);passed++};
  const content = '<section id="the-question">';
  const core = h => h.slice(h.indexOf(content),h.indexOf('</main>'));
  assert(article.length > 10000, 'substantive investigation');
  assert(article.includes('Loftus') && article.includes('Puységur'), 'studies and archive');
  assert(article.includes('The film') || article.includes('film'), 'source narrative');
  assert(article.includes('no broken glass'), 'critical experiment distinction');
  assert(article.includes('not the same') || article.includes('not a'), 'overclaim safeguard');
  assert(article.includes('https://doi.org/10.1101/lm.94705'), 'published review source');
  assert(article.includes('https://pubmed.ncbi.nlm.nih.gov/39032268/'), 'hypnosis theory source');
  assert(a.startsWith('<!doctype html>') && b.startsWith('<!doctype html>'), 'document modes');
  assert(a.includes('name="viewport"') && b.includes('name="viewport"'), 'mobile viewport');
  assert(a.includes('noindex,nofollow') && b.includes('noindex,nofollow'), 'unpublished previews deindex');
  assert(core(a)===core(b),'A/B core buyer copy exact parity');
  assert(a.includes('Affiliate disclosure:') && b.includes('Affiliate disclosure:'), 'near-offer disclosure');
  assert(a.includes('If you eventually purchase') && b.includes('If you eventually purchase'), 'plain financial interest');
  assert(a.includes('disabled aria-disabled="true"') && b.includes('disabled aria-disabled="true"'), 'disabled commerce CTA');
  assert(!a.includes('href="https://zen12.com/') && !b.includes('href="https://zen12.com/'), 'no merchant offer link');
  assert(!a.includes('<form') && !b.includes('<form'), 'single existing Jetpack form preserved');
  assert(!a.includes('<script') && !b.includes('<script'), 'no new scripts');
  assert(!a.includes('<iframe') && !b.includes('<iframe'), 'no uncontrolled embeds');
  assert(!a.includes('autoplay') && !b.includes('<video'), 'no forced/unencoded playback');
  assert(a.includes('https://finalvestige.com/focus/') && b.includes('https://finalvestige.com/focus/'), 'existing free resource');
  assert(a.toLowerCase().includes('seller-page') && b.toLowerCase().includes('seller-page'), 'price provenance caveat');
  assert(a.includes('one-year') && b.includes('one-year'), 'seller policy distinguished');
  assert(b.includes('id="optional-film"') && !a.includes('id="optional-film"'), 'only B contains optional treatment');
  assert(b.includes('r351-poster.svg') && b.includes('alt="'), 'poster accessible text');
  assert(b.includes('<details>') && b.includes('<summary>'), 'no-js transcript');
  assert(b.includes('not been encoded or hosted'), 'playback status honest');
  assert(poster.includes('<title') && poster.includes('<desc'), 'original poster descriptions');
  assert(captions.startsWith('WEBVTT') && (captions.match(/-->/g)||[]).length===6, 'six caption cues');
  assert(captions.includes('00:00:42.000'), '42 second end');
  assert(hub.includes('noindex,nofollow') && hub.includes('id="streams"'), 'four-stream hub offline');
  assert(['Perception &amp; Attention','History of Suggestion','Practice &amp; Reflection','Tools Under Review'].every(x=>hub.includes(x)), 'four streams');
  assert(hub.includes('Puységur') && hub.includes('https://finalvestige.com/focus/'), 'canonical live sources');
  assert(!hub.includes('<form') && !hub.includes('<script'), 'no extra list or analytics');
  assert(matrix.claims.length >= 28, 'substantial claim matrix');
  assert(Object.keys(matrix.source_urls).length >= 15, 'source coverage');
  assert(matrix.claims.every(x=>matrix.source_urls[x.source_id]), 'every claim mapped to citation URL');
  assert(matrix.release_gates.length >= 25, 'release gate coverage');
  assert(matrix.release_gates.every(x=>x.status==='HOLD'), 'commerce hard held');
  assert(matrix.claims.some(x=>x.id==='C25' && x.disposition==='unknown-required-auth'), 'partner eligibility not invented');
  assert(matrix.claims.some(x=>x.id==='C26' && x.disposition==='unknown-required-auth'), 'Payhip eligibility not invented');
  assert(dossier.includes('NOT COMPUTABLE') && dossier.includes('merchant_confirmed_paid_order'), 'verified revenue contract');
  assert(dossier.includes('asset_id') && dossier.includes('Praxxis / Grok'), 'creator mapping custody');
  assert(dossier.includes('7- and 30-day') && dossier.includes('refund'), 'cohort reconciliation');
  assert(!dossier.includes('We earned $') && !dossier.includes('verified paid sales: 1'), 'no invented outcomes');
  return passed;
}
function run() {
  const files={article:read('THE_WORD_THAT_WASNT_IN_THE_FILM.md'),a:read('ZEN12_A_TEXT_GUIDE.html'),b:read('ZEN12_B_OPTIONAL_FILM_GUIDE.html'),hub:read('MIND_HUB_WP_REVIEW_ONLY.html'),matrix:JSON.parse(read('PRODUCT_CLAIMS_AUTHORIZATION_MATRIX.json')),poster:read('r351-poster.svg'),captions:read('r351-captions.vtt'),dossier:read('CONVERSION_ACCEPTANCE_AND_ATTRIBUTION.md')};
  const count=check(files);
  const unsafe = [
    f=>({...f,a:f.a.replace('disabled aria-disabled="true"','')}),
    f=>({...f,a:f.a.replace('Merchant offer unavailable','<a href="https://zen12.com/">Buy Zen12</a> Merchant offer unavailable')}),
    f=>({...f,b:f.b.replace('The independent question','<form action="/subscribe"><input name="email"></form>The independent question')}),
    f=>({...f,a:f.a.replace('Affiliate disclosure:','Editorial disclosure:')}),
    f=>({...f,b:f.b.replace('Affiliate disclosure:','Editorial disclosure:')}),
    f=>({...f,b:f.b.replace('You can buy a recording. Not a guarantee.','Zen12 guarantees mental performance') .replace('<section id="the-question">','<section id="the-question"><p>Proven product efficacy.</p>')}),
    f=>({...f,matrix:{...f.matrix,release_gates:f.matrix.release_gates.map((g,i)=>i?g:{...g,status:'OPEN'})}}),
    f=>({...f,b:f.b.replace('<details>','<script>steal()</script><details>')}),
    f=>({...f,b:f.b.replace('not been encoded or hosted','is fully playable')}),
    f=>({...f,captions:f.captions.replace('00:00:42.000','00:00:28.000')})
  ];
  let rejected=0;
  for(let i=0;i<unsafe.length;i++){try{check(unsafe[i](files))}catch(e){rejected++}}
  if(rejected!==unsafe.length)throw Error('Fail-open mutation guard: '+rejected+'/'+unsafe.length);
  console.log('PASS '+count+' baseline assertions; REJECT '+rejected+'/'+unsafe.length+' unsafe modifications');
}
if(require.main===module)run();
module.exports={check,run};
