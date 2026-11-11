'use strict';
/**
 * Mind R282 commercial-integrity source checks. Run:
 *    node mind/r282/verify_r282.cjs
 * No external packages, web calls, service secrets or deployment.
 * Source inspection is NOT a real browser, WCAG audit, merchant checkout, or sales validation.
 */
const fs = require('node:fs');
const path = require('node:path');
const base = __dirname;
const P = {
 article:'THE-SECOND-THING-WAS-THERE-ALL-ALONG-UNPUBLISHED.md',
 a:'ZEN12-DECISION-A-TEXT-UNPUBLISHED.html',
 b:'ZEN12-DECISION-B-OPTIONAL-FILM-CONCEPT-UNPUBLISHED.html',
 matrix:'MERCHANT-CLAIM-REVENUE-GATES.json',
 plan:'ONE-OFFER-REVENUE-CONVERSION-ACCEPTANCE.md'
};
const GATES = [
'named_FV_partner_acceptance','current_signed_affiliate_terms','permitted_website_channel',
'permitted_organic_social_channel','permitted_email_channel_if_used','issued_earning_URL',
'tracking_parameter_rules','current_exact_offer_page','authenticated_cart_total',
'refundable_item_terms','verified_refund_fulfillment_process','creative_audio_video_rights',
'substantiation_for_any_claim','full_browsers_a11y_security_QA','founder_release_approval',
'merchant_reported_settled_commissions'];
const merchant=/^(?:www\.)?(?:zen12\.com|inspire3\.com|hypnosislive\.com|brainwaveshots\.com|affiliates\.inspire3\.com)$/i;
const fault=(errors,msg)=>errors.push(msg);
const words=t=>(t.trim().match(/\S+/g)||[]).length;
function attrs(tag) {
  // Forbid unknown HTML attributes that could cause navigation, event execution, or requests.
  const out={};
  const pat=/([A-Za-z_:][\w:.-]*)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))/g;
  let m;while((m=pat.exec(tag))) out[m[1].toLowerCase()]=m[2]??m[3]??m[4];
  return out;
}
function decode(s){return s.replace(/&(?:#x([0-9a-f]+)|#([0-9]+)|amp|colon|sol|tab|NewLine);/gi,(m,h,d)=>h?String.fromCodePoint(parseInt(h,16)):d?String.fromCodePoint(+d):({'&amp;':'&','&colon;':':','&sol;':'/','&tab;':'\t','&newline;':'\n'})[m.toLowerCase()]||m)}
function validateHTML(html,variant,errors){
  if(!/<!doctype html>/i.test(html)||!/<html lang="en">/.test(html)||!/<meta name="viewport"/.test(html))fault(errors,variant+': document semantics');
  if((html.match(/<h1\b/g)||[]).length!==1)fault(errors,variant+': require exactly one heading');
  if(!/class="fv-m282"/.test(html)||!/focus-visible/.test(html)||!/@media\(max-width:720px\)/.test(html))fault(errors,variant+': responsive/accessibility source');
  if(/<\s*(?:script|iframe|form|input|link|base|video|audio|source|object|embed)\b/i.test(html)||/\bon(?:click|load|error|mouseover|submit|focus|touchstart)\s*=/i.test(html)||/\bcontenteditable\s*=|\bautofocus\b/i.test(html))fault(errors,variant+': active content or form');
  if(/@import\b|url\s*\(|fetch\s*\(|navigator\.|localStorage|document\.cookie|googletagmanager|analytics\.js|gtag\b/i.test(html))fault(errors,variant+': possible external fetching / script');
  let tags=html.match(/<\s*a\b[^>]*>/gi)||[];
  for(const tag of tags){const a=attrs(tag);if(!('href'in a)){fault(errors,variant+': anchor without href');continue}const raw=decode(a.href).replace(/[\u0000-\u0020]+/g,'');let u;
    try{u=new URL(raw,'https://finalvestige.com/')}catch{fault(errors,variant+': invalid link');continue}
    if(!['https:','http:'].includes(u.protocol)||merchant.test(u.hostname)||(/payhip\.com$/i.test(u.hostname))||/affiliate|affid|ref=|clickid|utm_/i.test(u.search))fault(errors,variant+': unauthorized merchant/affiliate source href');
    if(u.protocol!=='https:')fault(errors,variant+': not https');
  }
  for(const tag of (html.match(/<\s*(?:button|a|svg)\b[^>]*>/gi)||[])){
    let a=attrs(tag);
    if(/<\s*button/i.test(tag)&&!/\sdisabled(?:\s|>|\/)/i.test(tag)&&/commercial-control/.test(tag))fault(errors,variant+': enabled commercial control');
  }
  const commercial=html.match(/<section class="section" aria-labelledby="m282-commercial">([\s\S]*?)<\/section>/);
  if(!commercial||!/<button[^>]*disabled\b[^>]*aria-disabled="true"/.test(commercial[1])||!/If a purchasing link is approved and activated/.test(commercial[1])||!/may earn a commission/.test(commercial[1])||!/no active commission-earning link here/i.test(commercial[1]))fault(errors,variant+': missing adjacent disabled CTA disclosure');
  if(!/seller's newsletter/.test(html)||!/Jetpack\/Dispatch/.test(html))fault(errors,variant+': consent separation');
  if(!/free timer/.test(html)||!/<a href="https:\/\/finalvestige\.com\/focus\/"/.test(html))fault(errors,variant+': useful alternative or current funnel missing');
  if(variant==='B'){
    if(!/42-second/.test(html)||!/<svg class="poster"/.test(html)||!/role="img"/.test(html)||!/<details><summary>Read the complete film transcript/.test(html))fault(errors,'B: absent accessible static film');
    const stamps=['00:00–00:06','00:06–00:12','00:12–00:18','00:18–00:24','00:24–00:30','00:30–00:36','00:36–00:42'];
    for(const s of stamps)if(!html.includes(s))fault(errors,'B: missing '+s);
    if((html.match(/<li><span class="time">/g)||[]).length!==7)fault(errors,'B: wrong transcript segments');
  } else if(/class="filmmodule"|<svg class="poster"/.test(html))fault(errors,'A: unexpected film');
}
function validate(f){
  const errors=[];
  if(words(f.article)<1800)fault(errors,'manuscript too short');
  for(const s of ['Raymond','Chun','Slagter','MacLean','Puységur','https://pubmed.ncbi.nlm.nih.gov/1500880/','not active','not a'])if(!f.article.includes(s))fault(errors,'missing original investigation boundary: '+s);
  if(/href\s*=|<script/i.test(f.article))fault(errors,'article contains rendered script or href');
  if(words(f.plan)<1200||!/NOT COMPUTABLE/.test(f.plan)||!/NO VERIFIED CAMPAIGN BUNDLE/.test(f.plan)||!/A\/B/.test(f.plan))fault(errors,'missing revenue acceptance plan');
  validateHTML(f.a,'A',errors);validateHTML(f.b,'B',errors);
  const fm=f.b.match(/<section class="filmmodule"[\s\S]*?<\/section>/);
  if(!fm||f.b.replace(fm[0],'').replace('unpublished B','unpublished A')!==f.a)fault(errors,'A/B not commercially identical except static film');
  let m;try{m=JSON.parse(f.matrix)}catch{fault(errors,'matrix not JSON');return errors}
  const ids=(m.authorization_gates||[]).map(x=>x.id);
  if(ids.length!==16||new Set(ids).size!==16||ids.slice().sort().join('|')!==GATES.slice().sort().join('|'))fault(errors,'16 required exact gate IDs missing');
  if((m.authorization_gates||[]).some(x=>x.status!=='HARD_HOLD'))fault(errors,'gate illegally cleared');
  if((m.source_register||[]).length<15||(m.claim_source_map||[]).length<15)fault(errors,'thin source/claim matrix');
  const allSource=new Set((m.source_register||[]).map(x=>x.id));
  for(const c of m.claim_source_map||[])for(const id of c.source_ids||[])if(!allSource.has(id))fault(errors,'unknown source '+id);
  for(const p of m.offer_inventory||[])if(p.id!=='FV_FOCUS_FREE'&&(p.active!==false||p.publisher_earning_url!==null))fault(errors,'unauthorized paid/merchant offer');
  if(m.verified_sales!==null||m.verified_settled_commission!==null||m.net_revenue_per_1000_qualified_humans!==null)fault(errors,'invented financial outcome');
  if(m.qualified_human_sessions!==null)fault(errors,'invented campaign session denominator');
  const idCheck=new Set((m.creator_topic_to_product_fit||[]).map(c=>c.topic));
  if(idCheck.size!==3||(m.creator_topic_to_product_fit||[]).some(c=>c.asset_id!==null))fault(errors,'fabricated or missing Grok asset');
  if(!m.consent_boundaries?.no_duplicate_forms||!/separate/i.test(m.consent_boundaries?.zen12_gift||''))fault(errors,'consent confusion');
  if(!/affiliate_click/.test(JSON.stringify(m.measurement_contract))||!/paid/.test(JSON.stringify(m.measurement_contract)))fault(errors,'outbound conflated with sale');
  return errors;
}
function runSelfTest(f){
 const baseline=validate(f);if(baseline.length)throw Error('BASELINE FAIL: '+baseline.join('; '));
 const mutations=[];
 const flip=(key,from,to)=>{mutations.push({key,from,to})};
 flip('a','<button type="button" class="commercial-control" disabled','<button type="button" class="commercial-control"');
 flip('b','<button type="button" class="commercial-control" disabled','<button type="button" class="commercial-control"');
 flip('a','may earn a commission','might recommend a product');
 flip('b','no active commission-earning link here','commission pathway ready');
 flip('a','<main class="fv-m282"','<form><main class="fv-m282"');
 flip('a','<main class="fv-m282"','<script>alert(1)</script><main class="fv-m282"');
 flip('b','<main class="fv-m282"','<iframe src="https://zen12.com"></iframe><main class="fv-m282"');
 flip('b','<main class="fv-m282"','<input type=email><main class="fv-m282"');
 flip('a','<main class="fv-m282"','<base href="https://zen12.com/"><main class="fv-m282"');
 flip('a','<main class="fv-m282"','<a href=https://zen12.com/?affid=123>Buy</a><main class="fv-m282"');
 flip('b','<main class="fv-m282"','<a href = "https://zen12.com">Buy</a><main class="fv-m282"');
 flip('b','<main class="fv-m282"','<a href="javascript:alert(1)">Buy</a><main class="fv-m282"');
 flip('a','<main class="fv-m282"','<a href="&#x68;ttps://zen12.com">Buy</a><main class="fv-m282"');
 flip('a','<main class="fv-m282"','<a href="https://payhip.com/b/fake">Purchase</a><main class="fv-m282"');
 flip('a','<main class="fv-m282"','<img src="https://tracking.example/pixel"><main class="fv-m282"');
 flip('a','<main class="fv-m282"','<link href="https://tracking.example/css"><main class="fv-m282"');
 flip('a','<main class="fv-m282"','<main onclick="steal()" class="fv-m282"');
 flip('a','<main class="fv-m282"','<style>@import url(https://tracking.example)</style><main class="fv-m282"');
 flip('a','<main class="fv-m282"','<style>.x{background:url(https://tracking.example)}</style><main class="fv-m282"');
 flip('b','00:36–00:42','00:42–00:48');
 flip('b','<svg class="poster"','<figure class="poster"');
 flip('b','<details><summary>Read the complete film transcript','<details><summary>Skip transcript');
 flip('a','seller\'s newsletter','our newsletter');
 flip('a','Jetpack/Dispatch','new pop-up signup');
 flip('a','free timer','paid timer');
 flip('a','<a href="https://finalvestige.com/focus/"','<a href="https://affiliate.example.com/ref"');
 flip('article','Slagter','SellerSays');
 flip('article','https://pubmed.ncbi.nlm.nih.gov/1500880/','https://seller.example/');
 flip('plan','NOT COMPUTABLE','$0');
 flip('plan','NO VERIFIED CAMPAIGN BUNDLE','EXACT VERIFIED MEDIA ID');
 flip('matrix','"status": "HARD_HOLD"','"status": "APPROVED"');
 flip('matrix','"publisher_earning_url": null','"publisher_earning_url": "https://fake.example/affiliate"');
 flip('matrix','"verified_sales": null','"verified_sales": 3');
 flip('matrix','"verified_settled_commission": null','"verified_settled_commission": 123');
 flip('matrix','"qualified_human_sessions": null','"qualified_human_sessions": 1000');
 flip('matrix','"net_revenue_per_1000_qualified_humans": null','"net_revenue_per_1000_qualified_humans": 999');
 flip('matrix','"asset_id": null','"asset_id": "MADE_UP"');
 flip('matrix','"no_duplicate_forms": true','"no_duplicate_forms": false');
 flip('matrix','"publisher_earning_url": null','"publisher_earning_url": "https://zen12.com/aff"');
 flip('matrix','"status": "HARD_HOLD"','"status": "LIVE"');
 let passed=0;
 for(const m of mutations){if(!f[m.key].includes(m.from))throw Error('BAD MUTATION FIXTURE '+m.key+': '+m.from);
   const other={...f,[m.key]:(m.key==='article'&&m.from==='Slagter')||(m.key==='plan'&&m.from==='NOT COMPUTABLE')?f[m.key].replaceAll(m.from,m.to):f[m.key].replace(m.from,m.to)};
   const failures=validate(other);if(!failures.length)throw Error('UNDETECTED UNSAFE MUTATION '+JSON.stringify(m));passed++;
 }
 return {baseline:'PASS',rejected:passed,total:mutations.length,commercial_gates:16,film_status:'STATIC_ONLY',source_level_only:true};
}
const files=Object.fromEntries(Object.entries(P).map(([k,v])=>[k,fs.readFileSync(path.join(base,v),'utf8')]));
const result=runSelfTest(files);
if(require.main===module)console.log(JSON.stringify(result,null,2));
module.exports={validate,runSelfTest,P,GATES};
