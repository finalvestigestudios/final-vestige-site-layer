/* FV Mind R188. Reproduce in a real repository checkout:
   node mind/r188/test_mind_r188.cjs
Source-level safety checks only. NOT browser, WCAG, performance, checkout, consent, video or sales tests. */
"use strict";
const files={
 article:"repetition-made-it-feel-true-INVESTIGATION-UNPUBLISHED.md",
 matrix:"source-to-claim-merchant-activation-ledger.json",
 hub:"mind-archive-four-stream-WORDPRESS-PREVIEW-UNPUBLISHED.html",
 A:"zen12-variant-A-independent-text-UNPUBLISHED.html",
 B:"zen12-variant-B-optional-42s-storyboard-UNPUBLISHED.html",
 plan:"offer-first-creator-fit-attribution-and-paid-proof-ACCEPTANCE.md",
 whitebear:"../r186/white-bear-thought-suppression-INVESTIGATION-UNPUBLISHED.md",
 oldfilm:"../r186/zen12-B-optional-42s-concept-UNPUBLISHED.html",
 oldplan:"../r187/one-offer-creator-fit-privacy-ab-paid-revenue-ACCEPTANCE.md",
 oldtest:"../r187/test_mind_r187.cjs"
};
function validate(f){
 const labels=[], failures=[];
 const ck=(label,passed)=>{labels.push(label);if(!passed)failures.push(label)};
 for(const [key] of Object.entries(files))ck("file exists: "+key,typeof f[key]==="string"&&f[key].length>800);
 let m={};try{m=JSON.parse(f.matrix||"")}catch(e){}
 ck("16 independently linkable sources",Array.isArray(m.source_links)&&m.source_links.length>=16&&m.source_links.every(s=>/^https:\/\//.test(s.url)));
 ck("24 claim decisions",Array.isArray(m.claim_decisions)&&m.claim_decisions.length>=24);
 ck("14 explicit gates",Array.isArray(m.release_gates)&&m.release_gates.length>=14);
 ck("merchant earning link null",m.affiliate_earning_url===null);
 ck("affiliate activation disabled",m.affiliate_activation===false);
 ck("named partner approval unavailable",m.named_fv_publisher_approval===null);
 ck("approved channels unavailable",m.permitted_promotional_channels===null);
 ck("paid Mind Payhip unavailable",m.verified_owned_payhip_mind_sku===null);
 ck("merchant purchases unavailable",m.merchant_confirmed_purchases===null);
 ck("paid affiliate commissions unavailable",m.paid_affiliate_commissions===null);
 ck("qualified sessions unavailable",m.qualified_human_sessions===null);
 ck("net revenue unavailable",m.realized_net_revenue===null);
 ck("seller outcomes withheld",m.claim_decisions?.some(x=>x.id==="zen_one_hour_claim"&&x.decision.startsWith("WITHHELD")));
 ck("merchant channels gate closed",m.release_gates?.some(x=>x.id==="partner_channels"&&x.status==="BLOCKED"));
 ck("focus free not paid SKU",m.claim_decisions?.some(x=>x.id==="owned_mind"&&x.decision.includes("FREE")));
 const intro=f.article||"";
 ck("article >=1700 words",intro.trim().split(/\s+/).length>=1700);
 ck("article title present",intro.includes("The Sentence That Became True"));
 ck("1977 first study source linked",intro.includes("10.1016/S0022-5371(77)80012-1"));
 ck("2015 experimental study linked",intro.includes("pubmed.ncbi.nlm.nih.gov/26301795"));
 ck("meta-analysis source linked",intro.includes("10.1177/1088868309352251"));
 ck("historical context labeled interpretive",intro.includes("an error to rewrite"));
 ck("article denies product evidence transfer",intro.includes("neither 1977 trivia experiments nor 2015 truth-rating studies")||intro.includes("Neither 1977 trivia experiments nor 2015 truth-rating studies"));
 ck("article points to one free Focus resource",intro.includes("https://finalvestige.com/focus/"));
 ck("article not an affiliate advertisement",!intro.includes("affiliate earning URL")&&!intro.includes("I used Zen12"));
 const html=["hub","A","B"];
 for(const name of html){
  const s=f[name]||"";
  ck(name+" labeled unpublished",/unpublished|preview|draft/i.test(s));
  ck(name+" no JavaScript",!/<script\b/i.test(s));
  ck(name+" no form or inputs",!/<form\b|<input\b/i.test(s));
  ck(name+" no iframe",!/<iframe\b/i.test(s));
  ck(name+" no paid link patterns",!/awin1\.com|clickbank\.net|hop\.click|affiliate_id=|aff_id=|ref=finalvestige/i.test(s));
  ck(name+" no autoplay",!/autoplay\b/i.test(s.replace(/no autoplay|autoplay feature/gi,"")));
 }
 ck("hub 4 distinct streams",["Perception & attention","History of suggestion","Practice & reflection","Tools under review"].every(x=>f.hub?.includes(x)));
 ck("hub existing Focus not new signup",f.hub?.includes("https://finalvestige.com/focus/")&&!/<form\b/i.test(f.hub));
 ck("A native disabled CTA",/<button[^>]+disabled[^>]*>Purchase option unavailable/.test(f.A||""));
 ck("B native disabled CTA",/<button[^>]+disabled[^>]*>Purchase option unavailable/.test(f.B||""));
 for(const name of ["A","B"]){
  const s=f[name]||"";
  const i=s.indexOf("Affiliate disclosure (prospective)");
  const j=s.indexOf("Purchase option unavailable");
  ck(name+" nearby disclosure",i>=0&&j>i&&j-i<900);
  ck(name+" no fixed checkout promise",!s.includes("$87.99")&&!s.includes("$87")&&!s.includes("guaranteed results"));
  ck(name+" merchant only informational citation",s.includes('rel="nofollow noopener noreferrer"')&&s.includes("not an affiliate link"));
  ck(name+" free alternative without list duplication",s.includes("https://finalvestige.com/focus/")&&!/<form/i.test(s));
 }
 const filmMatch=(f.B||"").match(/<section id="optional-film"[\s\S]*?<\/section>/);
 ck("B includes one optional film block",!!filmMatch&&filmMatch[0].includes("00:35–00:42"));
 ck("A/B exact parity except film",!!filmMatch&&f.B.replace(filmMatch[0],"")===f.A);
 ck("B film static storyboard only",!!filmMatch&&filmMatch[0].includes("no playable asset")&&!/<video\b|<audio\b|\.mp4/i.test(filmMatch[0]));
 ck("B film includes caption-transcript disclosure",!!filmMatch&&/caption transcript/i.test(filmMatch[0])&&/role="img"/i.test(filmMatch[0]));
 ck("B film optional accessible details",!!filmMatch&&filmMatch[0].includes("<details><summary>"));
 ck("plan single verified offer first",f.plan?.includes("HARD HOLD")&&f.plan.includes("an authenticated, rights-cleared"));
 ck("plan creator roles separate",f.plan?.includes("Grok independently produces and posts")&&f.plan.includes("Praxxis reviews"));
 ck("plan 3 topic rows",["twelve minutes","sentence sound truer","changed right in front"].every(x=>f.plan?.includes(x)));
 ck("plan affiliate_click != sale",f.plan?.includes("affiliate_click")&&f.plan.includes("never")&&f.plan.includes("affiliate_network_confirmed_sale"));
 ck("plan meaningful money denominator",f.plan?.includes("per 1,000 qualified human sessions")&&f.plan.includes("refunds")&&f.plan.includes("7-day and 30-day"));
 ck("plan no unapproved tracking",f.plan?.includes("Do not duplicate scripts"));
 ck("white bear expression instruction corrected",f.whitebear?.includes("explicitly instructed to think about it from the outset"));
 ck("old film expression instruction corrected",f.oldfilm?.includes("Both groups were told to think of the bear."));
 ck("Grok alone owns original creator work",f.oldplan?.includes("Grok owns original social content creation")&&f.oldplan.includes("Praxxis independently researches"));
 ck("inherited source test ownership updated",f.oldtest?.includes("Grok owns original social content creation")&&!f.oldtest.includes('f.plan.includes("Grok and Praxxis own")'));
 return {passed:labels.length-failures.length,total:labels.length,failures};
}
const mutations=[
 ["affiliate activation",a=>{a.matrix=a.matrix.replace('"affiliate_activation": false','"affiliate_activation": true')}],
 ["earning link",a=>{a.matrix=a.matrix.replace('"affiliate_earning_url": null','"affiliate_earning_url": "https://unapproved.example/offer"')}],
 ["publisher invented",a=>{a.matrix=a.matrix.replace('"named_fv_publisher_approval": null','"named_fv_publisher_approval": "APPROVED"')}],
 ["channels invented",a=>{a.matrix=a.matrix.replace('"permitted_promotional_channels": null','"permitted_promotional_channels": ["email"]')}],
 ["owned SKU invented",a=>{a.matrix=a.matrix.replace('"verified_owned_payhip_mind_sku": null','"verified_owned_payhip_mind_sku": "fake"')}],
 ["revenue invented",a=>{a.matrix=a.matrix.replace('"realized_net_revenue": null','"realized_net_revenue": 5000')}],
 ["sales invented",a=>{a.matrix=a.matrix.replace('"merchant_confirmed_purchases": null','"merchant_confirmed_purchases": 12')}],
 ["claim transferred",a=>{a.matrix=a.matrix.replace('"WITHHELD_NO_PRODUCT_SPECIFIC_INDEPENDENT_SUBSTANTIATION"','"PROVEN"')}],
 ["article source removed",a=>{a.article=a.article.replace("pubmed.ncbi.nlm.nih.gov/26301795","example.invalid/123")}],
 ["false historical analog",a=>{a.article=a.article.replace("an error to rewrite","a mistake to rewrite")}],
 ["form injection",a=>{a.hub+="<form></form>"}],
 ["script injection",a=>{a.A+="<script src='http://evil'></script>"}],
 ["iframe injection",a=>{a.B+="<iframe src='x'></iframe>"}],
 ["tracking link",a=>{a.B+="<a href='https://www.awin1.com/test'>Earn</a>"}],
 ["button enabled",a=>{a.A=a.A.replace("disabled aria-disabled","aria-disabled")}],
 ["near disclosure missing",a=>{a.B=a.B.replace("Affiliate disclosure (prospective)","Commercial details")}],
 ["fixed unverified price",a=>{a.A=a.A.replace("Public presentations have varied.","$87.99 Public presentations have varied.")}],
 ["A/B copy mismatch",a=>{a.B=a.B.replace("A recording is a product.","A recording is proof.")}],
 ["film injected into control",a=>{a.A=a.A.replace("<section aria-labelledby=\"questions\">","<section id=\"optional-film\"></section><section aria-labelledby=\"questions\">")}],
 ["invented creator role",a=>{a.oldplan=a.oldplan.replace("Grok owns original social content creation","Grok and Praxxis jointly own content")}],
 ["white bear regression",a=>{a.whitebear=a.whitebear.replace("explicitly instructed to think about it from the outset","permitted to think about it from the outset")}],
 ["legacy film regression",a=>{a.oldfilm=a.oldfilm.replace("Both groups were told to think of the bear.","Both groups could think of the bear.")}],
 ["focus signup duplicated",a=>{a.A+="<form><input /></form>"}]
];
function run(f){
 const baseline=validate(f);
 const failures=mutations.map(([label,mutate])=>{let a={...f};mutate(a);return {label,caught:validate(a).failures.length>0}});
 return {baseline,mutation_total:failures.length,mutation_caught:failures.filter(x=>x.caught).length,escaped:failures.filter(x=>!x.caught).map(x=>x.label)};
}
module.exports={files,validate,mutations,run};
if(require.main===module){
 const fs=require("fs"),path=require("path"), f={};
 for(const [name,rel] of Object.entries(files))f[name]=fs.readFileSync(path.join(__dirname,rel),"utf8");
 const result=run(f);console.log(JSON.stringify(result,null,2));
 if(result.baseline.failures.length||result.escaped.length)process.exitCode=1;
}
