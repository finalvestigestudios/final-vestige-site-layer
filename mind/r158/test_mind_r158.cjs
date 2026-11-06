/* Mind R158 — source-only test contract. Run: node mind/r158/test_mind_r158.cjs
   No website, partner account, mail or merchant transactions are touched.
   Passing source checks is NOT browser QA, real media, product efficacy or paid sale evidence. */
"use strict";
const fs=require("node:fs"), path=require("node:path"), assert=require("node:assert/strict");
const load=n=>fs.readFileSync(path.join(__dirname,n),"utf8");
const ORIGINAL={
 article:load("when-familiarity-masquerades-as-evidence-investigation.md"),
 guide:load("zen12-premium-independent-purchase-integrity-guide.md"),
 html:load("zen12-illusory-truth-conversion-UNPUBLISHED.html"),
 ledger:load("claim-evidence-offer-gates.json"),
 plan:load("single-offer-conversion-creator-and-experiment-contract.md")
};
const count=s=>(s.match(/\b[\w’'-]+\b/g)||[]).length;
function inspect(v){
 const errors=[], check=(ok,name)=>{if(!ok)errors.push(name)};
 let d={};try{d=JSON.parse(v.ledger)}catch(e){return ["ledger is not JSON"]};
 check(count(v.article)>1800,"article below substantive threshold");
 check(count(v.guide)>1100,"guide below substantial threshold");
 check(count(v.plan)>1200,"conversion plan incomplete");
 check(/Hasher, Goldstein and Thomas Toppino|Hasher, David Goldstein and Thomas Toppino|Hasher, Goldstein & Toppino/i.test(v.article),"primary 1977 study missing");
 check(/182 studies/i.test(v.article)&&/366 effect sizes/i.test(v.article)&&/31,184/i.test(v.article),"2026 meta population omitted");
 check(/0\.37/.test(v.article)&&/heterogeneity/i.test(v.article),"meta heterogeneity omitted");
 check(/Fazio/i.test(v.article)&&/Brashier/i.test(v.article),"independent studies missing");
 check(/not.{0,30}equivalen|does not demonstrate/i.test(v.guide),"unproven equivalence not rejected");
 check(/https:\/\/zen12\.com\/\?no-popup=1/.test(v.guide),"exact product URL not cited");
 check(/48 MP3/i.test(v.guide)&&/12 levels/i.test(v.guide),"exact Premium package missing");
 check(/seller-page figure|seller-page amount|observed seller-page/i.test(v.guide),"observed price caveat absent");
 check(/checkout experience|checkout total|actual checkout/i.test(v.guide),"checkout unverified caveat absent");
 check(/one-year money-back guarantee|one-year guarantee/i.test(v.guide),"seller guarantee not described");
 check(/not independently|not established|does not automatically/i.test(v.article),"no evidence limitations");
 check(/Puys[eé]gur/i.test(v.article)&&/finalvestige.com\/focus\//.test(v.article),"original FV archive or Fieldbook unlinked");
 check(/<button\b[^>]*\bdisabled\b[^>]*>/i.test(v.html),"native disabled attribute missing");
 check(/<button\b[^>]*\bdisabled\b[^>]*>Zen12 Premium purchase/i.test(v.html),"paid control not physically disabled");
 check(!/<a\b[^>]*(?:[?&](?:affiliate|aff|ref|hop|clickid)=|tracking[.])/i.test(v.html),"affiliate link or tracking in href");
 check(!/href=["']https?:\/\/(?:payhip\.com|checkout\.|go\.)[^"']+["']/i.test(v.html),"merchant checkout URL present");
 check(!/<form\b/i.test(v.html),"new subscription or checkout form");
 check(!/<script\b/i.test(v.html),"new tracking or JS script");
 check(!/<iframe\b/i.test(v.html),"third-party player iframe");
 check(!/<video\b[^>]*autoplay/i.test(v.html),"autoplay found");
 check(/prefers-reduced-motion/.test(v.html)&&/:focus-visible/.test(v.html),"accessibility CSS missing");
 check(/Skip to the investigation/.test(v.html)&&/main id="main"/.test(v.html),"skip link absent");
 check(/<meta name="robots" content="noindex,nofollow">/.test(v.html),"unpublished SEO safety absent");
 const disclosure=v.html.indexOf("If you purchase through an approved link");
 const button=v.html.indexOf("Zen12 Premium purchase — unavailable");
 check(disclosure>=0&&button>disclosure&&button-disclosure<750,"affiliate disclosure not adjacent");
 check(/aria-describedby="purchase-hold"/.test(v.html),"disabled control accessibility description missing");
 check(/POSTER CONCEPT — NOT A PLAYABLE VIDEO/.test(v.html),"storyboard mislabeled as playable");
 check(/0–08 s:/.test(v.html)&&/33–40 s:/.test(v.html),"40-second transcript/captions missing");
 check(/data-experiment="variant-b-optional-video-storyboard-only"/.test(v.html),"A/B video hypothesis not identified");
 check(/existing Focus\/Jetpack route/.test(v.html),"one existing signup route not preserved");
 check(!/new.*<form/i.test(v.html),"duplicated signup UI");
 check(d.status==="UNPUBLISHED_HARD_HOLD","ledger incorrectly opens release");
 check(d.affiliate_url===null&&d.partner_account_id===null,"partner approval or earning URL fabricated");
 check(d.net_revenue_per_1000_qualified_sessions===null,"fake net revenue result");
 check(d.paid_order_count_verified===null,"fake confirmed sale");
 check(d.claim_matrix.length>=30,"claim matrix too small");
 check(d.release_gates.length>=40,"release gate matrix too small");
 check(d.release_gates.every(g=>g.release_authorized===false),"some gate marked released");
 check(d.claim_matrix.every(c=>c.source_keys.length>0&&c.source_keys.every(k=>!!d.source_links[k])),"unreferenced claim");
 check(d.claim_matrix.some(c=>c.decision==="DO_NOT_REPEAT_AS_FACT"),"seller efficacy not rejected");
 check(/NOT COMPUTABLE/i.test(v.plan)&&/qualified human sessions/i.test(v.plan),"denominator not guarded");
 check(/merchant_confirmed_order/i.test(v.plan)&&/paid_affiliate_commission/i.test(v.plan),"orders conflated with clicks");
 check(/asset_id|asset ID/i.test(v.plan)&&/NULL/i.test(v.plan),"creator IDs fabricated");
 check(/Arm A/.test(v.plan)&&/Arm B/.test(v.plan),"A/B hypothesis not specified");
 check(/seven-|7-/.test(v.plan)&&/thirty-|30-/.test(v.plan),"7/30 cohorts missing");
 check(/issue #174/i.test(v.plan)&&/PR #49/.test(v.plan),"ownership governance not preserved");
 return errors;
}
assert.deepEqual(inspect(ORIGINAL),[],"R158 source contract failed");
const mutate=[
 ["affiliate_button",x=>x.html=x.html.replace(/<button type="button" disabled/,'<button type="button"')],
 ["near_link_disclosure",x=>x.html=x.html.replace("If you purchase through an approved link","One of the links")],
 ["fake_partner_approval",x=>{const d=JSON.parse(x.ledger);d.partner_account_id="approved";x.ledger=JSON.stringify(d)}],
 ["fake_affiliate_url",x=>{const d=JSON.parse(x.ledger);d.affiliate_url="https://fake.invalid/?aff=1";x.ledger=JSON.stringify(d)}],
 ["fake_paid_order",x=>{const d=JSON.parse(x.ledger);d.paid_order_count_verified=2;x.ledger=JSON.stringify(d)}],
 ["release_gate_flip",x=>{const d=JSON.parse(x.ledger);d.release_gates[0].release_authorized=true;x.ledger=JSON.stringify(d)}],
 ["remove_exact_product",x=>x.guide=x.guide.replace("https://zen12.com/?no-popup=1","https://example.com/")],
 ["replace_primary_meta",x=>x.article=x.article.replace("182 studies","82 studies")],
 ["duplicate_signup",x=>x.html=x.html.replace("</main>","<form><input type='email'></form></main>")],
 ["inject_tracking",x=>x.html=x.html.replace("</head>","<script src='https://third.invalid/track.js'></script></head>")],
 ["fake_playable_poster",x=>x.html=x.html.replace("POSTER CONCEPT — NOT A PLAYABLE VIDEO","WATCH THIS PLAYABLE VIDEO")],
 ["remove_noindex",x=>x.html=x.html.replace('<meta name="robots" content="noindex,nofollow">',"")],
 ["remove_variant",x=>x.html=x.html.replace('data-experiment="variant-b-optional-video-storyboard-only"',"")],
 ["obliterate_claim_sources",x=>{const d=JSON.parse(x.ledger);d.claim_matrix[0].source_keys=["MISSING"];x.ledger=JSON.stringify(d)}],
 ["remove_revenue_caution",x=>x.plan=x.plan.replace(/NOT COMPUTABLE/g,"REVENUE VERIFIED")],
 ["remove_focus_route",x=>x.html=x.html.replace("existing Focus/Jetpack route","new external list")],
 ["remove_Dispatch_governance",x=>x.plan=x.plan.replace("Issue #174","unspecified")],
 ["remove_caption_end",x=>x.html=x.html.replace("33–40 s:","late:")]
];
for(const [name,fn] of mutate){const clone={...ORIGINAL};fn(clone);assert.ok(inspect(clone).length>0,"Undetected adverse mutation: "+name)}
console.log("PASS R158: baseline 46+ source assertions and "+mutate.length+"/"+mutate.length+" adverse mutations detected; NO browser, CI, customer or sales QA.");
