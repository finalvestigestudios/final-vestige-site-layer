"use strict";
/* Final Vestige Mind R283 - source-only, fail-closed regression suite.
   Run: node mind/r283/verify_r283.cjs
   Optional: require(module).run(sourceMap) for an isolated V8 with *exact fetched blobs*.
   This is NOT real-browser, WordPress, merchant or payment testing. */
const files={
 article:"THE-ALARM-YOU-DID-NOT-HEAR-INATTENTIONAL-DEAFNESS-UNPUBLISHED.md",
 claims:"PRODUCT-CLAIM-SOURCE-COMMERCIAL-GATES.json",
 a:"ZEN12-INATTENTIONAL-DEAFNESS-BUYER-A-TEXT-UNPUBLISHED.html",
 b:"ZEN12-INATTENTIONAL-DEAFNESS-BUYER-B-OPTIONAL-VIDEO-CONCEPT-UNPUBLISHED.html",
 plan:"OFFER-TO-VERIFIED-REVENUE-AB-RELEASE-ACCEPTANCE.md"
};
const requiredGates=[
"named_FV_partner_acceptance","current_signed_affiliate_terms","permitted_website_channel","permitted_organic_social_channel",
"permitted_email_channel_if_used","issued_earning_URL","tracking_parameter_rules","current_exact_offer_page",
"authenticated_cart_total","refundable_item_terms","verified_refund_fulfillment_process","creative_audio_video_rights",
"substantiation_for_any_claim","full_browsers_a11y_security_QA","founder_release_approval","merchant_reported_settled_commissions"];
const assert=(condition,label,fail)=>{if(!condition)fail.push(label)};
const norm=s=>s.replace(/\s+/g," ").trim();
function stripFilm(s){
  return s.replace(/<section class="section" data-optional-film="R283_STATIC_ONLY"[\s\S]*?<\/section>/g,"")
  .replace(/<title>[\s\S]*?<\/title>/g,"<title>same</title>");
}
function check(data){
  let fail=[];
  for(const k of Object.keys(files))assert(typeof data[k]==="string" && data[k].length>800,"missing/short "+k,fail);
  if(fail.length)return fail;
  let e;
  try{e=JSON.parse(data.claims)}catch(_){return ["JSON invalid"]}
  assert(e.version==="R283" && e.commercial_mode==="HARD_HOLD" && e.publication_state==="UNPUBLISHED","release state",fail);
  assert(Array.isArray(e.source_register) && e.source_register.length>=18,"source count",fail);
  assert(Array.isArray(e.claim_source_map) && e.claim_source_map.length>=20,"claim count",fail);
  assert(Array.isArray(e.creator_topic_to_product_fit) && e.creator_topic_to_product_fit.length===3,"creator route count",fail);
  assert(Array.isArray(e.authorization_gates) && e.authorization_gates.length===16,"exact gate count",fail);
  const ids=(e.authorization_gates||[]).map(g=>g.id);
  assert(requiredGates.every(id=>ids.includes(id)) && new Set(ids).size===16,"exact gate identity",fail);
  assert((e.authorization_gates||[]).every(g=>g.status==="HARD_HOLD"),"authorization must all be held",fail);
  assert(e.verified_sales===null && e.verified_settled_commission===null &&
    e.qualified_human_sessions===null && e.net_revenue_per_1000_qualified_humans===null,"cannot fabricate commerce",fail);
  assert((e.offer_inventory||[]).every(o=>o.activated===false || o.activated_for_commerce===false),"no offer activation",fail);
  assert(e.measurement_contract?.no_new_tracking_script===true && e.consent_boundaries?.no_pii_tracking===true,"privacy safe",fail);
  assert(e.consent_boundaries?.fv_jetpack?.includes("existing") && e.consent_boundaries?.merchant_zen12?.includes("distinct"),"separate consent",fail);
  assert(e.claim_source_map.some(x=>x.id==="C08" && x.classification==="seller_assertion_unsubstantiated"),"equivalence held",fail);
  assert(e.claim_source_map.some(x=>x.id==="C16" && x.limitation?.includes("actual processing not authenticated")),"refund qualification",fail);
  assert((e.creator_topic_to_product_fit||[]).every(r=>r.asset_id===null),"no fake internal asset id",fail);
  const sellerHost=/href\s*=\s*["'][^"']*(?:zen12\.com|inspire3\.com|hypnosislive\.com|brainwaveshots\.com|payhip\.com)[^"']*["']/i;
  for(const k of ["a","b"]){
    const h=data[k];
    assert(/<html lang="en">/i.test(h)&&/name="viewport"/i.test(h)&&/noindex,nofollow/.test(h),"draft mobile+robots "+k,fail);
    assert(!sellerHost.test(h),"no unauthorized seller link "+k,fail);
    assert(!/<(?:form|script|iframe|video|audio|source|input)\b/i.test(h),"no form/script/media "+k,fail);
    assert(!/\bon(?:click|load|error)\s*=/i.test(h),"no inline event "+k,fail);
    assert(!/autoplay/i.test(h.replace(/no autoplay/g,"")),"no autoplay attribute "+k,fail);
    assert(!/data-(?:gtm|ga|pixel)/i.test(h),"no duplicate tracker "+k,fail);
    assert(/<button[^>]*\bdisabled\b[^>]*>Compare Zen12/i.test(h),"disabled CTA "+k,fail);
    assert(/If you purchase through a future approved link, Final Vestige may earn a commission at no additional cost to you/.test(h),"adjacent FTC disclosure "+k,fail);
    const section=h.match(/<div class="commercial"[\s\S]*?<\/div>/i)?.[0]||"";
    assert(section.indexOf("If you purchase through a future approved link")>section.indexOf("<button")&&section.indexOf("If you purchase through a future approved link")<section.indexOf("</div>"),"disclosure in same commerce box "+k,fail);
    assert(/https:\/\/finalvestige\.com\/focus\//.test(h),"existing Fieldbook "+k,fail);
    assert(/separate marketing newsletter/.test(h),"separate merchant consent "+k,fail);
    assert(/prefers-reduced-motion:reduce/.test(h),"reduced-motion CSS "+k,fail);
    assert(/:focus-visible/.test(h),"keyboard outline "+k,fail);
    assert(!/free trial guaranteed|scientifically proven to improve focus|we personally used Zen12/i.test(h),"no fabricated outcomes "+k,fail);
  }
  assert(norm(stripFilm(data.a))===norm(stripFilm(data.b)),"A/B identical buyer copy outside optional film",fail);
  assert(!data.a.includes('data-optional-film="R283_STATIC_ONLY"') && data.b.includes('data-optional-film="R283_STATIC_ONLY"'),"optional film only B",fail);
  assert(data.b.includes("There is no playable video")===false && data.b.includes("no playable video"),"B clear static status",fail);
  assert(data.b.includes('aria-labelledby="m283-title m283-desc"') && data.b.includes("<details>") && data.b.includes("<summary>"),"accessible static film alternative",fail);
  const stamps=Array.from(data.b.matchAll(/<strong>(\d\d:\d\d)[–-](\d\d:\d\d):<\/strong>/g));
  assert(stamps.length===7,"seven film transcript beats",fail);
  for(let i=0;i<7;i++){
    const fmt=n=>"00:"+String(n).padStart(2,"0");
    assert(stamps[i]?.[1]===fmt(i*6)&&stamps[i]?.[2]===fmt((i+1)*6),"timecode "+i,fail);
  }
  assert(data.article.length>7500 && data.article.includes("79 percent") &&
    data.article.includes("Raveh") && data.article.includes("Scheer") &&
    data.article.includes("https://pubmed.ncbi.nlm.nih.gov/25287617/") &&
    /no affiliate checkout link/i.test(data.article),"article sources/evidence",fail);
  assert(data.plan.includes("NOT COMPUTABLE") && data.plan.includes("HARD_HOLD") &&
    data.plan.includes("qualified_human_session") && data.plan.includes("settled_commission") &&
    data.plan.includes("paid commission")&&data.plan.includes("no playable video"),"conversion/release plan",fail);
  return fail;
}
function mutationTests(data){
  const cases=[];
  const alter=(name,k,from,to)=>cases.push([name,()=>{const next={...data};if(!next[k].includes(from))throw Error("fixture not found: "+name);next[k]=next[k].replace(from,to);return next}]);
  for(const id of requiredGates){
    cases.push(["gate-"+id,()=>{let v=JSON.parse(data.claims);v.authorization_gates.find(g=>g.id===id).status="APPROVED";return {...data,claims:JSON.stringify(v)};}]);
  }
  alter("merchant-earning-link-A","a","<button class=\"btn\"","<a href=\"https://zen12.com/hnp\" class=\"btn\"");
  alter("merchant-earning-link-B","b","<button class=\"btn\"","<a href=\"https://affiliates.inspire3.com/\" class=\"btn\"");
  alter("remove-disabled-A","a",'type="button" disabled','type="button"');
  alter("remove-disabled-B","b",'type="button" disabled','type="button"');
  alter("disclosure-A","a","may earn a commission","may receive nothing");
  alter("disclosure-B","b","may earn a commission","may receive nothing");
  alter("form-A","a","</body>","<form><input type=email></form></body>");
  alter("form-B","b","</body>","<form><input type=email></form></body>");
  alter("script-A","a","</body>","<script src=\"https://track.example/x.js\"></script></body>");
  alter("script-B","b","</body>","<script src=\"https://track.example/x.js\"></script></body>");
  alter("autoplay-B","b","<details>","<video autoplay></video><details>");
  alter("missing-film-B","b",'data-optional-film="R283_STATIC_ONLY"','data-optional-film="UNLABELED"');
  alter("caption-timing-B","b","00:36–00:42","00:36–00:48");
  alter("change-copy-A","a"," twelve-minute focus/meditation ritual"," ten-minute focus ritual");
  alter("missing-trial-source","article","https://pubmed.ncbi.nlm.nih.gov/25287617/","https://example.invalid/no-proof");
  alter("fake-revenue","claims",'"verified_sales": null','"verified_sales": 12');
  alter("reprogram-guarantee","a","a free timer","scientifically proven to improve focus");
  alter("fake-founder-approval","plan","**Release judgment: HARD HOLD.**","**Release judgment: APPROVED.**");
  cases.push(["duplicate-creators",()=>{let o=JSON.parse(data.claims);o.creator_topic_to_product_fit.pop();return {...data,claims:JSON.stringify(o)}}]);
  cases.push(["merchant-consent-confusion",()=>{let o=JSON.parse(data.claims);o.consent_boundaries.merchant_zen12="same list";return {...data,claims:JSON.stringify(o)}}]);
  cases.push(["fabricated-asset",()=>{let o=JSON.parse(data.claims);o.creator_topic_to_product_fit[0].asset_id="GROK-FABRICATED";return {...data,claims:JSON.stringify(o)}}]);
  let passed=0;for(const [name,make] of cases){let errors=check(make());if(!errors.length)throw Error("unsafe mutation escaped: "+name);passed++;}
  return {passed,total:cases.length};
}
function run(data){
  if(!data){
    const fs=require("node:fs"),path=require("node:path");data={};
    for(let [key,f] of Object.entries(files))data[key]=fs.readFileSync(path.join(__dirname,f),"utf8");
  }
  const errors=check(data);
  if(errors.length)throw Error("BASELINE FAIL:\n"+errors.join("\n"));
  return {baseline:"PASS",mutationTests:mutationTests(data),gateCount:16,limitations:"source-only; not native browser, WordPress, checkout, CI, video or settlement"};
}
module.exports={run,check,mutationTests,files};
if(require.main===module){
  try{console.log(JSON.stringify(run(),null,2));}catch(e){console.error(e.stack||e);process.exitCode=1}
}
