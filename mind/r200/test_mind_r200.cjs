'use strict';
/**
 * Final Vestige Studios Mind R200:
 * Pure source and claims gate tests. Not live performance, browser, checkout
 * or subscription verification. Execute after checkout:
 *     node mind/r200/test_mind_r200.cjs
 * Dependencies: Node built-ins only. No network, analytics or CMS effects.
 */
const paths = {
  article: 'mind/r200/the-memory-that-arrived-afterward-SUGGESTION-HYPNOSIS-UNPUBLISHED.md',
  hub: 'mind/r200/mind-memory-four-stream-WP-PREVIEW-UNPUBLISHED.html',
  matrix: 'mind/r200/SUGGESTION-MEMORY-OFFERS-SOURCES-CLAIMS-GATES.json',
  plan: 'mind/r200/ONE-OFFER-THREE-CREATOR-FITS-PAID-CONVERSION-GATE.md',
  priorArticle: 'mind/r199/the-thought-that-left-the-room-MIND-WANDERING-INVESTIGATION-UNPUBLISHED.md',
  priorMatrix: 'mind/r199/MIND-WANDERING-ZEN12-SOURCE-CLAIM-MERCHANT-GATES.json',
  a: 'mind/r199/zen12-offer-guide-A-TEXT-UNPUBLISHED.html',
  b: 'mind/r199/zen12-offer-guide-B-OPTIONAL-FILM-UNPUBLISHED.html'
};
function validate(d) {
  const t=[];const check=(name,pass)=>t.push({name,pass:!!pass});
  let j,prior;try{j=JSON.parse(d.matrix);prior=JSON.parse(d.priorMatrix);}catch(e){
    return {ok:false,checks:[{name:'JSON parsing',pass:false}],passed:0,failures:[String(e)]};
  }
  const has=(k,s)=>d[k].includes(s),plain=s=>s.replace(/<[^>]*>/g,' ');
  const src=new Set(j.sources.map(s=>s.id));
  const h=d.hub,a=d.a,b=d.b;
  const filmRemoved=b.replace(/<section class="film panel"[\s\S]*?<\/section>/,'');
  const compact=s=>s.replace(/\s+/g,'');
  check('article >= 2400 words',d.article.trim().split(/\s+/).length>=2400);
  check('article is unpublished',has('article','UNPUBLISHED')&&has('article','NOT LIVE'));
  check('Loftus primary study named',has('article','Loftus')&&has('article','Palmer'));
  check('DRM primary study named',has('article','Roediger')&&has('article','McDermott'));
  check('hypnosis consensus caution',has('article','Kihlstrom')&&has('article','JAMA'));
  check('hypnosis theory nuance',has('article','Zahedi')&&has('article','continuing debate'));
  check('false memory risks scoped',has('article','not percentages of people')&&has('article','not automatically false'));
  check('no memory-recovery exercise',has('article','not a recovered-memory exercise'));
  check('voluntary exercise caveat',has('article','not a scientifically controlled test'));
  check('no active affiliate in investigation',has('article','no active affiliate recommendation'));
  check('no fabricated seller testimony',!/\bI (used|tested|bought) (Zen12|Hypnosis Live)\b/i.test(d.article));
  check('published Focus route',has('article','https://finalvestige.com/focus/'));
  check('published Puységur route',has('article','https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/'));
  check('article specific primary DOIs',has('article','10.1016/S0022-5371')&&has('article','10.1037/0278-7393'));
  check('editorial separate from merchant proof',has('article','seller descriptions')&&has('article','independent tests'));
  check('four thematic streams',['attention','history','practice','tools'].every(id=>h.includes('id="'+id+'"')));
  check('hub noindex',h.includes('noindex,nofollow'));
  check('hub skip link',h.includes('class="skip" href="#main"'));
  check('hub keyboard focus',h.includes(':focus-visible'));
  check('hub motion preference',h.includes('prefers-reduced-motion:reduce'));
  check('hub 390px layout',h.includes('max-width:390px'));
  check('hub 760px layout',h.includes('max-width:760px'));
  check('hub external stylesheet absent',!/<link\b[^>]*stylesheet|@font-face|@import/i.test(h));
  check('hub no JS script/inline event',!/<script\b|onload=|onclick=|javascript:/i.test(h));
  check('hub no second signup',!/<form\b|<input\b|<iframe\b/i.test(h));
  check('hub no playable autoplay',!/<video\b|<audio\b|autoplay\b/i.test(h));
  check('hub no earning link',!/<a\b[^>]*href=["'][^"']*(zen12\.com|hypnosislive\.com|awin1\.com|affiliates\.inspire3\.com)/i.test(h));
  check('hub native disabled CTA',/<button\b[^>]*\bdisabled\b/.test(h));
  check('disclosure precedes commerce control',h.indexOf('may earn a commission')>=0&&h.indexOf('may earn a commission')<h.indexOf('Purchase link unavailable'));
  check('hub seller price qualified',h.includes('$87.99')&&h.includes('Final checkout'));
  check('hub published scientific routes',h.includes('/2026/11/02/change-blindness/')&&h.includes('/2026/11/02/mesmerism/'));
  check('hub no unpublished article href',!/<a\b[^>]*href=["'][^"']*\/mind\/memory-suggestion-hypnosis\//.test(h));
  check('one canonical Focus',h.includes('https://finalvestige.com/focus/'));
  check('matrix at least 20 sources',j.sources.length>=20);
  check('matrix at least 30 claims',j.claims.length>=30);
  check('matrix 25 or more gates',j.release_gates.length>=25);
  check('all source refs resolvable',j.claims.every(c=>c.source_ids.every(id=>src.has(id))));
  check('every source https',j.sources.every(s=>s.url.startsWith('https://')));
  check('all gates open',j.release_gates.every(g=>g.state==='OPEN'));
  check('unique gate ids',new Set(j.release_gates.map(g=>g.id)).size===j.release_gates.length);
  check('no invented partner approval',j.partner_approval==='UNVERIFIED'&&j.earning_url===null);
  check('no invented orders',j.verified_paid_orders===null&&j.earned_commission===null);
  check('no invented owned product',j.verified_owned_mind_sku===null);
  check('no invented qualified sessions',j.qualified_human_sessions===null);
  check('never coerce no data to zero',j.net_revenue_per_1000_qualified_humans==='NOT_COMPUTABLE');
  check('FTC adjacent disclosure encoded',j.prospective_disclosure.includes('may earn a commission'));
  check('Zen12 unverified equivalence excluded',j.claims.some(c=>c.id==='zen12_equivalence'&&c.decision==='EXCLUDE_UNSUBSTANTIATED'));
  check('Total Focus unsubstantiated focus excluded',j.claims.some(c=>c.id==='total_focus_concentration'&&c.decision==='EXCLUDE_UNSUBSTANTIATED'));
  check('affiliate not approved',j.claims.some(c=>c.id==='affiliate_approval'&&c.decision==='UNKNOWN_HARD_HOLD'));
  check('subscription view not lead',j.claims.some(c=>c.id==='focus_leads'&&c.decision==='REJECT_INFERENCE'));
  check('click not sale',j.claims.some(c=>c.id==='paid_sales'&&c.decision==='REJECT_INFERENCE'));
  check('event schema separates outbound from sale',j.attribution_contract.outbound_is_sale===false);
  check('no PII marketing track',j.attribution_contract.retain_pii===false);
  check('7/30 cohorts',j.attribution_contract.seven_day_cohort&&j.attribution_contract.thirty_day_cohort);
  check('plan concrete topic fit',has('plan','Change blindness')&&has('plan','Mesmerism and Puységur')&&has('plan','Suggestion and memory'));
  check('plan creator asset ID controlled',has('plan','utm_content')&&has('plan','UNKNOWN'));
  check('plan commercial gate',has('plan','HARD HOLD')&&has('plan','NOT COMPUTABLE'));
  check('plan 7/30 cohorts',has('plan','seven- and thirty-day cohorts'));
  check('plan A/B equal information',has('plan','same substance and CTA'));
  check('plan actual seller URLs',has('plan','https://zen12.com/hnp')&&has('plan','https://affiliates.inspire3.com/'));
  check('plan owner boundaries',has('plan','Grok/Praxxis')&&has('plan','Dispatch #174')&&has('plan','PR #49'));
  check('plan no WP release',has('plan','No live WordPress changes'));
  check('R199 first retreat research corrected',has('priorArticle','did **not** improve')&&has('priorArticle','27 complete cases'));
  check('R199 Mrazek comparator corrected',has('priorArticle','48 undergraduates')&&has('priorArticle','nutrition-education'));
  check('R199 high baseline subgroup corrected',has('priorArticle','higher baseline mind-wandering'));
  check('R199 matrix aligns MacLean',prior.claims.some(c=>c.id==='lab_vigilance'&&c.limits.includes('not compelling direct vigilance')));
  check('R199 matrix aligns Mrazek',prior.claims.some(c=>c.id==='mrazek_results'&&c.statement.includes('higher baseline wandering')));
  check('A MacLean caveat',a.includes('27 complete cases')&&a.includes('recalibrating target difficulty'));
  check('B MacLean caveat',b.includes('27 complete cases')&&b.includes('recalibrating target difficulty'));
  check('A/B film only difference',compact(a)===compact(filmRemoved));
  check('A&B native disabled', [a,b].every(s=>/<button\b[^>]*\bdisabled\b/.test(s)));
  check('A&B near CTA disclosure',[a,b].every(s=>s.includes('may earn a commission')&&s.indexOf('may earn a commission')<s.lastIndexOf('</button>')));
  check('A&B no earning URL',[a,b].every(s=>!/<a\b[^>]*href=["'][^"']*(zen12\.com|awin1\.com)/i.test(s)));
  check('B optional short concept',b.includes('42-second')&&b.includes('id="optional-film"'));
  check('B captions concept',b.includes('WebVTT')&&b.includes('poster-title')&&b.includes('poster-desc'));
  check('no external tracking',[a,b,h].every(s=>!/<script\b|<iframe\b/i.test(s)));
  const failures=t.filter(c=>!c.pass).map(c=>c.name);
  return {ok:!failures.length,checks:t,passed:t.length-failures.length,failures};
}
function mutations(d){
 const cases=[
  ['drop hub disabled','hub',' disabled aria-describedby',' aria-describedby'],
  ['commercial anchor','hub','<button class="off"','<a href="https://zen12.com/hnp" class="off"'],
  ['delete near disclosure','hub','may earn a commission','could perhaps get something'],
  ['new form','hub','</main>','<form><input type="email"></form></main>'],
  ['new external script','hub','</head>','<script src="https://tracker.example/test.js"></script></head>'],
  ['new autoplay','hub','</main>','<video autoplay></video></main>'],
  ['missing published Focus','hub','https://finalvestige.com/focus/','https://example.com/new-list'],
  ['missing change article','hub','/2026/11/02/change-blindness/','/unpublished-change/'],
  ['fabricate approval','matrix','"partner_approval": "UNVERIFIED"','"partner_approval": "APPROVED"'],
  ['fabricate earning URL','matrix','"earning_url": null','"earning_url": "https://example.com/affiliate"'],
  ['fake order','matrix','"verified_paid_orders": null','"verified_paid_orders": 18'],
  ['zero instead unknown','matrix','"net_revenue_per_1000_qualified_humans": "NOT_COMPUTABLE"','"net_revenue_per_1000_qualified_humans": 0'],
  ['close gate','matrix','"state": "OPEN"','"state": "PASSED"'],
  ['broken claim ref','matrix','"source_ids": [\n        "loftus1974"','"source_ids": [\n        "fake_missing_study"'],
  ['allow unsupported Zen12','matrix','"id": "zen12_equivalence"','"id": "no_equiv_restriction"'],
  ['conflate click with sale','matrix','"outbound_is_sale": false','"outbound_is_sale": true'],
  ['claim publisher SKU','matrix','"verified_owned_mind_sku": null','"verified_owned_mind_sku": "FAKE"'],
  ['ignore guide caveat','a','27 complete cases','a guaranteed attention miracle'],
  ['ignore B caveat','b','27 complete cases','a guaranteed attention miracle'],
  ['erase A disable','a',' disabled aria-disabled="true"',' aria-disabled="true"'],
  ['erase B disable','b',' disabled aria-disabled="true"',' aria-disabled="true"'],
  ['distort mediation','priorArticle','higher baseline mind-wandering','all persons universally'],
  ['change matrix limit','priorMatrix','not compelling direct vigilance','definitely direct improvement'],
  ['commercial trial invented','article','no active affiliate recommendation','active affiliate recommendation'],
  ['delete source DOI','article','10.1037/0278-7393','doi-invalid'],
  ['remove Grok ownership','plan','Grok/Praxxis','Other team']
 ];
 const misses=[];let caught=0;
 for(const [name,key,from,to] of cases){
  if(!d[key].includes(from)){misses.push(name+' [target absent]');continue;}
  const modified={...d,[key]:name==='missing published Focus'?d[key].split(from).join(to):d[key].replace(from,to)};
  if(!validate(modified).ok)caught++;else misses.push(name+' [escaped]');
 }
 return {total:cases.length,caught,misses};
}
module.exports={paths,validate,mutations};
if(typeof require!=='undefined' && require.main===module){
 const fs=require('fs'),path=require('path'),d={};
 for(const [key,p] of Object.entries(paths))d[key]=fs.readFileSync(path.resolve(process.cwd(),p),'utf8');
 const r=validate(d),m=mutations(d);
 console.log('R200 assertions:',r.passed,'/',r.checks.length,'; unsafe mutations:',m.caught,'/',m.total);
 if(r.failures.length)console.error('FAILED',r.failures);
 if(m.misses.length)console.error('UNDETECTED',m.misses);
 if(!r.ok||m.caught!==m.total)process.exitCode=1;
}
