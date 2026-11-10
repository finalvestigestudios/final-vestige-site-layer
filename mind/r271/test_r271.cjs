"use strict";
/**
 * Mind R271 source custody tests for held R268 A/B + R257 original VTT + new R271
 * research/claim/revenue artifacts.
 * Run from repository root: node mind/r271/test_r271.cjs
 * This is NOT a browser, WordPress, merchant, WCAG, paid-sale or full-site test.
 */
const fs=require("node:fs");
const PATHS={
 article:"mind/r271/THE-VOICE-YOU-HEARD-WASNT-ON-THE-RECORDING-UNPUBLISHED.md",
 matrix:"mind/r271/CLAIMS-SELLER-APPROVAL-REVENUE-HARD-HOLD.json",
 plan:"mind/r271/OFFER-TO-VERIFIED-NET-REVENUE-ACCEPTANCE.md",
 a:"mind/r268/ZEN12-A-TEXT-UNPUBLISHED.html",
 b:"mind/r268/ZEN12-B-OPTIONAL-FILM-UNPUBLISHED.html",
 vtt:"mind/r257/zen12_42s_preview.vtt"
};
const GATES=["named_inspire3_acceptance","issued_publisher_specific_earning_url",
"exact_zen12_offer_identity","current_authenticated_cart_total",
"refund_policy_scope_and_fulfillment","approved_web_promotion_channels",
"approved_email_promotion_channels","approved_creatives_or_swipe_terms",
"product_specific_claim_substantiation","affiliate_attribution_permissions",
"ftc_adjacent_disclosure_qa","signed_out_mobile_browser_qa",
"word_press_sanitization_qa","founder_commercial_release_approval",
"independent_settled_commission_report","verified_product_sales_and_refunds_reconciliation"];
function load(){return Object.fromEntries(Object.entries(PATHS).map(([k,p])=>[k,fs.readFileSync(p,"utf8")]))}
function check(d){
 const errors=[],bad=(x,msg)=>{if(x)errors.push(msg)};
 for(const k of Object.keys(PATHS))bad(typeof d[k]!=="string"||d[k].length<500,"missing "+k);
 if(errors.length)return errors;
 let m;try{m=JSON.parse(d.matrix)}catch(e){return ["matrix invalid JSON"]}
 bad(m.schema!=="fv-mind-r271-source-claim-and-conversion-custody-v1","schema");
 bad(m.commercial_decision!=="HARD_HOLD"||m.status!=="UNPUBLISHED","decision");
 bad(!Array.isArray(m.commercial_gates)||m.commercial_gates.length!==16,"gate count");
 const ids=(m.commercial_gates||[]).map(g=>g.id);
 bad(JSON.stringify(ids)!==JSON.stringify(GATES),"exact gate identities/order");
 bad((m.commercial_gates||[]).some(g=>g.status!=="HARD_HOLD"||g.evidence!=="NOT_VERIFIED"||g.release_blocker!==true),"gate condition");
 bad(!Array.isArray(m.sources)||m.sources.length!==15||!Array.isArray(m.claims)||m.claims.length!==24,"matrix sources/claims count");
 const sourceIds=new Set((m.sources||[]).map(s=>s.id));
 bad(sourceIds.size!==15,"duplicate source IDs");
 bad((m.sources||[]).some(s=>!/^https:\/\//.test(s.url)),"non-https source");
 bad((m.claims||[]).some(c=>!c.id||!c.claim||!c.status||!Array.isArray(c.source_ids)||c.source_ids.some(i=>!sourceIds.has(i))),"invalid claim citations");
 const claimMap=Object.fromEntries((m.claims||[]).map(c=>[c.id,c]));
 for(const id of ["C09","C12","C13","C14"])bad(!/unsupported|do_not_claim/i.test(claimMap[id]?.status||""),"unsupported efficacy "+id);
 for(const id of ["C20","C21","C22"])bad(!/not_verified/i.test(claimMap[id]?.status||""),"merchant certainty "+id);
 bad(claimMap.C23?.status!=="false_static_only"||claimMap.C24?.status!=="false_event_distinction","media/conversion classification");
 const offers=Object.fromEntries((m.offers||[]).map(o=>[o.id,o]));
 const zen=offers.zen12_premium||{};
 bad(zen.decision!=="HARD_HOLD"||zen.earning_url!==null||zen.checkout_total!==null||zen.publisher_approval!=="NOT_VERIFIED"||zen.settled_commissions!==null,"zen12 offer activation");
 bad(!Array.isArray(zen.approved_channels)||zen.approved_channels.length!==0,"approved channels fabricated");
 const own=offers.owned_paid_mind_sku||{};
 bad(own.decision!=="HARD_HOLD"||own.rights_cleared!==false||own.checkout_verified!==false||own.product_id!==null,"paid fallback fabricated");
 const free=offers.focus_fieldbook||{};
 bad(free.paid_order!==false||free.type!=="FREE_EXISTING_JETPACK_FUNNEL","free represented as paid");
 const mc=m.measurement_contract||{};
 bad(mc.metric_status!=="NOT_COMPUTABLE"||mc.no_pii!==true||mc.no_new_tracking_script!==true||mc.no_client_identity_stitching!==true,"measurement contract");
 bad(!mc.events?.includes("merchant_confirmed_paid_order")||!mc.events?.includes("independent_settled_affiliate_commission")||!mc.events?.includes("affiliate_outbound_click")||!mc.events?.includes("refund"),"event distinction missing");
 bad(!mc.do_not_count_as_paid?.includes("outbound_click")||!mc.do_not_count_as_paid?.includes("email_subscribe"),"wrong purchase status");
 bad(JSON.stringify(mc.cohorts_days)!==JSON.stringify([7,30]),"cohorts");
 const release=m.release||{};
 for(const k of ["cms_write","merchant_link","site_nav_write","new_jetpack_form","blog_publish","video_autoplay","script_injection","release_approved"])bad(release[k]!==false,"release "+k);
 bad(release.source_tests_only!==true,"release source scope");
 bad(!d.article.startsWith("# The Voice You Heard Wasn't on the Recording"),"article title");
 for(const u of ["https://www.nature.com/articles/264746a0","https://pmc.ncbi.nlm.nih.gov/articles/PMC6231656/","https://pubmed.ncbi.nlm.nih.gov/28207734/","https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance","https://finalvestige.com/focus/"])bad(!d.article.includes(u),"source article "+u);
 bad(!d.article.includes("0% to 100%")||!d.article.includes("not evidence")&&!d.article.includes("not establish"),"individual differences/limitations");
 bad(/<script|<iframe|href=["']https:\/\/(?:zen12|inspire3|brainwaveshots)|utm_campaign=|rel=["']sponsored/i.test(d.article),"article commercial activation");
 for(const u of ["https://finalvestige.com/2026/11/02/change-blindness/","https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/","https://finalvestige.com/focus/"])bad(!d.plan.includes(u),"plan existing first-party "+u);
 bad(!d.plan.includes("NO VERIFIED CREATOR MATCH")||!d.plan.includes("R268")||!d.plan.includes("NOT COMPUTABLE"),"plan unknown/reuse/KPI");
 for(const [k,h] of [["a",d.a],["b",d.b]]){
  bad(!/<meta\b[^>]*name="robots"[^>]*content="noindex,nofollow"/i.test(h),k+" noindex");
  bad(!/<button\b[^>]*\bid="zen12-buy-button"[^>]*\bdisabled\b[^>]*aria-disabled="true"/i.test(h),k+" disabled purchase");
  const p=h.indexOf('id="zen12-buy-button"'),q=h.indexOf('id="affiliate-disclosure"');
  bad(p<0||q<p||q-p>850,k+" near CTA disclosure");
  bad(!/no active affiliate link here now/i.test(h),k+" inactive disclosure");
  bad(/<\s*(?:script|form|iframe|video|audio|source|track|input|img)\b/i.test(h),k+" added executable/resource/form");
  bad(/(?:@import\s|url\s*\(|\bon[a-z]+\s*=|\bautoplay\b|http-equiv\s*=)/i.test(h),k+" hidden fetch/event/autoplay");
  bad(/<a\b[^>]*href=["']https?:\/\/(?:www\.)?(?:zen12|inspire3|hypnosislive|brainwaveshots)\./i.test(h),k+" earning/merchant link");
 }
 const choice=h=>h.slice(h.indexOf('<section id="choice">'),h.indexOf("</main>",h.indexOf('<section id="choice">')));
 bad(!d.a.includes('<section id="choice">')||choice(d.a).length<4000||choice(d.a)!==choice(d.b),"A/B buyer-copy parity");
 const cues=d.vtt.split(/\n\n+/).filter(x=>x.includes("-->")).map(x=>x.split("\n").slice(1).join(" ").trim());
 bad(cues.length!==7||cues.some(x=>!d.b.includes(x)),"B transcript vs actual source VTT");
 bad(/<\s*(?:video|audio|source)\b/i.test(d.b),"B falsely playable/forced media");
 return errors;
}
function mutationCases(d){
 const j=fn=>{const x=structuredClone(d);const m=JSON.parse(x.matrix);fn(m);x.matrix=JSON.stringify(m);return x};
 const h=(key,fn)=>{const x=structuredClone(d);x[key]=fn(x[key]);return x};
 const cases=[
 ["approve-partner",j(m=>m.offers[0].publisher_approval="APPROVED")],
 ["invent-link",j(m=>m.offers[0].earning_url="https://tracking.invalid/?ref=fv")],
 ["invent-price",j(m=>m.offers[0].checkout_total=37)],
 ["invent-settlement",j(m=>m.offers[0].settled_commissions=15)],
 ["invent-channel",j(m=>m.offers[0].approved_channels=["email"])],
 ["clear-gate",j(m=>m.commercial_gates[0].status="PASS")],
 ["remove-gate",j(m=>m.commercial_gates.pop())],
 ["swap-gate",j(m=>m.commercial_gates[1].id="other")],
 ["clear-evidence",j(m=>m.commercial_gates[0].evidence="VERIFIED")],
 ["unblock-gate",j(m=>m.commercial_gates[0].release_blocker=false)],
 ["enable-cms",j(m=>m.release.cms_write=true)],
 ["enable-link",j(m=>m.release.merchant_link=true)],
 ["enable-new-form",j(m=>m.release.new_jetpack_form=true)],
 ["enable-autoplay",j(m=>m.release.video_autoplay=true)],
 ["allow-script",j(m=>m.release.script_injection=true)],
 ["release-approved",j(m=>m.release.release_approved=true)],
 ["clinical-claim",j(m=>m.claims.find(c=>c.id==="C13").status="supported_research")],
 ["zen12-claim",j(m=>m.claims.find(c=>c.id==="C12").status="supported_research")],
 ["music-efficacy",j(m=>m.claims.find(c=>c.id==="C14").status="supported_research")],
 ["claim-studied",j(m=>m.claims.find(c=>c.id==="C09").status="supported_research")],
 ["sell-free-resource",j(m=>m.offers.find(o=>o.id==="focus_fieldbook").paid_order=true)],
 ["invent-owned-rights",j(m=>m.offers.find(o=>o.id==="owned_paid_mind_sku").rights_cleared=true)],
 ["claim-numerical-kpi",j(m=>m.measurement_contract.metric_status="VERIFIED")],
 ["drop-paid-event",j(m=>m.measurement_contract.events=m.measurement_contract.events.filter(x=>x!=="merchant_confirmed_paid_order"))],
 ["count-click-as-sale",j(m=>m.measurement_contract.do_not_count_as_paid=[])],
 ["remove-source",j(m=>m.sources.pop())],
 ["remove-citation",j(m=>m.claims[0].source_ids=["UNKNOWN"])],
 ["article-claim",h("article",x=>x+'<a href="https://zen12.com/">BUY NOW</a>')],
 ["article-uncited",h("article",x=>x.replace("https://www.nature.com/articles/264746a0",""))],
 ["miss-source",h("plan",x=>x.replace("NO VERIFIED CREATOR MATCH","VERIFIED CREATOR MATCH"))],
 ["A-enable-button",h("a",x=>x.replace('type="button" disabled aria-disabled="true"','type="button" aria-disabled="true"'))],
 ["B-enable-button",h("b",x=>x.replace('type="button" disabled aria-disabled="true"','type="button" aria-disabled="true"'))],
 ["remove-A-disclosure",h("a",x=>x.replace('id="affiliate-disclosure"','id="hidden-text"'))],
 ["B-paid-link",h("b",x=>x.replace("</main>",'<a href="https://zen12.com/hnp">Buy</a></main>'))],
 ["A-hidden-fetch",h("a",x=>x.replace("</style>",'body{background:url(https://tracking.invalid/pixel)}</style>'))],
 ["B-autoplay",h("b",x=>x.replace("</main>",'<video autoplay src="evil.mp4"></video></main>'))],
 ["B-extra-form",h("b",x=>x.replace("</main>",'<form action="/subscribe"></form></main>'))],
 ["B-change-caption",h("b",x=>x.replace("Twelve minutes is an amount of time—not a measured benefit.","This cures anxiety."))],
 ["B-buyer-diverge",h("b",x=>x.replace("If the only problem is choosing background sounds","If the only problem is getting medical treatment"))],
 ];
 return cases;
}
module.exports={check,load,mutationCases,PATHS,GATES};
if(require.main===module){
 const data=load(),issues=check(data);
 if(issues.length){console.error("BASELINE FAIL",issues);process.exitCode=1}
 else{
  const mut=mutationCases(data),miss=mut.filter(([name,x])=>{const errs=check(x);if(!errs.length){console.error("ESCAPED:",name);return true}return false});
  console.log("BASELINE PASS; "+(mut.length-miss.length)+"/"+mut.length+" effective unsafe mutations rejected");
  if(miss.length)process.exitCode=1;
 }
}
