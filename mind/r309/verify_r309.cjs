/* Final Vestige Mind R309: source-only offline guard.
   Run: node mind/r309/verify_r309.cjs
   This tests committed review files; it is NOT a real-browser, WordPress or partner checkout test. */
"use strict";
const fs=require("node:fs"),path=require("node:path"),assert=require("node:assert/strict");
const root=__dirname;
const names={
 article:"THE-WORD-YOU-COULD-NOT-STOP-READING-UNPUBLISHED.md",
 a:"ZEN12-A-TEXT-ONLY-REVIEW.html",
 b:"ZEN12-B-OPTIONAL-42S-FILM-STORYBOARD-REVIEW.html",
 hub:"MIND-ARCHIVE-FOUR-STREAM-REVIEW-ONLY.html",
 matrix:"SOURCE-CLAIM-PRODUCT-AND-RELEASE-GATES.json",
 dossier:"RELEASE-CONVERSION-AND-CREATOR-ACCEPTANCE.md"
};
function load(){return Object.fromEntries(Object.entries(names).map(([k,p])=>[k,fs.readFileSync(path.join(root,p),"utf8")]));}
function inspection(F){
 const errors=[];
 const req=(ok,id)=>{if(!ok)errors.push(id);};
 const data=(()=>{try{return JSON.parse(F.matrix)}catch{return null}})();
 req(F.article.includes("63.3 seconds")&&F.article.includes("110.3 seconds")&&F.article.includes("47 seconds"),"STROOP_PRECISE_BASELINES");
 req(F.article.includes("2.3 seconds")&&F.article.includes("not regard as reliable"),"REVERSE_CONTROL_ASYMMETRY");
 req(F.article.includes("https://psychclassics.yorku.ca/Stroop/"),"STROOP_PRIMARY");
 req(F.article.includes("not a universal")&&F.article.includes("not evidence"),"SCIENCE_LIMITS");
 req(F.article.includes("Unpublished"),"ARTICLE_UNPUBLISHED");
 req(Boolean(data),"PARSE_SOURCE_MATRIX");
 if(data){
  req(data.sources.length>=18,"SOURCES_MINIMUM");
  req(data.claims.length>=30,"CLAIMS_MINIMUM");
  req(data.authorization_gates.length===18,"RELEASE_GATES_COUNT");
  req(data.authorization_gates.every(g=>g.decision==="HARD_HOLD"&&g.proven===false),"RELEASE_HARD_HOLD");
  req(data.offers.every(o=>o.affiliate_url===null),"NO_AFFILIATE_URL");
  req(data.measurement.kpi_status==="NOT_COMPUTABLE","REVENUE_NOT_COMPUTABLE");
  req(data.measurement.event_instrumentation==="SPEC_ONLY_NOT_DEPLOYED","NO_ANALYTICS_DEPLOY_CLAIM");
  req(data.claims.some(c=>c.id==="C20"&&c.status==="UNSUBSTANTIATED_SELLER_CLAIM"),"MERCHANT_EFFICACY_HOLD");
  req(data.claims.some(c=>c.id==="C22"&&c.status==="DYNAMIC_MERCHANT_PRICE"),"NO_FIXED_PRICES");
  const ids=new Set(data.sources.map(s=>s.id));
  req(data.claims.every(c=>c.source_ids.every(id=>ids.has(id))),"CLAIM_CITATION_INTEGRITY");
 }
 for(const key of ["a","b","hub"]){
  const html=F[key];
  req(/<html lang="en">/.test(html)&&/<main\b/.test(html)&&/<h1\b/.test(html),"SEMANTIC_"+key);
  req(!/<script\b|<iframe\b|<form\b|<input\b|<meta[^>]*http-equiv|on(?:click|load|submit|error)\s*=/i.test(html),"NO_EXECUTION_"+key);
  req(!/https?:\/\/(?:www\.)?(?:zen12|hypnosislive|brainwaveshots|affiliates\.inspire3)\.com/i.test(html),"NO_PRODUCT_OUTBOUND_"+key);
  req(!/utm_content=|fbclid|gclid|gtag\(|pixel|dataLayer/i.test(html),"NO_TRACKING_"+key);
  req(html.includes("https://finalvestige.com/focus/"),"ONE_EXISTING_FUNNEL_"+key);
  req(html.includes("noindex,nofollow"),"UNPUBLISHED_META_"+key);
 }
 for(const key of ["a","b"]){
  const html=F[key];
  req(/<button\b[^>]*\bdisabled\b[^>]*\baria-disabled="true"/i.test(html),"ACTUAL_DISABLED_BUTTON_"+key);
  req(/Affiliate disclosure:[\s\S]{0,220}<button\b/i.test(html),"NEAR_BUTTON_DISCLOSURE_"+key);
  req(html.includes("There is no active buying link"),"NO_ACTIVE_SALE_"+key);
  req(html.includes("<strong>48 MP3 recordings</strong>"),"SEMANTIC_PACKAGE_FORMAT_"+key);
  req(html.includes("not purchased, used or independently tested"),"NO_INVENTED_TESTIMONIAL_"+key);
  req(!/\b(?:guaranteed focus|cures anxiety|100% proven|60% commission for FV)\b/i.test(html),"NO_OUTCOME_AD_"+key);
 }
 const stripFilm=s=>s.replace(/<figure class="film"[\s\S]*?<\/figure>/,"");
 req(stripFilm(F.b)===F.a,"A_B_IDENTICAL_BUYER_COPY");
 req(!F.a.includes('<figure class="film"'),"A_TEXT_ONLY");
 req(F.b.includes("Optional 42-second original short-film treatment"),"B_FILM_TREATMENT");
 req(F.b.includes("<details open>")&&F.b.includes('role="img"')&&F.b.includes("00:35–00:42"),"B_ACCESSIBLE_STORYBOARD");
 req(!/<video\b|autoplay|<audio\b/i.test(F.b),"B_NOT_FALSE_PLAYABLE");
 req(F.hub.includes("Perception &amp; Attention")&&F.hub.includes("History of Suggestion")&&F.hub.includes("Practice &amp; Reflection")&&F.hub.includes("Tools Under Review"),"HUB_FOUR_STREAMS");
 req(F.hub.includes("source-controlled WordPress HTML")||F.hub.includes("source-controlled WordPress HTML review"),"HUB_NOT_CMS");
 req(F.dossier.includes("OFFER → FUNNEL STEP → BLOCKER → CHANGE/EXPERIMENT → PASS/FAIL EVIDENCE → OWNER"),"COMMERCIAL_DECISION_TABLE");
 req(F.dossier.includes("NOT COMPUTABLE")&&F.dossier.includes("affiliate_outbound_click"),"MONEY_EVENT_DISAMBIGUATION");
 req(F.dossier.includes("actual_asset_id")&&F.dossier.includes("seven-day")&&F.dossier.includes("thirty-day"),"CAMPAIGN_COHORT_CONTRACT");
 req(F.dossier.includes("HARD HOLD"),"RELEASE_HOLD_DOC");
 return errors;
}
function mutate(F,key,replace,withText){
 const out={...F};out[key]=out[key].replace(replace,withText);
 if(out[key]===F[key]) throw new Error("Bad fixture: no change for "+key+" / "+replace);
 return out;
}
function mutationCases(F){
 const cases=[
 ["article",/63\.3 seconds/,"63 seconds"],["article",/110\.3 seconds/,"some seconds"],
 ["article",/47 seconds/,"several seconds"],["article",/2\.3 seconds/,"2 seconds"],
 ["article",/not regard as reliable/,"regard as highly reliable"],
 ["article",/https:\/\/psychclassics.yorku.ca\/Stroop\//,"https://example.invalid/"],
 ["article",/not a universal/,"a universal"],["article",/Unpublished/,"Published"],
 ["a",/ disabled aria-disabled="true"/,' aria-disabled="true"'],["b",/ disabled aria-disabled="true"/,' aria-disabled="true"'],
 ["a",/Affiliate disclosure:/,"Editorial aside:"],["b",/Affiliate disclosure:/,"Advertisement:"],
 ["a",/<\/main>/,'<script src="https://tracker.example/x.js"></script></main>'],
 ["b",/<\/main>/,'<form action="/capture"><input name="email"></form></main>'],
 ["hub",/<\/main>/,'<iframe src="https://example.com"></iframe></main>'],
 ["a",/<\/main>/,'<a href="https://zen12.com/getstarted">Buy</a></main>'],
 ["b",/<\/main>/,'<a href="https://hypnosislive.com/mental-skills/total-focus">Buy</a></main>'],
 ["hub",/<\/main>/,'<a href="https://brainwaveshots.com/focus-shot">Buy</a></main>'],
 ["a",/<\/main>/,'<button onclick="buy()">Buy</button></main>'],
 ["a",/https:\/\/finalvestige.com\/focus\//g,"/new-unverified-signup/"],
 ["hub",/https:\/\/finalvestige.com\/focus\//g,"/new-unverified-signup/"],
 ["a",/<strong>48 MP3 recordings<\/strong>/,"48 MP3 recordings"],
 ["b",/not purchased, used or independently tested/,"purchased, used and tested"],
 ["b",/<figure class="film"/,'<figure class="movie"'],
 ["b",/<details open>/,"<div>"],
 ["b",/role="img"/,'role="presentation"'],
 ["b",/00:35–00:42/,"final words"],
 ["b",/<\/main>/,'<video autoplay></video></main>'],
 ["hub",/History of Suggestion/,"History of Something"],
 ["matrix",/"decision": "HARD_HOLD"/,'"decision": "APPROVED"'],
 ["matrix",/"affiliate_url": null/,'"affiliate_url": "https://merchant.example/earned"'],
 ["matrix",/"kpi_status": "NOT_COMPUTABLE"/,'"kpi_status": "VERIFIED_REVENUE"'],
 ["matrix",/"event_instrumentation": "SPEC_ONLY_NOT_DEPLOYED"/,'"event_instrumentation": "DEPLOYED"'],
 ["matrix",/"status": "UNSUBSTANTIATED_SELLER_CLAIM"/,'"status": "INDEPENDENTLY_PROVEN"'],
 ["dossier",/NOT COMPUTABLE/g,"$999"],
 ["dossier",/HARD HOLD/g,"APPROVED"],
 ["dossier",/actual_asset_id/g,"invented_video_123"]
 ];
 return cases.map(([key,from,to],i)=>({id:i+1,key,from,to}));
}
const F=load(),baseline=inspection(F);
assert.deepEqual(baseline,[],"R309 baseline: "+baseline.join(", "));
const cases=mutationCases(F);
for(const c of cases){const bad=mutate(F,c.key,c.from,c.to),err=inspection(bad);assert(err.length>0,"unsafe mutation undetected #"+c.id);console.log("PASS mutation "+c.id+" "+c.key+" "+err[0]);}
console.log("R309 BASELINE PASS; "+cases.length+"/"+cases.length+" unsafe mutations rejected; no production/write tests or merchant verification.");
