#!/usr/bin/env node
'use strict';
// Run: node mind/r306/verify_r306.cjs
// Source-only guards. Does not imply browser, WordPress, media, partner or paid conversion verification.
const fs = require('node:fs');
const path = require('node:path');
const root = __dirname;
const names = {
  article: 'THE-MEMORY-HYPNOSIS-COULD-NOT-VERIFY-UNPUBLISHED.md',
  a: 'ZEN12-TEXT-ONLY-REVIEW.html',
  b: 'ZEN12-OPTIONAL-VIDEO-REVIEW.html',
  hub: 'MIND-ARCHIVE-WP-REVIEW-CANDIDATE.html',
  matrix: 'HYPNOSIS-MEMORY-SOURCE-CLAIM-AND-COMMERCE-GATES.json',
  plan: 'ONE-OFFER-REALIZED-REVENUE-RELEASE-ACCEPTANCE.md'
};
function load() {
  return Object.fromEntries(Object.entries(names).map(([k,f])=>[k,fs.readFileSync(path.join(root,f),'utf8')]));
}
function stripFilm(s) {
  return s.replace(/<section class="section" id="optional-film"[\s\S]*?<\/section>/, '');
}
function validate(f) {
  const failures=[];
  const check=(ok,code)=>{if(!ok) failures.push(code);};
  let m;
  try{m=JSON.parse(f.matrix)}catch(e){return ['MATRIX_INVALID_JSON']}
  const urls=new Set(m.sources.map(x=>x.url));
  const ids=new Set(m.sources.map(x=>x.id));
  check(m.schema==='FV-MIND-R306-v1','MATRIX_SCHEMA');
  check(m.published===false && m.commerce==='HARD_HOLD','MATRIX_HOLD');
  check(m.sources.length===18&&urls.size===18&&ids.size===18,'SOURCE_COUNT_UNIQUE');
  check(m.claims.length===30&&new Set(m.claims.map(c=>c.id)).size===30,'CLAIM_COUNT_UNIQUE');
  check(m.claims.every(c=>ids.has(c.source_id)&&c.status&&c.scope),'CLAIM_LINKS');
  check(m.gates.length===18&&new Set(m.gates.map(g=>g.id)).size===18,'GATE_COUNT');
  check(m.gates.every(g=>g.status==='HARD_HOLD'&&g.proof===null),'GATE_HOLD');
  check(m.offers.find(o=>o.id==='zen12')?.earning_url===null,'NO_EARNING_URL');
  check(m.offers.every(o=>o.commercial_status!=='LIVE'), 'NO_LIVE_OFFER');
  check(m.creator_routes.length===3&&m.creator_routes.every(r=>r.asset_id===null&&r.media_url===null),'NO_FABRICATED_CREATOR_ID');
  check(m.ab.video_rendered===false&&m.ab.video_hosted===false&&m.ab.rollout_allowed===false,'NO_FAKE_VIDEO_LAUNCH');
  check(m.tracking.reported_performance==='NOT_COMPUTABLE','NO_FAKE_REVENUE');
  check(m.claims.find(c=>c.id==='C12')?.status==='unsupported_merchant_efficacy_exclude','NO_ZEN12_EFFICACY_CLAIM');
  for (const k of ['a','b','hub']){
    const h=f[k];
    check(/<html lang="en">/.test(h)&&/<meta name="viewport"/.test(h),'HTML_SEMANTICS_'+k);
    check(/<meta name="robots" content="noindex,nofollow">/.test(h),'UNPUBLISHED_ROBOTS_'+k);
    check(/<button[^>]*\sdisabled(\s|>)[^>]*>/.test(h),'DISABLED_BUTTON_'+k);
    check(/aria-disabled="true"/.test(h),'ARIA_DISABLED_'+k);
    const btn=h.indexOf('<button'); const note=h.indexOf('Affiliate disclosure:',btn);
    // Archive uses 'Prospective disclosure:', not the commercial-specimen phrase.
    const note2=h.indexOf('Prospective disclosure:',btn);
    check(btn>=0&&((note>btn&&note-btn<900)||(note2>btn&&note2-btn<900)),'DISCLOSURE_ADJACENT_'+k);
    check(!/<script\b|<form\b|<iframe\b|autoplay|<video\b/gi.test(h),'NO_SCRIPT_FORM_MEDIA_'+k);
    check(!/href="https:\/\/(?:www\.)?(?:zen12\.com|hypnosislive\.com|brainwaveshots\.com|affiliates\.inspire3\.com)[^"]*"/gi.test(h),'NO_OUTBOUND_SELLER_LINK_'+k);
    check(!/utm_source=|aff_id=|affiliate_id=|referral_id=/i.test(h),'NO_TRACKING_QUERY_'+k);
    check(/prefers-reduced-motion:reduce/.test(h),'REDUCED_MOTION_'+k);
    check(/:focus-visible/.test(h),'FOCUS_VISIBLE_'+k);
    check(/grid-template-columns:1fr/.test(h),'MOBILE_LAYOUT_'+k);
  }
  check(stripFilm(f.b)===f.a,'VARIANT_COPY_PARITY');
  check(/id="optional-film"/.test(f.b)&&!(/id="optional-film"/.test(f.a)),'FILM_VARIANT_ONLY');
  check(/<details>/.test(f.b)&&/<summary>/.test(f.b)&&/aria-label=/.test(f.b),'FILM_STATIC_ACCESS');
  check(/00:00–00:08/.test(f.b)&&/00:29–00:42/.test(f.b),'FILM_TIMECODED_TRANSCRIPT');
  check(!/is now playable|hosted film is live|activated affiliate/i.test(f.b),'NO_FAKE_FILM_STATUS');
  check(/21 hypnotized and 20 non-hypnotized/.test(f.article),'STUDY_SAMPLE');
  check(/12 of 32/.test(f.article)&&/12 of 16/.test(f.article),'SUGGESTION_DENOMINATORS');
  check(/did not impair recognition above and beyond/i.test(f.article)||/nor a greater false-recognition penalty/i.test(f.article),'NO_FALSE_HYPNOSIS_CONCLUSION');
  check(/source trail and reading depth/i.test(f.article),'EDITORIAL_SOURCE_TRAIL');
  check(/NOT COMPUTABLE/.test(f.plan)&&/HARD HOLD/.test(f.plan),'PLAN_REVENUE_HOLD');
  check(/PRA?XXIS/i.test(f.plan)||/Praxxis/.test(f.plan),'CREATOR_OWNER');
  return failures;
}
const originals=load();
const baseline=validate(originals);
if(baseline.length){console.error('BASELINE FAIL',baseline);process.exit(1)}
const mutations=[
  ['activate merchant control','a',s=>s.replace(' disabled aria-disabled="true"',' aria-disabled="true"')],
  ['hide affiliate disclosure','a',s=>s.replace('Affiliate disclosure:','Marketing note:')],
  ['insert outbound Zen12 checkout','a',s=>s.replace('</body>','<a href="https://zen12.com/getstarted">Buy</a></body>')],
  ['inject new script','a',s=>s.replace('</body>','<script src="/x.js"></script></body>')],
  ['add form','a',s=>s.replace('</body>','<form action="/x"></form></body>')],
  ['add iframe','b',s=>s.replace('</body>','<iframe src="https://example.com"></iframe></body>')],
  ['enable autoplay','b',s=>s.replace('</body>','<video autoplay></video></body>')],
  ['remove storyboard','b',s=>s.replace('id="optional-film"','id="removed-film"')],
  ['change film-only commercial copy','b',s=>s.replace('Potential fit','Guaranteed fit')],
  ['remove video transcript','b',s=>s.replace('00:29–00:42','00:30–00:42')],
  ['remove mobile layout','hub',s=>s.replace('grid-template-columns:1fr','grid-template-columns:2fr')],
  ['activate hub CTA','hub',s=>s.replace(' disabled aria-disabled="true"',' aria-disabled="true"')],
  ['hub disclosure absent','hub',s=>s.replace('Prospective disclosure:','Some note:')],
  ['invent affiliate tracking','hub',s=>s.replace('</body>','<a href="https://affiliates.inspire3.com/?aff_id=1">merchant</a></body>')],
  ['fake publisher permission','matrix',s=>s.replace('"commerce": "HARD_HOLD"','"commerce": "ACTIVE"')],
  ['gate lifted','matrix',s=>s.replace('"status": "HARD_HOLD"','"status": "APPROVED"')],
  ['invent commission url','matrix',s=>s.replace('"earning_url": null','"earning_url": "https://example.com/affiliate"')],
  ['invent media id','matrix',s=>s.replace('"asset_id": null','"asset_id": "madeup"')],
  ['publish video falsely','matrix',s=>s.replace('"video_rendered": false','"video_rendered": true')],
  ['invent revenue','matrix',s=>s.replace('"reported_performance": "NOT_COMPUTABLE"','"reported_performance": "$500"')],
  ['break claim source','matrix',s=>s.replace('"source_id": "S01"','"source_id": "DOES_NOT_EXIST"')],
  ['invent efficacy','matrix',s=>s.replace('"unsupported_merchant_efficacy_exclude"','"proven_efficacy"')],
  ['change study sample','article',s=>s.replace('21 hypnotized and 20 non-hypnotized','210 hypnotized')],
  ['erase journal source trail','article',s=>s.replace('Source trail and reading depth','Notes')],
  ['fabricate plan receipts','plan',s=>s.replaceAll('NOT COMPUTABLE','USD $999')],
  ['remove creator owner','plan',s=>s.replaceAll('Praxxis','Editorial')]
];
let caught=0;
for(const [name,key,modify] of mutations){
  const changed=modify(originals[key]);
  if(changed===originals[key])throw Error('INVALID MUTATION: '+name);
  const after=validate({...originals,[key]:changed});
  if(!after.length)throw Error('UNDETECTED MUTATION: '+name);
  caught++;
}
console.log('R306 BASELINE PASS; negative mutations rejected '+caught+'/'+mutations.length+'; source-level only');
