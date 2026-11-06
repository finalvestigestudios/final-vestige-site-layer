// Mind R165 source/commerce gate regression. Run: node mind/r165/test_mind_r165.cjs
// No network, merchant credential, CMS, form submission, or external test dependency.
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const ROOT = path.join(__dirname, '..');
const text = p => fs.readFileSync(path.join(ROOT,p),'utf8');
const files = {
  article:text('r165/the-detail-that-arrived-after-the-witness-UNPUBLISHED.md'),
  page:text('r165/zen12-memory-evidence-buyer-pilot-UNPUBLISHED.html'),
  ledger:text('r165/verified-science-seller-authorization-and-gates.json'),
  plan:text('r165/creator-offer-provenance-and-settled-revenue-acceptance.md'),
  r164article:text('r164/choice-blindness-the-answer-you-never-gave-UNPUBLISHED.md'),
  r164page:text('r164/zen12-choice-record-buyer-bridge-UNPUBLISHED.html'),
  r164ledger:text('r164/zen12-commercial-evidence-and-release-matrix.json')
};
const HAS=(s,q)=>s.includes(q);
const issues=(s)=>{
  const err=[];
  const {article,page,ledger,plan,r164article,r164page,r164ledger}=s;
  let j; try{j=JSON.parse(ledger)}catch(e){err.push('invalid ledger JSON');return err}
  let legacy; try{legacy=JSON.parse(r164ledger)}catch(e){err.push('invalid R164 ledger JSON');return err}
  function check(ok,msg){if(!ok)err.push(msg)}
  check(article.trim().split(/\s+/).length>=1800,'article must be substantive');
  check(HAS(article,'misinformation effect')&&HAS(article,'McCloskey')&&HAS(article,'Wiechert'),'article must cover replication and alternative explanation');
  check(HAS(article,'https://pubmed.ncbi.nlm.nih.gov/621467/')&&HAS(article,'https://pubmed.ncbi.nlm.nih.gov/3156942/')&&HAS(article,'https://pubmed.ncbi.nlm.nih.gov/41021526/'),'article must include primary source trail');
  check(HAS(article,'not a clinical')||HAS(article,'not memory improvement')||HAS(article,'not a clinical or forensic'),'exercise must limit clinical claims');
  check(HAS(article,'commercial_links: none')&&!/href\s*=\s*['"]https?:\/\/(?:zen12|affiliates\.inspire3)/i.test(article),'scientific investigation is not an affiliate placement');
  check(HAS(page,'noindex,nofollow')&&HAS(page,'strict-origin-when-cross-origin'),'unpublished indexing/referrer policy');
  check(HAS(page,'<main id="main">')&&HAS(page,'<h1')&&HAS(page,'Skip to content'),'semantic landmarks');
  check(HAS(page,'aria-labelledby')&&HAS(page,'aria-describedby')&&HAS(page,'prefers-reduced-motion'),'a11y smoke controls');
  check(!/<script\b|<iframe\b|<form\b|autoplay\b|\bonfocus\s*=|\bonblur\s*=|\bonclick\s*=/i.test(page),'no scripts/forms/iframe/autoplay/inline handlers');
  check(!/<a\b[^>]*href\s*=\s*['"]https?:\/\/(?:zen12\.com|affiliates\.inspire3\.com|www\.awin1\.com)/i.test(page),'no seller or earning click-through');
  check(/<button\b[^>]*\bdisabled\b/i.test(page),'merchant control must be natively disabled');
  check(HAS(page,'If a future authorized purchase link is enabled, Final Vestige may earn a commission at no additional cost to you'),'adjacent plain commission disclosure');
  check(page.indexOf('Potential affiliate disclosure:')>0&&page.indexOf('Potential affiliate disclosure:')<page.indexOf('<button type="button" class="disabled"'),'disclosure precedes disabled CTA');
  check(HAS(page,'https://finalvestige.com/focus/')&&HAS(page,'Seven Day Focus Fieldbook'),'preserve single Focus resource');
  check(HAS(page,'12 levels and 48 MP3')&&HAS(page,'$87.99')&&HAS(page,'November 6, 2026')&&HAS(page,'seller-listed terms'),'exact seller page observations are bounded');
  check(HAS(page,'not been independently tested')&&HAS(page,'has not established product-specific evidence'),'objective product claims not adopted');
  check(HAS(page,'42-second')&&HAS(page,'34–42s:')&&HAS(page,'no MP4, VTT, poster file or player'),'video must be clearly unproduced');
  check(HAS(page,'Variant A:')&&HAS(page,'Variant B:'),'optional video A/B hypothesis');
  check(j.claims.length>=30&&j.sources.length>=18&&j.release_gates.length>=20,'source-linked matrix breadth');
  check(j.release_gates.every(x=>x.status==='CLOSED'),'all commercial gates remain closed');
  check(j.partner_approval_verified===false&&j.authorized_earning_url===null&&j.confirmed_paid_orders===null&&j.confirmed_commissions===null,'permissions/outcomes must stay null');
  check(j.qualified_human_sessions===null&&j.net_revenue_per_1000_qualified_human_sessions===null&&j.AB_experiment_run===false,'do not invent measurement outcome or experiment');
  check(j.claims.some(c=>c.id==='MF-16'&&c.status==='unsupported_product_efficacy'),'12 minutes product claim not independently validated');
  check(j.claims.some(c=>c.id==='MF-28'&&HAS(c.statement,'tasting jam and smelling tea')),'sensory method correctly classified');
  check(HAS(plan,'settled gross receipts - refunds - processing fees')&&HAS(plan,'NOT COMPUTABLE'),'paid KPI must subtract refunds and fees and handle unknowns');
  check(HAS(plan,'asset_id = null')&&HAS(plan,'TASK-008'),'Grok content IDs not invented');
  check(HAS(r164article,'tasted jam or smelled tea')&&HAS(r164article,'before* the final choice'),'old article correction preserved');
  check(!HAS(r164article,'During some follow-up tastings, researchers secretly swapped'),'old mechanism error removed');
  check(HAS(r164page,'jam tasting, tea smelling')&&!HAS(r164page,'jam and tea tastings'),'old buyer-guide sensory correction preserved');
  check(legacy.claims.some(c=>c.id==='CB-04'&&HAS(c.statement,'during initial sampling before final choice')),'old claim ledger reversal timing corrected');
  check(HAS(page,'No affiliate link or commission arrangement for this specific offer has been verified'),'no claim that affiliate approval exists');
  return err;
};
const baseline=issues(files);if(baseline.length){console.error('FAIL baseline '+JSON.stringify(baseline));process.exitCode=1}else console.log('PASS baseline: 30+ source and release integrity checks');
const mutationCases=[
['remove scientific citation','article','https://pubmed.ncbi.nlm.nih.gov/621467/','link-to-removed-citation'],
['erase mechanism counterpoint','article','McCloskey',''],
['article too short','article',null,'SHORT'],
['remove indexing ban','page','noindex,nofollow','index,follow'],
['leak referrer policy','page','strict-origin-when-cross-origin','unsafe-url'],
['delete a11y landmark','page','<main id="main">','<div id="main">'],
['remove keyboard skip','page','Skip to content','Read'],
['remove motion preference','page','prefers-reduced-motion','ignored-motion'],
['inject script','page','</head>','<script src="https://example.com/track.js"></script></head>'],
['inject form','page','</main>','<form><input type="email"></form></main>'],
['inject autoplay','page','<main id="main">','<video autoplay></video><main id="main">'],
['inject inline JS handler','page','<main id="main">','<main id="main" onclick="alert(1)">'],
['add merchant href','page','</main>','<a href="https://zen12.com/?id=publisher">Buy</a></main>'],
['enable purchase button','page','class="disabled" disabled','class="disabled"'],
['delete near FTC disclosure','page','Potential affiliate disclosure:','Not a disclosure:'],
['invert disclosure order','page','<p class="disclosure"','<p class="removed-disclosure"'],
['remove free Focus link','page','https://finalvestige.com/focus/','https://example.com/'],
['misstate exact SKU files','page','12 levels and 48 MP3','4 levels and 12 MP3'],
['drop seller outcome caveat','page','has not established product-specific evidence','has established product-specific evidence'],
['misstate video production','page','no MP4, VTT, poster file or player','finished MP4 delivered'],
['claim verified partner approval','ledger','"partner_approval_verified": false','"partner_approval_verified": true'],
['insert earning URL','ledger','"authorized_earning_url": null','"authorized_earning_url": "https://example.com/ref"'],
['claim paid sales','ledger','"confirmed_paid_orders": null','"confirmed_paid_orders": 20'],
['open a release gate','ledger','"status": "CLOSED"','"status": "OPEN"'],
['claim AB test completed','ledger','"AB_experiment_run": false','"AB_experiment_run": true'],
['remove bankability KPI','plan','settled gross receipts - refunds - processing fees','pageviews'],
['fabricate Grok ID','plan','asset_id = null','asset_id = 1234'],
['undo R164 jam/tea','r164page','jam tasting, tea smelling','jam and tea tastings'],
['undo R164 mechanical timing','r164article','before* the final choice','after the final choice'],
['undo R164 ledger correction','r164ledger','during initial sampling before final choice','after selection']
];
let caught=0;const escaped=[];
for(const [name,k,before,after] of mutationCases){
  const mutated={...files};
  if(before===null)mutated[k]=after;
  else{
    if(!HAS(mutated[k],before)){escaped.push(name+' (precondition missing)');continue}
    mutated[k]=mutated[k].replace(before,after);
  }
  if(issues(mutated).length) caught++;
  else escaped.push(name);
}
if(escaped.length){console.error('FAIL mutations '+JSON.stringify(escaped));process.exitCode=1}
else console.log('PASS mutations: '+caught+'/'+mutationCases.length+' independently caught');
