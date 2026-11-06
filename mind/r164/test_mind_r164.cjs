"use strict";
/* R164 source-level security, editorial, accessibility, disclosure and commerce gate regression.
 * Native command: node mind/r164/test_mind_r164.cjs
 * The tests intentionally do not claim real-browser, checkout, partner or WordPress validation.
 */
const paths = {
 article: "mind/r164/choice-blindness-the-answer-you-never-gave-UNPUBLISHED.md",
 html: "mind/r164/zen12-choice-record-buyer-bridge-UNPUBLISHED.html",
 matrix: "mind/r164/zen12-commercial-evidence-and-release-matrix.json",
 plan: "mind/r164/creator-offer-fit-settlement-and-ab-test-contract.md",
 doorway: "mind/r160/the-room-that-erased-your-errand-investigation.md",
 hypnosis: "mind/r163/the-suggestion-is-not-the-evidence.md",
 hypnosisHtml: "mind/r163/total-focus-suggestion-presell-UNPUBLISHED.html"
};
function inspect(files) {
 const problems=[]; let checked=0;
 const test=(name,condition)=>{checked++;if(!condition) problems.push(name);};
 const article=String(files.article||""), html=String(files.html||""), plan=String(files.plan||"");
 const doorway=String(files.doorway||""),hypnosis=String(files.hypnosis||""),hypnosisHtml=String(files.hypnosisHtml||"");
 let m;
 try {m=JSON.parse(files.matrix||"{}");}catch(e){m={};problems.push("matrix_json_parse");}
 test("article_unpublished",article.includes("UNPUBLISHED_EDITORIAL_DRAFT")&&!/status: PUBLISHED/.test(article));
 test("article_original_primary_study",article.includes("10.1126/science.1111709")&&article.includes("Johansson"));
 test("article_marketplace_study",article.includes("10.1016/j.cognition.2010.06.010"));
 test("article_moral_study",article.includes("10.1371/journal.pone.0045457"));
 test("article_limit_on_choice_blindness",article.includes("did **not** show")&&article.includes("not evidence of"));
 test("article_separate_commerce",article.includes("No affiliate links")&&!/\[[^\]]*(buy now|affiliate offer|purchase through)/i.test(article));
 test("article_freely_usable_exercise",article.includes("consent-based demonstration")&&article.includes("Before"));
 test("article_historical_context",article.includes("Puységur"));
 test("html_noindex",/name="robots" content="noindex,nofollow"/.test(html));
 test("html_explicit_unpublished",html.includes("unpublished")&&html.includes("No sale enabled"));
 test("html_accessible_main",/<main\b[^>]+id="content"/.test(html)&&/class="skip" href="#content"/.test(html));
 test("html_keyboard_focus",html.includes(":focus-visible"));
 test("html_reduced_motion",html.includes("prefers-reduced-motion"));
 test("html_responsive",html.includes("name=\"viewport\"")&&html.includes("@media"));
 test("html_graphic_description",html.includes('role="img"')&&html.includes('aria-labelledby="svg-title svg-description"'));
 test("html_exercise_and_source",html.includes("Try it free")&&html.includes("16210542"));
 test("html_existing_focus_only",html.includes('href="https://finalvestige.com/focus/"')&&!/<form\b/i.test(html));
 test("html_no_external_scripts",!/<script\b|<iframe\b|onload=|onclick=/i.test(html));
 test("html_no_hidden_product_href",!/<a\b[^>]*href=["'][^"']*(zen12\.com|hypnosislive\.com|inspire3\.com|payhip\.com)/i.test(html));
 test("html_purchase_native_disabled",/<button\b[^>]*\bdisabled\b[^>]*>Purchase link unavailable/.test(html));
 const disclosureIndex=html.indexOf("Potential affiliate relationship:"),buttonIndex=html.indexOf('class="disabled"');
 test("html_disclosure_immediately_beside_purchase",disclosureIndex>=0&&buttonIndex>disclosureIndex&&buttonIndex-disclosureIndex<550);
 test("html_product_correct",html.includes("48 MP3")&&html.includes("twelve-level program"));
 test("html_price_observed_not_guaranteed",html.includes("$87.99 displayed")&&html.includes("checkout")&&html.includes("unverified"));
 test("html_refund_is_seller_only",html.includes("Merchant representation")&&html.includes("refund"));
 test("html_reject_unproven_12minute_equivalence",html.includes("not established for this particular program"));
 test("html_video_no_autoplay",html.includes("storyboard")&&!/<video\b[^>]*autoplay/i.test(html)&&html.includes("<details>"));
 test("html_no_duplicated_jetpack",!/<form\b|jetpack-subscribe|mailchimp|convertkit/i.test(html));
 test("matrix_sources_count",Array.isArray(m.sources)&&m.sources.length>=10);
 test("matrix_claims_count",Array.isArray(m.claims)&&m.claims.length>=25);
 test("matrix_seller_sources",Array.isArray(m.sources)&&m.sources.some(x=>x.url==="https://zen12.com/?no-popup=1"));
 test("matrix_ftc_sources",Array.isArray(m.sources)&&m.sources.some(x=>/ftc\.gov/.test(x.url)));
 test("matrix_gates_all_closed",Array.isArray(m.gates)&&m.gates.length>=20&&m.gates.every(x=>x.status==="CLOSED"));
 test("matrix_affiliate_authorization_unverified",m.individual_partner_eligibility_verified===false&&m.offer_authorization==="UNVERIFIED");
 test("matrix_affiliate_url_inactive",m.commercial_cta_active===false&&m.product_link_active===false);
 test("matrix_no_revenue_fabrication",m.confirmed_transactions===null&&m.confirmed_commissions===null&&m.net_revenue_per_1000_qualified_human_sessions===null);
 test("matrix_first_party_privacy",Array.isArray(m.data_policy?.never_collect)&&m.data_policy.never_collect.includes("IP address")&&m.data_policy.measurement_not_activated===true);
 test("plan_grok_ownership",plan.includes("Grok owns actual asset")&&plan.includes("Praxxis"));
 test("plan_paid_order_distinction",plan.includes("affiliate_click")&&plan.includes("merchant_paid_order_confirmed")&&plan.includes("refund_or_chargeback"));
 test("plan_7_30day_cohorts",plan.includes("Seven-day and thirty-day")&&plan.includes("NOT COMPUTABLE"));
 test("plan_experiment_unrun",plan.includes("NOT RUN")&&plan.includes("text-only")&&plan.includes("optional"));
 test("plan_high_intent_offer_fit",plan.includes("HIGH")&&plan.includes("LOW"));
 test("plan_no_duplication",plan.includes("single Jetpack funnel")||plan.includes("No new public tracking links")||plan.includes("single Jetpack"));
 test("doorway_experiments_distinct",doorway.includes("16 butterfly photographs")&&doorway.includes("loaded virtual-reality Experiment 2"));
 test("hypnosis_2022_date_fixed",hypnosis.includes('clinical pilot trial” (2022).')&&!hypnosis.includes("(2022/23)"));
 test("hypnosis_buyer_2022_date_fixed",hypnosisHtml.includes("2022 weight-related audio pilot")&&!hypnosisHtml.includes("2022/23 weight-related"));
 return {checked,problems,passed:problems.length===0};
}
function mutations(files) {
 const bad=[
 ["remove_disclosure","html","Potential affiliate relationship:","No relationships:"],
 ["activate_button","html","<button class=\"disabled\" disabled","<button class=\"disabled\""],
 ["merchant_link","html","<main class=\"frame\"","<a href=\"https://zen12.com/buy\">Buy now</a><main class=\"frame\""],
 ["inject_script","html","</head>","<script src=\"https://example.org/track.js\"></script></head>"],
 ["inject_iframe","html","</head>","<iframe src=\"https://example.org/x\"></iframe></head>"],
 ["remove_noindex","html",'name="robots" content="noindex,nofollow"','name="robots" content="index,follow"'],
 ["remove_disabled_cta","html","Purchase link unavailable — authorization required","Buy Zen12 now"],
 ["inflate_price_claim","html","$87.99 displayed","$87.99 guaranteed checkout"],
 ["remove_refund_caution","html","Merchant representation","Verified refund fulfillment"],
 ["erase_video_concept","html","storyboard","promotion"],
 ["remove_accessible_main","html",'id="content"','id="missing"'],
 ["remove_aria_description","html",'aria-labelledby="svg-title svg-description"','aria-label=""'],
 ["add_email_form","html","</footer>","<form><input type=\"email\"></form></footer>"],
 ["replace_research_abstract","article","10.1126/science.1111709","10.1126/unknown"],
 ["remove_history","article","Puységur","archived subject"],
 ["erase_plan_outcomes","plan","merchant_paid_order_confirmed","click_sale"],
 ["erase_review_gate","plan","NOT COMPUTABLE","0 US dollars"],
 ["hide_grok","plan","Grok owns actual asset","Anyone owns asset"],
 ["erase_doorway_correction","doorway","loaded virtual-reality Experiment 2","general load experiment"],
 ["erase_date_correction","hypnosis","(2022).","(2022/23)."],
 ["erase_buyer_date","hypnosisHtml","2022 weight-related audio pilot","2022/23 weight-related audio pilot"]
 ];
 const result=[];
 for(const [name,key,from,to] of bad){
  if(!String(files[key]||"").includes(from)) {result.push({name,error:"mutation_anchor_missing"});continue;}
  const copy={...files,[key]:String(files[key]).replace(from,to)};
  const output=inspect(copy);
  result.push({name,detected:output.problems.length>0,newFailures:output.problems});
 }
 const matrix=JSON.parse(files.matrix);
 for(const [name,change] of [
 ["activate_affiliate",o=>{o.commercial_cta_active=true}],
 ["open_release_gate",o=>{o.gates[0].status="OPEN"}],
 ["fabricate_revenue",o=>{o.confirmed_transactions=10}],
 ["fabricate_approval",o=>{o.individual_partner_eligibility_verified=true}],
 ["fake_tracking",o=>{o.data_policy.measurement_not_activated=false}]
 ]){const copy=JSON.parse(JSON.stringify(matrix));change(copy);const inspected=inspect({...files,matrix:JSON.stringify(copy)});result.push({name,detected:!inspected.passed,newFailures:inspected.problems});}
 return result;
}
module.exports={paths,inspect,mutations};
if(require.main===module){
 const fs=require("node:fs"),path=require("node:path"),base=path.resolve(__dirname,"../..");
 const files=Object.fromEntries(Object.entries(paths).map(([key,p])=>[key,fs.readFileSync(path.join(base,p),"utf8")]));
 const review=inspect(files),m=mutations(files);
 console.log(JSON.stringify({source_assertions:review.checked,source_problems:review.problems,mutations:m.length,detected:m.filter(x=>x.detected).length,missed:m.filter(x=>!x.detected)},null,2));
 if(!review.passed||m.some(x=>!x.detected))process.exitCode=1;
}
