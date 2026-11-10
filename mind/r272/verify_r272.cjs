'use strict';
// Reproducible Mind R272 source/claims/commercial-release checks.
// Run from repository root: node mind/r272/verify_r272.cjs
// Does not request the network, change WordPress, call affiliate links or collect personal data.
const EXACT_GATES = [
'named_inspire3_acceptance','issued_publisher_specific_earning_url','exact_zen12_offer_identity',
'current_authenticated_cart_total','refund_policy_scope_and_fulfillment','approved_web_promotion_channels',
'approved_email_promotion_channels','approved_creatives_or_swipe_terms','product_specific_claim_substantiation',
'affiliate_attribution_permissions','ftc_adjacent_disclosure_qa','signed_out_mobile_browser_qa',
'word_press_sanitization_qa','founder_commercial_release_approval','independent_settled_commission_report',
'verified_product_sales_and_refunds_reconciliation'];
const SCIENCE_SOURCE_URLS = ['https://pubmed.ncbi.nlm.nih.gov/37205669/',
'https://pubmed.ncbi.nlm.nih.gov/38458383/','https://pubmed.ncbi.nlm.nih.gov/33049431/'];
function readPlain(data) {
  const errors=[];
  let m; try {m=JSON.parse(data.matrix);} catch(e){return ['matrix JSON invalid'];}
  const article=data.article||'', plan=data.plan||'', a=data.a||'', b=data.b||'';
  if(m.schema!=='fv-mind-r272-auditory-source-claim-commercial-proof-v1'||m.decision!=='HARD_HOLD'||m.status!=='UNPUBLISHED_DRAFT') errors.push('matrix release state');
  const gates=m.commercial_gates||[];
  if(gates.length!==EXACT_GATES.length||new Set(gates.map(g=>g.id)).size!==16||
    EXACT_GATES.some(g=>!gates.find(x=>x.id===g&&x.status==='HARD_HOLD'&&x.evidence==='NOT_VERIFIED'&&x.release_blocker===true)))errors.push('authorization gate identity/status');
  if(!m.release || Object.values(m.release).some(x=>x!==false))errors.push('release flags');
  if(!Array.isArray(m.sources)||m.sources.length<18||m.sources.some(s=>!/^https:\/\//.test(s.url)||!s.id))errors.push('source identifiers/urls');
  if(!Array.isArray(m.claims)||m.claims.length<25||m.claims.some(c=>!c.id||!c.limitation||!Array.isArray(c.source_ids)||c.source_ids.some(id=>!m.sources.find(s=>s.id===id))))errors.push('claim-source mapping');
  const prohibited=['C03','C06','C09','C10','C11','C12','C14','C15','C16','C17','C19','C22','C23','C24','C25','C26'];
  if(prohibited.some(id=>!(m.claims.find(c=>c.id===id)||{}).status.match(/^(not_|false_|seller_claim_|unsupported_)/)))errors.push('unsafe claim classification');
  const expectedOffers=['zen12_premium','hypnosis_live_total_focus','brainwave_shots','owned_paid_mind_product','seven_day_focus_fieldbook'];
  if(expectedOffers.some(id=>!m.offers.some(o=>o.id===id)))errors.push('missing offer');
  const zen=m.offers.find(o=>o.id==='zen12_premium')||{};
  if(zen.authorization!=='NOT_VERIFIED'||zen.issued_earning_url!==null||zen.cart_total!==null||zen.action!=='NO_ACTIVE_AFFILIATE_LINK')errors.push('zen12 commercial gate');
  const owned=m.offers.find(o=>o.id==='owned_paid_mind_product')||{};
  if(owned.sku!==null||owned.active_checkout!=='NOT_VERIFIED'||owned.action!=='DO_NOT_ADVERTISE')errors.push('owned product preapproval');
  const free=m.offers.find(o=>o.id==='seven_day_focus_fieldbook')||{};
  if(free.pricing!=='FREE'||free.new_form!==false||free.paid_order!==false)errors.push('duplicated/paid Focus funnel');
  if(m.measurement.metrics_status!=='NOT_COMPUTABLE'||m.measurement.cohorts_days.join(',')!=='7,30'||m.measurement.events.includes('affiliate_sale'))errors.push('attribution/revenue distinction');
  if(!Array.isArray(m.creator_fit)||m.creator_fit.length!==3||m.creator_fit.some(c=>c.asset_id!==null))errors.push('fabricated creator asset mapping');
  if(article.trim().split(/\s+/).length<2000 || !article.includes('five reported findings') ||
     !article.includes('eight reported contradictory') || !article.includes('one presented mixed') ||
     !article.includes('did **not**') || !article.includes('Seven Day Focus Fieldbook'))errors.push('article integrity');
  for(const u of ['https://pmc.ncbi.nlm.nih.gov/articles/PMC10198548/','https://pubmed.ncbi.nlm.nih.gov/38458383/','https://pubmed.ncbi.nlm.nih.gov/33049431/','https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance']){
    if(!article.includes(u))errors.push('missing primary source '+u);
  }
  if(!plan.includes('NOT COMPUTABLE')||!plan.includes('42-second')||!plan.includes('Grok')||!plan.includes('360, 390, 768, 1440, 1920'))errors.push('acceptance/owners/performance missing');
  const section = h => (h.match(/<section id="direct-evidence">[\s\S]*?<\/section>/)||[])[0];
  if(!section(a)||!section(b)||section(a)!==section(b)||SCIENCE_SOURCE_URLS.some(u=>!section(a).includes(u)))errors.push('A/B science evidence consistency');
  if(a.includes('Ströberg, Andersen')||b.includes('Ströberg, Andersen'))errors.push('irrelevant sem-satiation transfer');
  const choice = h => h.slice(h.indexOf('<section id="choice">'),h.indexOf('</main>'));
  if(!choice(a)||!choice(b)||choice(a)!==choice(b))errors.push('A/B purchasing-copy mismatch');
  for(const [n,h] of [['A',a],['B',b]]){
    const card = (h.match(/<div class="card" id="commercial-card">[\s\S]*?<\/div>/)||[])[0]||'';
    const buttons=(h.match(/<button\b[^>]*>/gi)||[]);
    if(buttons.length!==1||!buttons[0].includes(' disabled ')||!buttons[0].includes('aria-disabled="true"')||
       !card.includes(buttons[0]))errors.push(n+' activated purchase button');
    const ctl=card.indexOf('id="zen12-buy-button"'),d=card.indexOf('id="affiliate-disclosure"');
    if(ctl<0||d<ctl||d-ctl>350||!card.includes('Final Vestige may earn a commission')||!card.includes('no active affiliate link'))errors.push(n+' affiliate disclosure proximity');
    if(/<(script|form|iframe|video|audio|source|track)\b/i.test(h)||/<(?:video|audio)[^>]*\sautoplay(?:[=\s>])/i.test(h)||/\bonclick\s*=|http-equiv=["\x27]refresh/i.test(h))errors.push(n+' unapproved scripts/forms/forced media');
    if(/<a\b[^>]*href=["']https?:\/\/(?:www\.)?(zen12\.com|inspire3\.com|hypnosislive\.com|brainwaveshots\.com)/i.test(h))errors.push(n+' unapproved merchant link');
    if(/(?:url\s*\(\s*['"]?https?:|<image\b|<use\b|<img\b|<link\b[^>]*href=)/i.test(h))errors.push(n+' unreviewed external resource');
    if(!h.includes('href="https://finalvestige.com/focus/"'))errors.push(n+' existing free route');
  }
    const EXACT_FILM_CAPTIONS = ["<p data-time=\"0-6\">00:00–06:00 · Twelve minutes is an amount of time—not a measured benefit.</p>","<p data-time=\"6-12\">06:00–12:00 · A listener may feel calmer. That experience deserves respect.</p>","<p data-time=\"12-18\">12:00–18:00 · But a free timer, a guided voice, and expectation can all matter.</p>","<p data-time=\"18-24\">18:00–24:00 · The 2023 EEG review found mixed results for binaural-beat entrainment.</p>","<p data-time=\"24-30\">24:00–30:00 · It did not test Zen12 Premium or prove twelve minutes equals sixty.</p>","<p data-time=\"30-36\">30:00–36:00 · Compare the format with a free session. Record what you noticed.</p>","<p data-time=\"36-42\">36:00–42:00 · Read the evidence and the terms before deciding to purchase.</p>"];
  const actualCaptions=b.match(/<p data-time="[^"]+">[^<]+<\/p>/g)||[];
  if(JSON.stringify(actualCaptions)!==JSON.stringify(EXACT_FILM_CAPTIONS))errors.push('original R257 film caption timing/text drift');
  if(!b.includes('NOT HOSTED')||!b.includes('static poster')||(b.match(/data-time="/g)||[]).length!==7)errors.push('video source status and captions');
  if(/<video\b|<audio\b/i.test(b)||b.includes('src="https://'))errors.push('video unexpectedly hosted/external');
  return errors;
}
function clone(x) {return JSON.parse(JSON.stringify(x));}
function runAdversarial(d){
 const cases=[];
 const add=(name,data)=>cases.push([name,data]);
 const parsed=JSON.parse(d.matrix);
 for(const id of EXACT_GATES){
   const m=clone(parsed);m.commercial_gates.find(x=>x.id===id).status='APPROVED';add('gate status '+id,{...d,matrix:JSON.stringify(m)});
   const m2=clone(parsed);m2.commercial_gates.find(x=>x.id===id).release_blocker=false;add('gate bypass '+id,{...d,matrix:JSON.stringify(m2)});
 }
 for(const change of [
  m=>{m.decision='LIVE'},
  m=>{m.release.affiliate_url_active=true},
  m=>{m.offers.find(o=>o.id==='zen12_premium').issued_earning_url='https://example.org/affiliate'},
  m=>{m.offers.find(o=>o.id==='zen12_premium').authorization='APPROVED'},
  m=>{m.offers.find(o=>o.id==='owned_paid_mind_product').sku='IMAGINARY'},
  m=>{m.offers.find(o=>o.id==='seven_day_focus_fieldbook').new_form=true},
  m=>{m.measurement.metrics_status='VERIFIED'},
  m=>{m.creator_fit[0].asset_id='FAKE_VIDEO'},
  m=>{m.claims.find(c=>c.id==='C09').status='supported_scientific_review'},
  m=>{m.sources[0].url='javascript:alert(1)'},
  m=>{m.claims.find(c=>c.id==='C02').source_ids=['MISSING_SOURCE']}
 ]){const m=clone(parsed);change(m);add('matrix negative '+cases.length,{...d,matrix:JSON.stringify(m)});}
 for(const [name,field,from,to] of [
 ['A enabled CTA','a','type="button" disabled','type="button"'],
 ['B enabled CTA','b','type="button" disabled','type="button"'],
 ['A missing disclosure','a','id="affiliate-disclosure"','id="deleted-disclosure"'],
 ['B missing disclosure','b','id="affiliate-disclosure"','id="deleted-disclosure"'],
 ['A external merchant','a','href="https://finalvestige.com/focus/"','href="https://zen12.com/secret/"'],
 ['B external merchant','b','href="https://finalvestige.com/focus/"','href="https://zen12.com/hnp"'],
 ['A extra subscription','a','</main>','<form action="/subscribe"><input></form></main>'],
 ['B injected script','b','</main>','<script src="https://cdn.example.test/pixel.js"></script></main>'],
 ['A CSS beacon','a','</style>','body{background-image:url(https://x.invalid/t.gif)}</style>'],
 ['B SVG external','b','</svg>','<use href="https://x.invalid/a.svg#art"></use></svg>'],
 ['B forced playback','b','</main>','<video autoplay></video></main>'],
 ['B missing poster claim','b','NOT HOSTED','NOW HOSTED'],
 ['B altered caption','b','data-time="0-6"','data-time="0-5"'],
 ['A altered science','a','five studies were consistent','seven studies were consistent'],
 ['B buyer parity tamper','b','Start with the actual problem','Start with guaranteed results'],
 ['A missing free CTA','a','href="https://finalvestige.com/focus/"','href="#not-the-focus-route"']
 ]){if(!d[field].includes(from))throw Error('non-effective mutation '+name);add(name,{...d,[field]:d[field].replace(from,to)});}
 add('short article',{...d,article:d.article.slice(0,220)});
 add('missing release plan',{...d,plan:'none'});
 let passed=0,failed=[];
 for(const [name,input] of cases){if(readPlain(input).length)passed++;else failed.push(name)}
 return {total:cases.length,passed,failed};
}
module.exports={validate:readPlain,runAdversarial,EXACT_GATES};
if(typeof require!=='undefined'&&require.main===module){
 const fs=require('fs');
 const d={a:fs.readFileSync('mind/r268/ZEN12-A-TEXT-UNPUBLISHED.html','utf8'),
 b:fs.readFileSync('mind/r268/ZEN12-B-OPTIONAL-FILM-UNPUBLISHED.html','utf8'),
 article:fs.readFileSync('mind/r272/THE-THIRD-TONE-THAT-DID-NOT-PROVE-A-CURE-UNPUBLISHED.md','utf8'),
 matrix:fs.readFileSync('mind/r272/PRODUCT-EVIDENCE-AND-REVENUE-GATES.json','utf8'),
 plan:fs.readFileSync('mind/r272/CONVERSION-AND-VIDEO-AB-RELEASE-ACCEPTANCE.md','utf8')};
 const errors=readPlain(d),out=runAdversarial(d);
 console.log('R272 baseline:',errors.length?'FAIL '+errors.join(' | '):'PASS');
 console.log('R272 negative tests:',out.passed+'/'+out.total,'rejected',out.failed.join(', '));
 if(errors.length||out.failed.length)process.exitCode=1;
}
