// FV Mind & Perception R220 — reproducible source-only validator, not a production release approval.
// Run from a complete checkout: node mind/r220/test_mind_r220.cjs
"use strict";
const PATHS={
 article:"mind/r220/the-syllable-that-wasnt-there-PHONEMIC-RESTORATION-UNPUBLISHED.md",
 hub:"mind/r220/mind-archive-phonemic-restoration-UNPUBLISHED.html",
 matrix:"mind/r220/source-claim-offer-release-matrix.json",
 plan:"mind/r220/OFFER-FUNNEL-BLOCKER-CHANGE-EVIDENCE-OWNER.md",
 priorArticle:"mind/r219/the-sound-that-never-arrived-INATTENTIONAL-DEAFNESS-UNPUBLISHED.md",
 priorMatrix:"mind/r219/DEAFNESS-ZEN12-CLAIMS-AUTHORIZATION-REVENUE-MATRIX.json",
 priorTest:"mind/r219/test_mind_r219.cjs"
};
function tags(s,name){return [...s.matchAll(new RegExp("<"+name+"\\b([^>]*)>","gi"))].map(x=>x[1]);}
function hrefs(s){return [...s.matchAll(/<(?:a|area)\b([^>]*)>/gi)].map(z=>{
 const m=z[1].match(/\bhref\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'=<>]+))/i);
 return m?(m[1]??m[2]??m[3]):null;
}).filter(Boolean);}
function isCommerce(h){return /(?:awin1\.com|(?:^|[\/?&])(?:checkout|order|cart)(?:[\/?&=#]|$)|[?&](?:aff|affiliate|ref|subid|clickref)=)/i.test(h);}
function validate(f){
 const errors=[],req=(v,k)=>{if(!v)errors.push(k);};
 for(const k of Object.keys(PATHS))req(typeof f[k]==="string"&&f[k].length>300,"missing_"+k);
 if(errors.length)return errors;
 const {article,hub,plan,priorArticle,priorTest}=f;
 let m,p;try{m=JSON.parse(f.matrix);p=JSON.parse(f.priorMatrix);}catch(e){return ["invalid_JSON"];}
 req(article.split(/\s+/).length>=2900,"research_depth");
 for(const s of ["10.1126/science.167.3917.392","BF03212667","6457110","BF03205070","38458383","2026-11-08"])
   req(article.includes(s),"research_source_"+s);
 for(const s of ["Abstract-level review","not a phonemic-restoration test","NOT","twelve minutes"]){
  // The manuscript must distinguish source limits and the free analogy from an experiment.
  if(s!=="NOT")req(article.toLowerCase().includes(s.toLowerCase()),"research_limit_"+s);
 }
 req(!/awin1\.com|<script\b|[?&]affiliate=|commission earned/i.test(article),"no_affiliate_investigation");
 req(article.includes("https://finalvestige.com/focus/")&&article.includes("puysegurs-animal-magnetism-files"),"historical_focus_bridge");
 req(article.includes("No purchase link is activated here."),"article_no_commerce");
 req(hub.includes("<!doctype html>")&&hub.includes('lang="en"')&&hub.includes("noindex,nofollow"),"unpublished_markup");
 req(hub.includes('role="img"')&&hub.includes('aria-labelledby="waveTitle waveDesc"')&&hub.includes("<desc"),"svg_alt");
 req(hub.includes("focus-visible")&&hub.includes("prefers-reduced-motion")&&hub.includes("@media(max-width:"),"accessibility_css");
 req(hub.includes('href="#content"')&&hub.includes('id="content"'),"skip_link");
 req(!/<form\b|<script\b|<iframe\b|<video\b/i.test(hub),"no_scripts_forms_video");
 req(!/\son[a-z]+\s*=|\sformaction\s*=|\sdata-(?:checkout|affiliate|redirect|purchase)\s*=/i.test(hub),"no_handlers");
 req(!hrefs(hub).some(isCommerce),"no_checkout_links");
 const buttons=tags(hub,"button");req(buttons.length===1&&buttons.every(s=>/\bdisabled(?:\s|=|$)/.test(s)&&/\baria-disabled="true"/.test(s)),"all_buttons_inactive");
 req(hub.includes("Prospective affiliate disclosure:")&&hub.includes("No affiliate link is active."),"adjacent_disclosure");
 req(hub.includes("https://finalvestige.com/focus/")&&hub.includes("four-stream")===false,"reuse_focus");
 req(hub.includes("Mind hub proposal remains PR #172"),"canonical_hub");
 req(m.sources?.length>=19&&m.claims?.length>=25&&m.gates?.length===16,"matrix_depth");
 const sid=new Set(m.sources?.map(x=>x.id));
 req(sid.size===m.sources?.length&&m.claims?.every(x=>x.source_ids?.every(id=>sid.has(id))),"source_integrity");
 req(m.gates?.length===new Set(m.gates?.map(x=>x.id)).size,"gates_unique");
 for(let i=1;i<=16;i++){
   const id="G"+String(i).padStart(2,"0"),expected=i<=8?"HARD_HOLD":i===15?"OPEN_REVIEW":"UNKNOWN";
   req(m.gates?.filter(g=>g.id===id&&g.status===expected).length===1,"gate_"+id);
 }
 req(m.offer?.activation_allowed===false&&m.offer?.authorized_earning_url===null&&m.offer?.named_approval_verified===false,"offer_hard_hold");
 req(m.alternative_owned?.activation_allowed===false&&m.alternative_owned?.product_id===null,"no_invented_owned_sku");
 req(m.claims?.find(x=>x.id==="C14")?.status==="SELLER_CLAIM_NOT_SUBSTANTIATED","no_meditation_equivalence");
 req(m.claims?.find(x=>x.id==="C25")?.status==="INVALID_INFERENCE","no_click_as_sale");
 req(m.conversion_contract?.no_pii===true&&m.conversion_contract?.no_fingerprinting===true&&m.conversion_contract?.new_tracking_script_allowed===false,"privacy");
 req(m.conversion_contract?.affiliate_click_is_paid_sale===false&&m.conversion_contract?.data_status==="NOT_COMPUTABLE_without_merchant_and_human_denom","commercial_truth");
 req(plan.includes("OFFER → FUNNEL STEP")&&plan.includes("HARD HOLD")&&plan.includes("NOT COMPUTABLE"),"plan_priorities");
 req(plan.includes("TASK-008")&&plan.includes("Grok")&&plan.includes("Praxxis")&&plan.includes("Claude")&&plan.includes("Dispatch"),"ownership");
 req(plan.includes("7-")&&plan.includes("30-day")&&plan.includes("1000"),"revenue_cohorts");
 req(plan.includes("R210")&&plan.includes("42s")&&plan.includes("UNRENDERED")===false,"AB_freeze"); // 'not rendered' wording elsewhere
 req(priorArticle.includes("Katharine Molloy")&&priorArticle.includes("13 MEG participants")&&priorArticle.includes("10 behavioral participants")&&priorArticle.includes("19 of 24 participants"),"R219_science_correction");
 req(priorArticle.includes("complete scene")&&priorArticle.includes("different experimental manipulations"),"R219_design_correction");
 req(p.claims.find(x=>x.id==="C05")?.limits.includes("NOT isolated"),"R219_matrix_correction");
 req(priorTest.includes("add_unquoted_checkout_anchor")&&priorTest.includes("rename_G12")&&priorTest.includes("i<=16"),"R219_validator_correction");
 return errors;
}
function run(f){
 const baseline=validate(f),tests=[];
 function mutate(name,fn){let x={...f};fn(x);tests.push([name,validate(x).length>0]);}
 const edit=(x,fn,key="matrix")=>{const o=JSON.parse(x[key]);fn(o);x[key]=JSON.stringify(o);};
 mutate("remove_article_source",x=>x.article=x.article.replaceAll("6457110","removed"));
 mutate("shrink_article",x=>x.article=x.article.slice(0,800));
 mutate("remove_free_exercise_limit",x=>x.article=x.article.replace("not a phonemic-restoration test","actual phonemic test"));
 mutate("make_experience_claim",x=>x.article+="\n commission earned");
 mutate("activate_button",x=>x.hub=x.hub.replace(' disabled aria-disabled="true"',""));
 mutate("append_active_button",x=>x.hub=x.hub.replace("</main>","<button>Pay</button></main>"));
 mutate("unquoted_checkout_link",x=>x.hub=x.hub.replace("</main>","<a href=https://bad.invalid/checkout?ref=yes>Pay</a></main>"));
 mutate("inline_handler",x=>x.hub=x.hub.replace("<button","<button onclick='alert(1)'"));
 mutate("js_tracking",x=>x.hub=x.hub.replace("</body>","<script>go()</script></body>"));
 mutate("extra_signup",x=>x.hub=x.hub.replace("</main>","<form><input type='email'></form></main>"));
 mutate("remove_disclosure",x=>x.hub=x.hub.replace("Prospective affiliate disclosure:","Disclosure"));
 mutate("remove_svg_alt",x=>x.hub=x.hub.replace('aria-labelledby="waveTitle waveDesc"',""));
 mutate("remove_safety_gate_G01",x=>edit(x,o=>o.gates=o.gates.filter(g=>g.id!=="G01")));
 mutate("rename_safety_gate_G12",x=>edit(x,o=>o.gates.find(g=>g.id==="G12").id="G99"));
 mutate("unhold_G16",x=>edit(x,o=>o.gates.find(g=>g.id==="G16").status="HARD_HOLD"));
 mutate("invent_approval",x=>edit(x,o=>o.offer.named_approval_verified=true));
 mutate("turn_on_offer",x=>edit(x,o=>o.offer.activation_allowed=true));
 mutate("fabricate_url",x=>edit(x,o=>o.offer.authorized_earning_url="https://bad.invalid/aff"));
 mutate("invent_owned_sku",x=>edit(x,o=>o.alternative_owned.product_id="fake"));
 mutate("publish_meditation_equivalence",x=>edit(x,o=>o.claims.find(c=>c.id==="C14").status="PRODUCT_PROVEN"));
 mutate("equate_click_sale",x=>edit(x,o=>o.conversion_contract.affiliate_click_is_paid_sale=true));
 mutate("enable_fingerprinting",x=>edit(x,o=>o.conversion_contract.no_fingerprinting=false));
 mutate("remove_campaign_proof",x=>x.plan=x.plan.replace("TASK-008","UNKNOWN"));
 mutate("remove_QA_repair",x=>x.priorTest=x.priorTest.replace("add_unquoted_checkout_anchor","removed"));
 mutate("remove_R219_correct_name",x=>x.priorArticle=x.priorArticle.replace("Katharine Molloy","Katie Molloy"));
 return {baseline,detected:tests.filter(z=>z[1]).length,total:tests.length,missing:tests.filter(z=>!z[1]).map(z=>z[0]),passed:baseline.length===0&&tests.every(z=>z[1])};
}
module.exports={PATHS,validate,run};
if(typeof require==="function"&&require.main===module){
 const fs=require("fs"),path=require("path"),root=path.resolve(__dirname,"../.."),f={};
 for(const [k,p] of Object.entries(PATHS))f[k]=fs.readFileSync(path.join(root,p),"utf8");
 const result=run(f);console.log(JSON.stringify(result,null,2));if(!result.passed)process.exitCode=1;
}
