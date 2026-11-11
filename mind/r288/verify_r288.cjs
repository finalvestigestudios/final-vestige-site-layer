#!/usr/bin/env node
"use strict";
/**
 * Final Vestige Mind R288 source-integrity checks.
 * Run: node mind/r288/verify_r288.cjs
 * Dependency-free Node.js; no network, no WordPress, no merchant requests, no tracking.
 * Does NOT establish browser accessibility or commercial authorization.
 */
const fs = require("node:fs");
const path = require("node:path");
const here = __dirname;
function read(f){ return fs.readFileSync(path.join(here,f),"utf8"); }
function bundle(){
 return {
 article:read("THE-SYLLABLE-THAT-WAS-NOT-THERE-UNPUBLISHED.md"),
 hub:read("MIND-SOURCE-LED-READING-ROOM-WP-CANDIDATE-UNPUBLISHED.html"),
 matrix:read("PHONEMIC-RESTORATION-OFFER-COMPLIANCE-CLAIM-MATRIX.json"),
 plan:read("ONE-OFFER-CONVERSION-ACCEPTANCE-AND-CREATOR-HANDOFF.md"),
 a:fs.readFileSync(path.join(here,"../r284/ZEN12-BUYER-GUIDE-A-TEXT-ONLY-UNPUBLISHED.html"),"utf8"),
 b:fs.readFileSync(path.join(here,"../r284/ZEN12-BUYER-GUIDE-B-FILM-STORYBOARD-UNPUBLISHED.html"),"utf8")
 };
}
const exactGates = [
"merchant_account_acceptance","merchant_identity_matches_fv","affiliate_terms_current","permitted_traffic_channels",
"approved_presell_placement","issued_earning_url","test_tracking_accepted","offer_route_exact",
"checkout_price_and_charges","returns_eligibility_restrictions","seller_creative_rights",
"original_video_media_rights","product_specific_claims_review","adjacent_disclosure_qa",
"browser_mobile_accessibility","conversion_reporting_access","founder_live_release_approval",
"founder_commercial_activation_approval"
];
const error = (bad,msg)=>{ if(bad) throw new Error(msg); };
function verify(v){
 const M = JSON.parse(v.matrix);
 error(M.version!=="R288"||M.publication_status!=="UNPUBLISHED"||M.commercial_status!=="HARD_HOLD","draft/commercial status changed");
 error(!Array.isArray(M.sources)||M.sources.length!==20,"source count changed");
 const sourceIds=new Set(M.sources.map(s=>s.id));
 error(sourceIds.size!==20||M.sources.some(s=>!/^https:\/\/[^\s]+$/.test(s.url)),"duplicate or invalid source");
 const pinned={
 warren1970:"https://pubmed.ncbi.nlm.nih.gov/5409744/",
 samuel1981:"https://pubmed.ncbi.nlm.nih.gov/6457110/",
 shahin2009:"https://pubmed.ncbi.nlm.nih.gov/19275331/",
 leonard2016:"https://www.nature.com/articles/ncomms13619",
 ftc_endorsement:"https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking",
 ftc_health:"https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance",
 zen12_order:"https://zen12.com/getstarted", zen12_free:"https://zen12.com/welcome",
 brainwave_faq:"https://brainwaveshots.com/faq", fv_focus:"https://finalvestige.com/focus/"
 };
 for (const [id,url] of Object.entries(pinned))error(!M.sources.some(s=>s.id===id&&s.url===url),"unverified source mapping "+id);
 error(!Array.isArray(M.claims)||M.claims.length!==24,"claim count changed");
 error(new Set(M.claims.map(c=>c.id)).size!==24,"claim IDs duplicated");
 error(M.claims.some(c=>!sourceIds.has(c.source_id)),"claim points to absent source");
 error(M.claims.some(c=>c.statement.toLowerCase().includes("guarantee")&&!c.decision.startsWith("REJECT")),"unsupported guarantee allowed");
 error(M.claims.some(c=>c.decision.startsWith("SELLER")&&c.sales_eligibility!=="BLOCK"),"seller claim monetization allowed");
 error(!Array.isArray(M.commercial_gates)||M.commercial_gates.length!==18,"gate number changed");
 error(new Set(M.commercial_gates.map(g=>g.id)).size!==18,"duplicate gate");
 for(const id of exactGates)error(!M.commercial_gates.some(g=>g.id===id&&g.state==="HARD_HOLD"&&g.verified_proof===null&&g.approval_reference===null),"gate not hard-held: "+id);
 error(!Array.isArray(M.offers)||M.offers.length!==5,"offer register changed");
 const zen=M.offers.find(o=>o.id==="zen12");
 error(!zen||zen.approved_affiliate_earning_url!==null||zen.partner_accepted!==false||zen.verified_checkout_price!==null||zen.cta_state!=="DISABLED"||zen.actual_fulfillment_verified!==false,"Zen12 partner/checkout fabricated");
 const fallback=M.offers.find(o=>o.id==="fv_paid_mind_product_fallback");
 error(!fallback||fallback.sku!==null||fallback.payhip_listing_verified!==false||fallback.cta_state!=="DISABLED","owned paid product invented");
 error(M.creator_routes.length!==3||M.creator_routes.some(o=>o.grok_asset_id!==null||o.media_url!==null),"creator asset invented");
 error(M.measurement.qualified_human_sessions!==null||M.measurement.verified_paid_orders!==null||M.measurement.verified_paid_affiliate_conversions!==null||M.measurement.settled_net_revenue!==null||M.measurement.net_revenue_per_1000_qualified_human_sessions!==null,"revenue/visits fabricated");
 error(M.measurement.identifiable_data_collection!==false||M.measurement.affiliate_click_event!=="NOT_IMPLEMENTED","privacy/analytics status violated");
 error(M.experiments.variant_b_media_status!=="NOT_RENDERED_NOT_HOSTED"||M.experiments.paid_outcomes_measured!==false,"experiment/video claimed live");
 error(Object.values(M.release_controls).some(x=>x!==false),"release control enabled");
 error(v.article.split(/\s+/).length<1700||!v.article.includes("1970")||!v.article.includes("1981")||!v.article.includes("2016"),"new sourced investigation missing");
 for(const term of ["https://pubmed.ncbi.nlm.nih.gov/5409744/","https://pubmed.ncbi.nlm.nih.gov/6457110/","https://pubmed.ncbi.nlm.nih.gov/19275331/","https://www.nature.com/articles/ncomms13619","https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance"]){
  error(!v.article.includes(term),"article essential citation missing: "+term);
 }
 error(!v.article.includes("No affiliate links belong in this article"),"editorial/commercial firewall missing");
 error(!v.plan.includes("NOT COMPUTABLE")||!/not a playable movie/i.test(v.plan)||!v.plan.includes("NO MERGE"),"acceptance / missing metric semantics");
 error(!v.plan.includes("TASK-008")||!v.plan.includes("Claude")||!v.plan.includes("Grok"),"handoff/ownership missing");
 error(!v.hub.includes("id=\"fv-mind-r288\"")||!v.hub.includes("id=\"fvm-title\""),"scoped hub/landmark missing");
 for(const heading of ["Attention & Perception","History of Suggestion","Practice & Reflection","Tools Under Review"])error(!v.hub.includes(heading),"four-stream structure missing: "+heading);
 error(!v.hub.includes("https://finalvestige.com/focus/")||!v.hub.includes("puysegurs-animal-magnetism-files/"),"original existing routes missing");
 error(!v.hub.includes("If you purchase through a link on a future approved Final Vestige guide, Final Vestige may earn a commission at no additional cost to you."),"adjacent earning disclosure missing");
 const disclosurePos=v.hub.indexOf("Future earning-link disclosure:");
 const buttonPos=v.hub.indexOf('<button class="fvm-disabled"');
 error(disclosurePos<0||buttonPos<0||buttonPos-disclosurePos>550||buttonPos<disclosurePos,"commercial disclosure not adjacent to CTA");
 error(!/<button\b[^>]*\bdisabled\b[^>]*\baria-disabled="true"/i.test(v.hub),"disabled offer control missing");
 error(/<(script|iframe|form|input|video|audio|canvas|object|embed|img)\b/i.test(v.hub),"executable/third-party/form/media injected");
 error(/\bon(?:click|load|error|submit|mouseover|focus|pointerdown)\s*=/i.test(v.hub),"event attribute injection");
 error(/(?:javascript:|data:text\/html|https?:\/\/[^\s"'<>]*?(?:affiliate|tracker|pixel\.))/i.test(v.hub),"unsafe scheme or pixel");
 const attr=[...v.hub.matchAll(/\bhref\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))/gi)];
 error(attr.length<4,"reader links missing");
 for(const m of attr){let u=m[1]||m[2]||m[3],test=u.replace(/&amp;/g,"&").replace(/&#(\d+);/g,(_,n)=>String.fromCharCode(Number(n)));try{test=decodeURIComponent(test);}catch{}
  error(!(/^#[a-z0-9_-]+$/i.test(test)||/^https:\/\/finalvestige\.com\/[a-z0-9_/%.-]*\/?$/i.test(test)),"external/unsafe hub href "+test);
 }
 for(const ab of ["a","b"]){const h=v[ab];error(!h.includes('noindex,nofollow')||!/<button\b[^>]*\bdisabled\b/i.test(h)||!h.includes("Prospective affiliate disclosure"),"inherited buyer guide activation "+ab);error(!h.includes("fewer than half of the ordered items have been downloaded"),"refund restriction lost "+ab);error(/<script\b|<form\b/i.test(h),"inherited page gained scripts/form "+ab);}
 error(/<video\b/i.test(v.b)||!v.b.includes("42-second"),"B static video status unexpectedly changed");
 return true;
}
const clone=v=>({...v});
function mutate(v,key,fn){let o=clone(v);o[key]=fn(o[key]);return o;}
function editM(v,fn){return mutate(v,"matrix",raw=>{let m=JSON.parse(raw);fn(m);return JSON.stringify(m);});}
function editH(v,fn){return mutate(v,"hub",fn);}
function editP(v,fn){return mutate(v,"plan",fn);}
function editA(v,fn){return mutate(v,"article",fn);}
function mutants(){
 return [
 ["approve_partner",v=>editM(v,m=>m.offers[0].partner_accepted=true)],
 ["issue_earning_url",v=>editM(v,m=>m.offers[0].approved_affiliate_earning_url="https://example.com/?aff=123")],
 ["set_affiliate_price",v=>editM(v,m=>m.offers[0].verified_checkout_price=1)],
 ["fake_fulfillment",v=>editM(v,m=>m.offers[0].actual_fulfillment_verified=true)],
 ["unlock_purchase_button",v=>editM(v,m=>m.offers[0].cta_state="ACTIVE")],
 ["add_paid_sku",v=>editM(v,m=>m.offers[4].sku="FV-TOTALLY-UNVERIFIED")],
 ["pretend_payhip",v=>editM(v,m=>m.offers[4].payhip_listing_verified=true)],
 ["set_sales",v=>editM(v,m=>m.measurement.verified_paid_orders=1)],
 ["set_commission",v=>editM(v,m=>m.measurement.settled_net_revenue=2)],
 ["set_visits",v=>editM(v,m=>m.measurement.qualified_human_sessions=400)],
 ["set_roi",v=>editM(v,m=>m.measurement.net_revenue_per_1000_qualified_human_sessions=4)],
 ["invent_media_id",v=>editM(v,m=>m.creator_routes[0].grok_asset_id="invented")],
 ["invent_media_url",v=>editM(v,m=>m.creator_routes[0].media_url="https://youtube.com/watch?v=fake")],
 ["claim_live_test",v=>editM(v,m=>m.experiments.paid_outcomes_measured=true)],
 ["claim_playable",v=>editM(v,m=>m.experiments.variant_b_media_status="HOSTED")],
 ["enable_merchant_click",v=>editM(v,m=>m.measurement.affiliate_click_event="LIVE")],
 ["collect_pii",v=>editM(v,m=>m.measurement.identifiable_data_collection=true)],
 ["gate_partner_yes",v=>editM(v,m=>m.commercial_gates[0].state="PASS")],
 ["gate_proof_fake",v=>editM(v,m=>m.commercial_gates[1].verified_proof="yes")],
 ["delete_gate",v=>editM(v,m=>m.commercial_gates.pop())],
 ["duplicate_gate",v=>editM(v,m=>m.commercial_gates[0].id=m.commercial_gates[1].id)],
 ["release_now",v=>editM(v,m=>m.release_controls.deploy=true)],
 ["corrupt_source_url",v=>editM(v,m=>m.sources.find(s=>s.id==="warren1970").url="https://example.com/unverified")],
 ["delete_claim_source",v=>editM(v,m=>m.claims[0].source_id="source_does_not_exist")],
 ["allow_seller_claim",v=>editM(v,m=>m.claims.find(c=>c.id==="R08").sales_eligibility="COMMERCIAL_ALLOWED")],
 ["allow_guaranteed_result",v=>editM(v,m=>m.claims.find(c=>c.id==="R13").decision="ALLOW_SCIENTIFIC_PROOF")],
 ["remove_article_ftc",v=>editA(v,s=>s.replace("https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance",""))],
 ["short_article",v=>editA(v,s=>s.slice(0,1200))],
 ["erase_ed_commerce_wall",v=>editA(v,s=>s.replace("No affiliate links belong in this article","affiliate links welcomed"))],
 ["remove_hub_disclosure",v=>editH(v,s=>s.replace("Future earning-link disclosure:","Disclosure:"))],
 ["remove_hub_disabled",v=>editH(v,s=>s.replace(' disabled aria-disabled="true"',''))],
 ["insert_merchant_anchor",v=>editH(v,s=>s+'<a href="https://zen12.com/getstarted">Buy Zen12</a>')],
 ["inject_script",v=>editH(v,s=>s+'<script>alert(1)</script>')],
 ["inject_email_form",v=>editH(v,s=>s+'<form><input type="email"></form>')],
 ["inject_autoplay",v=>editH(v,s=>s+'<video autoplay src="https://example.com/x.mp4"></video>')],
 ["inject_tracking_pixel",v=>editH(v,s=>s+'<img src="https://tracker.example/pixel" width="1">')],
 ["event_handler",v=>editH(v,s=>s.replace('<section id="fv-mind-r288"','<section onclick="bad()" id="fv-mind-r288"'))],
 ["javascript_href",v=>editH(v,s=>s+'<a href="javascript:alert(1)">unsafe</a>')],
 ["encoded_javascript_href",v=>editH(v,s=>s+'<a href="java%73cript:alert(1)">unsafe</a>')],
 ["external_promo_link",v=>editH(v,s=>s+'<a href="https://affiliates.inspire3.com/">merchant</a>')],
 ["remove_focus",v=>editH(v,s=>s.replaceAll("https://finalvestige.com/focus/","/dead-link"))],
 ["remove_study_stream",v=>editH(v,s=>s.replace("History of Suggestion","History (removed)"))],
 ["remove_source_dossier",v=>editH(v,s=>s.replaceAll("puysegurs-animal-magnetism-files/","broken/"))],
 ["erase_plan_metric",v=>editP(v,s=>s.replace("NOT COMPUTABLE","ZERO"))],
 ["erase_plan_release",v=>editP(v,s=>s.replace("NO MERGE","MERGE OK"))],
 ["change_parent_offer",v=>editM(v,m=>m.offers.pop())],
 ["turn_B_into_film",v=>mutate(v,"b",s=>s+'<video src="fake.mp4"></video>')],
 ["erase_refund_A",v=>mutate(v,"a",s=>s.replace("fewer than half of the ordered items have been downloaded","any downloads okay"))],
 ["erase_refund_B",v=>mutate(v,"b",s=>s.replace("fewer than half of the ordered items have been downloaded","any downloads okay"))]
 ];
}
function run(){
 const v=bundle();verify(v);let passed=0;for(const [label,transform] of mutants()){let blocked=false;try{verify(transform(v));}catch(e){blocked=true;}if(!blocked)throw new Error("MUTATION NOT REJECTED: "+label);passed++;}
 console.log("R288 SOURCE BASELINE PASS; "+passed+"/"+mutants().length+" unsafe mutants rejected; 18/18 gates HARD_HOLD");
 console.log("No live browser, WordPress, checkout, video rendering or settlement tested.");
}
if(require.main===module)run();
module.exports={verify,mutants,bundle,run};
