/* R190: source-only, no merchant/browser claim. Run: node mind/r190/test_mind_r190.cjs */
"use strict";
const files={
 article:"the-recording-is-not-the-experiment-SELF-HYPNOSIS-EVIDENCE-UNPUBLISHED.md",
 ledger:"HYPNOSIS-CLAIM-PROOF-COMMERCE-GATES.json",
 funnel:"CREATOR-TO-ONE-OFFER-FUNNEL-AND-PAID-PROOF.md",
 hub:"../r189/mind-archive-four-stream-WORDPRESS-PREVIEW-UNPUBLISHED.html",
 priorArticle:"../r189/the-pendulum-that-answered-a-question-IDEOMOTOR-INVESTIGATION-UNPUBLISHED.md",
 priorLedger:"../r189/verified-claims-merchant-permissions-revenue-gates.json",
 priorTest:"../r188/test_mind_r188.cjs",
 A:"../r188/zen12-variant-A-independent-text-UNPUBLISHED.html",
 B:"../r188/zen12-variant-B-optional-42s-storyboard-UNPUBLISHED.html"
};
function nativelyDisabled(html){
 const b=[...(html||"").matchAll(/<button\b([^>]*)>Purchase option unavailable[^<]*<\/button>/gi)];
 return b.length===1&&/(?:^|\s)disabled(?=\s|=|$)/i.test(b[0][1]);
}
function validate(f){
 const labels=[],failures=[];const ck=(name,ok)=>{labels.push(name);if(!ok)failures.push(name);};
 for(const k of Object.keys(files))ck("exists "+k,typeof f[k]==="string"&&f[k].length>700);
 let r={},p={};try{r=JSON.parse(f.ledger)}catch(e){}try{p=JSON.parse(f.priorLedger)}catch(e){}
 ck("R190 substantive >=2000 words",(f.article||"").split(/\s+/).length>=2000);
 ck("2026 synthesis DOI",f.article?.includes("10.1002/ejp.70369"));
 ck("2025 apps review DOI",f.article?.includes("10.1080/00207144.2024.2434085"));
 ck("33 screened/15 scanned/11 analyzed/7 connectivity",(f.article||"").includes("**33**")&&(f.article||"").includes("**15**")&&(f.article||"").includes("**11**")&&(f.article||"").includes("**seven**"));
 ck("article not product endorsement",f.article?.includes("no commercial link or buyer-facing endorsement"));
 ck("original official seller links",f.article?.includes("zen12.com/hnp")&&f.article?.includes("hypnosislive.com/mental-skills/total-focus"));
 ck("free Focus route",f.article?.includes("https://finalvestige.com/focus/"));
 ck("historical Puységur",f.article?.includes("puysegurs-animal-magnetism-files/"));
 ck("app population denominator",f.article?.includes("**679 unique apps**")&&f.article?.includes("**168**"));
 ck("prior article corrected denominators",f.priorArticle?.includes("**11** in the final imaging analysis")&&f.priorArticle?.includes("**seven**"));
 ck("prior ledger repaired FK",p.source_links?.some(x=>x.id==="issue818"));
 ck("prior ledger FMRI 7 denominator",p.claim_decisions?.find(x=>x.id==="motor_fmri")?.claim.includes("7 for supplementary"));
 ck("all new source keys map",Array.isArray(r.sources)&&r.sources.length>=15&&r.claims?.length>=22&&r.claims.every(x=>r.sources.some(y=>y.id===x.source_id)));
 ck("source URL https",r.sources?.every(x=>/^https:\/\//.test(x.url)));
 ck("commercial gates documented",r.gates?.length>=13);
 ck("partner approval remains null",r.named_final_vestige_approval===null);
 ck("permitted channels null",r.permitted_channels===null);
 ck("affiliate url null",r.affiliate_url===null);
 ck("affiliate off",r.affiliate_activation===false);
 ck("paid orders null",r.verified_paid_orders===null&&r.verified_affiliate_sales===null);
 ck("gross-to-net still unknown",r.realized_net_revenue===null&&r.net_revenue_per_1000_humans===null);
 ck("owned SKU unverified",r.verified_payhip_mind_sku===null);
 ck("withdraw Zen12 equivalence",r.claims?.find(x=>x.id==="zen_equivalence")?.decision==="WITHHELD_NO_PRODUCT_SPECIFIC_PROOF");
 ck("withdraw branded focus",r.claims?.find(x=>x.id==="total_results")?.decision==="WITHHELD_NO_PRODUCT_SPECIFIC_PROOF");
 ck("FTC source proof",r.sources?.some(x=>x.id==="ftc_endorse")&&r.sources?.some(x=>x.id==="ftc_health"));
 ck("conversion paid-first",f.funnel?.includes("Revenue / 1,000 qualified humans")&&f.funnel.includes("NOT COMPUTABLE"));
 ck("3 creator topics",f.funnel?.includes("pendulum")&&f.funnel.includes("12-minute recording")&&f.funnel.includes("recorded hypnosis"));
 ck("Grok remains publisher",f.funnel?.includes("Grok owns all original social content"));
 ck("no new Jetpack list",f.funnel?.includes("do not modify the welcome message")||f.funnel?.includes("do not modify the welcome message".toUpperCase())||f.funnel?.includes("Do not duplicate subscriptions"));
 ck("hub integrates unpublished R190",f.hub?.includes("The Recording Is Not the Experiment")&&f.hub.includes("R190 archive study"));
 ck("hub public Mesmerism canonical",f.hub?.includes("https://finalvestige.com/2026/11/02/mesmerism/"));
 ck("hub no production writes",f.hub?.includes("No WordPress, navigation, email or merchant state was changed."));
 ck("A native disabled",nativelyDisabled(f.A));
 ck("B native disabled",nativelyDisabled(f.B));
 ck("A proximal disclosure",f.A?.includes("Affiliate disclosure (prospective)")&&f.A.indexOf("Purchase option unavailable")-f.A.indexOf("Affiliate disclosure (prospective)")<850);
 ck("B proximal disclosure",f.B?.includes("Affiliate disclosure (prospective)")&&f.B.indexOf("Purchase option unavailable")-f.B.indexOf("Affiliate disclosure (prospective)")<850);
 ck("B-only regression fixed",f.priorTest?.includes('["B button enabled"')&&(f.priorTest.match(/\\sdisabled/g)||[]).length>=2);
 ck("A has no film",!f.A?.includes('id="optional-film"'));
 ck("B has film",f.B?.includes('id="optional-film"')&&f.B.includes("00:35–00:42"));
 for(const k of ["A","B","hub"]){let h=f[k]||"";ck(k+" no active JS",!/<script\b/i.test(h));ck(k+" no subscription",!/<form\b|<input\b/i.test(h));ck(k+" no active player",!/<video\b|<audio\b|<iframe\b/i.test(h));ck(k+" no earning URL",!/awin1\.com|hop\.click|clickbank|affiliate_id=|aff_id=/i.test(h));ck(k+" draft noindex",/noindex,nofollow/.test(h));}
 return {assertions:labels.length,passed:labels.length-failures.length,failures};
}
const mutations=[
 ["remove A native disabled",f=>f.A=f.A.replace('disabled aria-disabled','aria-disabled')],
 ["remove B native disabled",f=>f.B=f.B.replace('disabled aria-disabled','aria-disabled')],
 ["remove both native disabled",f=>{f.A=f.A.replace('disabled aria-disabled','aria-disabled');f.B=f.B.replace('disabled aria-disabled','aria-disabled');}],
 ["invent partner approval",f=>f.ledger=f.ledger.replace('"named_final_vestige_approval": null','"named_final_vestige_approval": "approved"')],
 ["activate affiliate",f=>f.ledger=f.ledger.replace('"affiliate_activation": false','"affiliate_activation": true')],
 ["invent earning link",f=>f.ledger=f.ledger.replace('"affiliate_url": null','"affiliate_url": "https://example.com/affiliate"')],
 ["invent paid sale",f=>f.ledger=f.ledger.replace('"verified_paid_orders": null','"verified_paid_orders": 12')],
 ["invent Payhip SKU",f=>f.ledger=f.ledger.replace('"verified_payhip_mind_sku": null','"verified_payhip_mind_sku": "madeup"')],
 ["inflate net money",f=>f.ledger=f.ledger.replace('"realized_net_revenue": null','"realized_net_revenue": 12000')],
 ["convert seller claim to proved",f=>f.ledger=f.ledger.replace('"WITHHELD_NO_PRODUCT_SPECIFIC_PROOF"','"SCIENTIFICALLY_PROVEN"')],
 ["remove 2026 paper",f=>f.article=f.article.replace("10.1002/ejp.70369","incorrect.paper")],
 ["revert fMRI detail",f=>f.priorArticle=f.priorArticle.replace("**11** in the final imaging analysis","**15** in the final imaging analysis")],
 ["break seller link",f=>f.article=f.article.replace("hypnosislive.com/mental-skills/total-focus","example.org/irrelevant")],
 ["duplicate email form",f=>f.hub+="<form><input></form>"],
 ["inject JS",f=>f.B+="<script>bad()</script>"],
 ["inject affiliate link",f=>f.A+='<a href="https://www.awin1.com/cread">Purchase</a>'],
 ["enable autoplay",f=>f.B+='<video autoplay src="fake.mp4"></video>'],
 ["remove prospective disclosure",f=>f.A=f.A.replace("Affiliate disclosure (prospective)","Commercial")],
 ["lose source FK",f=>f.ledger=f.ledger.replace('"source_id": "zen12"','"source_id": "not_a_source"')],
 ["revert B test",f=>f.priorTest=f.priorTest.replace('["B button enabled"','["not B check"')]
];
function run(f){
 const baseline=validate(f);
 const results=mutations.map(([name,mutate])=>{const copy={...f};mutate(copy);const negative=validate(copy);return {name,caught:negative.failures.length>0};});
 return {baseline,mutations:results.length,caught:results.filter(x=>x.caught).length,escaped:results.filter(x=>!x.caught).map(x=>x.name)};
}
module.exports={files,validate,mutations,run};
if(typeof require!=="undefined" && require.main===module){
 const fs=require("node:fs"),path=require("node:path"),f={};
 for(const [k,p] of Object.entries(files))f[k]=fs.readFileSync(path.resolve(__dirname,p),"utf8");
 const output=run(f);console.log(JSON.stringify(output,null,2));
 if(output.baseline.failures.length||output.escaped.length)process.exitCode=1;
}
