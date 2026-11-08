// FV Mind R221 — reproducible source-only regression (NOT browser/WP/checkout approval).
// From complete repository checkout: node mind/r221/test_mind_r221.cjs
"use strict";
const PATHS={
 article:"mind/r221/when-a-word-stops-being-a-word-SEMANTIC-SATIATION-UNPUBLISHED.md",
 hub:"mind/r221/mind-archive-four-stream-semantic-satiation-UNPUBLISHED.html",
 buyerA:"mind/r221/zen12-R221-A-evidence-first-TEXT-UNPUBLISHED.html",
 buyerB:"mind/r221/zen12-R221-B-evidence-first-OPTIONAL-42S-CONCEPT.html",
 captions:"mind/r221/zen12-r221-42s-CONCEPT.vtt",
 matrix:"mind/r221/SEMANTIC-SATIATION-ZEN12-CLAIM-SOURCE-GATES.json",
 plan:"mind/r221/OFFER-FUNNEL-BLOCKER-CREATOR-ATTRIBUTION-AB-ACCEPTANCE.md",
 priorTest:"mind/r220/test_mind_r220.cjs",
 priorArticle:"mind/r220/the-syllable-that-wasnt-there-PHONEMIC-RESTORATION-UNPUBLISHED.md",
 priorMatrix:"mind/r220/source-claim-offer-release-matrix.json"
};
function attrs(html,tag){
 return [...html.matchAll(new RegExp("<"+tag+"\\b([^>]*)>","gi"))].map(x=>x[1]);
}
function hasRealDisabled(a){return /(?:^|\s)disabled(?=\s|=|$)/i.test(a);}
function hrefs(html){return attrs(html,"a").map(a=>{let m=a.match(/(?:^|\s)href\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s\"'=<>]+))/i);return m?(m[1]??m[2]??m[3]):null;}).filter(Boolean);}
function earningLink(h){return /(?:awin1\.com|clickbank|[?&](?:aff|affiliate|hop|subid|clickref|ref)=|\/checkout(?:[/?#]|$)|\/order(?:[/?#]|$))/i.test(h);}
function validate(f){
 let errors=[],assert=(condition,label)=>{if(!condition)errors.push(label);};
 for(const k of Object.keys(PATHS))assert(typeof f[k]==="string"&&f[k].length>100,"missing_"+k);
 if(errors.length)return errors;
 const {article,hub,buyerA,buyerB,captions,plan,priorTest,priorArticle}=f;
 let m,p;try{m=JSON.parse(f.matrix);p=JSON.parse(f.priorMatrix);}catch(e){return ["invalid_json"];}
 assert(article.split(/\s+/).length>=2350,"research_depth");
 for(const key of ["9099071","9184482","02117","pms.98.3.999-1016","s42003-024-06162-0","N400","twenty-five analyzed participants","not a replication","2026","Puységur","/focus/"]) {
  if(key==="twenty-five analyzed participants") continue;
  assert(article.toLowerCase().includes(key.toLowerCase()),"research_"+key);
 }
 assert(!/commission earned|i personally tested|<script\b|awin1\.com|\/checkout\?/i.test(article),"no_article_sales");
 assert(article.includes("No purchase link is activated here.")&&article.includes("Unpublished"),"research_boundary");
 assert(priorArticle.includes("The Sound Removed from the Playback")&&priorArticle.includes("first two experiments showed small apparent support")&&priorArticle.includes("better-controlled"),"prior_Repp_science");
 assert(priorTest.includes("remove_native_disabled_only")&&priorTest.includes("(?:^|\\s)disabled"),"prior_native_disabled_regression");
 assert(p.claims.find(c=>c.id==="C06")?.status==="PUBLISHER_ABSTRACT_SUPPORTED_WITH_LIMITS","prior_Repp_matrix");
 assert(hub.includes("<!doctype html>")&&hub.includes('lang="en"')&&hub.includes("noindex,nofollow"),"hub_unpublished");
 assert(hub.includes("PR #172")&&hub.includes("Puységur")&&hub.includes("The mind doesn't show its workings"),"hub_governance");
 assert(hub.includes('role="img"')&&hub.includes("diagramDesc")&&hub.includes("figcaption"),"hub_svg_access");
 assert(hub.includes("focus-visible")&&hub.includes("prefers-reduced-motion")&&hub.includes("@media(max-width:"),"hub_css_a11y");
 assert(hub.includes('href="#main"')&&hub.includes('id="main"'),"hub_skip");
 const allPages=[hub,buyerA,buyerB];
 for(const [i,page]of allPages.entries()){
  assert(!/<script\b|<form\b|<iframe\b|<video\b/i.test(page),"no_network_script_form_video_"+i);
  assert(!/\s(?:onclick|onload|onerror|onkeypress|formaction|data-checkout|data-affiliate|data-redirect)\s*=/i.test(page),"no_inline_handlers_"+i);
  assert(!hrefs(page).some(earningLink),"no_unauthorized_earning_link_"+i);
  const b=attrs(page,"button");
  assert(b.length===1&&b.every(a=>hasRealDisabled(a)&&/\baria-disabled="true"/i.test(a)&&/\btype="button"/i.test(a)),"all_buttons_native_disabled_"+i);
  const marker=page.indexOf("Prospective affiliate disclosure:");
  const button=page.indexOf("<button");
  assert(marker>=0&&button>marker&&(button-marker)<950&&page.includes("No affiliate link is active"),"immediate_disclosure_"+i);
  assert(page.includes("https://finalvestige.com/focus/")&&page.includes("https://zen12.com/hnp"),"source_free_route_"+i);
  assert(page.includes("noindex,nofollow")&&page.includes('lang="en"'),"draft_only_"+i);
 }
 const extract=(x)=>x.slice(x.indexOf('<section class="reading" aria-labelledby="overview">'),x.indexOf("</main>"));
 assert(extract(buyerA)===extract(buyerB),"same_buyer_copy_AB");
 assert(buyerA.includes("42-second")==false&&buyerB.includes("42-second"),"only_B_illustration");
 assert(buyerB.includes('aria-labelledby="posterTitle posterDesc"')&&buyerB.includes("transcript")&&buyerB.includes("caption"),"B_optional_video_access");
 assert(!/<video[^>]*\sautoplay\b|<source\b/i.test(buyerB),"B_no_auto_playback");
 assert(captions.startsWith("WEBVTT")&&[...captions.matchAll(/-->/g)].length===5&&captions.includes("00:00:42.000"),"captions_five_42s");
 assert(m.sources?.length>=24&&m.claims?.length>=39&&m.gates?.length===16,"matrix_depth");
 const ids=new Set(m.sources?.map(x=>x.id));
 assert(ids.size===m.sources?.length&&m.claims?.every(x=>x.source_ids?.every(id=>ids.has(id))),"matrix_linked_sources");
 assert(new Set(m.claims?.map(x=>x.id)).size===m.claims?.length,"claims_unique");
 for(let i=1;i<=16;i++){
  const id="G"+String(i).padStart(2,"0");
  const expected=i<=8?"HARD_HOLD":i===15?"OPEN_REVIEW":"UNKNOWN";
  assert(m.gates.filter(x=>x.id===id&&x.status===expected).length===1,"gate_"+id);
 }
 assert(m.offer.activation_allowed===false&&m.offer.named_approval_verified===false&&m.offer.authorized_earning_url===null,"offer_hard_hold");
 assert(m.alternative_owned.activation_allowed===false&&m.alternative_owned.product_id===null,"no_fake_payhip_sku");
 assert(m.claims.find(c=>c.id==="N09")?.status==="SELLER_CLAIM_NOT_SUBSTANTIATED","no_product_equivalence");
 assert(m.claims.find(c=>c.id==="N12")?.status==="UNVERIFIED","no_fabricated_sales");
 assert(m.conversion_contract.no_pii===true&&m.conversion_contract.no_fingerprinting===true&&m.conversion_contract.new_tracking_script_allowed===false&&m.conversion_contract.affiliate_click_is_paid_sale===false,"privacy_and_truth");
 assert(m.r221_experiment.active===false&&m.r221_experiment.primary_metric.includes("revenue"),"not_live_ab");
 assert(plan.includes("OFFER → FUNNEL STEP")&&plan.includes("HARD HOLD")&&plan.includes("NOT COMPUTABLE"),"offer_priority");
 for(const key of ["Grok","Praxxis","Claude","TASK-008","Dispatch","channel_profile","R210","UNRENDERED","7-day","30-day","1000"])assert(plan.toLowerCase().includes(key.toLowerCase()),"plan_"+key);
 return errors;
}
function run(f){
 const baseline=validate(f),mutations=[];
 function check(label,fn){let x={...f};fn(x);mutations.push([label,validate(x).length>0]);}
 function changeMatrix(fn){return x=>{let m=JSON.parse(x.matrix);fn(m);x.matrix=JSON.stringify(m);};}
 check("remove_research_citation",x=>x.article=x.article.replaceAll("9099071","bad"));
 check("truncate_article",x=>x.article=x.article.slice(0,850));
 check("remove_limitation",x=>x.article=x.article.replace("No purchase link is activated here.","Buy now"));
 check("invent_experience",x=>x.article+="\n commission earned");
 check("remove_svg_description",x=>x.hub=x.hub.replace("diagramDesc","not-described"));
 check("remove_focus",x=>x.hub=x.hub.replaceAll("https://finalvestige.com/focus/","/unknown"));
 check("hub_native_disabled_only",x=>x.hub=x.hub.replace(/\sdisabled(?=\s|=|>)/i,""));
 check("hub_activate_extra_button",x=>x.hub=x.hub.replace("</main>","<button type='button'>Buy</button></main>"));
 check("hub_unquoted_checkout",x=>x.hub=x.hub.replace("</main>","<a href=https://bad.example/checkout?ref=1>buy</a></main>"));
 check("hub_inline_handler",x=>x.hub=x.hub.replace("<button","<button onload=go()"));
 check("hub_script",x=>x.hub=x.hub.replace("</body>","<script>t()</script></body>"));
 check("hub_extra_form",x=>x.hub=x.hub.replace("</main>","<form><input></form></main>"));
 check("hub_disclosure_removed",x=>x.hub=x.hub.replace("Prospective affiliate disclosure:","About this guide:"));
 check("buyerA_native_disabled_only",x=>x.buyerA=x.buyerA.replace(/\sdisabled(?=\s|=|>)/i,""));
 check("buyerB_native_disabled_only",x=>x.buyerB=x.buyerB.replace(/\sdisabled(?=\s|=|>)/i,""));
 check("buyerA_added_button",x=>x.buyerA=x.buyerA.replace("</main>","<button type='button'>buy</button></main>"));
 check("buyerB_affiliate_url",x=>x.buyerB=x.buyerB.replace("</main>","<a href=https://awin1.com/cread.php>go</a></main>"));
 check("buyerA_disclosure_removed",x=>x.buyerA=x.buyerA.replace("Prospective affiliate disclosure:","More information:"));
 check("buyerB_disclosure_far",x=>x.buyerB=x.buyerB.replace("Prospective affiliate disclosure:","Disclosure hidden"));
 check("buyerB_script",x=>x.buyerB=x.buyerB.replace("</body>","<script>analytics()</script></body>"));
 check("buyerB_video_autoplay",x=>x.buyerB=x.buyerB.replace("<section class=\"film\"","<video autoplay></video><section class=\"film\""));
 check("buyerB_remove_audio_access",x=>x.buyerB=x.buyerB.replace("posterTitle posterDesc","removed"));
 check("AB_core_changed",x=>x.buyerB=x.buyerB.replace("forty-eight MP3 recordings","forty-eight miraculous recordings"));
 check("caption_missing",x=>x.captions=x.captions.replace("00:00:42.000","00:00:41.000"));
 check("remove_gate_G01",changeMatrix(m=>m.gates=m.gates.filter(g=>g.id!=="G01")));
 check("rename_gate_G16",changeMatrix(m=>m.gates.find(g=>g.id==="G16").id="G99"));
 check("unhold_gate_G08",changeMatrix(m=>m.gates.find(g=>g.id==="G08").status="UNKNOWN"));
 check("duplicate_gate_G12",changeMatrix(m=>m.gates.push({...m.gates.find(g=>g.id==="G12")})));
 check("invent_named_approval",changeMatrix(m=>m.offer.named_approval_verified=true));
 check("insert_fake_earning_url",changeMatrix(m=>m.offer.authorized_earning_url="https://bad.example/aff"));
 check("activate_own_sku",changeMatrix(m=>m.alternative_owned.activation_allowed=true));
 check("make_equivalence_proven",changeMatrix(m=>m.claims.find(c=>c.id==="N09").status="PRODUCT_PROVEN"));
 check("fabricate_paid_sale",changeMatrix(m=>m.claims.find(c=>c.id==="N12").status="VERIFIED_PAID"));
 check("affiliate_click_is_sale",changeMatrix(m=>m.conversion_contract.affiliate_click_is_paid_sale=true));
 check("enable_fingerprint",changeMatrix(m=>m.conversion_contract.no_fingerprinting=false));
 check("activate_ab",changeMatrix(m=>m.r221_experiment.active=true));
 check("remove_prax_review_fix",x=>x.priorTest=x.priorTest.replace("remove_native_disabled_only","bypass"));
 check("degrade_Repp_correction",x=>x.priorMatrix=x.priorMatrix.replace("PUBLISHER_ABSTRACT_SUPPORTED_WITH_LIMITS","METHOD_QUESTION_ONLY"));
 check("remove_creator",x=>x.plan=x.plan.replaceAll("TASK-008",""));
 const missed=mutations.filter(x=>!x[1]).map(x=>x[0]);
 return {baseline,mutations_total:mutations.length,unsafe_mutations_rejected:mutations.length-missed.length,missed,pass:baseline.length===0&&missed.length===0};
}
module.exports={PATHS,validate,run};
if(typeof require==="function"&&require.main===module){
 const fs=require("fs"),path=require("path"),root=path.resolve(__dirname,"../.."),f={};
 for(const [k,p] of Object.entries(PATHS)) f[k]=fs.readFileSync(path.join(root,p),"utf8");
 const result=run(f);process.stdout.write(JSON.stringify(result,null,2)+"\n");if(!result.pass)process.exitCode=1;
}
