/* Final Vestige Studios / Mind R263
 * Run: node mind/r263/test_r263.cjs
 * SOURCE INTEGRITY ONLY; deliberately does NOT run browsers, CMS, merchant or affiliate APIs.
 * One explicit baseline and distinct adversarial mutations. Do not treat a pass as approval.
 */
"use strict";
const files={
 article:"THE-HALF-SECOND-YOUR-ATTENTION-COULD-NOT-KEEP-UNPUBLISHED.md",
 hub:"MIND-ATTENTION-ARCHIVE-WP-SOURCE-UNPUBLISHED.html",
 matrix:"CLAIM-PROOF-COMMERCE-HARD-HOLD.json",
 plan:"OFFER-TO-REVENUE-AND-VIDEO-AB-ACCEPTANCE.md"
};
const exactGates=[
"publisher_named_acceptance","issued_affiliate_url","specific_zen12_product_and_destination",
"website_channel_permission","social_channel_permission","email_channel_permission",
"approved_creative_usage_rights","exact_checkout_price_and_currency",
"merchant_tax_shipping_or_extra_charges","product_inclusion_equivalence_promo_vs_standard",
"refund_terms_specific_offer","merchant_refund_actual_process","buyer_facing_compliant_disclosure",
"first_party_event_definition_owner_signoff","merchant_confirmed_paid_commission_feed",
"founder_editorial_QA_release_approval"
];
const exactRelease=["wordpress_write","menu_write","affiliate_activation","subscriber_list_change","social_post","merge","deploy","paid_service"];
const requireIds=["S01","S02","S03","S04","S05","S06","S07","S08","S09","S10","S11","S12","S13","S14","S15","S16","S17","S18"];
function validate(v){
 const failures=[];
 function ok(test,message){if(!test)failures.push(message)}
 let m;
 try{m=JSON.parse(v.matrix);}catch(e){return ["invalid JSON matrix"];}
 const a=v.article,h=v.hub,p=v.plan;
 ok(a.trim().split(/\s+/).length>=2100,"article word count");
 for(const token of ["Raymond","Shapiro","Arnell","lag-one sparing","Olivers","Slagter","three months","Puységur","https://finalvestige.com/focus/","https://pubmed.ncbi.nlm.nih.gov/37205669/","UNPUBLISHED"])
   ok(a.includes(token),"article missing scientific cue "+token);
 for(const url of ["https://pubmed.ncbi.nlm.nih.gov/1500880/","https://pmc.ncbi.nlm.nih.gov/articles/PMC2848898/","https://pubmed.ncbi.nlm.nih.gov/16341546/","https://pubmed.ncbi.nlm.nih.gov/17488185/"])
   ok(a.includes(url),"article missing independent source "+url);
 ok(!/\]\(https?:\/\/(?:www\.)?(?:zen12|inspire3|hypnosislive|payhip)\.com/i.test(a),"active commercial link in investigation");
 ok(!/guarantees? (?:better|health|income|treatment|focus)/i.test(a),"unsupported guarantee in article");
 ok(/<html lang="en">/.test(h),"HTML lang");
 ok(/name="viewport"/.test(h),"mobile viewport");
 ok(/name="robots" content="noindex,nofollow"/.test(h),"noindex missing");
 ok(/<main>/.test(h)&&/<h1>/.test(h),"document landmark");
 for(const id of ["perception","history","practice","tools"]) ok(h.includes('id="'+id+'"'),"missing stream "+id);
 for(const url of ["https://finalvestige.com/focus/","https://finalvestige.com/2026/11/02/change-blindness/","https://finalvestige.com/2026/11/02/mesmerism/","https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/"])ok(h.includes(url),"published path missing "+url);
 ok(/<button\b[^>]*\bdisabled\b[^>]*\baria-disabled="true"[^>]*>Merchant link withheld/i.test(h),"merchant button not genuinely disabled");
 const c=h.indexOf("Merchant link withheld"),d=h.indexOf("may earn a commission",c);
 ok(c>=0&&d>c&&d-c<600,"FTC notice absent or distant");
 ok(h.includes("No affiliate link is active here"),"inactive disclosure missing");
 ok(!/<(?:script|iframe|form|video|audio|input)\b/i.test(h),"added script/form/media/inputs");
 ok(!/\bon(?:click|load|error|mouseover|focus)\s*=/i.test(h),"inline JS event handler");
 ok(!/\bhref\s*=\s*["'][^"']*https?:\/\/(?:www\.)?(?:zen12|inspire3|hypnosislive|payhip)\.com/i.test(h),"active commercial link");
 ok(!/\b(?:data-pixel|gtm\.js|fbq\()\b/i.test(h),"tracking/autoplay");
 ok(/<details>/.test(h)&&/<summary>/.test(h),"film noJS access missing");
 const cap=[...h.matchAll(/<time>(\d\d:\d\d)–(\d\d:\d\d)<\/time>/g)].map(x=>[x[1],x[2]]);
 ok(cap.length===7,"seven film transcript captions");
 if(cap.length===7){ok(cap[0][0]==="00:00"&&cap[6][1]==="00:42","film duration");
 for(let i=0;i<6;i++)ok(cap[i][1]===cap[i+1][0],"film gap "+i);}
 ok(h.includes('role="img" aria-label='),"poster accessible label missing");
 ok(h.includes("prefers-reduced-motion"),"reduced motion missing");
 ok(Array.isArray(m.source_inventory)&&m.source_inventory.length===18,"source count");
 ok(new Set(m.source_inventory.map(s=>s.id)).size===18&&requireIds.every(id=>m.source_inventory.some(s=>s.id===id)),"source IDs");
 ok(m.source_inventory.every(s=>/^https:\/\//.test(s.url)),"bad source URL");
 ok(Array.isArray(m.claims)&&m.claims.length===26,"claims count");
 ok(new Set(m.claims.map(c=>c.id)).size===26,"claim ID uniqueness");
 for(const id of ["C05","C06","C10","C12","C13","C15","C17","C18","C22","C23","C24","C25","C26"]){const cl=m.claims.find(c=>c.id===id); ok(cl&&/^PROHIBITED/.test(cl.decision),"prohibition "+id);}
 ok(m.claims.find(c=>c.id==="C04")?.classification==="CONDITION_SPECIFIC_STUDY","training evidence overclaimed");
 ok(m.claims.find(c=>c.id==="C14")?.classification==="SYSTEMATIC_REVIEW","review misclassified");
 ok(m.commercial_gates?.length===16,"sixteen commercial gates");
 ok(m.commercial_gates&&new Set(m.commercial_gates.map(g=>g.id)).size===16&&exactGates.every(id=>m.commercial_gates.some(g=>g.id===id)),"exact gates");
 ok(m.commercial_gates?.every(g=>g.status==="HARD_HOLD"&&g.evidence===null&&g.decision==="NO_ACTIVATION"),"unapproved release gate");
 ok(Object.keys(m.release_bounds||{}).length===8&&exactRelease.every(id=>m.release_bounds[id]===false),"release boundaries");
 ok(m.commercial_status?.named_inspire3_acceptance==="NOT_VERIFIED"&&m.commercial_status?.authorized_affiliate_url===null,"partner approval/link invented");
 ok(m.commercial_status?.fv_owned_mind_product==="NOT_AUTHENTICATED"&&m.commercial_status?.merchant_verified_checkout===null,"invented purchasable SKU/checkout");
 ok(m.measurement?.realized_net_revenue_per_1000_qualified_humans==="NOT_COMPUTABLE","claimed paid revenue");
 ok(m.measurement?.plan_only===true,"claimed live tracking");
 ok(m.social_join?.length===3&&m.social_join.every(x=>x.asset_id===null&&x.published_url===null),"fake creator asset");
 ok(m.design?.not_live===true&&m.design?.film_asset==="LOCAL_REVIEW_ONLY_NOT_HOSTED","fake film playback");
 ok(m.single_focus_funnel?.new_form===false&&m.single_focus_funnel?.existing_jetpack_unchanged===true,"duplicate signup");
 for(const phrase of ["NOT COMPUTABLE","HARD HOLD","R257","PR #49","PR #172","Claude","Grok","Praxxis","Dispatch","paid affiliate commission","confirmed_paid_order"]) ok(p.includes(phrase),"plan lacks "+phrase);
 ok(!/live variant [ab] launched|paid sales achieved/i.test(p),"invented active experiment");
 return failures;
}
function mutants(b){
 const all=[]; const mutateText=(name,k,from,to)=>{
 const n={...b,[k]:b[k].split(from).join(to)};if(n[k]===b[k])throw Error("ineffective mutation "+name);all.push([name,n])};
 const mutateJSON=(name,fn)=>{const n={...b},m=JSON.parse(n.matrix);fn(m);n.matrix=JSON.stringify(m);all.push([name,n])};
 mutateText("remove primary paper","article","https://pubmed.ncbi.nlm.nih.gov/1500880/","BROKEN");
 mutateText("remove review","article","https://pmc.ncbi.nlm.nih.gov/articles/PMC2848898/","BROKEN");
 mutateText("remove nuance","article","lag-one sparing","simple refractory period");
 mutateText("remove training context","article","three months","two minutes");
 mutateText("affiliate inside investigation","article","## The consumer question", "[Buy Zen12](https://zen12.com/hnp)\n\n## The consumer question");
 mutateText("remove hero title","hub","<h1>","<h6>");
 mutateText("remove viewport","hub",'name="viewport"','name="vport"');
 mutateText("enable index","hub",'noindex,nofollow','index,follow');
 mutateText("break focus path","hub","https://finalvestige.com/focus/","https://invalid.example/focus");
 mutateText("enable CTA","hub",'disabled aria-disabled="true"','class="enabled"');
 mutateText("drop disclosure","hub","may earn a commission","will never receive payment");
 mutateText("separate disclosure","hub","may earn a commission"," ".repeat(1000)+"may earn a commission");
 mutateText("hide inactive note","hub","No affiliate link is active here","Click now");
 mutateText("add merchant href","hub","<footer>","<a href=\"https://zen12.com/hnp\">BUY</a><footer>");
 mutateText("add tracker","hub","</body>","<script src=\"https://example.org/pixel.js\"></script></body>");
 mutateText("add extra form","hub","</body>","<form><input type=\"email\"></form></body>");
 mutateText("add autoplay video","hub","</body>","<video autoplay src=\"https://example.org/test.mp4\"></video></body>");
 mutateText("add injected handler","hub",'<main>','<main onmouseover="steal()">');
 mutateText("remove film details","hub","<details>","<div>");
 mutateText("damage first caption","hub","<time>00:00–00:06</time>","<time>00:01–00:06</time>");
 mutateText("damage last caption","hub","<time>00:36–00:42</time>","<time>00:36–00:48</time>");
 mutateText("remove poster alt","hub",'<div class="poster" role="img" aria-label=', '<div class="poster" data-info=');
 mutateText("remove reduced-motion","hub","prefers-reduced-motion","reduced-motion-off");
 mutateJSON("duplicate gate",m=>{m.commercial_gates[1].id=m.commercial_gates[0].id});
 mutateJSON("open gate without proof",m=>{m.commercial_gates[0].status="APPROVED"});
 mutateJSON("fake approval",m=>{m.commercial_status.named_inspire3_acceptance="APPROVED"});
 mutateJSON("fake earning link",m=>{m.commercial_status.authorized_affiliate_url="https://zen12.com/fake?affiliate=1"});
 mutateJSON("fake product",m=>{m.commercial_status.fv_owned_mind_product="VERIFIED"});
 mutateJSON("fake checkout",m=>{m.commercial_status.merchant_verified_checkout=87.99});
 mutateJSON("fabricated paid KPI",m=>{m.measurement.realized_net_revenue_per_1000_qualified_humans=900});
 mutateJSON("remove no-deploy",m=>{m.release_bounds.deploy=true});
 mutateJSON("invent creator ID",m=>{m.social_join[0].asset_id="made-up-id"});
 mutateJSON("claim film live",m=>{m.design.not_live=false});
 mutateJSON("add email form",m=>{m.single_focus_funnel.new_form=true});
 mutateJSON("prohibit becomes allowed",m=>{m.claims.find(x=>x.id==="C13").decision="ALLOW"});
 mutateJSON("misclassify study",m=>{m.claims.find(x=>x.id==="C04").classification="PRODUCT_SPECIFIC"});
 mutateJSON("remove evidence sources",m=>{m.source_inventory=[]});
 mutateText("erase revenue uncertainty","plan","NOT COMPUTABLE","900 USD");
 mutateText("erase hold","plan","HARD HOLD","APPROVED TO PUBLISH");
 mutateText("replace ownership","plan","Grok","A third party owns social");
 let rejected=0;let survivors=[];
 for(const [name,caseData] of all){if(validate(caseData).length)rejected++;else survivors.push(name)}
 return {total:all.length,rejected,survivors};
}
if(typeof module!=="undefined")module.exports={files,validate,mutants};
if(typeof require!=="undefined"&&require.main===module){
 const fs=require("node:fs"),path=require("node:path");
 const base=Object.fromEntries(Object.entries(files).map(([k,f])=>[k,fs.readFileSync(path.join(__dirname,f),"utf8")]));
 const baseErrors=validate(base),run=mutants(base);
 console.log(JSON.stringify({baseline:baseErrors.length?"FAIL":"PASS",errors:baseErrors,mutations:run,scope:"STATIC_SOURCE_ONLY"},null,2));
 if(baseErrors.length||run.survivors.length)process.exitCode=1;
}
