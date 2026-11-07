/* Final Vestige Mind R189 - reproducible, SOURCE-ONLY regression suite.
   From actual repo checkout: node mind/r189/test_mind_r189.cjs
   This is NOT a browser/axe/WCAG/CWV, merchant checkout, video, or live test. */
"use strict";
const files={
 article:"the-pendulum-that-answered-a-question-IDEOMOTOR-INVESTIGATION-UNPUBLISHED.md",
 matrix:"verified-claims-merchant-permissions-revenue-gates.json",
 plan:"ONE-VERIFIED-OFFER-CREATOR-FIT-AB-AND-NET-REVENUE-ACCEPTANCE.md",
 hub:"mind-archive-four-stream-WORDPRESS-PREVIEW-UNPUBLISHED.html",
 A:"../r188/zen12-variant-A-independent-text-UNPUBLISHED.html",
 B:"../r188/zen12-variant-B-optional-42s-storyboard-UNPUBLISHED.html",
 priorArticle:"../r188/repetition-made-it-feel-true-INVESTIGATION-UNPUBLISHED.md",
 priorTest:"../r188/test_mind_r188.cjs"
};
function nativeDisabled(html){
 const buttons=Array.from((html||"").matchAll(/<button\b([^>]*)>Purchase option unavailable[^<]*<\/button>/gi));
 return buttons.length===1&&/(?:^|\s)disabled(?=\s|=|$)/i.test(buttons[0][1]);
}
function verify(f){
 const failed=[],labels=[];const ck=(name,pass)=>{labels.push(name);if(!pass)failed.push(name)};
 for(const [key]of Object.entries(files))ck("exists "+key,typeof f[key]==="string"&&f[key].length>800);
 let m={};try{m=JSON.parse(f.matrix||"")}catch(e){}
 ck("matrix 20 URLs",m.source_links?.length>=20&&m.source_links.every(x=>/^https:\/\//.test(x.url)));
 ck("claim decisions >=22",m.claim_decisions?.length>=22);
 ck("release gates >=15",m.release_gates?.length>=15);
 ck("named FV acceptance null",m.named_fv_publisher_approval===null);
 ck("channels null",m.permitted_promotional_channels===null);
 ck("authorized earning URL null",m.affiliate_earning_url===null);
 ck("affiliate off",m.affiliate_activation===false);
 ck("Payhip Mind unverified",m.verified_owned_payhip_mind_sku===null);
 ck("paid purchases null",m.merchant_confirmed_purchases===null);
 ck("affiliate sales null",m.affiliate_network_confirmed_sales===null);
 ck("commission null",m.paid_affiliate_commissions===null);
 ck("net revenue null",m.realized_net_revenue===null);
 ck("qualified humans null",m.qualified_human_sessions===null);
 ck("product result not transferred",m.claim_decisions?.some(x=>x.id==="zen_equivalence"&&x.decision.startsWith("WITHHELD")));
 ck("exact seller claims separate",m.claim_decisions?.some(x=>x.id==="total_focus"&&x.decision.startsWith("WITHHELD")));
 ck("article >=2000 words",(f.article||"").trim().split(/\s+/).length>=2000);
 ck("article title scope accurate",f.article?.startsWith("# The Pendulum That Answered a Question: Who Moved It?"));
 ck("original pendulum source",f.article?.includes("10.1080/00221309.1976.9710871"));
 ck("2012 Ouija original",f.article?.includes("pubmed.ncbi.nlm.nih.gov/22377138"));
 ck("2018 online versus 2019 print",f.article?.includes("2018")&&f.article.includes("2019"));
 ck("hypnosis experiment source",f.article?.includes("PMC3804629"));
 ck("historic published Puységur route",f.article?.includes("finalvestige.com/free-resources/puysegurs-animal-magnetism-files/"));
 ck("correct Mesmerism canonical",f.article?.includes("finalvestige.com/2026/11/02/mesmerism/")&&!f.article.includes("mesmerism-franklins-1784-commission/"));
 ck("no investigation affiliate recommendation",f.article?.includes("There is no affiliate recommendation or compensated product link"));
 ck("prior headline precision",f.priorArticle?.startsWith("# The Sentence That Felt Truer the Second Time"));
 ck("poster describes two wave paths",f.B?.includes("two wave paths")&&!f.B.includes("three sound waves entering a listening room"));
 ck("R188 test uses native disabled attribute",f.priorTest?.includes("both native buttons enabled")&&f.priorTest.includes("\\sdisabled"));
 for(const key of ["hub","A","B"]){
   const s=f[key]||"";
   ck(key+" no JS",!/<script\b/i.test(s));
   ck(key+" no form",!/<form\b|<input\b/i.test(s));
   ck(key+" no iframe",!/<iframe\b/i.test(s));
   ck(key+" no autoplay",!/<video\b|<audio\b|<iframe\b[^>]*autoplay/i.test(s));
   ck(key+" no earning URLs",!/awin1\.com|clickbank|hop\.click|aff_id=|affiliate_id=/i.test(s));
   ck(key+" draft noindex",/noindex,nofollow/i.test(s));
 }
 ck("A disabled by native boolean attr",nativeDisabled(f.A));
 ck("B disabled by native boolean attr",nativeDisabled(f.B));
 ck("A proximate FTC disclosure",f.A?.includes("Affiliate disclosure (prospective)")&&f.A.indexOf("Purchase option unavailable")-f.A.indexOf("Affiliate disclosure (prospective)")<900);
 ck("B proximate FTC disclosure",f.B?.includes("Affiliate disclosure (prospective)")&&f.B.indexOf("Purchase option unavailable")-f.B.indexOf("Affiliate disclosure (prospective)")<900);
 const section=(f.B||"").match(/<section id="optional-film"[\s\S]*?<\/section>/)?.[0]||"";
 ck("film is optional poster and timed transcript",section.includes("00:35–00:42")&&section.includes("<details><summary>")&&section.includes("no playable asset"));
 ck("film no player or remote asset",!/<video\b|<audio\b|\.mp4/i.test(section));
 ck("A B parity except film",!!section&&f.B.replace(section,"")===f.A);
 ck("archive four streams",["Perception & attention","History of suggestion","Practice & reflection","Tools under review"].every(x=>f.hub?.includes(x)));
 ck("archive new unpublished featured investigation",f.hub?.includes("The Pendulum That Answered a Question")&&f.hub.includes("not yet a public WordPress article"));
 ck("single free Focus route",f.hub?.includes("https://finalvestige.com/focus/")&&!/<form/i.test(f.hub));
 ck("plan 3 creator intents",["The pendulum moved","12 minutes of sound","What disappeared"].every(x=>f.plan?.includes(x)));
 ck("Grok publisher only",f.plan?.includes("Grok independently produces/posts/distributes")&&f.plan.includes("Praxxis independently researches"));
 ck("accounting is paid-outcome based",f.plan?.includes("affiliate_network_confirmed_sale")&&f.plan.includes("qualified_human_sessions"));
 ck("net KPI not magically zero",f.plan?.includes("NOT COMPUTABLE")&&f.plan.includes("refunds")&&f.plan.includes("fees"));
 ck("no added SaaS/tracker",f.plan?.includes("no new scripts, pixels, SaaS"));
 return {passed:labels.length-failed.length,total:labels.length,failures:failed};
}
const mutations=[
 ["both purchase buttons enabled",a=>{a.A=a.A.replace("disabled aria-disabled","aria-disabled");a.B=a.B.replace("disabled aria-disabled","aria-disabled")}],
 ["A purchase button enabled",a=>{a.A=a.A.replace("disabled aria-disabled","aria-disabled")}],
 ["B purchase button enabled",a=>{a.B=a.B.replace("disabled aria-disabled","aria-disabled")}],
 ["A class disabled decoy",a=>{a.A=a.A.replace("disabled aria-disabled",'class="disabled" aria-disabled')}],
 ["B aria disabled decoy",a=>{a.B=a.B.replace("disabled aria-disabled",'aria-disabled="true"')}],
 ["no merchant approval",a=>{a.matrix=a.matrix.replace('"named_fv_publisher_approval": null','"named_fv_publisher_approval": "approved"')}],
 ["link invented",a=>{a.matrix=a.matrix.replace('"affiliate_earning_url": null','"affiliate_earning_url": "https://unknown.example"')}],
 ["activation invented",a=>{a.matrix=a.matrix.replace('"affiliate_activation": false','"affiliate_activation": true')}],
 ["sales invented",a=>{a.matrix=a.matrix.replace('"affiliate_network_confirmed_sales": null','"affiliate_network_confirmed_sales": 9')}],
 ["revenue invented",a=>{a.matrix=a.matrix.replace('"realized_net_revenue": null','"realized_net_revenue": 9000')}],
 ["owned product invented",a=>{a.matrix=a.matrix.replace('"verified_owned_payhip_mind_sku": null','"verified_owned_payhip_mind_sku": "fake"')}],
 ["audio evidence transferred",a=>{a.matrix=a.matrix.replace("WITHHELD_NO_PRODUCT_SPECIFIC_EVIDENCE","CLAIM_PROVEN")}],
 ["primary study removed",a=>{a.article=a.article.split("pubmed.ncbi.nlm.nih.gov/22377138").join("not-a-source.example.invalid")}],
 ["word count collapse",a=>{a.article=a.article.slice(0,650)}],
 ["history route broken",a=>{a.article=a.article.replace("finalvestige.com/2026/11/02/mesmerism/","finalvestige.com/2026/11/02/mesmerism-franklins-1784-commission/")}],
 ["new signup form",a=>{a.hub+="<form><input></form>"}],
 ["spy script",a=>{a.A+="<script src='https://spy.example'></script>"}],
 ["tracker injected",a=>{a.B+="<a href='https://www.awin1.com/fake'>Earn</a>"}],
 ["affiliate disclosure missing",a=>{a.B=a.B.replace("Affiliate disclosure (prospective)","Sales details")}],
 ["A/B content diverges",a=>{a.B=a.B.replace("Four objections worth taking seriously","Five objections worth taking seriously")}],
 ["autoplay injected",a=>{a.B+='<video autoplay></video>'}],
 ["original poster inaccurate",a=>{a.B=a.B.replace("two wave paths","three sound waves entering a listening room")}],
 ["prior title false truth",a=>{a.priorArticle=a.priorArticle.replace("The Sentence That Felt Truer","The Sentence That Became True")}],
 ["claim matrix source URLs removed",a=>{a.matrix=a.matrix.replace("https://doi.org/10.1080/00221309.1976.9710871","no-url")}],
 ["creator ownership seized",a=>{a.plan=a.plan.replace("Grok independently produces/posts/distributes","Mind publishes videos")}]
];
function run(f){
 const baseline=verify(f),checks=mutations.map(([label,mutate])=>{const a={...f};mutate(a);return {label,caught:verify(a).failures.length>0}});
 return {baseline,mutation_total:checks.length,mutation_caught:checks.filter(x=>x.caught).length,escaped:checks.filter(x=>!x.caught).map(x=>x.label)};
}
module.exports={files,nativeDisabled,verify,mutations,run};
if(require.main===module){
 const fs=require("fs"),path=require("path"),f={};
 for(const [key,relative]of Object.entries(files))f[key]=fs.readFileSync(path.join(__dirname,relative),"utf8");
 const r=run(f);console.log(JSON.stringify(r,null,2));
 if(r.baseline.failures.length||r.escaped.length)process.exitCode=1;
}
