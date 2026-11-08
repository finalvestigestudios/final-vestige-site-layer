// FV Mind R218 exact-source baseline and unsafe-mutation tests.
// Run in complete checkout: node mind/r218/test_mind_r218.cjs
// Source test only: not live browser, CMS, consent, payment or merchant authorization.
"use strict";
const FILES={
 article:"mind/r218/the-hand-that-wasnt-yours-RUBBER-HAND-UNPUBLISHED.md",
 a:"mind/r218/zen12-R218-A-TEXT-UNPUBLISHED.html",
 b:"mind/r218/zen12-R218-B-OPTIONAL-42S-UNRENDERED.html",
 vtt:"mind/r218/zen12-42s-OPTIONAL-CONCEPT.vtt",
 hub:"mind/r218/mind-archive-four-stream-WP-SOURCE-UNPUBLISHED.html",
 matrix:"mind/r218/BODY-OWNERSHIP-ZEN12-CLAIM-PROOF-GATES.json",
 plan:"mind/r218/OFFER-FIRST-PAID-REVENUE-EXPERIMENT-AND-GROK-HANDOFF.md",
 inheritedArticle:"mind/r217/the-face-they-never-picked-CHOICE-BLINDNESS-UNPUBLISHED.md",
 inheritedMatrix:"mind/r217/CHOICE-ZEN12-SOURCE-CLAIM-GATES.json"
};
function validate(f){
 const e=[],c=(v,id)=>{if(!v)e.push(id)};
 for(const k of Object.keys(FILES))c(typeof f[k]==="string"&&f[k].length>100,"file_"+k);
 if(e.length)return e;
 let m,im;try{m=JSON.parse(f.matrix);im=JSON.parse(f.inheritedMatrix)}catch(x){return ["json_parse"]};
 const {article,a,b,vtt,hub,plan,inheritedArticle}=f;
 c(article.trim().split(/\s+/).length>2500&&article.includes("UNPUBLISHED / SOURCE REVIEW"),"deep_article");
 for(const link of ["https://doi.org/10.1038/35784","https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0021659","https://online.ucpress.edu/collabra/article/6/1/22/113067/","https://www.psy.ox.ac.uk/publication/19214"])
  c(article.includes(link),"article_source_"+link.slice(-12));
 c(article.includes("demand characteristics")&&article.includes("as if it were a one-to-one ownership meter")&&article.includes("None of the experiments discussed here tested Zen12 Premium"),"science_limits");
 c(article.includes("https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/"),"history_bridge");
 c(!/awin1\.com|<script/i.test(article),"no_affiliate_research");
 const main=s=>(s.match(/<main class="wrap" id="content">[\s\S]*?<\/main>/)||[])[0];
 c(main(a)&&main(a)===main(b),"AB_same_buyer_copy");
 for(const [id,s] of [["A",a],["B",b],["HUB",hub]]){
  c(s.includes("noindex,nofollow")&&s.includes('lang="en"'),"unpublished_"+id);
  c(s.includes("focus-visible")&&s.includes("prefers-reduced-motion")&&s.includes("@media(max-width:"),"accessible_responsive_"+id);
  c(!/<script\b|<iframe\b|<form\b|<video\b|\sautoplay(?:\s|=|>)/i.test(s),"no_scripts_forms_or_video_"+id);
  const ids=[...s.matchAll(/\bid=["']([^"']+)["']/g)].map(x=>x[1]);
  c(ids.length===new Set(ids).size,"unique_html_ids_"+id);
  c(/<button[^>]*disabled[^>]*>/.test(s)&&s.includes('aria-disabled="true"'),"disabled_cta_"+id);
  c(s.includes("Prospective affiliate disclosure")&&s.includes("No affiliate link is active"),"adjacent_affiliate_disclosure_"+id);
  c(!/awin1\.com|gtag\(|approved affiliate link/i.test(s),"no_tracking_or_approval_"+id);
 }
 c(!a.includes("<svg")&&b.includes("<svg")&&b.includes("NOT RENDERED"),"optional_media_only_B");
 const cues=[...vtt.matchAll(/(\d\d):(\d\d):(\d\d)\.(\d{3}) --> (\d\d):(\d\d):(\d\d)\.(\d{3})/g)];
 const ms=(h,m,s,x)=>(((+h*60)+(+m))*60+(+s))*1000+(+x);
 const times=cues.map(x=>[ms(...x.slice(1,5)),ms(...x.slice(5,9))]);
 c(vtt.startsWith("WEBVTT")&&times.length===5&&times.every((t,i)=>t[1]>t[0]&&t[0]===(i?times[i-1][1]:0))&&times.at(-1)[1]===42000,"caption_continuity");
 c(m.offer?.activation_allowed===false&&m.offer?.affiliate_link===null&&m.offer?.named_approval_verified===false,"affiliate_hold");
 c(m.sources?.length>=18&&m.claims?.length>=24,"proof_depth");
 const src=new Set(m.sources?.map(x=>x.id));c(src.size===m.sources.length&&m.claims.every(x=>x.source_ids?.every(i=>src.has(i))),"references_resolve");
 c(m.claims.find(x=>x.id==="C14")?.status==="SELLER_UNSUBSTANTIATED_OMITTED","no_seller_acceleration");
 c(m.claims.find(x=>x.id==="C25")?.status==="UNSUPPORTED_OMITTED","no_illusion_product_equivalence");
 const ids=m.gates?.map(g=>g.id)||[];c(ids.length===new Set(ids).size,"no_duplicate_gates");
 for(let i=1;i<=8;i++){const id="G"+String(i).padStart(2,"0");c(m.gates.filter(x=>x.id===id&&x.status==="HARD_HOLD").length===1,"required_gate_"+id);}
 c(m.conversion_contract?.no_pii===true&&m.conversion_contract?.existing_instrumentation_only===true,"privacy_gate");
 c(m.conversion_contract?.null_if_no_authoritative_numerator_or_denominator===true,"no_fabricated_revenue");
 const formula="settled_owned_receipts + cleared_affiliate_commissions - refunded_amounts - transaction_fees - chargebacks - attributable_variable_costs";
 c(m.conversion_contract?.realized_net_formula===formula&&plan.includes(formula),"formula_consistency");
 c(plan.includes("NOT COMPUTABLE")&&plan.includes("7-day")&&plan.includes("30-day"),"7_30_cohorts");
 c(plan.includes("TASK-008")&&plan.includes("Praxxis")&&plan.includes("Grok")&&plan.includes("Dispatch")&&plan.includes("R210"),"ownership_handoff");
 c(plan.includes("qualified_human_session_estimate")&&plan.includes("affiliate_commission_cleared")&&plan.includes("focus_confirmed_optin"),"event_definitions");
 c(inheritedArticle.includes("smelled tea")&&inheritedArticle.includes("containers that could be inverted")&&inheritedArticle.includes("retrospective")&&inheritedArticle.includes("p = .93")&&inheritedArticle.includes("2010 general election"),"r217_science_corrections");
 c(im.claims.find(x=>x.id==="C03")?.limits.includes("retrospective")&&im.claims.find(x=>x.id==="C05")?.limits.includes("p=.93"),"r217_claim_corrections");
 return e;
}
function run(f){
 const baseline=validate(f),mutations=[];
 function attempt(id,fn){const x={...f};fn(x);mutations.push({id,detected:validate(x).length>0});}
 const j=(x,fn)=>{const o=JSON.parse(x.matrix);fn(o);x.matrix=JSON.stringify(o)};
 attempt("delete_G01",x=>j(x,o=>o.gates=o.gates.filter(g=>g.id!=="G01")));
 attempt("delete_G08",x=>j(x,o=>o.gates=o.gates.filter(g=>g.id!=="G08")));
 attempt("duplicate_G03",x=>j(x,o=>o.gates.push({...o.gates[2]})));
 attempt("rename_G02",x=>j(x,o=>o.gates.find(g=>g.id==="G02").id="G99"));
 attempt("unhold_G04",x=>j(x,o=>o.gates.find(g=>g.id==="G04").status="OPEN"));
 attempt("activate_affiliate",x=>j(x,o=>o.offer.activation_allowed=true));
 attempt("fake_earning_link",x=>j(x,o=>o.offer.affiliate_link="https://fake.example/aff=1"));
 attempt("fake_publisher",x=>j(x,o=>o.offer.named_approval_verified=true));
 attempt("missing_source",x=>j(x,o=>o.sources=o.sources.filter(s=>s.id!=="S01")));
 attempt("seller_claim_as_proof",x=>j(x,o=>o.claims.find(c=>c.id==="C14").status="SUPPORTED"));
 attempt("illusion_as_product_proof",x=>j(x,o=>o.claims.find(c=>c.id==="C25").status="SUPPORTED"));
 attempt("count_clicks_as_revenue",x=>j(x,o=>o.conversion_contract.realized_net_formula="affiliate_clicks"));
 attempt("allow_PII",x=>j(x,o=>o.conversion_contract.no_pii=false));
 attempt("new_tracking_script_allowed",x=>j(x,o=>o.conversion_contract.existing_instrumentation_only=false));
 attempt("remove_primary_citation",x=>x.article=x.article.replace("https://doi.org/10.1038/35784",""));
 attempt("remove_demand_challenge",x=>x.article=x.article.replace("demand characteristics",""));
 attempt("shorten_research",x=>x.article=x.article.slice(0,1200));
 attempt("add_affiliate_to_research",x=>x.article+="\n<a href='https://awin1.com'>buy</a>");
 attempt("enable_A",x=>x.a=x.a.replace('type="button" disabled','type="button"'));
 attempt("enable_B",x=>x.b=x.b.replace('type="button" disabled','type="button"'));
 attempt("enable_hub",x=>x.hub=x.hub.replace('disabled type="button"','type="button"'));
 attempt("remove_A_disclosure",x=>x.a=x.a.replace("Prospective affiliate disclosure","Product information"));
 attempt("remove_B_disclosure",x=>x.b=x.b.replace("Prospective affiliate disclosure","Product information"));
 attempt("inject_script",x=>x.b=x.b.replace("</body>","<script src='https://test.invalid/tracker.js'></script></body>"));
 attempt("inject_new_email_form",x=>x.hub=x.hub.replace("</main>","<form><input type='email'></form></main>"));
 attempt("force_autoplay",x=>x.b=x.b.replace("</main>","<video autoplay></video></main>"));
 attempt("AB_copy_not_identical",x=>x.b=x.b.replace("forty-eight MP3 recordings","forty-seven MP3 recordings"));
 attempt("break_VTT_end",x=>x.vtt=x.vtt.replace("00:00:42.000","00:00:43.000"));
 attempt("break_VTT_gap",x=>x.vtt=x.vtt.replace("00:00:26.000 --> 00:00:35.000","00:00:27.000 --> 00:00:35.000"));
 attempt("remove_handoff",x=>x.plan=x.plan.replaceAll("TASK-008","unknown"));
 attempt("change_r217_p",x=>x.inheritedArticle=x.inheritedArticle.replace("p = .93","p = .03"));
 attempt("erase_r217_matrix",x=>{const o=JSON.parse(x.inheritedMatrix);o.claims.find(c=>c.id==="C03").limits="No methods";x.inheritedMatrix=JSON.stringify(o)});
 return {baseline,caught:mutations.filter(x=>x.detected).length,total:mutations.length,mutations,pass:baseline.length===0&&mutations.every(x=>x.detected)};
}
module.exports={FILES,validate,run};
if(typeof require==="function"&&require.main===module){
 const fs=require("fs"),path=require("path"),data={},root=path.resolve(__dirname,"../..");
 for(const [key,p] of Object.entries(FILES))data[key]=fs.readFileSync(path.join(root,p),"utf8");
 const outcome=run(data);console.log(JSON.stringify(outcome,null,2));if(!outcome.pass)process.exitCode=1;
}
