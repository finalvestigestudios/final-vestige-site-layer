'use strict';
/**
 * Mind R245: run with node mind/r245/test_r245.cjs from the repository root.
 * Only source-level checks. NOT browser/WP/a11y/video/cart/affiliate/payout proof.
 * SHA-1 is Git's blob-object identity, not a file security signature.
 */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const crypto = require('node:crypto');
const paths = Object.freeze({
 article:'mind/r245/THE-FRAME-YOU-NEVER-SAW-SACCADES-UNPUBLISHED.md',
 matrix:'mind/r245/CLAIM-SOURCE-PARTNER-REVENUE-GATES.json',
 html:'mind/r245/zen12-approval-held-contextual-block.html',
 vtt:'mind/r245/zen12-42s-OPTIONAL-NOT-RENDERED.vtt',
 plan:'mind/r245/CANONICAL-REPAIR-OFFER-FIT-CONVERSION-ACCEPTANCE.md',
 old:'mind/r244/THE-CHOICE-THAT-CAME-BACK-CHANGED-UNPUBLISHED.md',
 oldMatrix:'mind/r244/CHOICE-BLINDNESS-CLAIMS-RELEASE-GATES.json'
});
const pins = Object.freeze({
 article:'9ec42b0bf713873e5b21b2bb87eed0b8177beae4',
 matrix:'ec38557f02139c7b6519dc160bb7bcb116ed21d9',
 html:'3ca1b88b2724e3717bfa3597755f674795c992f6',
 vtt:'84286c2a7f6f112a3eca7cfe77f19e743ce95591',
 plan:'be562ab2b35d712d887c1dec71330ab7a8ce747a',
 old:'1fcc40f86dddd7d9111bb41b60fdcd0885561ec4',
 oldMatrix:'0bd42d72e7f8d6f794baa92550b8b573910371e4'
});
const gitBlobSha=s=>crypto.createHash('sha1').update('blob '+Buffer.byteLength(s,'utf8')+'\0'+s).digest('hex');
function readPinned() {
 const x={};
 for(const [k,p] of Object.entries(paths)){
  x[k]=fs.readFileSync(p,'utf8');
  assert.equal(gitBlobSha(x[k]),pins[k], 'immutable source blob '+p);
 }
 x.matrix=JSON.parse(x.matrix); x.oldMatrix=JSON.parse(x.oldMatrix);
 return x;
}
function validate(x) {
 assert.ok(x.article.length>16000 && x.article.split(/\s+/).length>2400,'substantial original investigation');
 for(const phrase of ['UNPUBLISHED','saccad','blank','200 milliseconds','Bridgeman','Deubel',
 'https://pmc.ncbi.nlm.nih.gov/articles/PMC7424120/','https://pmc.ncbi.nlm.nih.gov/articles/PMC9469035/',
 'https://finalvestige.com/focus/','not a validated test','no earning link']){
   assert.ok(x.article.toLowerCase().includes(phrase.toLowerCase()),'article evidence/limit '+phrase);
 }
 const m=x.matrix;
 assert.equal(m.release,'HARD_HOLD');assert.equal(m.scope,'UNPUBLISHED_SOURCE_ONLY');
 for(const [a,b] of [['sources','source_count'],['claims','claim_count'],['gates','gate_count']]){
  assert.equal(m[a].length,m[b]);assert.equal(new Set(m[a].map(z=>z.id)).size,m[a].length,'unique '+a);
 }
 assert.equal(m.source_count,22);assert.equal(m.claim_count,29);assert.equal(m.gate_count,16);
 const sourceIds=new Set(m.sources.map(s=>s.id));
 for(const s of m.sources){const u=new URL(s.url);assert.equal(u.protocol,'https:');assert.ok(u.hostname.length>3);assert.ok(s.type);}
 for(const c of m.claims){assert.ok(sourceIds.has(c.source),'orphan source');assert.ok(c.claim.length>=20);assert.ok(c.status.length>=12);}
 for(const g of m.gates){assert.equal(g.state,'HARD_HOLD');assert.equal(g.verified,false);assert.equal(g.proof,null);}
 for(const value of ['affiliate_approved','affiliate_earning_url','authorized_channels','owned_mind_sku_verified','confirmed_paid_orders','confirmed_paid_affiliate_sales','qualified_human_sessions','net_revenue_per_1000']){
  assert.equal(m.commercial[value],null,'commercial evidence absent');
 }
 assert.equal(m.commercial.checkout_authenticated,false);
 assert.ok(m.evidence_notice.includes('NOT a verified cart'));
 assert.equal(m.experiment.video_rendered,false);
 assert.equal(m.experiment.randomization,'not_started');
 assert.ok(m.r244_quality_holds.length>=5);
 assert.ok(m.r244_quality_holds.some(s=>s.includes('tea smelled')));
 assert.ok(m.r244_quality_holds.some(s=>s.toLowerCase().includes('r203')));
 assert.ok(x.old.includes('The Choice That Came Back Changed'));
 assert.equal(x.oldMatrix.milestone,244);

 const h=x.html;
 assert.ok(h.includes('data-release-state="HARD_HOLD"') && h.includes('UNPUBLISHED'));
 assert.ok(h.length>5800 && h.includes('https://finalvestige.com/focus/'));
 const forbidden=/<\s*(script|iframe|form|input|audio|video|img|source|track|select|textarea|object|embed|link|meta|base|picture|template|canvas)\b|<[^>]*\s+on[a-z][a-z0-9_-]*\s*=|\bjavascript\s*:|\bdata\s*:|\burl\s*\(|<[^>]+\bautoplay(?=\s|=|>)/i;
 assert.ok(!forbidden.test(h),'no active tracking, scripts, form, media or handlers');
 const anchors=[...h.matchAll(/<a\b([^>]*)>/gi)];
 assert.equal(anchors.length,2,'precisely two first-party editorial choices');
 for(const [,attrs] of anchors){
  const match=attrs.match(/\bhref\s*=\s*"([^"]+)"/i);
  assert.ok(match,'quoted href');
  const u=new URL(match[1]); assert.equal(u.hostname,'finalvestige.com');
  assert.equal(u.protocol,'https:');assert.equal(u.search,'');assert.equal(u.hash,'');
  assert.ok(!/target\s*=/i.test(attrs));
 }
 const buttons=[...h.matchAll(/<button\b([^>]*)>/gi)];
 assert.equal(buttons.length,1,'one native HOLD CTA');
 const attrs=buttons[0][1];
 assert.ok(/(?:^|\s)disabled(?=\s|=|$)/i.test(attrs),'native disabled not aria substitute');
 assert.ok(/\baria-describedby\s*=\s*"fv245-disclosure fv245-hold"/i.test(attrs),'button must expose disclosure and hold to assistive technology');
 assert.ok(!/\bhref\s*=/i.test(attrs),'button may not carry destination');
 assert.ok(h.includes('id="fv245-disclosure"'));
 const disclosureAt=h.indexOf('id="fv245-disclosure"'),buttonAt=h.indexOf('<button');
 assert.ok(disclosureAt>=0 && disclosureAt<buttonAt && buttonAt-disclosureAt<1100,'near-link disclosure');
 assert.ok(h.includes('may earn a commission at no additional cost'));
 assert.ok(h.includes('No affiliate purchase link is active here'));
 assert.ok(h.includes("merchant's own newsletter") && h.includes('Jetpack/Dispatch'));
 assert.ok(h.includes('This does not start a new A/B allocation'));
 assert.ok(!/href\s*=\s*["']https?:\/\/(?:zen12|inspire3|brainwaveshots|hypnosislive)\./i.test(h));

 const v=x.vtt;
 assert.ok(v.startsWith('WEBVTT\n'));assert.ok(v.includes('NOT-RENDERED') || v.includes('not a video player') || v.includes('No rendered MP4'));
 const times=[...v.matchAll(/(\d{2}):(\d{2}):(\d{2})\.(\d{3}) --> (\d{2}):(\d{2}):(\d{2})\.(\d{3})/g)];
 assert.equal(times.length,6,'exactly six original caption cues');
 let last=0;
 for(const row of times){
  const start=(+row[1]*3600 + +row[2]*60 + +row[3])*1000 + +row[4];
  const end=(+row[5]*3600 + +row[6]*60 + +row[7])*1000 + +row[8];
  assert.equal(start,last,'contiguous captions');assert.ok(end>start);
  last=end;
 }
 assert.equal(last,42000,'exact 42s timed concept');
 assert.ok(v.includes('The purchase link is withheld pending approval'));
 const p=x.plan;
 for(const phrase of ['HARD HOLD','R203','Jam was','tea was','statement','R244','PLOS ONE','affiliate_click',
 'merchant_confirmed_paid_sale','not already netted','NOT COMPUTABLE','7-day','30-day','Grok','Praxxis',
 'HOLD','no new pixels','UNVERIFIED','R237','no authored']){
  if(phrase==='no authored') continue;
  assert.ok(p.toLowerCase().includes(phrase.toLowerCase()),'plan must retain '+phrase);
 }
 assert.ok(p.includes('https://docs.google.com/document/d/1_dqcJeqxbvYb1prGxy0nSWTsHu8p0PSRsDB_NPNbL48/edit'));
 assert.ok(p.includes('R203 \`mind/r203/the-decision-they-switched-choice-blindness-UNPUBLISHED.md\`'),'canonical exact reference');
 assert.ok(p.includes('**UNVERIFIED**'),'creator media ID warning');
 assert.ok(p.includes('https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance'),'health evidence guidance');
 return true;
}
function mutationTests(original) {
 const bad=[
 ['remove editorial source',x=>x.article=x.article.replace('https://pmc.ncbi.nlm.nih.gov/articles/PMC7424120/','REDACTED')],
 ['remove source limit',x=>x.article=x.article.replace('not a validated test','proven cure')],
 ['article cut',x=>x.article='short'],
 ['remove article status',x=>x.article=x.article.replaceAll('UNPUBLISHED','PUBLIC')],
 ['alter reference membership',x=>x.matrix.claims[0].source='UNLISTED'],
 ['duplicate source id',x=>x.matrix.sources[0].id=x.matrix.sources[1].id],
 ['duplicate claim id',x=>x.matrix.claims[0].id=x.matrix.claims[1].id],
 ['duplicate gate id',x=>x.matrix.gates[0].id=x.matrix.gates[1].id],
 ['release switch',x=>x.matrix.release='APPROVED'],
 ['gate cleared',x=>x.matrix.gates[0].state='PASS'],
 ['gate proof invented',x=>x.matrix.gates[0].verified=true],
 ['affiliate url inserted',x=>x.matrix.commercial.affiliate_earning_url='https://example.test/?aff=123'],
 ['fake order',x=>x.matrix.commercial.confirmed_paid_orders=1],
 ['fake net KPI',x=>x.matrix.commercial.net_revenue_per_1000=240],
 ['fake qualified traffic',x=>x.matrix.commercial.qualified_human_sessions=400],
 ['video marked rendered',x=>x.matrix.experiment.video_rendered=true],
 ['fake randomization',x=>x.matrix.experiment.randomization='live'],
 ['lost canonical QA',x=>x.matrix.r244_quality_holds=[]],
 ['lost html status',x=>x.html=x.html.replace('data-release-state="HARD_HOLD"','data-release-state="ACTIVE"')],
 ['activated button',x=>x.html=x.html.replace('type="button" disabled','type="button"')],
 ['aria-only disable',x=>x.html=x.html.replace('type="button" disabled','type="button" aria-disabled="true"')],
 ['added merchant anchor',x=>x.html+='<a href="https://zen12.com/hnp">Buy</a>'],
 ['added tracker',x=>x.html+='<script src="https://tracker.example/p.js"></script>'],
 ['added email input',x=>x.html+='<form><input type="email"></form>'],
 ['added extra button',x=>x.html+='<button disabled>Buy</button>'],
 ['js handler',x=>x.html+='<div onclick="alert(1)">x</div>'],
 ['inline style tracker',x=>x.html+='<style>body{background:url(https://tracker.test/x)}</style>'],
 ['unsafe scheme',x=>x.html=x.html.replace('https://finalvestige.com/focus/','javascript:alert(1)')],
 ['PII in URL',x=>x.html=x.html.replace('https://finalvestige.com/focus/','https://finalvestige.com/focus/?email=test@test.com')],
 ['removed disclosure',x=>x.html=x.html.replace('may earn a commission at no additional cost','may share experience')],
 ['disclosure relocated',x=>x.html=x.html.replace('id="fv245-disclosure"','id="unknown"')],
 ['duplicate signup',x=>x.html+='<form id="extra-list"></form>'],
 ['autoplay media',x=>x.html+='<audio autoplay></audio>'],
 ['caption shortened',x=>x.vtt=x.vtt.replace('00:00:42.000','00:00:40.000')],
 ['caption missing',x=>x.vtt=x.vtt.replace('00:00:21.000 --> 00:00:28.000','invalid cue')],
 ['caption gap',x=>x.vtt=x.vtt.replace('00:00:14.000 --> 00:00:21.000','00:00:15.000 --> 00:00:21.000')],
 ['plan loses financial caution',x=>x.plan=x.plan.replaceAll('not already netted','always subtract again')],
 ['plan loses prior canonical',x=>x.plan=x.plan.replaceAll('R203','previous')],
 ['plan loses media ID warning',x=>x.plan=x.plan.replaceAll('UNVERIFIED','VERIFIED')],
 ['plan loses FTC reference',x=>x.plan=x.plan.replace('https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance','REMOVED')]
 ];
 let rejected=0;const missed=[];
 for(const [name,change] of bad){
  const x=structuredClone(original);change(x);
  try{validate(x);missed.push(name);}catch(e){rejected++;}
 }
 assert.deepEqual(missed,[],'all deliberately unsafe changes must be rejected');
 return {baseline:'PASS',rejected,total:bad.length};
}
function runTests(){const x=readPinned();validate(x);return mutationTests(x);}
module.exports={paths,pins,readPinned,validate,mutationTests,runTests};
if(require.main===module){const result=runTests();console.log(JSON.stringify(result));}
