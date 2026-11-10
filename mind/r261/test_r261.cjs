/* R261 source-only fail-closed lint. Native: node mind/r261/test_r261.cjs
   Tests do NOT substitute for browser, actual WP rendering, merchant settlement, or scientific peer review. */
"use strict";
const REQUIRED_GATES=["publisher_named_acceptance","issued_affiliate_url","specific_zen12_product_and_destination",
"website_channel_permission","social_channel_permission","email_channel_permission","approved_creative_usage_rights",
"exact_checkout_price_and_currency","merchant_tax_shipping_or_extra_charges",
"product_inclusion_equivalence_promo_vs_standard","refund_terms_specific_offer","merchant_refund_actual_process",
"buyer_facing_compliant_disclosure","first_party_event_definition_owner_signoff","merchant_confirmed_paid_commission_feed",
"founder_editorial_QA_release_approval"];
const REQUIRED_FALSE=["wordpress_published","newsletter_sent","merchant_link_enabled","analytics_script_added","merge_or_deploy","paid_service"];
const requiredArticle=["https://www.nature.com/articles/35048669","https://pubmed.ncbi.nlm.nih.gov/12063138/",
"https://pmc.ncbi.nlm.nih.gov/articles/PMC2905511/","https://pubmed.ncbi.nlm.nih.gov/35435070/",
"https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance",
"https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/"];
const requiredHtml=["<html lang=\"en\">","name=\"robots\" content=\"noindex,nofollow\"",
"href=\"https://finalvestige.com/focus/\"","href=\"https://finalvestige.com/2026/11/02/change-blindness/\"",
"href=\"https://finalvestige.com/2026/11/02/mesmerism/\"",
"href=\"https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/\"",
"not independently substantiated for Zen12","type=\"button\" disabled aria-disabled=\"true\"",
"If an authorized purchase link is eventually added, Final Vestige may earn a commission",
"No earning link is active here."];
function validateBundle(b) {
  const errors=[];
  function err(code){errors.push(code);}
  let x;try{x=JSON.parse(b.matrix);}catch(_){err("invalid_matrix_json");return errors;}
  if(x.status!=="UNPUBLISHED_HARD_HOLD")err("release_status");
  if(x.partner_verified===true||x.affiliate_link_authorized===true||x.live_experiment===true)err("fabricated_partner_activation");
  if(!Array.isArray(x.commercial_gates)||x.commercial_gates.length!==16)err("gate_count");
  const gateIds=(x.commercial_gates||[]).map(q=>q.id);
  if(new Set(gateIds).size!==16||REQUIRED_GATES.some(g=>!gateIds.includes(g)))err("gate_identity");
  if((x.commercial_gates||[]).some(g=>g.status!=="HARD_HOLD"||g.verified_at!==null))err("authorization_claim");
  if(REQUIRED_FALSE.some(g=>x.release_boundary?.[g]!==false))err("release_boundary");
  if(x.owned_product_fallback?.status!=="UNKNOWN_NOT_AUTHENTICATED")err("owned_product_truth");
  if(x.pilot?.film_status!=="local review artifact, NOT HOSTED"||x.pilot?.autoplay!==false||x.pilot?.no_js!==true)err("video_status");
  if(x.attribution_contract?.net_revenue_per_1000_qualified_humans!=="NOT_COMPUTABLE")err("metric_truth");
  if(!Array.isArray(x.sources)||x.sources.length<18||!x.sources.every(s=>/^https:\/\//.test(s.url)))err("sources");
  const claimIds=(x.claims||[]).map(c=>c.id);
  if(claimIds.length<25||new Set(claimIds).size!==claimIds.length)err("claims_identity");
  const blockedTypes=new Set(["UNSUBSTANTIATED_SELLER_EFFICACY","NOT_VERIFIED","UNVERIFIED_PRICE","PROMO_TERMS_UNVERIFIED","SELLER_REFUND_PROMISE","FALSE_METRIC","SELLER_PROGRAM_PROMO"]);
  if((x.claims||[]).some(c=>blockedTypes.has(c.classification)&&c.eligible_for_sales_copy===true))err("unsupported_sales_claim");
  for(const id of ["C10","C11","C12","C13","C14","C15","C16","C17","C19","C20","C24","C25"])
    if(!(x.claims||[]).some(c=>c.id===id && c.eligible_for_sales_copy!==true))err("missing_blocked_claim:"+id);
  for(const ref of requiredArticle)if(!b.article.includes(ref))err("primary_source_missing:"+ref);
  if(!b.article.startsWith("# The Second Flash That Never Happened"))err("article_title");
  if(!b.article.includes("one flash")||!b.article.includes("two")||!b.article.includes("not a therapy trial"))err("science_scope");
  if(/\]\(https?:\/\/(?:zen12\.com|hypnosislive\.com|affiliates\.inspire3\.com)/i.test(b.article))err("editorial_merchant_link");
  for(const m of requiredHtml)if(!b.hub.includes(m))err("hub_required:"+m);
  if(/<\s*(?:script|form|iframe|video|audio|source)\b/i.test(b.hub))err("unauthorized_form_script_media");
  if(/\bonclick\s*=|\bonload\s*=|javascript:|data:text\/html|<\s*meta[^>]*http-equiv\s*=\s*["']?refresh/i.test(b.hub))err("injected_navigation");
  if(/\bautoplay\b|\bplaysinline\b/.test(b.hub))err("unauthorized_autoplay");
  if(/<\s*button\b(?![^>]*\bdisabled\b)[^>]*>/i.test(b.hub))err("enabled_button");
  const block=b.hub.match(/<div class="blocked"[^>]*>([\s\S]*?)<\/div>/i)?.[1]||"";
  if(!block.includes("disabled aria-disabled=\"true\"")||!block.includes("may earn a commission")||!block.includes("No earning link is active"))err("adjacent_disclosure_and_disabled");
  const hrefs=[...b.hub.matchAll(/href=["']([^"']+)["']/gi)].map(m=>m[1]);
  if(hrefs.some(v=>!/^#|^https:\/\/(?:finalvestige\.com|www\.nature\.com|www\.ftc\.gov)(?:\/|$)/i.test(v)))err("unauthorized_outbound_destination");
  if(/https:\/\/(?:zen12\.com|hypnosislive\.com|affiliates\.inspire3\.com)/i.test(hrefs.join("|")))err("merchant_href");
  if(/utm_[a-z]+=|[?&](?:aff|ref|hop)=/i.test(b.hub))err("injected_attribution");
  if(/<\s*(?:input|textarea|select)\b/i.test(b.hub))err("duplicate_signup");
  if(!b.plan.includes("NOT COMPUTABLE")||!b.plan.includes("HARD HOLD")||!b.plan.includes("42-second")||!b.plan.includes("no-JS"))err("experiment_contract");
  if(!b.plan.includes("https://zen12.com/hnp")||!b.plan.includes("https://zen12.com/secret/"))err("offer_page_parity");
  if(!b.plan.includes("UNKNOWN")||!b.plan.includes("TASK-008")||!b.plan.includes("Grok"))err("creator_truth");
  if(/(we earned \$|we received \$|affiliate sales confirmed|our affiliate link is live)/i.test(b.plan))err("fabricated_revenue");
  return [...new Set(errors)];
}
const copy=b=>({...b});
const mut=[
["publisher",b=>{const x=JSON.parse(b.matrix);x.partner_verified=true;b.matrix=JSON.stringify(x);}],
["only15",b=>{const x=JSON.parse(b.matrix);x.commercial_gates.pop();b.matrix=JSON.stringify(x);}],
["duplicate_gate",b=>{const x=JSON.parse(b.matrix);x.commercial_gates[0].id=x.commercial_gates[1].id;b.matrix=JSON.stringify(x);}],
["clear_gate",b=>{const x=JSON.parse(b.matrix);x.commercial_gates[0].status="PASS";b.matrix=JSON.stringify(x);}],
["verified_date",b=>{const x=JSON.parse(b.matrix);x.commercial_gates[0].verified_at="2026-11-09";b.matrix=JSON.stringify(x);}],
["merchant_enable",b=>{const x=JSON.parse(b.matrix);x.release_boundary.merchant_link_enabled=true;b.matrix=JSON.stringify(x);}],
["wp_enable",b=>{const x=JSON.parse(b.matrix);x.release_boundary.wordpress_published=true;b.matrix=JSON.stringify(x);}],
["newsletter_enable",b=>{const x=JSON.parse(b.matrix);x.release_boundary.newsletter_sent=true;b.matrix=JSON.stringify(x);}],
["analytic_enable",b=>{const x=JSON.parse(b.matrix);x.release_boundary.analytics_script_added=true;b.matrix=JSON.stringify(x);}],
["deploy_enable",b=>{const x=JSON.parse(b.matrix);x.release_boundary.merge_or_deploy=true;b.matrix=JSON.stringify(x);}],
["paid_enable",b=>{const x=JSON.parse(b.matrix);x.release_boundary.paid_service=true;b.matrix=JSON.stringify(x);}],
["claim_hour",b=>{const x=JSON.parse(b.matrix);x.claims.find(q=>q.id==="C10").eligible_for_sales_copy=true;b.matrix=JSON.stringify(x);}],
["claim_promoprice",b=>{const x=JSON.parse(b.matrix);x.claims.find(q=>q.id==="C13").eligible_for_sales_copy=true;b.matrix=JSON.stringify(x);}],
["claim_commission",b=>{const x=JSON.parse(b.matrix);x.claims.find(q=>q.id==="C15").eligible_for_sales_copy=true;b.matrix=JSON.stringify(x);}],
["claim_owned",b=>{const x=JSON.parse(b.matrix);x.claims.find(q=>q.id==="C20").eligible_for_sales_copy=true;b.matrix=JSON.stringify(x);}],
["claimed_order",b=>{const x=JSON.parse(b.matrix);x.claims.find(q=>q.id==="C24").eligible_for_sales_copy=true;b.matrix=JSON.stringify(x);}],
["owned_eligible",b=>{const x=JSON.parse(b.matrix);x.owned_product_fallback.status="VERIFIED";b.matrix=JSON.stringify(x);}],
["revenue_fake",b=>{const x=JSON.parse(b.matrix);x.attribution_contract.net_revenue_per_1000_qualified_humans="$21";b.matrix=JSON.stringify(x);}],
["video_live",b=>{const x=JSON.parse(b.matrix);x.pilot.film_status="HOSTED";b.matrix=JSON.stringify(x);}],
["autoplay_json",b=>{const x=JSON.parse(b.matrix);x.pilot.autoplay=true;b.matrix=JSON.stringify(x);}],
["missing_science",b=>{b.article=b.article.replace("https://www.nature.com/articles/35048669","[source missing]");}],
["missing_nccih",b=>{b.article=b.article.replace("https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance","[source removed]");}],
["editorial_merchant",b=>{b.article+="\n[Purchase](https://zen12.com/secret/)";}],
["enable_cta",b=>{b.hub=b.hub.replace('type="button" disabled aria-disabled="true"','type="button"');}],
["disclosure_removed",b=>{b.hub=b.hub.replace("If an authorized purchase link is eventually added, Final Vestige may earn a commission","A great deal awaits");}],
["declared_live",b=>{b.hub=b.hub.replace("No earning link is active here.","BUY NOW");}],
["direct_merchant_href",b=>{b.hub=b.hub.replace('href="https://finalvestige.com/focus/"','href="https://zen12.com/secret/"');}],
["unconsented_script",b=>{b.hub=b.hub.replace("</body>","<script src='https://tracker.example/pixel.js'></script></body>");}],
["signup",b=>{b.hub=b.hub.replace("</main>","<form><input type='email'></form></main>");}],
["forced_video",b=>{b.hub=b.hub.replace("</main>","<video autoplay src='https://example.org/zen12.mp4'></video></main>");}],
["forced_iframe",b=>{b.hub=b.hub.replace("</main>","<iframe src='https://example.org'></iframe></main>");}],
["js_click",b=>{b.hub=b.hub.replace("<button type=","<button onclick='alert(1)' type=");}],
["missing_focus",b=>{b.hub=b.hub.replace('href="https://finalvestige.com/focus/"','href="#missing"');}],
["plan_price_disappear",b=>{b.plan=b.plan.replaceAll("https://zen12.com/secret/","seller-link-removed");}],
["plan_fake_sale",b=>{b.plan+="\nWe earned $100 affiliate income.";}],
["both_bad",b=>{b.hub+="<script>malicious</script>";const x=JSON.parse(b.matrix);x.release_boundary.merchant_link_enabled=true;b.matrix=JSON.stringify(x);}]
];
function executeAll(b){const base=validateBundle(b);if(base.length)throw Error("Baseline failed: "+base.join("|"));let rejects=0;for(const [name,change] of mut){const m=copy(b);change(m);if(!validateBundle(m).length)throw Error("Did not reject "+name);rejects++;}return {baseline:"PASS",adversarial_rejected:rejects,declared_mutations:mut.length};}
module.exports={validateBundle,executeAll,mutations:mut.map(x=>x[0])};
if(typeof require==="function"&&require.main===module){const fs=require("node:fs"),p=require("node:path");const root=__dirname;const b={article:fs.readFileSync(p.join(root,"THE-SECOND-FLASH-THAT-NEVER-HAPPENED-UNPUBLISHED.md"),"utf8"),hub:fs.readFileSync(p.join(root,"MIND-ARCHIVE-WP-UNPUBLISHED-PREVIEW.html"),"utf8"),matrix:fs.readFileSync(p.join(root,"CLAIM-PROOF-OFFER-REVENUE-GATES.json"),"utf8"),plan:fs.readFileSync(p.join(root,"SINGLE-OFFER-CONVERSION-EXPERIMENT-AND-RELEASE-PLAN.md"),"utf8")};console.log(JSON.stringify(executeAll(b),null,2));}
