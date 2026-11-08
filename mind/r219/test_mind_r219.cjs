// Final Vestige Studios Mind R219: exact-source source and commercial safety regression.
// Native: node mind/r219/test_mind_r219.cjs
// Controlled source-only checks; NOT browser, WP sanitizer, merchant account, film render, or actual paid conversion.
"use strict";
const PATHS={
 article:"mind/r219/the-sound-that-never-arrived-INATTENTIONAL-DEAFNESS-UNPUBLISHED.md",
 hub:"mind/r219/mind-archive-crossmodal-FOUR-STREAM-UNPUBLISHED.html",
 a:"mind/r219/zen12-BUYING-DECISION-A-TEXT-UNPUBLISHED.html",
 b:"mind/r219/zen12-BUYING-DECISION-B-OPTIONAL-42S-UNRENDERED.html",
 vtt:"mind/r219/zen12-evidence-42s-concept.vtt",
 matrix:"mind/r219/DEAFNESS-ZEN12-CLAIMS-AUTHORIZATION-REVENUE-MATRIX.json",
 plan:"mind/r219/CONVERSION-FIRST-OFFER-CREATOR-AB-ACCEPTANCE.md",
 inherited:"mind/r218/test_mind_r218.cjs"
};
const htmlIDs=s=>[...s.matchAll(/\bid=["']([^"']+)["']/g)].map(m=>m[1]);
const core=s=>(s.match(/<main id="content" class="wrap">[\s\S]*?<\/main>/)||[])[0];
const duration=x=>{const a=x.split(":");return (Number(a[0])*3600+Number(a[1])*60+Number(a[2]))*1000};
const strip=s=>s.replace(/<[^>]+>/g," ").replace(/\s+/g," ").trim();
function validate(f){
 const bad=[],check=(p,id)=>{if(!p)bad.push(id)};
 for(const k of Object.keys(PATHS))check(typeof f[k]==="string"&&f[k].length>200,"exists_"+k);
 if(bad.length)return bad;
 let m;try{m=JSON.parse(f.matrix)}catch(e){return ["matrix_JSON"]};
 const {article,hub,a,b,vtt,plan,inherited}=f;
 check(article.split(/\s+/).length>=2400,"article_depth");
 for(const url of ["10.3758/s13414-011-0144-4","10.1016/j.cognition.2012.05.012","1454101","222363"])
  check(article.includes(url),"source_article_"+url);
 check(article.includes("21 of 28")&&article.includes("seven of 28")&&article.includes("79 percent"),"lab_counts");
 check(article.includes("2012")&&article.includes("nineteen seconds")&&article.includes("2015"),"historical_dates");
 check(article.includes("No reasonable reading of the evidence allows that shortcut")&&article.includes("not a diagnostic test"),"claims_and_limits");
 check(!/<script\b|awin1\.com|affiliate link is active/i.test(article),"research_independent");
 check(article.includes("https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/"),"historical_link");
 for(const [id,s] of [["H",hub],["A",a],["B",b]]){
  check(s.includes("noindex,nofollow")&&s.includes('lang="en"'),"unpublished_"+id);
  check(s.includes("focus-visible")&&s.includes("prefers-reduced-motion")&&/@media\(max-width:/.test(s),"a11y_source_"+id);
  check(!/<script\b|<iframe\b|<form\b|<video\b/i.test(s),"no_script_form_autoplay_"+id);
  check(!/\son[a-z]+\s*=|\sformaction\s*=|\sdata-(?:checkout|affiliate|redirect|purchase|href)\s*=/i.test(s),"no_dynamic_handlers_"+id);
  check(!/<(?:a|area)\b[^>]*href\s*=\s*["'][^"']*(?:awin1\.com|checkout|\/order|[?&](?:aff|affiliate|ref|subid|clickref)=)/i.test(s),"no_merchant_checkout_"+id);
  const buttons=[...s.matchAll(/<button\b([^>]*)>/gi)].map(z=>z[1]);
  check(buttons.length>=1&&buttons.every(attrs=>/\sdisabled(?:\s|=|$)/i.test(" "+attrs)&&/\saria-disabled\s*=\s*["']true["']/i.test(" "+attrs)),"every_button_disabled_"+id);
  const ids=htmlIDs(s);check(ids.length===new Set(ids).size,"unique_ids_"+id);
  check(s.includes("Prospective affiliate disclosure")&&s.includes("No affiliate link is active"),"adjacent_disclosure_"+id);
  check(s.includes("https://finalvestige.com/focus/"),"reuse_focus_"+id);
 }
 check(!hub.includes("<form")&&hub.includes("four streams / unpublished source-only WordPress preview"),"hub_source_only");
 check(core(a)&&core(a)===core(b),"AB_identical_core");
 check(!a.includes('class="wrap film"')&&b.includes('class="wrap film"'),"optional_film_only_B");
 check(b.includes("NOT RENDERED")&&b.includes("Full accessible transcript"),"unrendered_and_transcript");
 const cues=[...vtt.matchAll(/(\d\d:\d\d:\d\d\.\d{3}) --> (\d\d:\d\d:\d\d\.\d{3})/g)].map(x=>[duration(x[1]),duration(x[2])]);
 check(vtt.startsWith("WEBVTT")&&cues.length===5&&cues.every((t,i)=>t[1]>t[0]&&t[0]===(i?cues[i-1][1]:0))&&cues.at(-1)[1]===42000,"caption_42s_contiguous");
 const capt=vtt.replace(/^WEBVTT/,"").replace(/\d\d:\d\d:\d\d\.\d{3} --> \d\d:\d\d:\d\d\.\d{3}/g,"").replace(/\s+/g," ").trim();
 const match=b.match(/Full accessible transcript[\s\S]*?<p>([\s\S]*?)<\/p>/);
 check(Boolean(match)&&strip(match[1])===capt,"captions_equal_transcript");
 check(m.sources?.length>=16&&m.claims?.length>=27&&m.gates?.length===16,"matrix_depth");
 const ids=new Set(m.sources?.map(x=>x.id));check(ids.size===m.sources?.length&&m.claims?.every(x=>x.source_ids?.every(q=>ids.has(q))),"source_ids_integrity");
 check(m.offer?.activation_allowed===false&&m.offer?.affiliate_url===null&&m.offer?.named_approval_verified===false,"commerce_hard_hold");
 for(let i=1;i<=8;i++){let id="G"+String(i).padStart(2,"0");check(m.gates?.filter(x=>x.id===id&&x.status==="HARD_HOLD").length===1,"gate_"+id)}
 check(m.gates?.length===new Set(m.gates?.map(x=>x.id)).size,"unique_gates");
 check(m.claims?.find(x=>x.id==="C17")?.status==="SELLER_UNSUBSTANTIATED_OMITTED","no_1hr_claim");
 check(m.claims?.find(x=>x.id==="C19")?.status==="INVALID_INFERENCE_OMITTED","no_experiment_product_claim");
 check(m.conversion_contract?.no_pii===true&&m.conversion_contract?.new_tracking_script_allowed===false&&m.conversion_contract?.affiliate_click_is_paid_sale===false,"privacy_and_paid_distinction");
 const formula="settled_owned_receipts + cleared_affiliate_commissions - refunded_amounts - transaction_fees - chargebacks - attributable_variable_costs";
 check(m.conversion_contract?.realized_net_formula===formula&&plan.includes(formula),"revenue_formula");
 check(plan.includes("NOT COMPUTABLE")&&plan.includes("30-day")&&plan.includes("7-day"),"cohort_missing_data");
 check(plan.includes("TASK-008")&&plan.includes("Grok")&&plan.includes("Praxxis")&&plan.includes("R210")&&plan.includes("Dispatch"),"ownership_coordination");
 check(inherited.includes("all_buttons_natively_disabled")&&inherited.includes("append_enabled_HUB_button")&&inherited.includes("no_inline_handlers_or_commerce_redirects"),"r218_guard_fully_repaired");
 return bad;
}
function run(f){
 const baseline=validate(f),cases=[];
 function mutate(name,fn){const next={...f};fn(next);cases.push({name,detected:validate(next).length>0});}
 const j=(x,fn)=>{let m=JSON.parse(x.matrix);fn(m);x.matrix=JSON.stringify(m)};
 mutate("append_enabled_hub",x=>x.hub=x.hub.replace("</main>","<button type='button'>Pay now</button></main>"));
 mutate("append_enabled_A",x=>x.a=x.a.replace("</main>","<button type='button'>Pay now</button></main>"));
 mutate("append_enabled_B",x=>x.b=x.b.replace("</main>","<button type='button'>Pay now</button></main>"));
 mutate("add_inline_handler",x=>x.a=x.a.replace("<button","<button onclick='alert(1)'"));
 mutate("add_SVG_onload",x=>x.b=x.b.replace("<svg","<svg onload='alert(1)'"));
 mutate("add_formaction",x=>x.hub=x.hub.replace("<button","<button formaction='https://bad.invalid'"));
 mutate("add_redirect_data",x=>x.hub=x.hub.replace("<button","<button data-checkout='https://bad.invalid'"));
 mutate("add_checkout_anchor",x=>x.a=x.a.replace("</main>","<a href='https://bad.invalid/checkout?ref=bad'>Pay</a></main>"));
 mutate("add_script",x=>x.b=x.b.replace("</body>","<script src='https://bad.invalid'></script></body>"));
 mutate("add_email_form",x=>x.hub=x.hub.replace("</main>","<form><input type='email'></form></main>"));
 mutate("break_A_B_core",x=>x.b=x.b.replace("forty-eight downloadable MP3","forty-seven downloadable MP3"));
 mutate("remove_B_transcript",x=>x.b=x.b.replace("Full accessible transcript","No transcript"));
 mutate("change_caption_word",x=>x.vtt=x.vtt.replace("forty-eight","forty-seven"));
 mutate("break_caption_end",x=>x.vtt=x.vtt.replace("00:00:42.000","00:00:43.000"));
 mutate("break_caption_gap",x=>x.vtt=x.vtt.replace("00:00:17.000 -->","00:00:18.000 -->"));
 mutate("remove_merchant_disclosure",x=>x.a=x.a.replace("Prospective affiliate disclosure","Some text"));
 mutate("missing_primary_citation",x=>x.article=x.article.replace("10.3758/s13414-011-0144-4","removed"));
 mutate("reduce_article",x=>x.article=x.article.slice(0,2000));
 mutate("erase_science_limits",x=>x.article=x.article.replace("No reasonable reading of the evidence allows that shortcut","Unsupported shortcut"));
 mutate("enable_affiliate",x=>j(x,o=>o.offer.activation_allowed=true));
 mutate("fake_approval",x=>j(x,o=>o.offer.named_approval_verified=true));
 mutate("add_fabricated_link",x=>j(x,o=>o.offer.affiliate_url="https://bad.invalid"));
 mutate("remove_G01",x=>j(x,o=>o.gates=o.gates.filter(z=>z.id!=="G01")));
 mutate("duplicate_G08",x=>j(x,o=>o.gates.push({...o.gates.find(z=>z.id==="G08")})));
 mutate("unhold_G05",x=>j(x,o=>o.gates.find(z=>z.id==="G05").status="OPEN"));
 mutate("delete_source",x=>j(x,o=>o.sources=o.sources.filter(z=>z.id!=="S01")));
 mutate("endorse_1hr_claim",x=>j(x,o=>o.claims.find(z=>z.id==="C17").status="SUPPORTED"));
 mutate("allow_PII",x=>j(x,o=>o.conversion_contract.no_pii=false));
 mutate("equate_click_with_sale",x=>j(x,o=>o.conversion_contract.affiliate_click_is_paid_sale=true));
 mutate("remove_r218_fix",x=>x.inherited=x.inherited.replace("all_buttons_natively_disabled","disabled_cta"));
 return {baseline,detected:cases.filter(x=>x.detected).length,total:cases.length,missing:cases.filter(x=>!x.detected).map(x=>x.name),passed:baseline.length===0&&cases.every(x=>x.detected)};
}
module.exports={PATHS,validate,run};
if(typeof require==="function"&&require.main===module){
 const fs=require("fs"),path=require("path"),root=path.resolve(__dirname,"../.."),files={};
 for(const [k,p] of Object.entries(PATHS))files[k]=fs.readFileSync(path.join(root,p),"utf8");
 const result=run(files);console.log(JSON.stringify(result,null,2));if(!result.passed)process.exitCode=1;
}
