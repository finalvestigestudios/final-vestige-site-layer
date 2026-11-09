'use strict';
/* Mind R246. Run from repository root:
   node mind/r246/test_r246.cjs
   Node source-level only. Static checks cannot establish browser/WP/partner/merchant outcomes.
   All blob hashes below are Git object SHA-1 identities (not security signatures).
*/
const paths=Object.freeze({
 repairedArticle:'mind/r245/THE-FRAME-YOU-NEVER-SAW-SACCADES-UNPUBLISHED.md',
 repairedMatrix:'mind/r245/CLAIM-SOURCE-PARTNER-REVENUE-GATES.json',
 repairedPlan:'mind/r245/CANONICAL-REPAIR-OFFER-FIT-CONVERSION-ACCEPTANCE.md',
 repairedTest:'mind/r245/test_r245.cjs',
 article:'mind/r246/THE-FACE-THAT-CHANGED-WHEN-TURNED-UNPUBLISHED.md',
 matrix:'mind/r246/EVIDENCE-PRODUCT-CONVERSION-GATES.json',
 guideA:'mind/r246/zen12-decision-A-NO-COMMERCE-UNPUBLISHED.html',
 guideB:'mind/r246/zen12-decision-B-NO-COMMERCE-UNPUBLISHED.html',
 plan:'mind/r246/OFFER-FUNNEL-BLOCKER-EXPERIMENT-RELEASE.md'
});
const pins=Object.freeze({
 repairedArticle:'9ec42b0bf713873e5b21b2bb87eed0b8177beae4',
 repairedMatrix:'ec38557f02139c7b6519dc160bb7bcb116ed21d9',
 repairedPlan:'be562ab2b35d712d887c1dec71330ab7a8ce747a',
 repairedTest:'a3425a4495e9149b757e0b42ed0e44090eca2602',
 article:'d18858147b41f837bd1b6b961a88111fb267c119',
 matrix:'5f904cf9a1db73dd3d496a52e568f689d6edc9c4',
 guideA:'f9a273234cecd4efe99e9530ab240eb6f3bf2efb',
 guideB:'2361fef3fca364cf18f4a22a78ba8c7483f3dd19',
 plan:'15d04c828f741805180d65b18d554dc59db2a7b6'
});
function check(x,message){if(!x)throw Error('R246 '+message)}
function stripVideo(html){
 return html.replace(/ data-ab-variant="[AB]"/,'').replace(/<!-- BEGIN optional-video-only B:[\s\S]*?<!-- END optional-video-only B -->/,'');
}
function validate(x){
 check(Object.keys(paths).every(k=>typeof x[k]==='string'&&x[k].length>100),'required source files');
 const a=x.article;
 check(a.length>19500&&a.split(/\s+/).length>2700,'sourced substantial new article');
 for(const phrase of ['Thatcher illusion','Peter Thompson','Bertin','Psalta','Boutsen','rhesus monkeys did not','chimpanzees','hypnosis','UNPUBLISHED','no affiliate endorsements','https://doi.org/10.1068/p7755','https://pubmed.ncbi.nlm.nih.gov/23420511/']){
   check(a.toLowerCase().includes(phrase.toLowerCase()),'article source, nuance '+phrase);
 }
 check(a.includes('not a replicated laboratory experiment') && a.includes('original, rights-cleared diagram'),'rights and study limits');
 const prev=x.repairedArticle;
 check(prev.includes('October 23, 2012') && !prev.includes('open 2013 account'),'Tas 2012 history correction');
 check(prev.includes('Li, Hanning and Carrasco') && !prev.includes('Li and Carrasco (2021)'),'2021 authors restored');
 check(prev.includes('15 participants') && prev.includes('saccade/spatiotopic condition') && prev.includes('not a blanket improvement'),'2020 task-specific correction');
 const repaired=JSON.parse(x.repairedMatrix);
 check(repaired.sources.some(s=>s.url?.startsWith('https://www.lucs.lu.se/')),'Lund domain');
 check(repaired.sources.some(s=>s.scope?.includes('2012 updating')),'source publication year');
 check(x.repairedPlan.includes('fees AND platform costs not already netted'),'incremental platform cost accounting');
 check(x.repairedTest.includes('on[a-z][a-z0-9_-]*') && x.repairedTest.includes('aria-describedby'),'R245 guard coverage repairs');
 const m=JSON.parse(x.matrix);
 check(m.release==='HARD_HOLD'&&m.source_scope==='UNPUBLISHED_ONLY','source scope');
 for(const [array,min] of [['sources',21],['claims',33],['gates',16]]){
  check(Array.isArray(m[array])&&m[array].length===min,'matrix '+array+' count');
  check(new Set(m[array].map(z=>z.id)).size===min,'unique ids '+array);
 }
 const ids=new Set(m.sources.map(s=>s.id));
 for(const s of m.sources){
  check(/^https:\/\//.test(s.url),'source URL https');
  check(['seller','primary_reprinted','primary_abstract','regulatory','existing_site'].includes(s.type),'source classification');
 }
 for(const c of m.claims){
  check(ids.has(c.source),'claim with source '+c.id);
  check(c.claim.length>=30&&c.status.length>=8,'claim record complete '+c.id);
 }
 for(const g of m.gates)check(g.state==='HARD_HOLD'&&g.verified===false&&g.proof===null,'gate blocked '+g.id);
 for(const key of ['publisher_approved','issued_earning_url','authorized_channels','merchant_checkout_test','refund_test','cleared_affiliate_commissions','settled_owned_orders','qualified_human_sessions','net_revenue_per_1000','affiliate_click']){
  check(m.commercial[key]===null,'no fabricated commerce '+key);
 }
 check(m.claims.some(c=>c.id==='ZEN12_EQ'&&c.status.includes('UNSUBSTANTIATED')),'no product equivalence');
 check(m.claims.some(c=>c.id==='FV_PAYHIP'&&c.status==='NOT_VERIFIED'),'no unverified owned product activation');
 check(m.gates.length===16 && m.test_hypothesis.video_rendered===false && m.test_hypothesis.actual_randomization===false,'A/B not live');
 for(const [key,variant] of [['guideA','A'],['guideB','B']]){
  const h=x[key];
  check(h.includes('data-release="HARD_HOLD"')&&h.includes('data-ab-variant="'+variant+'"'),'HTML held '+key);
  check(h.includes('<html lang="en">')&&h.includes('name="viewport"'),'a11y mobile basics '+key);
  check(h.includes('prefers-reduced-motion:reduce')&&h.includes('focus-visible'),'reduced motion/focus '+key);
  check((h.match(/<button\b/gi)||[]).length===1,'one button '+key);
  check(/<button\b[^>]*\sdisabled\saria-describedby="offer-disclosure offer-hold"/i.test(h),'native disabled with accessible context '+key);
  check(h.includes('id="offer-disclosure"')&&h.includes('id="offer-hold"')&&h.includes('No active affiliate purchase link')===false,'disclosure and no mistaken active claim '+key);
  const posD=h.indexOf('id="offer-disclosure"'),posB=h.indexOf('<button');
  check(posD>=0&&posB>posD&&posB-posD<800,'disclosure immediately beside CTA '+key);
  check(h.includes('may earn a commission at no additional cost'),'clear commission text '+key);
  check(h.includes("merchant's own newsletter")&&h.includes('Jetpack/Dispatch'),'separate lists '+key);
  const risky=/<\s*(script|iframe|form|input|audio|video|img|source|track|select|textarea|object|embed|link|base|picture|template|canvas)\b|<[^>]*\s+on[a-z][a-z0-9_-]*\s*=|\bjavascript\s*:|\bdata\s*:|@import\b|\burl\s*\(|<[^>]+\bautoplay(?=\s|=|>)/i;
  check(!risky.test(h),'no active forms/tracking/media/handlers '+key);
  check((h.match(/<a\s/gi)||[]).length===2,'only two first party links '+key);
  for(const mt of h.matchAll(/<a\s+[^>]*href="([^"]+)"/g)){
   const u=new URL(mt[1]);check(u.protocol==='https:'&&u.hostname==='finalvestige.com'&&u.search===''&&u.hash==='','no merchant/referrer/PII href '+key);
  }
  check(!/<a[^>]*target=/i.test(h),'no unsafe target '+key);
  check(!/<style[^>]*@import/i.test(h),'no remote imports '+key);
 }
 check(!x.guideA.includes('data-optional-video="'),'A text only');
 check(x.guideB.includes('data-optional-video="concept-not-playable"'),'B concept only');
 check(x.guideB.includes('<svg ') && x.guideB.includes('<title id="video-title">') && x.guideB.includes('<desc id="video-desc">'),'original accessible static poster');
 check(x.guideB.includes('0–7 seconds:')&&x.guideB.includes('35–42:'),'42s transcript');
 check(stripVideo(x.guideA)===stripVideo(x.guideB),'strict A/B copy parity: only optional video section');
 check(x.plan.includes('net_revenue_per_1000_qualified')&&x.plan.includes('incremental_attributable_fees_and_platform_costs_not_already_net'),'net metric plan');
 check(x.plan.includes('metric status is `NOT_COMPUTABLE`') && x.plan.includes('No WordPress CMS/nav/settings writes'),'no fabricated outcomes/live changes');
 check(x.plan.includes('Grok produces/distributes')&&x.plan.includes('Dispatch'),'owner separation');
 return true;
}
function runMutations(base){
 const cases=[];
 const reg=(label,func)=>cases.push({label,func});
 const ht=(key,find,repl)=>reg(key+' replace '+find.slice(0,24),x=>{x[key]=x[key].replace(find,repl)});
 for(const k of ['guideA','guideB']){
  ht(k,' disabled aria-describedby',' aria-describedby');
  ht(k,'<button type="button"','<button type="button" onclick="buy()"');
  ht(k,'<button type="button"','<button type="button" onpointerenter="send()"');
  ht(k,'<button type="button"','<button type="button" onanimationstart="send()"');
  ht(k,'<button type="button"','<button type="button" onfocusin="send()"');
  ht(k,'<button type="button"','<button type="button" href="https://zen12.com/hnp"');
  ht(k,'</main>','<a href="https://zen12.com/hnp">Shop</a></main>');
  ht(k,'</main>','<form action="/signup"><input name="email"></form></main>');
  ht(k,'</main>','<iframe src="https://example.com"></iframe></main>');
  ht(k,'</main>','<script>alert(1)</script></main>');
  ht(k,'</main>','<video autoplay src="movie.mp4"></video></main>');
  ht(k,'</main>','<meta http-equiv="refresh" content="0;url=https://example.com"></main>');
  ht(k,'</main>','<img src="https://merchant.test/pixel"></main>');
  ht(k,'</main>','<link rel="preconnect" href="https://tracker.test"></main>');
  ht(k,'</main>','<button disabled>Second CTA</button></main>');
  ht(k,'id="offer-disclosure"','id="foo"');
  ht(k,'may earn a commission at no additional cost','may share their thoughts');
  ht(k,'merchant\'s own newsletter','our own newsletter');
  ht(k,'https://finalvestige.com/focus/','https://example.com/focus/');
  ht(k,'prefers-reduced-motion:reduce','prefers-reduced-motion:false');
 }
 ht('guideB','0–7 seconds:','0–8 seconds:');
 ht('guideB','<desc id="video-desc">','<desc id="lost-desc">');
 ht('guideB','Zen12 Premium is a paid collection','Zen12 Premium is a magical collection');
 ht('guideA','If your problem is','When your problem is');
 ht('article','rhesus monkeys did not','rhesus monkeys always did');
 ht('article','not a replicated laboratory experiment','a replicated experiment');
 ht('article','https://doi.org/10.1068/p7755','https://example.com/false');
 ht('repairedArticle','October 23, 2012','October 23, 2013');
 ht('repairedArticle','15 participants','1500 participants');
 ht('repairedPlan','fees AND platform costs not already netted','fees alone');
 ht('plan','NOT_COMPUTABLE','ZERO');
 reg('approved partner forged',x=>{const z=JSON.parse(x.matrix);z.commercial.publisher_approved=true;x.matrix=JSON.stringify(z)});
 reg('invented affiliate clicks',x=>{const z=JSON.parse(x.matrix);z.commercial.affiliate_click=121;x.matrix=JSON.stringify(z)});
 reg('paid sale invented',x=>{const z=JSON.parse(x.matrix);z.commercial.cleared_affiliate_commissions=119;x.matrix=JSON.stringify(z)});
 reg('release gate cleared',x=>{const z=JSON.parse(x.matrix);z.gates[0].verified=true;x.matrix=JSON.stringify(z)});
 reg('orphan source',x=>{const z=JSON.parse(x.matrix);z.claims[0].source='FAKE_SOURCE';x.matrix=JSON.stringify(z)});
 reg('duplicate claim identifier',x=>{const z=JSON.parse(x.matrix);z.claims[1].id=z.claims[0].id;x.matrix=JSON.stringify(z)});
 reg('seller claim disguised as established research',x=>{const z=JSON.parse(x.matrix);z.claims.find(c=>c.id==='ZEN12_EQ').status='independently_proven';x.matrix=JSON.stringify(z)});
 reg('owned SKU forged',x=>{const z=JSON.parse(x.matrix);z.claims.find(c=>c.id==='FV_PAYHIP').status='VERIFIED';x.matrix=JSON.stringify(z)});
 let rejected=0;const surprises=[];
 for(const {label,func} of cases){
  const x={...base};func(x);
  try{validate(x);surprises.push(label)}catch{rejected++}
 }
 return {total:cases.length,rejected,unexpected_passes:surprises};
}
if(typeof module!=='undefined')module.exports={paths,pins,validate,runMutations,stripVideo};
if(typeof require!=='undefined'&&require.main===module){
 const fs=require('node:fs'),crypto=require('node:crypto');
 const x={};
 for(const [k,path] of Object.entries(paths)){
  x[k]=fs.readFileSync(path,'utf8');
  const sha=crypto.createHash('sha1').update('blob '+Buffer.byteLength(x[k],'utf8')+'\0'+x[k]).digest('hex');
  check(sha===pins[k],'source blob mismatch '+path);
 }
 validate(x);const result=runMutations(x);
 check(result.rejected===result.total,'unsafe source mutation escaped: '+result.unexpected_passes.join(','));
 process.stdout.write(JSON.stringify({status:'PASS',pinned_files:Object.keys(paths).length,...result})+'\n');
}
