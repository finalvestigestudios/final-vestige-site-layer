/* Mind R185 source-quality regression; no dependency, network call or production write.
   Run in a checked-out repository: node mind/r185/test_mind_r185.cjs
   Exports validate() and mutationSafety() for read-only committed SHA testing. */
"use strict";
const paths = {
 article:"the-question-that-changed-the-crash-INVESTIGATION-UNPUBLISHED.md",
 matrix:"merchant-claims-acceptance-and-net-revenue-gates.json",
 A:"zen12-premium-A-text-UNPUBLISHED.html",
 B:"zen12-premium-B-optional-film-UNPUBLISHED.html",
 hub:"mind-four-stream-archive-WORDPRESS-PREVIEW-UNPUBLISHED.html",
 plan:"offer-first-creator-fit-ab-privacy-and-paid-proof.md"
};
function validate(f) {
 const err=[],pass=[];
 const check=(name,condition)=>{if(condition)pass.push(name);else err.push(name)};
 const a=f.article||"",m=f.matrix||"",A=f.A||"",B=f.B||"",h=f.hub||"",p=f.plan||"";
 let data;try{data=JSON.parse(m)}catch(e){data=null}
 check("all six source artifacts supplied",Object.keys(paths).every(k=>typeof f[k]==="string"&&f[k].length>300));
 check("article genuinely sourced",a.includes("10.1016/S0022-5371(74)80011-3")&&a.includes("pubmed.ncbi.nlm.nih.gov/621467/")&&a.includes("Source monitoring"));
 check("article correct 1974 two experiments",a.includes("45 students")&&a.includes("sixteen of fifty")&&a.includes("seven of fifty")&&a.includes("Six of fifty"));
 check("article correct 1978 program size",a.includes("1,242 people across five experiments and a pilot"));
 check("article admits limitations",a.includes("response bias")&&a.includes("source monitoring")&&a.includes("not a scientific recreation"));
 check("research has no earning-link call to action",!/href=["']https?:\/\/(?:www\.)?(?:awin1|zen12|affiliates\.inspire3)\b/i.test(a)&&!a.includes("Buy Now"));
 check("article separates hypnosis/memory",a.includes("hypnotic")&&a.includes("recovered")&&a.includes("not controlled demonstrations"));
 check("claims JSON parses",!!data);
 check("affiliate inactive",data?.affiliate_activation===false&&data?.affiliate_url===null);
 check("financial data unknown",data?.commission_received===null&&data?.qualified_human_sessions===null);
 check("substantive claim decisions",Array.isArray(data?.claim_decisions)&&data.claim_decisions.length>=15);
 check("substantive source trail",Array.isArray(data?.sources)&&data.sources.length>=12);
 check("release gates maintained",Array.isArray(data?.activation_gates)&&data.activation_gates.length>=12);
 check("named publisher approval held",data?.activation_gates?.find(x=>x.id==="G01")?.state==="HARD_HOLD");
 check("commercial earning URL held",data?.activation_gates?.find(x=>x.id==="G03")?.state==="HARD_HOLD");
 check("founder release held",data?.activation_gates?.find(x=>x.id==="G13")?.state==="HARD_HOLD");
 check("nonactivated claim ledger",data?.test_policy?.no_partner_url_before_verification===true);
 check("seller 12 levels and 48 MP3",data?.claim_decisions?.some(x=>x.claim.includes("12 levels")&&x.claim.includes("48")));
 check("pricing unresolved",data?.claim_decisions?.some(x=>x.verdict==="NOT_APPROVED_FOR_FIXED_PRICE_COPY"));
 check("product-specific efficacy blocked",data?.claim_decisions?.filter(x=>x.verdict==="UNSUBSTANTIATED_PRODUCT_EFFICACY_CLAIM").length>=2);
 const commercial=[A,B];
 for(const [i,s] of commercial.entries()){
   const n=i?"B":"A";
   check(n+" complete HTML",s.includes("<!doctype html>")&&s.includes("<main")&&s.includes("</html>"));
   check(n+" native disabled merchant control",/<button\b(?=[^>]*\sdisabled\b)[^>]*>Merchant purchase link unavailable/.test(s));
   check(n+" direct FTC disclosure adjacent to control",/<p class="disclosure">[\s\S]{0,400}<\/p>\s*<button\b/.test(s));
   check(n+" conditional plain commission wording",s.includes("Final Vestige may earn a commission at no additional cost to you"));
   check(n+" zero active affiliate links",!/<a\b[^>]*href=["'][^"']*(awin1|clickbank|hop=|affiliate|ref=|utm_source=inspire3|zen12\.com)/i.test(s));
   check(n+" no JS/frames/signup/autoplay",!/<(?:script|iframe|form|input|video|audio)\b/i.test(s)&&!s.includes("autoplay"));
   check(n+" uses one Focus path",s.includes("https://finalvestige.com/focus/"));
   check(n+" independent source trail",s.includes("pubmed.ncbi.nlm.nih.gov/37205669")&&s.includes("ftc.gov"));
   check(n+" no marketing certainty",!s.includes("12 minutes equals one hour")&&!s.includes("guaranteed concentration"));
   check(n+" price and returns qualified",s.includes("public page observations have differed")&&s.includes("has not verified fulfillment"));
   check(n+" keyboard and reduced-motion source",s.includes(":focus-visible")&&s.includes("prefers-reduced-motion")&&s.includes("max-width:760px"));
 }
 check("A deliberately without video",!A.includes('id="optional-film"'));
 check("B optional video poster & transcript",B.includes('id="optional-film"')&&B.includes("<details><summary>")&&B.includes("<svg")&&B.includes("00:36–00:42")&&B.includes("not a playable video"));
 const normalize=s=>s.replace(/\n<section id="optional-film"[\s\S]*?<\/section>/,"").replace(/VARIANT [AB]/g,"VARIANT A").replace(/Variant [AB]/g,"Variant A");
 check("A/B exact parity except film",normalize(A)===normalize(B));
 check("hub four streams",["PERCEPTION & ATTENTION","HISTORY OF SUGGESTION","PRACTICE & REFLECTION","TOOLS UNDER REVIEW"].every(x=>h.includes(x)));
 check("hub no fake published research",h.includes("UNPUBLISHED")&&h.includes("route not assigned")&&h.includes("https://finalvestige.com/focus/"));
 check("hub no duplicate forms, JS, commerce",!/<(?:form|script|iframe|input|button)\b/i.test(h)&&!h.includes("awin1.com"));
 check("hub existing source trails",h.includes("puysegurs-animal-magnetism-files")&&h.includes("change-blindness")&&h.includes("editorial-standards"));
 check("plan one concrete offer",p.includes("Zen12 Premium")&&p.includes("Payhip")&&p.includes("HARD HOLD"));
 check("plan distinct actual paid events",p.includes("merchant_confirmed_paid_purchase")&&p.includes("merchant_confirmed_paid_affiliate_conversion")&&p.includes("affiliate_outbound"));
 check("plan proof denominator and cohorts",p.includes("realized_net_revenue_per_1000_qualified_human_sessions")&&p.includes("7-day")&&p.includes("30-day"));
 check("plan correct roles",p.includes("Praxxis / Grok")&&p.includes("Dispatch")&&p.includes("Founder"));
 check("plan noninvented asset IDs",p.includes("<actual_asset_id>")&&p.includes("UNKNOWN"));
 return {pass,errors:err};
}
function mutationSafety(original) {
 const cases=[
 ["active merchant control", "A",s=>s.replace("class=\"inactive\" disabled","class=\"inactive\"")],
 ["remove near-link disclosure","A",s=>s.replace(/<p class="disclosure">[\s\S]*?<\/p>/,"")],
 ["inject earning URL","A",s=>s.replace("</main>","<a href=\"https://www.awin1.com/cread.php?test=1\">Purchase</a></main>")],
 ["inject script","B",s=>s.replace("</main>","<script>console.log('test')</script></main>")],
 ["inject iframe","A",s=>s.replace("</main>","<iframe title=\"ad\"></iframe></main>")],
 ["duplicate list","B",s=>s.replace("</main>","<form action=\"/subscribe\"><input name=\"email\"></form></main>")],
 ["remove B storyboard","B",s=>s.replace(/\n<section id="optional-film"[\s\S]*?<\/section>/,"")],
 ["make A/B unequal core offer","A",s=>s.replace("48 downloadable MP3 recordings","96 downloadable MP3 recordings")],
 ["enable commerce boolean","matrix",s=>s.replace('"affiliate_activation": false','"affiliate_activation": true')],
 ["add earning URL","matrix",s=>s.replace('"affiliate_url": null','"affiliate_url": "https://example.com/earning"')],
 ["falsify commission","matrix",s=>s.replace('"commission_received": null','"commission_received": 1000')],
 ["falsify approval","matrix",s=>s.replace('"criterion": "Publisher-specific Inspire3 acceptance for FV",\n      "state": "HARD_HOLD"','"criterion": "Publisher-specific Inspire3 acceptance for FV",\n      "state": "VERIFIED"')],
 ["fabricate claimed proof","matrix",s=>s.replace('"no_partner_url_before_verification": true','"no_partner_url_before_verification": false')],
 ["delete source trail","article",s=>s.replace("10.1016/S0022-5371(74)80011-3","missing-doi")],
 ["falsify experiment total","article",s=>s.replace("1,242 people across five experiments and a pilot","500 people in one study")],
 ["insert affiliate research CTA","article",s=>s.replace("**Editorial boundary:**","Buy Now\n\n**Editorial boundary:**")],
 ["remove hub stream","hub",s=>s.replace("TOOLS UNDER REVIEW","HIDDEN TOOLS")],
 ["inject hub signup","hub",s=>s.replace("</main>","<form><input name=\"email\"></form></main>")],
 ["remove campaign proof","plan",s=>s.replace("merchant_confirmed_paid_affiliate_conversion","affiliate_click_only")],
 ["rename denominator","plan",s=>s.replace("realized_net_revenue_per_1000_qualified_human_sessions","impressions")]
 ];
 const survived=[],caught=[];
 for(const [name,key,edit] of cases){
   const altered={...original,[key]:edit(original[key])};
   if(altered[key]===original[key]){survived.push(name+" (mutation no-op)");continue}
   const issues=validate(altered).errors;
   if(issues.length)caught.push({name,issues});else survived.push(name);
 }
 return {caught,survived,total:cases.length};
}
module.exports={paths,validate,mutationSafety};
if(typeof require!=="undefined"&&require.main===module){
 const fs=require("node:fs"),path=require("node:path");
 const input=Object.fromEntries(Object.entries(paths).map(([k,v])=>[k,fs.readFileSync(path.join(__dirname,v),"utf8")]));
 const checks=validate(input),mut=mutationSafety(input);
 console.log("R185 source baseline "+checks.pass.length+" PASS, "+checks.errors.length+" FAIL; unsafe mutations "+mut.caught.length+"/"+mut.total+" detected.");
 if(checks.errors.length)console.error("FAILED:",checks.errors.join("; "));
 if(mut.survived.length)console.error("UNDETECTED:",mut.survived.join("; "));
 process.exitCode=checks.errors.length||mut.survived.length?1:0;
}
